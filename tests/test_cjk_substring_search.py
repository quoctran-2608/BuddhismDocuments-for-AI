from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from corpus_research.index import rebuild_search_indexes
from corpus_research.retrieval import search


ROOT = Path(__file__).resolve().parents[1]


class CjkSubstringSearchTest(unittest.TestCase):
    def test_middle_substring_uses_trigram_candidates_for_long_cbeta_text(self) -> None:
        source_line = next(
            line
            for line in (
                ROOT / "cbeta/BM_u8/D/D11/new.txt"
            ).read_text(encoding="utf-8", errors="replace").splitlines()
            if line.startswith("D11n8817_p0001a02")
        )
        raw_text = source_line.split("##", 1)[-1] + ("續" * 2_100)
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "cjk.sqlite3"
            with sqlite3.connect(db) as con:
                con.executescript(
                    (ROOT / "schema/corpus-index.sql").read_text(encoding="utf-8")
                )
                con.execute(
                    """INSERT INTO records(
                       corpus,language,collection_name,work_id,segment_id,title,raw_text,
                       norm_text,folded_text,compact_text,lemma_text,source_path,source_sha,
                       evidence_class,witness,relation_ids,sequence_no)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        "cbeta-bm",
                        "lzh",
                        "D",
                        "D11n8817",
                        "D11n8817:0001a02",
                        None,
                        raw_text,
                        "",
                        "",
                        "",
                        "",
                        "cbeta/BM_u8/D/D11/new.txt",
                        "83bc009a6f3333fa2d61cb436ee6181b1335beb4",
                        "canonical_root",
                        "CBETA BM_u8",
                        "[]",
                        0,
                    ),
                )
                con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
                unicode_count = con.execute(
                    """SELECT COUNT(*) FROM records_fts
                       WHERE records_fts MATCH '"我聞一時"'"""
                ).fetchone()[0]
                rebuild_search_indexes(con)
            self.assertEqual(unicode_count, 0)
            result = search(db, "我聞一時", language="lzh")
            self.assertTrue(result["cjk_substring_index_available"])
            self.assertEqual(result["results"][0]["work_id"], "D11n8817")
            self.assertIn("我聞一時", result["results"][0]["raw_text"])


if __name__ == "__main__":
    unittest.main()
