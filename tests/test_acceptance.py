from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from corpus_research.index import build_index
from corpus_research.retrieval import parallels, provenance, resolve, search, variants, work


ROOT = Path(__file__).resolve().parents[1]


class AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.temp.name) / "acceptance.sqlite3"
        build_index(ROOT, cls.db, profile="acceptance", progress=False)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_pali_inflection_uses_corpus_lemma(self) -> None:
        result = search(self.db, "suta", language="pli", limit=20)
        matches = [
            row for row in result["results"]
            if row["corpus"] == "pali-canon-derived"
            and row["segment_id"] == "mn1:1.1"
            and "corpus-lemma" in row["match_reasons"]
        ]
        self.assertTrue(matches)
        self.assertIn("sutaṃ", matches[0]["raw_text"])

    def test_chinese_phrase_prefers_primary_cbeta(self) -> None:
        result = search(self.db, "如是我聞", language="lzh", limit=20)
        self.assertTrue(result["results"])
        cbeta = next(row for row in result["results"] if row["corpus"] == "cbeta-tei")
        self.assertEqual(cbeta["work_id"], "T01n0001")
        self.assertIn("0001b12", cbeta["segment_id"])

    def test_nikaya_agama_parallel_relation(self) -> None:
        result = parallels(self.db, "an1.1-5")
        self.assertTrue(result["found"])
        self.assertTrue(any(row["to_id"] == "ea9.7" for row in result["relations"]))

    def test_nikaya_agama_resolves_through_local_cbeta_bridge(self) -> None:
        parallel = parallels(self.db, "an1.1-5")
        parallel_edge = next(
            row
            for row in parallel["relations"]
            if row["to_id"] == "ea9.7"
            and row["relation_type"] == "suttacentral_parallel:full"
        )
        bridge = parallels(self.db, "ea9.7")
        work_edge = next(
            row
            for row in bridge["relations"]
            if row["relation_type"] == "suttacentral_cbeta:work"
            and row["to_id"] == "T02n0125"
        )
        range_edge = next(
            row
            for row in bridge["relations"]
            if row["relation_type"] == "suttacentral_cbeta:line_range"
        )
        self.assertEqual(
            range_edge["to_id"],
            "T02n0125:0563a14..0563a27",
        )
        primary = resolve(self.db, "ea9.7")
        self.assertTrue(primary["found"])
        self.assertEqual(
            {
                row["relation_type"]
                for row in primary["bridge_relations"]
            },
            {
                "suttacentral_cbeta:work",
                "suttacentral_cbeta:line_range",
            },
        )
        self.assertEqual(
            [row["segment_id"] for row in primary["records"]],
            [
                "T02n0125:0559b25..0563a14",
                "T02n0125:0563a15..0566c01q",
            ],
        )
        self.assertEqual(parallel_edge["evidence_class"], "metadata_relationship")
        self.assertEqual(work_edge["evidence_class"], "metadata_relationship")
        self.assertTrue(
            all(
                row["evidence_class"] == "canonical_root"
                and row["corpus"] == "cbeta-bm"
                for row in primary["records"]
            )
        )
        self.assertNotEqual(parallel_edge["source_path"], work_edge["source_path"])
        self.assertNotEqual(work_edge["source_sha"], primary["records"][0]["source_sha"])

    def test_cbeta_resolver_matches_suffix_case_insensitively(self) -> None:
        with __import__("sqlite3").connect(self.db) as con:
            con.execute(
                """INSERT INTO records(
                   corpus,language,collection_name,work_id,segment_id,title,raw_text,
                   norm_text,folded_text,compact_text,lemma_text,source_path,source_sha,
                   evidence_class,witness,relation_ids,sequence_no)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "cbeta-bm",
                    "lzh",
                    "T",
                    "T02n0150A",
                    "T02n0150A:0875b01..0875c20",
                    None,
                    "local suffix fixture",
                    "",
                    "",
                    "",
                    "",
                    "cbeta/BM_u8/T/T02/new.txt",
                    "0" * 40,
                    "canonical_root",
                    "CBETA BM_u8",
                    '["T02n0150A:0875b01","T02n0150A:0875c20"]',
                    999999,
                ),
            )
        with __import__("sqlite3").connect(self.db) as con:
            con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        result = resolve(self.db, "T02n0150a:0875b02..0875c19")
        self.assertTrue(result["found"])
        self.assertEqual(result["records"][0]["work_id"], "T02n0150A")

    def test_84000_work_has_toh_metadata_and_rdf_relation(self) -> None:
        result = work(self.db, "UT22084-001-001")
        self.assertTrue(result["found"])
        self.assertTrue(any("toh1-1" in str(row.get("metadata_json")) for row in result["works"]))
        rdf = parallels(self.db, "WATTOH1-1")
        self.assertTrue(rdf["found"])

    def test_buddhanexus_candidate_resolves_to_cbeta_primary(self) -> None:
        result = search(self.db, "如是我聞", language="lzh", limit=50)
        corpora = {row["corpus"] for row in result["results"]}
        self.assertIn("buddhanexus-chinese", corpora)
        self.assertIn("cbeta-tei", corpora)
        cbeta = next(row for row in result["results"] if row["corpus"] == "cbeta-tei")
        candidate = next(row for row in result["results"] if row["corpus"] == "buddhanexus-chinese")
        self.assertGreater(cbeta["score"], candidate["score"])
        proof = provenance(self.db, cbeta["id"])
        self.assertEqual(proof["provenance"]["evidence_class"], "authoritative_structured")

    def test_fail_closed_when_query_has_no_evidence(self) -> None:
        result = search(self.db, "ZXQ-NO-SUCH-BUDDHIST-EVIDENCE-992731", limit=10)
        self.assertTrue(result["fail_closed"])
        self.assertEqual(result["message"], "không đủ dữ liệu trong corpus hiện tại")

    def test_variant_workflow_returns_local_witnesses(self) -> None:
        result = variants(self.db, "T01n0001")
        self.assertTrue(result["found"])
        self.assertTrue(any(row["variant_type"] == "cbeta_app" for row in result["variants"]))


if __name__ == "__main__":
    unittest.main()
