"""Phase A: JSON-compatible evidence, source gate and quotation verification.

Usage: make_evidence_record(bundle_or_pointer, contract, evidence_id=...), then
evidence_gate(candidate, contract, opened_source). Only the gate's VERIFIED
result contains an Evidence Record; indexed text/context remain candidate data.

The contract is keyed by corpus, with repository, repo_path, source_sha and
evidence_class from project config/manifest. It is trusted configuration, NOT
metadata copied from the candidate. An opened_source is an UNTRUSTED reader's
observation: repository, source_sha, source_path, full UTF-8 content, optional
source_blob_sha, location, excerpt_range and context_range. Ranges are [start,
end] character offsets in content; context must contain the excerpt. Location
metadata must come from inspecting the source, not from echoing the candidate.
Structured-source readers must resolve their markup/identifiers themselves;
this module does not certify arbitrary TEI/JSON locations from string matches.

JSON data cannot establish its own authenticity. The host application must wire
source_reader and review_reader as executable capabilities OUTSIDE candidate,
opened_source, review and serialized contract data. Never let model-generated
code or JSON choose these capabilities or the trusted contract. source_reader
receives only a source identity/locator request, independently reads that exact
pinned revision, and resolves location/ranges from its content. It must not echo
opened_source or read a mutable file as though it were pinned. review_reader
receives only a review ID and retrieves an already approved assessment from an
authenticated reviewer/approval channel; an arbitrary review JSON file or an AI
proposal is not such a channel. No built-in remote reader or approval channel
is claimed here. Missing capabilities leave the gate UNVERIFIED.

Core code performs no direct I/O; optional callbacks are the host's execution
boundary and may perform I/O. Inputs/results remain JSON data; capabilities are
not serialized. read_local_source is an optional Git adapter: rev-parse binds
commit/path to a blob, cat-file reads it, never the mutable working-tree file.
Wire it inside source_reader, followed by a source-specific location resolver.
An earlier read_local_source result passed as JSON alone cannot verify a source.

VERIFIED means source identity, location and applicable quotation checks passed.
It grants NO claim support level or primary-witness authority. evidence_class,
text_role and witness retain their separate meanings; Stage B is not implemented.
"""

from __future__ import annotations

import copy
import hashlib
import re
import unicodedata


EVIDENCE_FIELDS = (
    "evidence_id", "run_id", "corpus", "repository", "source_sha",
    "source_blob_sha", "source_path", "indexed_source_path", "work_id",
    "segment_id", "sequence_no", "language", "evidence_class", "text_role",
    "witness", "quotation", "context", "quote_verification_status",
    "retrieval_query", "match_reasons", "relation_ids", "limitations",
)
LOCATION_FIELDS = ("work_id", "segment_id", "sequence_no", "language", "text_role", "witness")
DIRECT_QUOTE_STATUSES = {"VERIFIED_EXACT", "VERIFIED_NORMALIZED"}


def github_source_path(indexed_path: str, repo_path: str) -> str:
    """Shared locator/index path conversion, preserving existing behavior."""
    prefix = f"{repo_path}/"
    if not indexed_path.startswith(prefix):
        raise ValueError(f"indexed source path is outside mapped repository: {indexed_path}")
    source_path = indexed_path.removeprefix(prefix)
    if not source_path:
        raise ValueError(f"empty source path after repository prefix: {indexed_path}")
    return source_path


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _path(value: object) -> bool:
    return (
        _text(value) and not value.startswith("/")
        and not any(char in value for char in "\\:\x00")
        and all(part not in {"", ".", ".."} for part in value.split("/"))
    )


def git_blob_sha(content: bytes) -> str:
    """Git's blob object ID, equivalent to git hash-object for these bytes."""
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def _safe_normalize(text: str) -> str:
    # Retrieval's casefold/diacritic/compact normalization is NOT safe for quotes.
    return " ".join(unicodedata.normalize("NFC", text).split())


def _contains(source: str, quotation: str) -> bool:
    # Avoid certifying "permanent" from "impermanent". CJK excerpts need no
    # Latin word boundary, and punctuation/accents must stay unchanged.
    def word_part(char: str) -> bool:
        code = ord(char)
        cjk = (
            0x3400 <= code <= 0x4DBF or 0x4E00 <= code <= 0x9FFF
            or 0xF900 <= code <= 0xFAFF or 0x20000 <= code <= 0x2FA1F
        )
        return not cjk and (char.isalnum() or unicodedata.category(char).startswith("M"))

    for match in re.finditer(re.escape(quotation), source):
        start, end = match.span()
        joins_left = start > 0 and word_part(source[start - 1]) and word_part(quotation[0])
        joins_right = end < len(source) and word_part(source[end]) and word_part(quotation[-1])
        if not joins_left and not joins_right:
            return True
    return False


def _read_capability(reader, request) -> dict:
    """Invoke host-wired authority; unavailable/failed capabilities fail closed."""
    if callable(reader):
        try:
            result = reader(copy.deepcopy(request))
            return copy.deepcopy(result) if isinstance(result, dict) else {}
        except Exception:
            # Tool/transport/resolver failures cannot confer verification rights.
            return {}
    return {}


def verify_quote(
    quotation: str | None,
    source_text: str | None,
    *,
    kind: str = "direct",
    paraphrase_review: dict | None = None,
    review_reader=None,
) -> dict:
    """Return one of the five quote statuses and explicit presentation rights.

    paraphrase_review is a proposal with review_id, quotation, source_text,
    supported (bool), reviewer and rationale. Only review_reader(review_id),
    wired by the host to an authenticated approval channel, can establish an
    approved assessment. Both must match exactly, including reviewer/content.
    This checks approval/binding, not semantic truth; absent approval cannot pass.
    """
    status = "UNVERIFIED"
    if _text(quotation) and _text(source_text):
        if kind == "direct":
            if _contains(source_text, quotation):
                status = "VERIFIED_EXACT"
            elif _contains(_safe_normalize(source_text), _safe_normalize(quotation)):
                status = "VERIFIED_NORMALIZED"
            else:
                status = "QUOTE_MISMATCH"
        elif kind == "paraphrase" and isinstance(paraphrase_review, dict):
            review = paraphrase_review
            approved = _read_capability(review_reader, review["review_id"]) if _text(review.get("review_id")) else {}
            fields = ("review_id", "quotation", "source_text", "supported", "reviewer", "rationale")
            if (
                approved and all(key in review and key in approved for key in fields)
                and all(review[key] == approved[key] and type(review[key]) is type(approved[key]) for key in fields)
                and review.get("quotation") == quotation
                and review.get("source_text") == source_text
                and _text(review.get("reviewer")) and _text(review.get("rationale"))
            ):
                if review.get("supported") is True:
                    status = "PARAPHRASE"
                elif review.get("supported") is False:
                    status = "QUOTE_MISMATCH"
    return {
        "status": status,
        "direct_quote_allowed": status in DIRECT_QUOTE_STATUSES,
        "paraphrase_allowed": status == "PARAPHRASE",
    }


def make_evidence_record(
    payload: dict,
    source_contract: dict,
    *,
    evidence_id: str,
    quotation: str | None = None,
    run_id: str | None = None,
) -> dict:
    """Prepare a CANDIDATE; neither indexed prose nor labels verify a source."""
    bundled = isinstance(payload.get("record"), dict)
    row = payload["record"] if bundled else payload
    candidate = {key: copy.deepcopy(row.get(key)) for key in EVIDENCE_FIELDS}
    corpus = row.get("corpus")
    mapping = source_contract.get(corpus, {}) if isinstance(corpus, str) else {}
    mapping = mapping if isinstance(mapping, dict) else {}
    if bundled:
        candidate["indexed_source_path"] = row.get("source_path")
        candidate["repository"] = mapping.get("repository")
        try:
            candidate["source_path"] = github_source_path(
                row.get("source_path", ""), mapping.get("repo_path", ""),
            )
        except (ValueError, AttributeError):
            candidate["source_path"] = None
    candidate.update(
        evidence_id=evidence_id, run_id=run_id, quotation=quotation,
        context=None, quote_verification_status="UNVERIFIED", state="CANDIDATE",
    )
    candidate["indexed_text"] = copy.deepcopy(row.get("raw_text"))
    candidate["indexed_context"] = {
        "before": copy.deepcopy(payload.get("context_before")),
        "after": copy.deepcopy(payload.get("context_after")),
    } if bundled else None
    candidate["indexed_variants"] = copy.deepcopy(payload.get("variants")) if bundled else None
    return candidate


def _range(content: str, value: object) -> tuple[int, int] | None:
    if (
        isinstance(value, (list, tuple)) and len(value) == 2
        and all(type(x) is int for x in value)
        and 0 <= value[0] < value[1] <= len(content)
    ):
        return value[0], value[1]
    return None


def evidence_gate(
    candidate: dict,
    source_contract: dict,
    opened_source: dict | None = None,
    *,
    use: str = "textual",
    mode: str = "quick",
    quote_kind: str = "direct",
    paraphrase_review: dict | None = None,
    source_reader=None,
    review_reader=None,
) -> dict:
    """Recompute checks; VERIFIED is source verification, never claim acceptance.

    source_reader(request) must independently return the pinned source snapshot
    (same fields as opened_source), with source-resolved location/ranges. The
    request contains corpus/repository/source_sha/source_path plus work/segment/
    sequence selectors, never proposed content, hashes, roles or trust flags.
    Without this host-controlled execution boundary even consistent JSON stays
    UNVERIFIED. REJECTED/UNVERIFIED never expose verified evidence.
    """
    checks: dict[str, dict] = {}

    def check(name: str, status: str, detail: str = "", *, required: bool = True) -> None:
        checks[name] = {"status": status, "detail": detail, "required": required}

    def compare(name: str, expected: object, observed: object) -> None:
        if observed is None:
            check(name, "UNVERIFIED", "reader did not supply this observation")
        else:
            check(name, "PASS" if expected == observed else "FAIL", "compared with source reader")

    required = ("evidence_id", "corpus", "repository", "evidence_class", "text_role")
    check("required_provenance", "PASS" if all(_text(candidate.get(k)) for k in required) else "FAIL")
    check("source_sha_format", "PASS" if _sha(candidate.get("source_sha")) else "FAIL")
    check("source_path_format", "PASS" if _path(candidate.get("source_path")) else "FAIL")
    check("mode", "PASS" if mode in {"quick", "research"} else "FAIL")
    check("run_id", "FAIL" if mode == "research" and not _text(candidate.get("run_id")) else "PASS")
    check("use", "PASS" if use in {"textual", "relationship"} else "FAIL")
    role = candidate.get("text_role")
    check("text_role_known", "PASS" if _text(role) and role != "unspecified" else "FAIL")
    optional_text_fields = ("work_id", "segment_id", "language", "witness")
    sequence = candidate.get("sequence_no")
    location_valid = all(candidate.get(k) is None or _text(candidate[k]) for k in optional_text_fields)
    location_valid = location_valid and (sequence is None or (type(sequence) is int and sequence >= 0))
    check("location_format", "PASS" if location_valid else "FAIL")
    corpus = candidate.get("corpus")
    mapping = source_contract.get(corpus) if isinstance(corpus, str) else None
    check("corpus_mapping", "PASS" if isinstance(mapping, dict) and _path(mapping.get("repo_path")) else "FAIL")
    if isinstance(mapping, dict):
        compare("repository_mapping", mapping.get("repository"), candidate.get("repository"))
        compare("evidence_class", mapping.get("evidence_class"), candidate.get("evidence_class"))
        if _sha(mapping.get("source_sha")):
            compare("pinned_source_sha", mapping["source_sha"], candidate.get("source_sha"))
        else:
            check("pinned_source_sha", "UNVERIFIED", "trusted pinned revision unavailable")
        indexed = candidate.get("indexed_source_path")
        if indexed is not None:
            expected = f"{mapping.get('repo_path')}/{candidate.get('source_path')}"
            compare("indexed_source_path", expected, indexed)
    if use == "textual" and candidate.get("evidence_class") == "metadata_relationship":
        check("textual_source", "FAIL", "relationship metadata is not textual evidence")

    source = opened_source if isinstance(opened_source, dict) else {}
    content = source.get("content")
    source_opened = isinstance(content, str) and bool(content)
    check("source_opened", "PASS" if source_opened else "UNVERIFIED", "requires full source content from a reader")
    for key in ("repository", "source_sha", "source_path"):
        compare(f"opened_{key}", candidate.get(key), source.get(key))
    location = source.get("location")
    location = location if isinstance(location, dict) else {}
    for key in LOCATION_FIELDS:
        value = candidate.get(key)
        if value is None and key in location and location[key] is None:
            check(f"location_{key}", "NOT_APPLICABLE")
        elif key not in location:
            check(f"location_{key}", "UNVERIFIED", "location must be resolved by the source reader")
        else:
            # Includes missing candidate fields when the reader identifies them.
            same = value == location[key] and type(value) is type(location[key])
            check(f"location_{key}", "PASS" if same else "FAIL")

    # Neither candidate/provider hashes nor their matching identity labels bind
    # bytes to a commit. Re-read through authority wired by the application.
    basis = {}
    if (
        isinstance(mapping, dict) and _path(mapping.get("repo_path"))
        and _sha(mapping.get("source_sha")) and _path(candidate.get("source_path"))
        and candidate.get("repository") == mapping.get("repository")
        and candidate.get("source_sha") == mapping.get("source_sha")
    ):
        request = {
            "corpus": corpus, "repository": mapping.get("repository"),
            "source_sha": mapping["source_sha"], "source_path": candidate["source_path"],
            **{key: candidate.get(key) for key in ("work_id", "segment_id", "sequence_no")},
        }
        basis = _read_capability(source_reader, request)
    anchored = _text(basis.get("content"))
    check("independent_source", "PASS" if anchored else "UNVERIFIED", "requires an independent pinned read through host-wired authority")
    if anchored:
        for key in ("repository", "source_sha", "source_path"):
            compare(f"independent_{key}", request[key], basis.get(key))
        compare("independent_content", basis["content"], content)
        independent_blob = basis.get("source_blob_sha")
        if independent_blob is not None:
            check("independent_blob", "PASS" if _sha(independent_blob) and git_blob_sha(basis["content"].encode("utf-8")) == independent_blob else "FAIL")
        elif mapping.get("blob_check_required") is True:
            check("independent_blob", "UNVERIFIED", "mandatory independent blob identity unavailable")
        basis_location = basis.get("location")
        basis_location = basis_location if isinstance(basis_location, dict) else {}
        for key in LOCATION_FIELDS:
            if key not in basis_location or key not in location:
                check(f"independent_location_{key}", "UNVERIFIED")
            else:
                same = basis_location[key] == location[key] and type(basis_location[key]) is type(location[key])
                check(f"independent_location_{key}", "PASS" if same else "FAIL")
        for key in ("excerpt_range", "context_range"):
            expected = _range(basis["content"], basis.get(key))
            observed = _range(content, source.get(key)) if source_opened else None
            check(f"independent_{key}", "UNVERIFIED" if expected is None or observed is None else ("PASS" if expected == observed else "FAIL"))

    excerpt = context = None
    quote = verify_quote(None, None)
    if source_opened:
        actual_blob = git_blob_sha(content.encode("utf-8"))
        blob_required = source.get("blob_check_required") is True or (
            isinstance(mapping, dict) and mapping.get("blob_check_required") is True
        )
        for name, blob in (("expected_blob", candidate.get("source_blob_sha")), ("opened_blob", source.get("source_blob_sha"))):
            if blob is None:
                # A missing candidate blob is optional: a pinned source reader
                # may independently resolve it. Mandatory provider checks are
                # configured outside the candidate and cannot be skipped by it.
                check(name, "UNVERIFIED", "blob identity unavailable", required=name == "opened_blob" and blob_required)
            else:
                check(name, "PASS" if _sha(blob) and actual_blob == blob else "FAIL", "Git blob hash computed from full UTF-8 source bytes")
        excerpt = _range(content, source.get("excerpt_range"))
        context = _range(content, source.get("context_range"))
        for name, span in (("excerpt_range", excerpt), ("context_range", context)):
            check(name, "PASS" if span else ("UNVERIFIED" if source.get(name) is None else "FAIL"))
        if excerpt and context:
            check("context_contains_excerpt", "PASS" if context[0] <= excerpt[0] and excerpt[1] <= context[1] else "FAIL")
        if excerpt:
            quote = verify_quote(candidate.get("quotation"), content[excerpt[0]:excerpt[1]], kind=quote_kind, paraphrase_review=paraphrase_review, review_reader=review_reader)
    if use == "relationship" and candidate.get("quotation") is None:
        check("quotation", "NOT_APPLICABLE")
    else:
        quote_status = quote["status"]
        check("quotation", "FAIL" if quote_status == "QUOTE_MISMATCH" else ("UNVERIFIED" if quote_status == "UNVERIFIED" else "PASS"))

    failed = any(item["status"] == "FAIL" for item in checks.values())
    pending = any(item["required"] and item["status"] == "UNVERIFIED" for item in checks.values())
    status = "REJECTED" if failed else ("UNVERIFIED" if pending else "VERIFIED")
    # Matching supplied wording does not grant presentation rights while its
    # provenance/location still fails the evidence gate.
    quote = {
        **quote,
        "direct_quote_allowed": status == "VERIFIED" and quote["direct_quote_allowed"],
        "paraphrase_allowed": status == "VERIFIED" and quote["paraphrase_allowed"],
    }
    evidence = None
    if status == "VERIFIED":
        evidence = {key: copy.deepcopy(candidate.get(key)) for key in EVIDENCE_FIELDS}
        evidence["context"] = {
            "before": content[context[0]:excerpt[0]],
            "text": content[excerpt[0]:excerpt[1]],
            "after": content[excerpt[1]:context[1]],
        }
        evidence["quote_verification_status"] = quote["status"]
        evidence["state"] = "VERIFIED"
    return {"status": status, "source_opened": source_opened, "checks": checks, "quote": quote, "evidence": evidence}


def read_local_source(root, candidate: dict, source_contract: dict) -> dict:
    """Optional reader using the locator's pinned Git blob resolution.

    Returned JSON alone is insufficient. The host must invoke this inside
    source_reader(request) and independently resolve location and excerpt/context
    ranges from the returned pinned content, rather than echoing opened_source.
    Missing objects/capabilities remain UNVERIFIED; no downloads are attempted.
    """
    from pathlib import Path
    import subprocess
    from .pointer_export import _source_blob_sha

    result = {key: candidate.get(key) for key in ("repository", "source_sha", "source_path")}
    result.update(content=None, source_blob_sha=None, blob_check_required=True)
    corpus = candidate.get("corpus")
    mapping = source_contract.get(corpus, {}) if isinstance(corpus, str) else {}
    mapping = mapping if isinstance(mapping, dict) else {}
    if (
        not _path(mapping.get("repo_path")) or not _path(candidate.get("source_path"))
        or not _sha(candidate.get("source_sha"))
        or candidate.get("source_sha") != mapping.get("source_sha")
        or candidate.get("repository") != mapping.get("repository")
    ):
        result["error"] = "invalid source contract"
        return result
    root = Path(root).resolve()
    repo = (root / mapping["repo_path"]).resolve()
    if not repo.is_relative_to(root):
        result["error"] = "mapped repository is outside workspace"
        return result
    try:
        blob = _source_blob_sha(root, mapping, candidate["source_sha"], candidate["source_path"], {})
        if blob is None:
            result["error"] = "pinned Git object unavailable"
            return result
        opened = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "blob", blob],
            capture_output=True, check=False,
        )
        if opened.returncode:
            result["error"] = "cannot read pinned source blob"
        else:
            result.update(content=opened.stdout.decode("utf-8"), source_blob_sha=blob)
    except (OSError, UnicodeError) as exc:
        result["error"] = str(exc)
    return result
