"""Deterministic measurement artifact for the existing pointer export pipeline."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path
from typing import Iterable

from .index import connect_readonly
from .model import normalize
from .pointer_export import (
    POINTER_MARKER,
    _json_bytes,
    _replace_pointer_export,
    export_pointer_poc,
)


BENCHMARK_VERSION = 1
DEFAULT_LATIN_KEYS = 200
DEFAULT_CJK_KEYS = 200
DEFAULT_IDENTIFIER_KEYS = 100
DEFAULT_MAX_TOTAL_BYTES = 32 * 1024 * 1024
_CJK_RECORD_SAMPLE_LIMIT = 5_000
_IDENTIFIER_ROWS_PER_CORPUS = 1_500


def _is_cjk_character(value: str) -> bool:
    codepoint = ord(value)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x2FA1F
    )


def _stable_sample(values: Iterable[str], count: int, category: str) -> list[str]:
    """Choose real index values by normalized hash while preserving query spelling."""
    normalized: dict[str, str] = {}
    for value in values:
        if not isinstance(value, str):
            continue
        key = normalize(value)
        if not key:
            continue
        # Identifiers may contain punctuation required by exact lookup. Use the
        # normalized form only for deterministic de-duplication and selection.
        normalized.setdefault(key, value)
    ranked = sorted(
        normalized,
        key=lambda value: (
            hashlib.sha256(f"{category}\0{value}".encode("utf-8")).hexdigest(),
            value,
        ),
    )
    return [normalized[value] for value in ranked[:count]]


def _latin_keys(con, count: int) -> list[str]:
    values = (
        row["lemma"]
        for row in con.execute(
            """SELECT DISTINCT lemma FROM lemmas
               WHERE trim(lemma)<>'' ORDER BY lemma"""
        )
        if not any(_is_cjk_character(char) for char in row["lemma"])
        and any(char.isalpha() for char in row["lemma"])
    )
    return _stable_sample(values, count, "latin_romanized")


def _cjk_trigrams(value: str) -> Iterable[str]:
    run = ""
    for char in value:
        if _is_cjk_character(char):
            run += char
            continue
        for index in range(min(max(len(run) - 2, 0), 32)):
            yield run[index : index + 3]
        run = ""
    for index in range(min(max(len(run) - 2, 0), 32)):
        yield run[index : index + 3]


def _cjk_keys(con, count: int) -> list[str]:
    values = set()
    rows = con.execute(
        """SELECT raw_text FROM records
           WHERE language IN ('lzh','zh') AND raw_text<>''
           ORDER BY corpus,source_path,sequence_no,id LIMIT ?""",
        (_CJK_RECORD_SAMPLE_LIMIT,),
    )
    for row in rows:
        values.update(_cjk_trigrams(row["raw_text"]))
    return _stable_sample(values, count, "cjk")


def _identifier_keys(con, count: int) -> list[str]:
    values = set()
    corpora = [
        row["corpus"]
        for row in con.execute("SELECT corpus FROM source_state ORDER BY corpus")
    ]
    for corpus in corpora:
        rows = con.execute(
            """SELECT work_id FROM records
               WHERE corpus=? AND work_id IS NOT NULL AND trim(work_id)<>''
               ORDER BY source_path,sequence_no,id LIMIT ?""",
            (corpus, _IDENTIFIER_ROWS_PER_CORPUS),
        )
        values.update(row["work_id"] for row in rows)
    return _stable_sample(values, count, "identifier")


def sample_benchmark_queries(
    db_path: Path,
    latin_count: int = DEFAULT_LATIN_KEYS,
    cjk_count: int = DEFAULT_CJK_KEYS,
    identifier_count: int = DEFAULT_IDENTIFIER_KEYS,
) -> list[dict]:
    """Sample real search keys from existing index tables without writing state."""
    if min(latin_count, cjk_count, identifier_count) < 0:
        raise ValueError("benchmark key counts must be non-negative")
    con = connect_readonly(db_path)
    try:
        latin = _latin_keys(con, latin_count)
        cjk = _cjk_keys(con, cjk_count)
        identifiers = _identifier_keys(con, identifier_count)
    finally:
        con.close()
    return [
        *[
            {
                "category": "latin_romanized",
                "query_kind": "term",
                "query": query,
                "key": normalize(query),
                "sampling_source": "lemmas.lemma",
            }
            for query in latin
        ],
        *[
            {
                "category": "cjk",
                "query_kind": "term",
                "query": query,
                "key": normalize(query),
                "sampling_source": (
                    "records.raw_text CJK trigrams from a stable 5,000-row sample"
                ),
            }
            for query in cjk
        ],
        *[
            {
                "category": "identifier",
                "query_kind": "identifier",
                "query": identifier,
                "key": normalize(identifier),
                "sampling_source": (
                    "records.work_id from stable per-corpus row samples"
                ),
            }
            for identifier in identifiers
        ],
    ]


def _percentile(values: list[int], percentage: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * percentage) - 1)]


def _distribution(values: Iterable[int]) -> dict:
    items = list(values)
    return {
        "count": len(items),
        "average": sum(items) / len(items) if items else 0,
        "median": _percentile(items, 0.5),
        "p95": _percentile(items, 0.95),
        "max": max(items, default=0),
    }


def _locator_rows(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "locator").rglob("*.jsonl")):
        rows.extend(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
        )
    return rows


def _query_stats(rows: list[dict]) -> dict:
    pointers = [
        pointer
        for row in rows
        for pointer in row["pointers"]
    ]
    duplicate_keys = [
        (row["key"], pointer["corpus"], pointer["work_id"], pointer["source_path"])
        for row in rows
        for pointer in row["pointers"]
    ]
    query_bytes = [_json_bytes(row) for row in rows]
    return {
        "query_count": len(rows),
        "pointer_count": len(pointers),
        "distinct_work_file_count": len(
            {
                (pointer["corpus"], pointer["work_id"], pointer["source_path"])
                for pointer in pointers
            }
        ),
        "corpora_per_query": _distribution(
            [len({pointer["corpus"] for pointer in row["pointers"]}) for row in rows]
        ),
        "bytes_per_query": _distribution([len(value) for value in query_bytes]),
        "pointers_per_query": _distribution(
            [len(row["pointers"]) for row in rows]
        ),
        "queries_without_results": sum(not row["pointers"] for row in rows),
        "source_blob_sha_null_count": sum(
            pointer["source_blob_sha"] is None for pointer in pointers
        ),
        "duplicate_query_corpus_work_source_count": (
            len(duplicate_keys) - len(set(duplicate_keys))
        ),
        "raw_text_field_count": sum("raw_text" in pointer for pointer in pointers),
    }


def _write_json(path: Path, value: dict | list) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _tree_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def export_pointer_benchmark(
    db_path: Path,
    output_dir: Path,
    sources_config: Path,
    root: Path,
    latin_count: int = DEFAULT_LATIN_KEYS,
    cjk_count: int = DEFAULT_CJK_KEYS,
    identifier_count: int = DEFAULT_IDENTIFIER_KEYS,
    limit: int = 20,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict:
    """Measure the existing pointer pipeline on a deterministic real-key sample."""
    if max_total_bytes <= 0:
        raise ValueError("max_total_bytes must be positive")
    sampled = sample_benchmark_queries(
        db_path,
        latin_count=latin_count,
        cjk_count=cjk_count,
        identifier_count=identifier_count,
    )
    if not sampled:
        raise ValueError("benchmark sampling found no usable local search keys")

    output = output_dir.resolve()
    stage = output.parent / f".{output.name}.benchmark"
    if stage.exists():
        if not (stage / POINTER_MARKER).is_file():
            raise ValueError(f"refusing to replace unmarked benchmark stage: {stage}")
        shutil.rmtree(stage)

    terms = [row["query"] for row in sampled if row["query_kind"] == "term"]
    identifiers = [
        row["query"] for row in sampled if row["query_kind"] == "identifier"
    ]
    export_pointer_poc(
        db_path,
        stage,
        sources_config,
        terms,
        identifiers,
        limit=limit,
        root=root,
    )
    locator_rows = _locator_rows(stage)
    category_by_key = {
        (row["query_kind"], row["key"]): row["category"] for row in sampled
    }
    rows_by_category: dict[str, list[dict]] = {
        "latin_romanized": [],
        "cjk": [],
        "identifier": [],
    }
    for row in locator_rows:
        rows_by_category[category_by_key[(row["query_kind"], row["key"])]].append(
            row
        )

    manifest_path = stage / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_kind"] = "pointer_benchmark"
    manifest["proof_of_concept"] = False
    manifest["benchmark_query_list"] = "benchmark-queries.json"
    manifest["benchmark_summary"] = "benchmark-summary.json"
    manifest["benchmark"] = {
        "benchmark_version": BENCHMARK_VERSION,
        "sampling": {
            "strategy": "SHA-256(category + NUL + normalized key)",
            "requested": {
                "latin_romanized": latin_count,
                "cjk": cjk_count,
                "identifier": identifier_count,
            },
            "sampled": {
                category: sum(
                    item["category"] == category for item in sampled
                )
                for category in rows_by_category
            },
        },
        "max_total_bytes": max_total_bytes,
    }
    _write_json(manifest_path, manifest)
    locator_manifest_path = stage / "locator" / "manifest.json"
    locator_manifest = json.loads(locator_manifest_path.read_text(encoding="utf-8"))
    locator_manifest["artifact_kind"] = "pointer_benchmark"
    _write_json(locator_manifest_path, locator_manifest)
    _write_json(stage / "benchmark-queries.json", sampled)
    (stage / "README.md").write_text(
        """# Pointer Benchmark

This is a deterministic measurement artifact for the existing raw-text-free
pointer pipeline. It is not a production locator and does not change ranking,
evidence, source SHAs, or retrieval behavior.

- `benchmark-queries.json` records the real local index keys sampled for this run.
- `locator/` contains source pointers only; it contains no `raw_text`.
- `benchmark-summary.json` records size, pointer, duplicate, corpus, and blob-SHA
  measurements plus linear size extrapolations.

Each pointer was generated through the existing search/ranking pipeline, then
collapsed by `(corpus, work_id, source_path)` and bounded per corpus. Open the
pointer's pinned source file to verify any textual claim.
""",
        encoding="utf-8",
    )

    summary = {
        "benchmark_version": BENCHMARK_VERSION,
        "artifact_kind": "pointer_benchmark",
        "sampling": manifest["benchmark"]["sampling"],
        "selection": manifest["selection"],
        "overall": _query_stats(locator_rows),
        "by_category": {
            category: _query_stats(rows)
            for category, rows in rows_by_category.items()
        },
        "artifact": {
            "file_count": 0,
            "total_bytes": 0,
            "locator_bytes": sum(item["byte_size"] for item in manifest["locator"]["files"]),
            "max_total_bytes": max_total_bytes,
        },
        "scale_estimate_bytes": {},
    }
    summary_path = stage / "benchmark-summary.json"
    _write_json(summary_path, summary)
    if _tree_size(stage) > max_total_bytes:
        raise ValueError(
            "benchmark artifact exceeds safe size before replacement: "
            f"{_tree_size(stage)} > {max_total_bytes}; generated "
            f"{len(locator_rows)} of {len(sampled)} sampled queries"
        )
    for _ in range(3):
        summary["artifact"]["file_count"] = sum(
            path.is_file() for path in stage.rglob("*")
        )
        summary["artifact"]["total_bytes"] = _tree_size(stage)
        per_query = summary["artifact"]["total_bytes"] / len(locator_rows)
        summary["scale_estimate_bytes"] = {
            str(target): round(per_query * target)
            for target in (10_000, 50_000, 100_000)
        }
        _write_json(summary_path, summary)
    _replace_pointer_export(stage, output)
    return {
        "output": str(output),
        "query_count": len(locator_rows),
        "pointer_count": summary["overall"]["pointer_count"],
        "total_bytes": summary["artifact"]["total_bytes"],
        "summary": str(output / "benchmark-summary.json"),
        "queries": str(output / "benchmark-queries.json"),
        "raw_text_exported": False,
    }
