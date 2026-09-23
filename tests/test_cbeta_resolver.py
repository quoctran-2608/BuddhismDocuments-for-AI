from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from corpus_research.retrieval import resolve


ROOT = Path(__file__).resolve().parents[1]
WORK_ID = "T02n0125"
TARGET_RANGE = f"{WORK_ID}:0563a14..0563a27"


class CbetaResolverShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "resolver.sqlite3"
        with sqlite3.connect(self.db) as con:
            con.executescript(
                (ROOT / "schema/corpus-index.sql").read_text(encoding="utf-8")
            )
            con.executemany(
                """INSERT INTO relations(
                   corpus,relation_type,from_id,to_id,details_json,source_path,
                   source_sha,evidence_class) VALUES (?,?,?,?,?,?,?,?)""",
                [
                    (
                        "suttacentral-relations",
                        "suttacentral_cbeta:work",
                        "ea9.7",
                        WORK_ID,
                        "{}",
                        "suttacentral/sc-data/html_text/lzh/sutta/ea/ea9/ea9.7.html",
                        "1" * 40,
                        "metadata_relationship",
                    ),
                    (
                        "suttacentral-relations",
                        "suttacentral_cbeta:line_range",
                        "ea9.7",
                        TARGET_RANGE,
                        "{}",
                        "suttacentral/sc-data/html_text/lzh/sutta/ea/ea9/ea9.7.html",
                        "1" * 40,
                        "metadata_relationship",
                    ),
                ],
            )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_record(
        self,
        *,
        corpus: str = "cbeta-bm",
        work_id: str = WORK_ID,
        segment_id: str,
        relation_ids: list[str] | None = None,
        sequence_no: int = 0,
    ) -> None:
        with sqlite3.connect(self.db) as con:
            con.execute(
                """INSERT INTO records(
                   corpus,language,collection_name,work_id,segment_id,title,raw_text,
                   norm_text,folded_text,compact_text,lemma_text,source_path,source_sha,
                   evidence_class,witness,relation_ids,sequence_no)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    corpus,
                    "lzh",
                    "T",
                    work_id,
                    segment_id,
                    None,
                    "fixture",
                    "",
                    "",
                    "",
                    "",
                    "cbeta/source.fixture",
                    "2" * 40,
                    "canonical_root" if corpus == "cbeta-bm" else "authoritative_structured",
                    "fixture",
                    json.dumps(relation_ids or []),
                    sequence_no,
                ),
            )

    def test_core_chunk_uses_first_and_last_relation_ids(self) -> None:
        self.add_record(
            segment_id=f"{WORK_ID}:0559b25..0566c01q",
            relation_ids=[
                f"{WORK_ID}:0559b25",
                f"{WORK_ID}:0566c01q",
            ],
        )
        result = resolve(self.db, "ea9.7")
        self.assertTrue(result["found"])
        self.assertEqual(result["records"][0]["resolution_locator"], "relation_ids")

    def test_all_bm_line_uses_segment_id_as_single_line_interval(self) -> None:
        self.add_record(segment_id=f"{WORK_ID}:0563a14", sequence_no=1)
        self.add_record(segment_id=f"{WORK_ID}:0563a27", sequence_no=2)
        self.add_record(segment_id=f"{WORK_ID}:0563a28", sequence_no=3)
        result = resolve(self.db, "ea9.7")
        self.assertEqual(
            [row["segment_id"] for row in result["records"]],
            [
                f"{WORK_ID}:0563a14",
                f"{WORK_ID}:0563a27",
            ],
        )
        self.assertTrue(
            all(
                row["resolution_locator"] == "segment_id"
                for row in result["records"]
            )
        )

    def test_cbeta_tei_line_uses_segment_id(self) -> None:
        self.add_record(
            corpus="cbeta-tei",
            segment_id=f"{WORK_ID}:0563a20",
        )
        result = resolve(self.db, TARGET_RANGE)
        self.assertTrue(result["found"])
        self.assertEqual(result["records"][0]["corpus"], "cbeta-tei")
        self.assertEqual(result["records"][0]["resolution_locator"], "segment_id")

    def test_granular_record_after_5000_rows_is_not_truncated(self) -> None:
        rows = []
        for sequence_no in range(5_001):
            page = 1 + sequence_no // 90
            within_page = sequence_no % 90
            column = "abc"[within_page // 30]
            line = 1 + within_page % 30
            locator = f"{page:04d}{column}{line:02d}"
            rows.append(
                (
                    "cbeta-bm",
                    "lzh",
                    "T",
                    WORK_ID,
                    f"{WORK_ID}:{locator}",
                    None,
                    "non-overlapping fixture",
                    "",
                    "",
                    "",
                    "",
                    "cbeta/source.fixture",
                    "2" * 40,
                    "canonical_root",
                    "fixture",
                    "[]",
                    sequence_no,
                )
            )
        rows.append(
            (
                "cbeta-bm",
                "lzh",
                "T",
                WORK_ID,
                f"{WORK_ID}:0563a20",
                None,
                "target fixture",
                "",
                "",
                "",
                "",
                "cbeta/source.fixture",
                "2" * 40,
                "canonical_root",
                "fixture",
                "[]",
                5_001,
            )
        )
        with sqlite3.connect(self.db) as con:
            con.executemany(
                """INSERT INTO records(
                   corpus,language,collection_name,work_id,segment_id,title,raw_text,
                   norm_text,folded_text,compact_text,lemma_text,source_path,source_sha,
                   evidence_class,witness,relation_ids,sequence_no)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                rows,
            )
        result = resolve(self.db, TARGET_RANGE)
        self.assertEqual(
            [row["segment_id"] for row in result["records"]],
            [f"{WORK_ID}:0563a20"],
        )

    def test_invalid_relation_ids_fall_back_to_valid_segment_id(self) -> None:
        self.add_record(
            segment_id=f"{WORK_ID}:0563a20",
            relation_ids=["broken", "also-broken"],
        )
        result = resolve(self.db, TARGET_RANGE)
        self.assertTrue(result["found"])
        self.assertEqual(result["records"][0]["resolution_locator"], "segment_id")

    def test_valid_relation_ids_take_precedence_over_segment_id(self) -> None:
        self.add_record(
            segment_id=f"{WORK_ID}:0563a20",
            relation_ids=[
                f"{WORK_ID}:0564a01",
                f"{WORK_ID}:0564a02",
            ],
        )
        result = resolve(self.db, TARGET_RANGE)
        self.assertFalse(result["found"])

    def test_non_overlapping_segment_range_remains_fail_closed(self) -> None:
        self.add_record(segment_id=f"{WORK_ID}:0564a01..0564a30")
        result = resolve(self.db, "ea9.7")
        self.assertFalse(result["found"])
        self.assertEqual(result["message"], "không đủ dữ liệu trong corpus hiện tại")

    def test_reversed_input_range_remains_fail_closed(self) -> None:
        self.add_record(
            segment_id=f"{WORK_ID}:0559b25..0566c01q",
            relation_ids=[
                f"{WORK_ID}:0559b25",
                f"{WORK_ID}:0566c01q",
            ],
        )
        result = resolve(self.db, f"{WORK_ID}:0563a27..0563a14")
        self.assertFalse(result["found"])
        self.assertEqual(result["records"], [])

    def test_malformed_record_locator_remains_fail_closed(self) -> None:
        self.add_record(
            segment_id=f"{WORK_ID}:not-a-line",
            relation_ids=["bad", "worse"],
        )
        result = resolve(self.db, TARGET_RANGE)
        self.assertFalse(result["found"])

    def test_malformed_input_identifier_remains_fail_closed(self) -> None:
        result = resolve(self.db, f"{WORK_ID}:not-a-line")
        self.assertFalse(result["found"])
        self.assertEqual(result["records"], [])


if __name__ == "__main__":
    unittest.main()
