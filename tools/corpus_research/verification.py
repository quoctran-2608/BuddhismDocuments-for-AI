"""Phase A: JSON-compatible evidence, source gate and quotation verification.

Usage: make_evidence_record(bundle_or_pointer, contract, evidence_id=...), then
evidence_gate(candidate, contract, opened_source). Only the gate's VERIFIED
result contains an Evidence Record; indexed text/context remain candidate data.

The contract is keyed by corpus, with repository, repo_path, source_sha and
evidence_class from project config/manifest. It is trusted configuration, NOT
metadata copied from the candidate. An opened_source is a separate reader's
observation: repository, source_sha, source_path, full UTF-8 content, optional
source_blob_sha, location, excerpt_range and context_range. Ranges are [start,
end] character offsets in content; context must contain the excerpt. Location
metadata must come from inspecting the source, not from echoing the candidate.
Structured-source readers must resolve their markup/identifiers themselves;
this module does not certify arbitrary TEI/JSON locations from string matches.

Core functions perform no I/O. Provider observations and semantic paraphrase
reviews are trust boundaries, not cryptographic attestations. A separate review
must bind the exact quotation/source_text and name a reviewer and rationale;
the machine checks that binding, not semantic truth. Without it a declared
paraphrase stays UNVERIFIED. No candidate-supplied verification label is trusted.
read_local_source is an optional Git adapter; it reads the pinned blob, never
the mutable working-tree file. A reader still has to supply resolved location
and ranges before the gate can pass.
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


def verify_quote(
    quotation: str | None,
    source_text: str | None,
    *,
    kind: str = "direct",
    paraphrase_review: dict | None = None,
) -> dict:
    """Return one of the five quote statuses and explicit presentation rights.

    paraphrase_review is a separate trusted assessment with quotation,
    source_text, supported (bool), reviewer and rationale. It is never read
    from an evidence candidate. Missing/stale/incomplete reviews cannot pass.
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
            if (
                review.get("quotation") == quotation
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
) -> dict:
    """Recompute every check. REJECTED/UNVERIFIED never expose verified evidence."""
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
            quote = verify_quote(candidate.get("quotation"), content[excerpt[0]:excerpt[1]], kind=quote_kind, paraphrase_review=paraphrase_review)
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

    Returned content alone is insufficient: independently resolve location and
    excerpt/context ranges from that content before calling evidence_gate.
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
