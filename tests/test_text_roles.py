from __future__ import annotations

import sqlite3
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from corpus_research.index import (
    Writer,
    _tei_text_without_notes,
    connect,
    index_84000_tei,
    index_bilara,
    local_sha,
)
from corpus_research.model import Record
from corpus_research.retrieval import provenance


ROOT = Path(__file__).resolve().parents[1]


class TextRoleTests(unittest.TestCase):
    def test_legacy_migration_and_bilara_roles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "roles.sqlite3"
            with sqlite3.connect(db) as con:
                con.execute(
                    """CREATE TABLE records(
                       id INTEGER PRIMARY KEY, corpus TEXT NOT NULL, language TEXT,
                       collection_name TEXT, work_id TEXT, segment_id TEXT, title TEXT,
                       raw_text TEXT NOT NULL, norm_text TEXT NOT NULL,
                       folded_text TEXT NOT NULL, compact_text TEXT NOT NULL,
                       lemma_text TEXT NOT NULL DEFAULT '', source_path TEXT NOT NULL,
                       source_sha TEXT NOT NULL, evidence_class TEXT NOT NULL,
                       witness TEXT, relation_ids TEXT NOT NULL DEFAULT '[]',
                       sequence_no INTEGER NOT NULL DEFAULT 0,
                       UNIQUE(corpus,source_path,segment_id,language,witness))"""
                )
                con.executemany(
                    """INSERT INTO records(
                       corpus,language,segment_id,raw_text,norm_text,folded_text,
                       compact_text,source_path,source_sha,evidence_class,witness)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    [
                        (
                            "cbeta-bm",
                            "lzh",
                            "T01n0001:0001b12",
                            "如是我聞",
                            "",
                            "",
                            "",
                            "cbeta/BM_u8/T/T01/new.txt",
                            "1" * 40,
                            "canonical_root",
                            "CBETA BM_u8",
                        ),
                        (
                            "legacy-unknown",
                            "en",
                            "legacy:1",
                            "legacy",
                            "legacy",
                            "",
                            "legacy",
                            "legacy.txt",
                            "2" * 40,
                            "auxiliary_reference",
                            None,
                        ),
                    ],
                )
            con = connect(db, ROOT / "schema/corpus-index.sql")
            migrated = dict(
                con.execute(
                    "SELECT corpus,text_role FROM records ORDER BY corpus"
                ).fetchall()
            )
            self.assertEqual(migrated["cbeta-bm"], "root_text")
            self.assertEqual(migrated["legacy-unknown"], "unspecified")
            writer = Writer(con)
            with con:
                index_bilara(
                    ROOT,
                    local_sha(ROOT, "suttacentral/bilara-data"),
                    writer,
                    "acceptance",
                )
                writer.flush()
            rows = con.execute(
                """SELECT text_role,evidence_class,COUNT(*)
                   FROM records WHERE corpus='suttacentral-bilara'
                   GROUP BY text_role,evidence_class"""
            ).fetchall()
            roles = {(row[0], row[1]) for row in rows}
            self.assertIn(("root_text", "canonical_root"), roles)
            self.assertIn(("translation_main", "authoritative_structured"), roles)
            self.assertIn(("translator_comment", "authoritative_structured"), roles)

    def test_84000_note_isolation_parent_relation_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "notes.sqlite3"
            con = connect(db, ROOT / "schema/corpus-index.sql")
            writer = Writer(con)
            sha = local_sha(ROOT, "84000/data-tei")
            with con:
                index_84000_tei(ROOT, sha, writer, "acceptance")
                writer.flush()
            parent = con.execute(
                """SELECT id,raw_text,text_role,evidence_class,source_path,source_sha
                   FROM records
                   WHERE corpus='84000-tei'
                     AND segment_id='UT22084-072-037-78'
                     AND text_role='translation_main'"""
            ).fetchone()
            note = con.execute(
                """SELECT id,raw_text,text_role,evidence_class,source_path,source_sha
                   FROM records
                   WHERE corpus='84000-tei'
                     AND segment_id='UT22084-072-037-94'"""
            ).fetchone()
            edge = con.execute(
                """SELECT relation_type,from_id,to_id,details_json
                   FROM relations
                   WHERE corpus='84000-tei'
                     AND from_id='UT22084-072-037-94'"""
            ).fetchone()
            self.assertIsNotNone(parent)
            self.assertIsNotNone(note)
            self.assertIsNotNone(edge)
            note_prose = (
                "The equivalent section in Toh 1 begins at this point "
                "(p. 42b.3) and in Toh 301 (p. 60a.1)."
            )
            self.assertNotIn(note_prose, parent["raw_text"])
            self.assertIn("Thus did I hear at one time", parent["raw_text"])
            self.assertIn(
                "At that time the Blessed One spoke to the group of five monks",
                parent["raw_text"],
            )
            self.assertEqual(note["raw_text"], note_prose)
            self.assertEqual(note["text_role"], "translation_note")
            self.assertEqual(note["evidence_class"], "authoritative_structured")
            self.assertEqual(note["source_path"], parent["source_path"])
            self.assertEqual(note["source_sha"], parent["source_sha"])
            self.assertEqual(
                tuple(edge[:3]),
                (
                    "84000:note_of",
                    "UT22084-072-037-94",
                    "UT22084-072-037-78",
                ),
            )
            note_id = note["id"]
            con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            con.close()
            note_provenance = provenance(db, note_id)
            self.assertEqual(
                note_provenance["provenance"]["text_role"],
                "translation_note",
            )
            self.assertEqual(
                note_provenance["provenance"]["source_sha"],
                sha,
            )

    def test_note_exclusion_preserves_inline_text_and_note_tail(self) -> None:
        element = ET.fromstring(
            """<p xmlns="http://www.tei-c.org/ns/1.0">
                 Main A <title>inline title</title> Main B
                 <note xml:id="N1">note text</note> Main C
               </p>"""
        )
        self.assertEqual(
            _tei_text_without_notes(element),
            "Main A inline title Main B Main C",
        )


if __name__ == "__main__":
    unittest.main()
