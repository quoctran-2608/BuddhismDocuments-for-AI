from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from corpus_research.pointer_export import (
    _select_corpus_candidates,
    _source_blob_sha,
    _term_rows,
    export_pointer_poc,
)
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
                evidence_class = "canonical_root"
                if sequence_no == 1:
                    text = "anicca low-priority evidence"
                    evidence_class = "auxiliary_reference"
                if sequence_no == 3:
                    text = "central anicca evidence 無常 如是我聞"
                rows.append(
                    (
                        "fixture-corpus",
                        "lzh" if sequence_no == 3 else "pli",
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
                        evidence_class,
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
            con.executemany(
                """INSERT INTO lemmas(
                   corpus,language,work_id,segment_id,surface,lemma,pos,
                   morphology_json,source_path,source_sha,evidence_class)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    (
                        "fixture-corpus",
                        "pli",
                        "mn-fixture",
                        "mn-fixture:3",
                        "anicca",
                        "anicca",
                        None,
                        "{}",
                        "fixture/source/mn.json",
                        "a" * 40,
                        "canonical_root",
                    )
                ],
            )
            con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
        with sqlite3.connect(self.db) as con:
            con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        self.sources_config = Path(self.temp.name) / "corpus-sources.json"
        self.sources_config.write_text(
            json.dumps(
                {
                    "sources": [
                        {
                            "corpus": "fixture-corpus",
                            "repo": "fixture/source",
                            "github_repository": "fixture-org/fixture-source",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

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
        locator_manifest = json.loads(
            (output / "locator/manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(locator_manifest["locator_version"], 2)
        self.assertGreater(locator_manifest["file_count"], 0)
        self.assertEqual(manifest["locator"]["manifest"], "locator/manifest.json")
        self.assertEqual(
            locator_manifest["generated_from"]["record_count"],
            manifest["index"]["record_count"],
        )
        locator_rows = [
            json.loads(line)
            for path in sorted((output / "locator").rglob("*.jsonl"))
            for line in path.read_text(encoding="utf-8").splitlines()
        ]
        by_key = {row["key"]: row for row in locator_rows}
        self.assertTrue(by_key["anicca"]["records"])
        self.assertTrue(by_key["無常"]["records"])
        self.assertTrue(by_key["mn-fixture"]["records"])
        self.assertTrue(by_key["mn-fixture"]["relations"])
        self.assertTrue(by_key["mn-fixture"]["variants"])
        anicca_shards = by_key["anicca"]["records"]
        self.assertEqual(len(anicca_shards), 2)
        primary_ids_by_shard = {}
        for shard_index in anicca_shards:
            shard = manifest_shards(manifest)[shard_index]
            primary_ids_by_shard[shard_index] = [
                row["id"]
                for row in (
                    json.loads(line)
                    for line in (output / shard["path"])
                    .read_text(encoding="utf-8")
                    .splitlines()
                )
                if row["export_role"] == "primary"
            ]
        self.assertIn(3, primary_ids_by_shard[anicca_shards[0]])
        self.assertIn(1, primary_ids_by_shard[anicca_shards[1]])
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

    def test_pointer_poc_is_deterministic_and_never_exports_raw_text(self) -> None:
        output = Path(self.temp.name) / "pointer-poc"
        result = export_pointer_poc(
            self.db,
            output,
            self.sources_config,
            ["anicca", "無常"],
            ["mn-fixture"],
            limit=10,
            root=ROOT,
        )
        self.assertFalse(result["raw_text_exported"])
        first_digest = tree_digest(output)
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["proof_of_concept"])
        self.assertFalse(manifest["raw_text_exported"])
        locator_manifest = json.loads(
            (output / "locator/manifest.json").read_text(encoding="utf-8")
        )
        self.assertFalse(locator_manifest["raw_text_exported"])
        self.assertEqual(
            locator_manifest["pointer_fields"],
            manifest["pointer_fields"],
        )
        self.assertEqual(
            manifest["runtime"],
            "GitHub Connector -> pinned source repository file",
        )
        self.assertEqual(
            manifest["pointer_fields"],
            [
                "rank",
                "score",
                "match_reasons",
                "record_id",
                "corpus",
                "repository",
                "source_sha",
                "source_path",
                "source_blob_sha",
                "indexed_source_path",
                "work_id",
                "segment_id",
                "sequence_no",
                "evidence_class",
                "text_role",
                "witness",
            ],
        )
        payload = b"".join(
            path.read_bytes()
            for path in (output / "locator").rglob("*.jsonl")
        )
        self.assertNotIn(b"raw_text", payload)
        self.assertNotIn(b"central anicca evidence", payload)
        rows = [
            json.loads(line)
            for path in output.rglob("*.jsonl")
            for line in path.read_text(encoding="utf-8").splitlines()
        ]
        by_key = {row["key"]: row for row in rows}
        anicca = by_key["anicca"]["pointers"]
        self.assertEqual(
            [pointer["record_id"] for pointer in anicca],
            [3],
        )
        self.assertEqual(anicca[0]["score"], 275)
        self.assertEqual(anicca[0]["match_reasons"], ["exact", "corpus-lemma"])
        self.assertIsNone(anicca[0]["source_blob_sha"])
        self.assertEqual(anicca[0]["repository"], "fixture-org/fixture-source")
        self.assertEqual(anicca[0]["source_path"], "mn.json")
        self.assertEqual(
            anicca[0]["indexed_source_path"],
            "fixture/source/mn.json",
        )
        self.assertEqual(by_key["無常"]["pointers"][0]["record_id"], 3)
        self.assertTrue(by_key["mn-fixture"]["pointers"])
        export_pointer_poc(
            self.db,
            output,
            self.sources_config,
            ["anicca", "無常"],
            ["mn-fixture"],
            limit=10,
            root=ROOT,
        )
        self.assertEqual(first_digest, tree_digest(output))

    def test_pointer_selection_keeps_best_distinct_work_file_per_corpus(self) -> None:
        rows = [
            {
                "id": 3,
                "corpus": "alpha",
                "work_id": "shared",
                "source_path": "alpha/shared.json",
                "sequence_no": 2,
                "score": 195,
            },
            {
                "id": 2,
                "corpus": "alpha",
                "work_id": "shared",
                "source_path": "alpha/shared.json",
                "sequence_no": 1,
                "score": 195,
            },
            {
                "id": 1,
                "corpus": "alpha",
                "work_id": "other",
                "source_path": "alpha/other.json",
                "sequence_no": 1,
                "score": 150,
            },
            {
                "id": 4,
                "corpus": "beta",
                "work_id": "beta-work",
                "source_path": "beta/work.json",
                "sequence_no": 1,
                "score": 130,
            },
        ]
        selected = _select_corpus_candidates(rows, per_corpus_limit=1)
        self.assertEqual([row["id"] for row in selected], [2, 4])
        self.assertEqual({row["corpus"] for row in selected}, {"alpha", "beta"})

    def test_term_pointer_candidates_reuse_search_per_corpus(self) -> None:
        sources = {
            "alpha": {"repository": "org/alpha", "repo_path": "alpha"},
            "beta": {"repository": "org/beta", "repo_path": "beta"},
        }
        responses = {
            "alpha": [
                {
                    "id": 1,
                    "corpus": "alpha",
                    "work_id": "one-work",
                    "source_path": "alpha/one.json",
                    "sequence_no": 1,
                    "score": 195,
                    "match_reasons": ["exact"],
                },
                {
                    "id": 2,
                    "corpus": "alpha",
                    "work_id": "one-work",
                    "source_path": "alpha/one.json",
                    "sequence_no": 2,
                    "score": 195,
                    "match_reasons": ["exact"],
                },
                {
                    "id": 3,
                    "corpus": "alpha",
                    "work_id": "two-work",
                    "source_path": "alpha/two.json",
                    "sequence_no": 1,
                    "score": 190,
                    "match_reasons": ["exact"],
                },
            ],
            "beta": [
                {
                    "id": 4,
                    "corpus": "beta",
                    "work_id": "beta-work",
                    "source_path": "beta/work.json",
                    "sequence_no": 1,
                    "score": 100,
                    "match_reasons": ["fts"],
                },
            ],
        }

        def existing_search(
            _db: Path,
            _query: str,
            limit: int,
            _language: str | None = None,
            corpus: str | None = None,
        ) -> dict:
            self.assertEqual(limit, 5)
            return {"results": responses[corpus or ""]}

        with patch(
            "corpus_research.pointer_export.search",
            side_effect=existing_search,
        ) as mocked_search:
            rows = _term_rows(self.db, "anicca", sources, per_corpus_limit=1)

        self.assertEqual(mocked_search.call_count, 2)
        self.assertEqual([row["id"] for row in rows], [1, 4])
        self.assertEqual({row["corpus"] for row in rows}, {"alpha", "beta"})

    def test_source_blob_sha_matches_pinned_local_source_file(self) -> None:
        source = {"repo_path": "cbeta/BM_u8"}
        source_sha = "83bc009a6f3333fa2d61cb436ee6181b1335beb4"
        source_path = "T/T02/new.txt"
        expected = subprocess.check_output(
            [
                "git",
                "-C",
                str(ROOT / source["repo_path"]),
                "rev-parse",
                f"{source_sha}:{source_path}",
            ],
            text=True,
        ).strip()
        self.assertEqual(
            _source_blob_sha(ROOT, source, source_sha, source_path, {}),
            expected,
        )

    def test_pointer_benchmark_is_deterministic_and_reports_pointer_invariants(
        self,
    ) -> None:
        from corpus_research.pointer_benchmark import (
            _stable_sample,
            export_pointer_benchmark,
            sample_benchmark_queries,
        )

        self.assertEqual(
            _stable_sample(["pli-tv-bi-vb-pc22"], 1, "identifier"),
            ["pli-tv-bi-vb-pc22"],
        )
        sample = sample_benchmark_queries(
            self.db,
            latin_count=1,
            cjk_count=1,
            identifier_count=1,
        )
        self.assertEqual(
            [(row["category"], row["sampling_source"]) for row in sample],
            [
                ("latin_romanized", "lemmas.lemma"),
                (
                    "cjk",
                    "records.raw_text CJK trigrams from a stable 5,000-row sample",
                ),
                (
                    "identifier",
                    "records.work_id from stable per-corpus row samples",
                ),
            ],
        )
        output = Path(self.temp.name) / "pointer-benchmark"
        result = export_pointer_benchmark(
            self.db,
            output,
            self.sources_config,
            ROOT,
            latin_count=1,
            cjk_count=1,
            identifier_count=1,
            limit=10,
            max_total_bytes=1_000_000,
        )
        self.assertEqual(result["query_count"], 3)
        self.assertFalse(result["raw_text_exported"])
        first_digest = tree_digest(output)
        summary = json.loads(
            (output / "benchmark-summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(summary["overall"]["raw_text_field_count"], 0)
        self.assertEqual(
            summary["overall"]["duplicate_query_corpus_work_source_count"],
            0,
        )
        self.assertEqual(summary["overall"]["source_blob_sha_null_count"], 2)
        self.assertTrue((output / "benchmark-queries.json").is_file())
        self.assertEqual(
            json.loads((output / "manifest.json").read_text(encoding="utf-8"))[
                "artifact_kind"
            ],
            "pointer_benchmark",
        )
        export_pointer_benchmark(
            self.db,
            output,
            self.sources_config,
            ROOT,
            latin_count=1,
            cjk_count=1,
            identifier_count=1,
            limit=10,
            max_total_bytes=1_000_000,
        )
        self.assertEqual(first_digest, tree_digest(output))

    def test_compact_pointer_poc_reconstructs_benchmark_exactly(self) -> None:
        from corpus_research.pointer_benchmark import export_pointer_benchmark
        from corpus_research.pointer_compact import (
            _locator_rows,
            export_pointer_compact_poc,
            reconstruct_compact_rows,
        )

        benchmark = Path(self.temp.name) / "pointer-benchmark"
        export_pointer_benchmark(
            self.db,
            benchmark,
            self.sources_config,
            ROOT,
            latin_count=1,
            cjk_count=1,
            identifier_count=1,
            limit=10,
            max_total_bytes=1_000_000,
        )
        compact = Path(self.temp.name) / "pointer-compact-poc"
        result = export_pointer_compact_poc(benchmark, compact)
        self.assertEqual(result["query_count"], 3)
        self.assertFalse(result["raw_text_exported"])
        self.assertEqual(
            reconstruct_compact_rows(compact),
            _locator_rows(benchmark),
        )
        summary = json.loads(
            (compact / "compact-summary.json").read_text(encoding="utf-8")
        )
        self.assertTrue(summary["equivalent_to_source_benchmark"])
        self.assertEqual(
            summary["locator_references"],
            sum(len(row["pointers"]) for row in _locator_rows(benchmark)),
        )
        self.assertEqual(summary["dangling_pointer_id_count"], 0)
        self.assertEqual(summary["raw_text_field_count"], 0)
        self.assertEqual(summary["shared_pointer_records"], 2)
        payload = b"".join(
            path.read_bytes()
            for path in compact.rglob("*.jsonl")
        )
        self.assertNotIn(b"raw_text", payload)
        first_digest = tree_digest(compact)
        export_pointer_compact_poc(benchmark, compact)
        self.assertEqual(first_digest, tree_digest(compact))


if __name__ == "__main__":
    unittest.main()
