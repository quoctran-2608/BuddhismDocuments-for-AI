from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from corpus_research.remote_export import export_remote
from corpus_research.retrieval import evidence, search


ROOT = Path(__file__).resolve().parents[1]


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def manifest_shards(manifest: dict) -> list[dict]:
    fields = manifest["shard_fields"]
    return [dict(zip(fields, row, strict=True)) for row in manifest["shards"]]


class RemoteAccessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "small.sqlite3"
        with sqlite3.connect(self.db) as con:
            con.executescript(
                (ROOT / "schema/corpus-index.sql").read_text(encoding="utf-8")
            )
            con.execute(
                """INSERT INTO source_state(
                   corpus,repo_path,source_sha,parser_version,evidence_class,indexed_at,
                   record_count,relation_count,variant_count,lemma_count)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    "fixture-corpus",
                    "fixture/source",
                    "a" * 40,
                    "fixture-v1",
                    "canonical_root",
                    "ignored-by-export",
                    6,
                    1,
                    1,
                    0,
                ),
            )
            rows = []
            for sequence_no in range(1, 6):
                text = f"neighbor {sequence_no}"
                if sequence_no == 3:
                    text = "central anicca evidence"
                rows.append(
                    (
                        "fixture-corpus",
                        "pli",
                        "MN",
                        "mn-fixture",
                        f"mn-fixture:{sequence_no}",
                        "Fixture",
                        text,
                        text,
                        "",
                        text.replace(" ", ""),
                        "",
                        "fixture/source/mn.json",
                        "a" * 40,
                        "canonical_root",
                        "root_text",
                        "fixture witness",
                        "[]",
                        sequence_no,
                    )
                )
            rows.append(
                (
                    "fixture-corpus",
                    "pli",
                    "SN",
                    "other-work",
                    "other-work:1",
                    "Other",
                    "must not leak into context",
                    "must not leak into context",
                    "",
                    "mustnotleakintocontext",
                    "",
                    "fixture/source/other.json",
                    "a" * 40,
                    "canonical_root",
                    "root_text",
                    "other witness",
                    "[]",
                    2,
                )
            )
            con.executemany(
                """INSERT INTO records(
                   corpus,language,collection_name,work_id,segment_id,title,raw_text,
                   norm_text,folded_text,compact_text,lemma_text,source_path,source_sha,
                   evidence_class,text_role,witness,relation_ids,sequence_no)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                rows,
            )
            con.execute(
                """INSERT INTO works(
                   corpus,work_id,language,collection_name,title,metadata_json,
                   source_path,source_sha,evidence_class)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    "fixture-corpus",
                    "mn-fixture",
                    "pli",
                    "MN",
                    "Fixture",
                    "{}",
                    "fixture/source/mn.json",
                    "a" * 40,
                    "canonical_root",
                ),
            )
            con.execute(
                """INSERT INTO relations(
                   corpus,relation_type,from_id,to_id,details_json,source_path,
                   source_sha,evidence_class) VALUES (?,?,?,?,?,?,?,?)""",
                (
                    "fixture-corpus",
                    "fixture:parallel",
                    "mn-fixture",
                    "other-work",
                    '{"kind":"fixture"}',
                    "fixture/source/relations.json",
                    "a" * 40,
                    "metadata_relationship",
                ),
            )
            con.execute(
                """INSERT INTO variants(
                   corpus,work_id,segment_id,lemma,reading,witnesses,variant_type,
                   confidence,notes,source_path,source_sha,evidence_class)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "fixture-corpus",
                    "mn-fixture",
                    "mn-fixture:3",
                    "anicca",
                    "aniccaṃ",
                    "A",
                    "fixture_variant",
                    1.0,
                    None,
                    "fixture/source/variants.json",
                    "a" * 40,
                    "canonical_root",
                ),
            )
            con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
        with sqlite3.connect(self.db) as con:
            con.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_evidence_bundles_record_context_provenance_and_variants(self) -> None:
        hit = search(self.db, "anicca")["results"][0]
        result = evidence(self.db, hit["id"], window=2)
        self.assertTrue(result["found"])
        self.assertEqual(
            [row["sequence_no"] for row in result["context_before"]],
            [1, 2],
        )
        self.assertEqual(
            [row["sequence_no"] for row in result["context_after"]],
            [4, 5],
        )
        self.assertEqual(result["provenance"]["source_sha"], "a" * 40)
        self.assertEqual(result["provenance"]["text_role"], "root_text")
        self.assertEqual(result["variants"][0]["reading"], "aniccaṃ")

    def test_search_defaults_stay_plain_and_options_add_evidence(self) -> None:
        plain = search(self.db, "anicca")
        enriched = search(
            self.db,
            "anicca",
            context_window=2,
            with_provenance=True,
        )
        self.assertEqual(
            [row["id"] for row in plain["results"]],
            [row["id"] for row in enriched["results"]],
        )
        self.assertNotIn("context_before", plain["results"][0])
        self.assertNotIn("provenance", plain["results"][0])
        self.assertEqual(len(enriched["results"][0]["context_before"]), 2)
        self.assertEqual(
            enriched["results"][0]["provenance"]["corpus"],
            "fixture-corpus",
        )

    def test_remote_export_is_deterministic_and_preserves_evidence(self) -> None:
        output = Path(self.temp.name) / "remote"
        export_remote(self.db, output, max_shard_bytes=1_000)
        first_digest = tree_digest(output)
        manifest = json.loads(
            (output / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["index"]["record_count"], 6)
        self.assertEqual(
            manifest["record_count_per_corpus"],
            {"fixture-corpus": 6},
        )
        self.assertEqual(
            manifest["source_contract"]["sources"][0]["source_sha"],
            "a" * 40,
        )
        self.assertLessEqual(
            (output / "manifest.json").stat().st_size,
            512 * 1024,
        )

        record_rows = []
        for path in sorted((output / "records").rglob("*.jsonl")):
            record_rows.extend(
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
            )
        primary = [
            row
            for row in record_rows
            if row["export_role"] == "primary" and row["raw_text"].startswith("central")
        ][0]
        self.assertEqual(primary["evidence_class"], "canonical_root")
        self.assertEqual(primary["text_role"], "root_text")
        self.assertEqual(primary["source_sha"], "a" * 40)
        self.assertTrue(list((output / "relations").rglob("*.jsonl")))
        self.assertTrue(list((output / "variants").rglob("*.jsonl")))
        record_shards = [
            shard
            for shard in manifest_shards(manifest)
            if shard["kind"] == "records"
            and shard["corpus"] == "fixture-corpus"
            and shard["overlap_count"]
        ]
        self.assertTrue(record_shards)
        for shard in record_shards:
            rows = [
                json.loads(line)
                for line in (output / shard["path"]).read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            primary_indexes = [
                index
                for index, row in enumerate(rows)
                if row["export_role"] == "primary"
                and row["work_id"] == "mn-fixture"
            ]
            if not primary_indexes:
                continue
            first = primary_indexes[0]
            last = primary_indexes[-1]
            self.assertLessEqual(
                len(
                    [
                        row
                        for row in rows[:first]
                        if row["export_role"] == "context_overlap"
                        and row["work_id"] == "mn-fixture"
                    ]
                ),
                2,
            )
            self.assertLessEqual(
                len(
                    [
                        row
                        for row in rows[last + 1 :]
                        if row["export_role"] == "context_overlap"
                        and row["work_id"] == "mn-fixture"
                    ]
                ),
                2,
            )

        export_remote(self.db, output, max_shard_bytes=1_000)
        self.assertEqual(first_digest, tree_digest(output))

    def test_remote_export_refuses_to_replace_unrelated_directory(self) -> None:
        output = Path(self.temp.name) / "not-an-export"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "refusing to replace directory"):
            export_remote(self.db, output)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_remote_export_includes_committed_wal_rows(self) -> None:
        wal_db = Path(self.temp.name) / "wal.sqlite3"
        with sqlite3.connect(wal_db) as con:
            con.executescript(
                (ROOT / "schema/corpus-index.sql").read_text(encoding="utf-8")
            )
            con.execute("PRAGMA journal_mode=WAL")
            con.execute(
                """INSERT INTO records(
                   corpus,language,collection_name,work_id,segment_id,title,raw_text,
                   norm_text,folded_text,compact_text,lemma_text,source_path,source_sha,
                   evidence_class,text_role,witness,relation_ids,sequence_no)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "wal-corpus",
                    "pli",
                    "MN",
                    "wal-work",
                    "wal-work:1",
                    None,
                    "committed WAL evidence",
                    "committed wal evidence",
                    "",
                    "committedwalevidence",
                    "",
                    "fixture/wal.json",
                    "b" * 40,
                    "canonical_root",
                    "root_text",
                    "wal witness",
                    "[]",
                    1,
                ),
            )
        output = Path(self.temp.name) / "wal-remote"
        export_remote(wal_db, output)
        rows = [
            json.loads(line)
            for path in (output / "records").rglob("*.jsonl")
            for line in path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            [row["raw_text"] for row in rows if row["export_role"] == "primary"],
            ["committed WAL evidence"],
        )


if __name__ == "__main__":
    unittest.main()
