from __future__ import annotations

import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from corpus_research.verification import (
    evidence_gate, git_blob_sha, github_source_path, make_evidence_record,
    read_local_source, verify_quote,
)


ROOT = Path(__file__).resolve().parents[1]
QUOTE = "All conditioned things are impermanent."
LOCATION = {
    "work_id": "fixture1", "segment_id": "fixture1:1", "sequence_no": 1,
    "language": "en", "text_role": "translation_main", "witness": "Fixture edition",
}
# The source itself carries its location/role, so readers need not copy them
# from an index candidate. Fixtures are invented software data, not corpus proof.
CONTENT = json.dumps(LOCATION, sort_keys=True) + "\nBefore the passage.\n" + QUOTE + "\nAfter the passage.\n"
CONTRACT = {
    "fixture": {
        "repository": "fixture-org/source", "repo_path": "fixture/source",
        "source_sha": "1" * 40, "evidence_class": "authoritative_structured",
    },
}


def resolve_fixture(snapshot: dict) -> dict:
    """A tiny independent fixture reader; not a generic upstream parser."""
    result = copy.deepcopy(snapshot)
    content = result["content"]
    result["location"] = json.loads(content.splitlines()[0])
    start = content.index(QUOTE)
    result["excerpt_range"] = [start, start + len(QUOTE)]
    result["context_range"] = [content.index("Before the passage."), len(content)]
    return result


class VerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = copy.deepcopy(CONTRACT)
        self.pointer = {
            "corpus": "fixture", "repository": "fixture-org/source",
            "source_sha": "1" * 40, "source_path": "texts/work.txt",
            "indexed_source_path": "fixture/source/texts/work.txt",
            "source_blob_sha": git_blob_sha(CONTENT.encode("utf-8")),
            "evidence_class": "authoritative_structured", **LOCATION,
            "relation_ids": ["fixture-relation"], "match_reasons": ["exact"],
        }
        self.candidate = make_evidence_record(
            self.pointer, self.contract, evidence_id="ev-1", quotation=QUOTE,
        )
        self.source = resolve_fixture({
            "repository": "fixture-org/source", "source_sha": "1" * 40,
            "source_path": "texts/work.txt", "content": CONTENT,
            "source_blob_sha": git_blob_sha(CONTENT.encode("utf-8")),
        })
        # Independent test oracle, configured by the test host, never taken from
        # candidate/provider input. Actual pinned reads are tested with Git below.
        self.approved_source = copy.deepcopy(self.source)

    def read_fixture_source(self, request) -> dict | None:
        if all(request.get(key) == self.approved_source[key] for key in ("repository", "source_sha", "source_path")):
            return copy.deepcopy(self.approved_source)
        return None

    def configure_fixture_location(self, location: dict) -> dict:
        """Configure a different tiny source in the host's independent oracle."""
        content = json.dumps(location, sort_keys=True) + "\nBefore the passage.\n" + QUOTE + "\nAfter the passage.\n"
        self.approved_source = resolve_fixture({
            **self.approved_source, "content": content,
            "source_blob_sha": git_blob_sha(content.encode("utf-8")),
        })
        return copy.deepcopy(self.approved_source)

    def gate(self, candidate=None, source=None, **kwargs) -> dict:
        kwargs.setdefault("source_reader", self.read_fixture_source)
        return evidence_gate(
            self.candidate if candidate is None else candidate,
            self.contract, self.source if source is None else source, **kwargs,
        )

    def test_opened_source_passes_and_context_comes_from_source(self) -> None:
        result = self.gate()
        self.assertEqual(result["status"], "VERIFIED")
        record = result["evidence"]
        self.assertEqual(record["quote_verification_status"], "VERIFIED_EXACT")
        self.assertEqual(record["context"], {
            "before": "Before the passage.\n", "text": QUOTE,
            "after": "\nAfter the passage.\n",
        })
        for key in LOCATION:
            self.assertEqual(record[key], LOCATION[key])
        self.assertNotIn("indexed_text", record)

    def test_pointer_and_index_hit_remain_candidates_without_opened_source(self) -> None:
        bundle = {
            "found": True,
            "record": {**self.pointer, "source_path": self.pointer["indexed_source_path"], "raw_text": "Unverified index prose."},
            "context_before": [{"raw_text": "Unverified index context."}],
            "context_after": [], "variants": [{"reading": "candidate variant"}],
        }
        for payload in (self.pointer, bundle):
            with self.subTest(bundled="record" in payload):
                record = make_evidence_record(payload, self.contract, evidence_id="ev-1", quotation=QUOTE)
                self.assertEqual(record["state"], "CANDIDATE")
                self.assertIsNone(record["context"])
                result = evidence_gate(record, self.contract)
                self.assertEqual(result["status"], "UNVERIFIED")
                self.assertIsNone(result["evidence"])
        self.assertEqual(record["indexed_text"], "Unverified index prose.")
        self.assertEqual(record["indexed_variants"], bundle["variants"])
        result = self.gate(record)
        self.assertEqual(result["evidence"]["context"]["before"], "Before the passage.\n")

    def test_required_provenance_missing_is_rejected(self) -> None:
        for key in ("evidence_id", "corpus", "repository", "source_sha", "source_path", "evidence_class", "text_role"):
            with self.subTest(key=key):
                record = copy.deepcopy(self.candidate)
                record[key] = None
                self.assertEqual(self.gate(record)["status"], "REJECTED")

    def test_wrong_repository_sha_path_and_segment_are_rejected(self) -> None:
        for key, wrong in (
            ("repository", "other/source"), ("source_sha", "2" * 40),
            ("source_path", "texts/other.txt"), ("segment_id", "fixture1:2"),
            ("work_id", "fixture2"), ("sequence_no", 2),
        ):
            with self.subTest(key=key):
                record = copy.deepcopy(self.candidate)
                record[key] = wrong
                result = self.gate(record)
                self.assertEqual(result["status"], "REJECTED")
                self.assertIsNone(result["evidence"])

    def test_reader_identity_is_compared_not_assumed(self) -> None:
        for key, wrong in (("repository", "other/source"), ("source_sha", "2" * 40), ("source_path", "wrong.txt")):
            with self.subTest(key=key):
                source = copy.deepcopy(self.source)
                source[key] = wrong
                self.assertEqual(self.gate(source=source)["checks"][f"opened_{key}"]["status"], "FAIL")

    def test_matching_words_cannot_grant_quote_rights_without_passing_gate(self) -> None:
        for source in (
            {**self.source, "source_sha": "2" * 40},
            {**self.source, "repository": None},
        ):
            result = self.gate(source=source)
            self.assertEqual(result["quote"]["status"], "VERIFIED_EXACT")
            self.assertFalse(result["quote"]["direct_quote_allowed"])
            self.assertIsNone(result["evidence"])

    def test_missing_capabilities_are_unverified_with_separate_check_states(self) -> None:
        for key in ("content", "repository", "source_sha", "source_path", "location", "excerpt_range", "context_range"):
            with self.subTest(key=key):
                source = copy.deepcopy(self.source)
                source.pop(key)
                result = self.gate(source=source)
                self.assertEqual(result["status"], "UNVERIFIED")
                self.assertIsNone(result["evidence"])
                self.assertTrue(any(c["status"] == "PASS" for c in result["checks"].values()))
                self.assertTrue(any(c["status"] == "UNVERIFIED" for c in result["checks"].values()))

    def test_unavailable_trusted_pin_and_unknown_corpus_cannot_pass(self) -> None:
        self.contract["fixture"].pop("source_sha")
        self.assertEqual(self.gate()["status"], "UNVERIFIED")
        self.contract.clear()
        self.assertEqual(self.gate()["status"], "REJECTED")

    def test_unsafe_paths_and_bad_sha_are_rejected(self) -> None:
        for path in ("../outside.txt", "/absolute.txt", "C:/file.txt", "texts\\file.txt", "a//b", "a/./b", "a/../b", "a\0b"):
            with self.subTest(path=path):
                self.assertEqual(self.gate({**self.candidate, "source_path": path})["status"], "REJECTED")
        for sha in ("main", "1234", "g" * 40, "1" * 39):
            with self.subTest(sha=sha):
                self.assertEqual(self.gate({**self.candidate, "source_sha": sha})["status"], "REJECTED")

    def test_malformed_location_values_are_rejected(self) -> None:
        for key, value in (("corpus", []), ("text_role", []), ("segment_id", []), ("witness", {}), ("sequence_no", True), ("sequence_no", -1)):
            with self.subTest(key=key):
                result = self.gate({**self.candidate, key: value})
                self.assertEqual(result["status"], "REJECTED")
        source = copy.deepcopy(self.source)
        source["location"]["sequence_no"] = True
        self.assertEqual(self.gate(source=source)["status"], "REJECTED")

    def test_index_path_conversion_is_shared_with_locator(self) -> None:
        from corpus_research.pointer_export import _github_source_path
        self.assertIs(_github_source_path, github_source_path)
        self.assertEqual(github_source_path("fixture/source/texts/work.txt", "fixture/source"), "texts/work.txt")
        with self.assertRaises(ValueError):
            github_source_path("outside/text.txt", "fixture/source")
        bad = {**self.candidate, "indexed_source_path": "other/source/texts/work.txt"}
        self.assertEqual(self.gate(bad)["status"], "REJECTED")

    def test_blob_hash_checks_full_file_not_only_the_quotation(self) -> None:
        source = copy.deepcopy(self.source)
        source["content"] += "Modified elsewhere in the file."
        self.assertEqual(self.gate(source=source)["checks"]["expected_blob"]["status"], "FAIL")
        record = {**self.candidate, "source_blob_sha": "0" * 40}
        self.assertEqual(self.gate(record)["status"], "REJECTED")

    def test_required_unavailable_blob_check_cannot_pass(self) -> None:
        source = {**self.source, "source_blob_sha": None, "blob_check_required": True}
        result = self.gate(source=source)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertEqual(result["checks"]["expected_blob"]["status"], "PASS")

    def test_blob_policy_comes_from_trusted_contract_not_candidate_labels(self) -> None:
        self.contract["fixture"]["blob_check_required"] = True
        source = {**self.source, "source_blob_sha": None, "blob_check_required": False}
        record = {**self.candidate, "blob_check_required": False, "verified": True}
        result = self.gate(record, source)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertTrue(result["checks"]["opened_blob"]["required"])

    def test_resolved_source_blob_does_not_require_inventing_a_candidate_blob(self) -> None:
        record = {**self.candidate, "source_blob_sha": None}
        source = {**self.source, "blob_check_required": True}
        result = self.gate(record, source)
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["checks"]["expected_blob"]["status"], "UNVERIFIED")
        self.assertFalse(result["checks"]["expected_blob"]["required"])

    def test_optional_unknown_fields_remain_empty_without_guessing(self) -> None:
        record = copy.deepcopy(self.candidate)
        source = copy.deepcopy(self.source)
        for key in ("work_id", "segment_id", "sequence_no", "language", "witness"):
            record[key] = None
            source["location"][key] = None  # Reader confirms non-applicability.
        source = self.configure_fixture_location(source["location"])
        record["source_blob_sha"] = None
        record["relation_ids"] = None
        result = self.gate(record, source)
        self.assertEqual(result["status"], "VERIFIED")
        for key in ("work_id", "segment_id", "sequence_no", "language", "witness", "source_blob_sha", "relation_ids", "run_id"):
            self.assertIsNone(result["evidence"][key])

    def test_required_witness_cannot_be_dropped(self) -> None:
        result = self.gate({**self.candidate, "witness": None})
        self.assertEqual(result["checks"]["location_witness"]["status"], "FAIL")

    def test_note_cannot_masquerade_as_root_text(self) -> None:
        source = copy.deepcopy(self.source)
        source["location"]["text_role"] = "translation_note"
        source = self.configure_fixture_location(source["location"])
        record = {**self.candidate, "text_role": "root_text"}
        record["source_blob_sha"] = source["source_blob_sha"]
        self.assertEqual(self.gate(record, source)["status"], "REJECTED")
        record["text_role"] = "translation_note"
        self.assertEqual(self.gate(record, source)["evidence"]["text_role"], "translation_note")

    def test_metadata_is_only_verified_for_relationship_use(self) -> None:
        self.contract["fixture"]["evidence_class"] = "metadata_relationship"
        record = {**self.candidate, "evidence_class": "metadata_relationship", "quotation": None}
        self.assertEqual(self.gate(record)["status"], "REJECTED")
        result = self.gate(record, use="relationship")
        self.assertEqual(result["status"], "VERIFIED")
        self.assertIsNone(result["evidence"]["quotation"])
        self.assertFalse(result["quote"]["direct_quote_allowed"])

    def test_invalid_ranges_and_insufficient_context_are_rejected(self) -> None:
        for span in ([-1, 1], [1, 1], [2, 1], [0, len(CONTENT) + 1], [True, 10]):
            with self.subTest(span=span):
                self.assertEqual(self.gate(source={**self.source, "excerpt_range": span})["status"], "REJECTED")
        source = {**self.source, "context_range": [0, 10]}
        self.assertEqual(self.gate(source=source)["status"], "REJECTED")

    def test_quote_must_match_resolved_excerpt_not_somewhere_else_in_file(self) -> None:
        source = {**self.source, "excerpt_range": [0, 10], "context_range": [0, len(CONTENT)]}
        result = self.gate(source=source)
        self.assertEqual(result["quote"]["status"], "QUOTE_MISMATCH")
        self.assertIsNone(result["evidence"])

    def test_self_declared_verified_labels_cannot_bypass_gate(self) -> None:
        record = {**self.candidate, "state": "VERIFIED", "verified": True, "quote_verification_status": "VERIFIED_EXACT", "gate_status": "VERIFIED"}
        source = {"opened": True, "verified": True, "status": "VERIFIED"}
        result = self.gate(record, source)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertIsNone(result["evidence"])
        record["quotation"] = QUOTE.replace("impermanent", "permanent")
        self.assertEqual(self.gate(record)["status"], "REJECTED")

    def test_research_requires_run_id_without_creating_a_run_system(self) -> None:
        self.assertEqual(self.gate(mode="research")["status"], "REJECTED")
        self.assertEqual(self.gate({**self.candidate, "run_id": "run-1"}, mode="research")["status"], "VERIFIED")

    def test_exact_and_safe_normalized_quotes(self) -> None:
        for quote, source, expected in (
            (QUOTE, QUOTE, "VERIFIED_EXACT"),
            ("things are impermanent", QUOTE, "VERIFIED_EXACT"),
            ("Sutaṃ", "Sutam\u0323", "VERIFIED_NORMALIZED"),
            ("All conditioned things", "All\n conditioned\tthings", "VERIFIED_NORMALIZED"),
            ("無常", "諸行無常是生滅法", "VERIFIED_EXACT"),
        ):
            with self.subTest(quote=quote):
                result = verify_quote(quote, source)
                self.assertEqual(result["status"], expected)
                self.assertTrue(result["direct_quote_allowed"])

    def test_content_changes_are_never_safe_normalization(self) -> None:
        for quote in (
            "All conditioned things are permanent.",
            "All things are impermanent.",
            "All conditioned things are always impermanent.",
            "Conditioned all things are impermanent.",
            QUOTE.upper(), QUOTE.replace(".", "!"),
        ):
            with self.subTest(quote=quote):
                result = verify_quote(quote, QUOTE)
                self.assertEqual(result["status"], "QUOTE_MISMATCH")
                self.assertFalse(result["direct_quote_allowed"])
        self.assertEqual(verify_quote("sutam", "sutaṃ")["status"], "QUOTE_MISMATCH")
        self.assertEqual(verify_quote("permanent", "impermanent")["status"], "QUOTE_MISMATCH")
        self.assertEqual(verify_quote("suta", "sutaṃ")["status"], "QUOTE_MISMATCH")
        self.assertEqual(verify_quote("nicca", "ānicca")["status"], "QUOTE_MISMATCH")
        self.assertEqual(verify_quote("suta", "sutam\u0323")["status"], "QUOTE_MISMATCH")
        self.assertEqual(verify_quote("1", "①")["status"], "QUOTE_MISMATCH")

    def test_missing_quote_data_is_unverified(self) -> None:
        for quote, source in ((None, QUOTE), (QUOTE, None), ("", QUOTE), (" ", QUOTE)):
            with self.subTest(quote=quote, source=source):
                self.assertEqual(verify_quote(quote, source)["status"], "UNVERIFIED")

    def test_paraphrase_needs_separate_bound_review_and_is_not_a_direct_quote(self) -> None:
        paraphrase = "Conditioned phenomena do not last forever."
        self.assertEqual(verify_quote(paraphrase, QUOTE)["status"], "QUOTE_MISMATCH")
        self.assertEqual(verify_quote(paraphrase, QUOTE, kind="paraphrase")["status"], "UNVERIFIED")
        self.assertEqual(verify_quote(QUOTE, QUOTE, kind="paraphrase")["status"], "UNVERIFIED")
        review = {"review_id": "review-1", "quotation": paraphrase, "source_text": QUOTE, "supported": True, "reviewer": "fixture-reviewer", "rationale": "Fixture assessment of the same passage."}
        # Only the host's pre-approved store can establish approval. The proposed
        # JSON alone used to pass here; that unsafe expectation is tightened.
        approvals = {"review-1": copy.deepcopy(review)}
        reader = approvals.get
        self.assertEqual(verify_quote(paraphrase, QUOTE, kind="paraphrase", paraphrase_review=review)["status"], "UNVERIFIED")
        result = verify_quote(paraphrase, QUOTE, kind="paraphrase", paraphrase_review=review, review_reader=reader)
        self.assertEqual(result["status"], "PARAPHRASE")
        self.assertTrue(result["paraphrase_allowed"])
        self.assertFalse(result["direct_quote_allowed"])
        record = {**self.candidate, "quotation": paraphrase}
        self.assertEqual(self.gate(record, quote_kind="paraphrase", paraphrase_review=review, review_reader=reader)["status"], "VERIFIED")
        for key in ("review_id", "quotation", "source_text", "reviewer", "rationale", "supported"):
            stale = copy.deepcopy(review)
            stale.pop(key)
            self.assertEqual(verify_quote(paraphrase, QUOTE, kind="paraphrase", paraphrase_review=stale, review_reader=reader)["status"], "UNVERIFIED")
        review["supported"] = False
        approvals["review-1"] = copy.deepcopy(review)  # Authenticated negative review.
        self.assertEqual(self.gate(record, quote_kind="paraphrase", paraphrase_review=review, review_reader=reader)["status"], "REJECTED")

    def test_self_declared_paraphrase_status_is_not_a_review(self) -> None:
        record = {**self.candidate, "quotation": "An explanation of the passage.", "quote_verification_status": "PARAPHRASE", "paraphrase_review": {"supported": True}}
        self.assertEqual(self.gate(record, quote_kind="paraphrase")["status"], "UNVERIFIED")

    def test_json_roundtrip_and_verification_do_not_mutate_inputs(self) -> None:
        inputs = [self.candidate, self.contract, self.source]
        original = copy.deepcopy(inputs)
        result = evidence_gate(*json.loads(json.dumps(inputs)), source_reader=self.read_fixture_source)
        self.assertEqual(json.loads(json.dumps(result)), self.gate())
        self.assertEqual(inputs, original)

    def test_core_import_and_verification_do_not_require_sqlite_or_shell(self) -> None:
        code = """
import builtins, json, sys
sys.path.insert(0, sys.argv[1])
original = builtins.__import__
def isolated(name, *args, **kwargs):
    if name in {'sqlite3', 'subprocess'} or name.startswith('corpus_research.pointer_export'):
        raise ImportError('unavailable provider capability')
    return original(name, *args, **kwargs)
builtins.__import__ = isolated
from corpus_research.verification import verify_quote, evidence_gate
assert verify_quote('source', 'source')['status'] == 'VERIFIED_EXACT'
assert evidence_gate({}, {})['status'] == 'REJECTED'
assert evidence_gate(*json.load(sys.stdin))['status'] == 'UNVERIFIED'
"""
        result = subprocess.run(
            [sys.executable, "-c", code, str(ROOT / "tools")],
            input=json.dumps([self.candidate, self.contract, self.source]),
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_retrieval_evidence_integration_keeps_legacy_output_and_candidate_boundary(self) -> None:
        from corpus_research.retrieval import evidence
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "corpus.sqlite3"
            con = sqlite3.connect(db)
            try:
                con.executescript((ROOT / "schema/corpus-index.sql").read_text(encoding="utf-8"))
                for seq, text in enumerate(("Indexed before.", "Stale indexed prose.", "Indexed after.")):
                    con.execute(
                        """INSERT INTO records(corpus,language,work_id,segment_id,raw_text,
                           norm_text,folded_text,compact_text,source_path,source_sha,
                           evidence_class,text_role,witness,sequence_no)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        ("fixture", "en", "fixture1", f"fixture1:{seq}", text, text,
                         "", "", "fixture/source/texts/work.txt", "1" * 40,
                         "authoritative_structured", "translation_main", "Fixture edition", seq),
                    )
                record_id = con.execute("SELECT id FROM records WHERE sequence_no=1").fetchone()[0]
                con.commit()
                con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            finally:
                con.close()
            bundle = evidence(db, record_id)
            unchanged = copy.deepcopy(bundle)
            record = make_evidence_record(bundle, self.contract, evidence_id="ev-1", quotation=QUOTE)
            self.assertEqual(evidence_gate(record, self.contract)["status"], "UNVERIFIED")
            result = self.gate(record)
            self.assertEqual(result["status"], "VERIFIED")
            self.assertEqual(result["evidence"]["quotation"], QUOTE)
            self.assertEqual(record["indexed_text"], "Stale indexed prose.")
            self.assertEqual(bundle, unchanged)
            self.assertEqual(evidence(db, record_id), unchanged)

    def test_local_pinned_git_and_github_style_reader_use_the_same_core(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "fixture/source"
            (repo / "texts").mkdir(parents=True)
            source_file = repo / "texts/work.txt"
            source_file.write_bytes(CONTENT.encode("utf-8"))
            def git(*args):
                return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE).decode().strip()
            git("init", "-q")
            git("add", "texts/work.txt")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
            sha = git("rev-parse", "HEAD")
            self.contract["fixture"]["source_sha"] = sha
            record = {**self.candidate, "source_sha": sha}
            self.assertEqual(git("rev-parse", f"{sha}:texts/work.txt"), record["source_blob_sha"])
            source_file.write_bytes(b"Uncommitted replacement; must never become evidence.")
            local = read_local_source(root, record, self.contract)
            self.assertEqual(local["content"], CONTENT)
            self.assertEqual(self.gate(record, local)["status"], "UNVERIFIED")
            local = resolve_fixture(local)
            remote = json.loads(json.dumps(local))  # Simulated connector payload.
            remote.pop("blob_check_required")
            def pinned_reader(request):
                snapshot = read_local_source(root, request, self.contract)
                return resolve_fixture(snapshot) if snapshot.get("content") else snapshot
            a = self.gate(record, local, source_reader=pinned_reader)
            # A remote-shaped JSON snapshot is unverified on its own. Local Git
            # can independently authenticate either data transport, same core.
            self.assertEqual(self.gate(record, remote, source_reader=None)["status"], "UNVERIFIED")
            b = self.gate(record, remote, source_reader=pinned_reader)
            self.assertEqual(a["status"], "VERIFIED")
            self.assertEqual(a, b)
            forged_content = CONTENT + "Self-consistent forgery, absent from the pinned commit."
            forged_blob = git_blob_sha(forged_content.encode("utf-8"))
            forged = resolve_fixture({**remote, "content": forged_content, "source_blob_sha": forged_blob})
            rejected = self.gate({**record, "source_blob_sha": forged_blob}, forged, source_reader=pinned_reader)
            self.assertEqual(rejected["status"], "REJECTED")
            self.assertEqual(rejected["checks"]["independent_content"]["status"], "FAIL")
            missing = read_local_source(root, {**record, "source_path": "missing.txt"}, self.contract)
            self.assertEqual(self.gate({**record, "source_path": "missing.txt", "indexed_source_path": "fixture/source/missing.txt"}, missing)["status"], "UNVERIFIED")

    def test_consistent_self_report_without_independent_read_is_unverified(self) -> None:
        result = self.gate(source_reader=None)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertTrue(result["source_opened"])
        self.assertEqual(result["checks"]["expected_blob"]["status"], "PASS")
        self.assertEqual(result["checks"]["opened_blob"]["status"], "PASS")
        self.assertIsNone(result["evidence"])
        self.assertFalse(result["quote"]["direct_quote_allowed"])

    def test_forged_content_with_consistent_self_hash_is_not_authenticated(self) -> None:
        content = CONTENT + "Forged addition outside the quoted passage."
        blob = git_blob_sha(content.encode("utf-8"))
        source = resolve_fixture({**self.source, "content": content, "source_blob_sha": blob})
        candidate = {**self.candidate, "source_blob_sha": blob}
        self.assertEqual(self.gate(candidate, source, source_reader=None)["status"], "UNVERIFIED")
        result = self.gate(candidate, source)
        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["checks"]["independent_content"]["status"], "FAIL")

    def test_remote_capability_missing_failed_or_not_callable_is_unverified(self) -> None:
        def unavailable(_):
            raise OSError("Pinned remote revision cannot be retrieved")
        for reader in (None, unavailable, lambda _: None, lambda _: {"verified": True}, {"trusted": True}):
            with self.subTest(reader=type(reader).__name__):
                self.assertEqual(self.gate(source_reader=reader)["status"], "UNVERIFIED")

    def test_json_trust_flags_cannot_supply_execution_capabilities(self) -> None:
        flags = {"trusted": True, "verified": True, "attested": True, "source_reader": "trusted-reader", "review_reader": "approved"}
        candidate = {**self.candidate, **flags, "blob_check_required": False}
        source = {**self.source, **flags}
        contract = copy.deepcopy(self.contract)
        contract["fixture"].update(flags)
        result = evidence_gate(candidate, contract, source)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertIsNone(result["evidence"])

    def test_independent_reader_gets_identity_selectors_not_proposed_content(self) -> None:
        requests = []
        def reader(request):
            requests.append(copy.deepcopy(request))
            request["source_sha"] = "9" * 40  # Cannot mutate caller inputs.
            return copy.deepcopy(self.approved_source)
        self.assertEqual(self.gate(source_reader=reader)["status"], "VERIFIED")
        self.assertEqual(set(requests[0]), {"corpus", "repository", "source_sha", "source_path", "work_id", "segment_id", "sequence_no"})
        self.assertEqual(self.candidate["source_sha"], "1" * 40)

    def test_independent_identity_conflicts_are_rejected(self) -> None:
        for key, wrong in (("repository", "other/repo"), ("source_sha", "2" * 40), ("source_path", "wrong.txt"), ("source_blob_sha", "0" * 40)):
            with self.subTest(key=key):
                basis = {**self.approved_source, key: wrong}
                result = self.gate(source_reader=lambda _: basis)
                self.assertEqual(result["status"], "REJECTED")
                self.assertIsNone(result["evidence"])

    def test_location_and_ranges_cannot_be_self_attested_even_for_real_content(self) -> None:
        candidate = {**self.candidate, "text_role": "root_text"}
        source = copy.deepcopy(self.source)
        source["location"]["text_role"] = "root_text"
        result = self.gate(candidate, source)
        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["checks"]["independent_location_text_role"]["status"], "FAIL")
        source = {**self.source, "context_range": [0, len(CONTENT)]}
        self.assertEqual(self.gate(source=source)["checks"]["independent_context_range"]["status"], "FAIL")

    def test_missing_independent_observations_and_mandatory_blob_fail_closed(self) -> None:
        for key in ("repository", "source_sha", "source_path", "content", "location", "excerpt_range", "context_range"):
            with self.subTest(key=key):
                basis = copy.deepcopy(self.approved_source)
                basis.pop(key)
                self.assertEqual(self.gate(source_reader=lambda _: basis)["status"], "UNVERIFIED")
        self.contract["fixture"]["blob_check_required"] = True
        basis = {**self.approved_source, "source_blob_sha": None}
        self.assertEqual(self.gate(source_reader=lambda _: basis)["status"], "UNVERIFIED")

    def test_self_proposed_paraphrase_review_cannot_approve_itself(self) -> None:
        review = {"review_id": "invented", "quotation": "A paraphrase.", "source_text": QUOTE, "supported": True,
                  "reviewer": "invented-reviewer", "rationale": "AI says yes", "approved": True, "trusted": True}
        for reader in (None, {"approved": True}, lambda _: None):
            with self.subTest(reader=type(reader).__name__):
                result = verify_quote(review["quotation"], QUOTE, kind="paraphrase", paraphrase_review=review, review_reader=reader)
                self.assertEqual(result["status"], "UNVERIFIED")
                self.assertFalse(result["paraphrase_allowed"])

    def test_approved_review_is_bound_to_exact_content_identity_and_reviewer(self) -> None:
        approved = {"review_id": "approved-1", "quotation": "Conditioned phenomena do not last forever.",
                    "source_text": QUOTE, "supported": True, "reviewer": "human-reviewer",
                    "rationale": "Assessment of this exact passage."}
        approval_store = {"approved-1": copy.deepcopy(approved)}
        requests = []
        def reader(review_id):
            requests.append(review_id)
            return approval_store.get(review_id)
        self.assertEqual(verify_quote(approved["quotation"], QUOTE, kind="paraphrase", paraphrase_review=approved, review_reader=reader)["status"], "PARAPHRASE")
        self.assertEqual(requests, ["approved-1"])
        for key, changed in (("quotation", "Changed paraphrase."), ("source_text", QUOTE + " Changed context."),
                             ("reviewer", "AI self-reviewer"), ("review_id", "unknown-review"), ("supported", 1), ("rationale", "Changed rationale")):
            with self.subTest(key=key):
                proposed = {**approved, key: changed}
                result = verify_quote(proposed["quotation"], proposed["source_text"], kind="paraphrase", paraphrase_review=proposed, review_reader=reader)
                self.assertEqual(result["status"], "UNVERIFIED")
        self.assertEqual(verify_quote(approved["quotation"], QUOTE + " Changed after approval.", kind="paraphrase", paraphrase_review=approved, review_reader=reader)["status"], "UNVERIFIED")
        def unavailable(_):
            raise OSError("Approval channel unavailable")
        self.assertEqual(verify_quote(approved["quotation"], QUOTE, kind="paraphrase", paraphrase_review=approved, review_reader=unavailable)["status"], "UNVERIFIED")

    def test_source_verification_never_grants_claim_support_or_promotes_classes(self) -> None:
        for evidence_class in ("computational_segmented", "parallel_alignment", "canonical_root", "auxiliary_reference"):
            with self.subTest(evidence_class=evidence_class):
                self.contract["fixture"]["evidence_class"] = evidence_class
                candidate = {**self.candidate, "evidence_class": evidence_class, "claim_status": "accepted", "support_level": "DIRECT"}
                result = self.gate(candidate)
                self.assertEqual(result["status"], "VERIFIED")
                self.assertEqual(result["evidence"]["evidence_class"], evidence_class)
                self.assertEqual(result["evidence"]["text_role"], LOCATION["text_role"])
                self.assertEqual(result["evidence"]["witness"], LOCATION["witness"])
                for key in ("support_level", "claim_status", "primary_witness"):
                    self.assertNotIn(key, result["evidence"])

    def test_serializing_data_never_serializes_authority(self) -> None:
        inputs = json.loads(json.dumps([self.candidate, self.contract, self.source]))
        verified = evidence_gate(*inputs, source_reader=self.read_fixture_source)
        self.assertEqual(json.loads(json.dumps(verified))["status"], "VERIFIED")
        self.assertEqual(evidence_gate(*inputs)["status"], "UNVERIFIED")
        # Replaying a previously verified result as source data conveys no rights.
        self.assertEqual(evidence_gate(self.candidate, self.contract, verified)["status"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
