"""Read-only repetition and byte analysis for an existing pointer benchmark."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable

from .pointer_benchmark import _locator_rows
from .pointer_export import POINTER_FIELDS, _json_bytes


ANALYSIS_VERSION = 1
SOURCE_FILE_FIELDS = (
    "repository",
    "source_sha",
    "source_path",
    "source_blob_sha",
)
INDEXED_SOURCE_FIELDS = (*SOURCE_FILE_FIELDS, "indexed_source_path")
WORK_FIELDS = ("corpus", "work_id")
SOURCE_WORK_FIELDS = (
    "corpus",
    *SOURCE_FILE_FIELDS,
    "work_id",
)
QUERY_FIELDS = ("rank", "score", "match_reasons")
WORK_SEGMENT_FIELDS = (
    "record_id",
    "corpus",
    "work_id",
    "segment_id",
    "sequence_no",
    "evidence_class",
    "text_role",
    "witness",
)
FULL_STATIC_FIELDS = tuple(
    field for field in POINTER_FIELDS if field not in QUERY_FIELDS
)


def _canonical_value(fields: Iterable[str], pointer: dict) -> str:
    return json.dumps(
        {field: pointer[field] for field in fields},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _stable_id(prefix: str, fields: Iterable[str], pointer: dict) -> str:
    value = _canonical_value(fields, pointer).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(value).hexdigest()}"


def _percentile(values: list[int], percentage: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * percentage) - 1)]


def _reuse_stats(keys: Iterable[str]) -> dict:
    counts = Counter(keys)
    reuse = list(counts.values())
    total = sum(reuse)
    unique = len(counts)
    duplicate = total - unique
    return {
        "total_pointer_occurrences": total,
        "unique_records": unique,
        "duplicate_occurrences": duplicate,
        "dedup_ratio": duplicate / total if total else 0,
        "unique_ratio": unique / total if total else 0,
        "average_reuse_count": total / unique if unique else 0,
        "median_reuse_count": _percentile(reuse, 0.5),
        "p95_reuse_count": _percentile(reuse, 0.95),
        "max_reuse_count": max(reuse, default=0),
    }


def _field_fragment_bytes(pointer: dict, fields: Iterable[str]) -> int:
    """Count UTF-8 bytes for `"field":value` fragments, excluding JSON commas."""
    return sum(
        len(
            json.dumps(field, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        )
        + 1
        + len(
            json.dumps(pointer[field], ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        )
        for field in fields
    )


def _tree_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def _locator_jsonl_size(root: Path) -> int:
    return sum(
        path.stat().st_size
        for path in (root / "locator").rglob("*.jsonl")
    )


def _source_file_table(
    pointers: list[dict],
) -> tuple[dict[str, dict], dict[str, str]]:
    table: dict[str, dict] = {}
    identities: dict[str, str] = {}
    for pointer in pointers:
        source_id = _stable_id("source", INDEXED_SOURCE_FIELDS, pointer)
        metadata = {field: pointer[field] for field in INDEXED_SOURCE_FIELDS}
        existing = table.setdefault(source_id, metadata)
        if existing != metadata:
            raise ValueError(f"source ID collision: {source_id}")
        identities[id(pointer)] = source_id
    return table, identities


def _work_table(pointers: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
    table: dict[str, dict] = {}
    identities: dict[str, str] = {}
    for pointer in pointers:
        work_ref_id = _stable_id("work", WORK_FIELDS, pointer)
        metadata = {field: pointer[field] for field in WORK_FIELDS}
        existing = table.setdefault(work_ref_id, metadata)
        if existing != metadata:
            raise ValueError(f"work ID collision: {work_ref_id}")
        identities[id(pointer)] = work_ref_id
    return table, identities


def _simulate_source_file_only(
    rows: list[dict],
    source_ids: dict[str, str],
    source_table: dict[str, dict],
) -> dict:
    locator_rows = []
    for row in rows:
        pointers = []
        for pointer in row["pointers"]:
            pointers.append(
                {
                    "source_id": source_ids[id(pointer)],
                    **{
                        field: pointer[field]
                        for field in POINTER_FIELDS
                        if field not in INDEXED_SOURCE_FIELDS
                    },
                }
            )
        locator_rows.append(
            {
                "key": row["key"],
                "query_kind": row["query_kind"],
                "pointer_count": row["pointer_count"],
                "pointers": pointers,
            }
        )
    source_table_bytes = sum(
        len(_json_bytes({"source_id": source_id, **source_table[source_id]}))
        for source_id in sorted(source_table)
    )
    return {
        "source_table_records": len(source_table),
        "source_table_bytes": source_table_bytes,
        "simulated_locator_jsonl_bytes": sum(
            len(_json_bytes(row)) for row in locator_rows
        ),
    }


def _simulate_source_file_and_work(
    rows: list[dict],
    source_ids: dict[str, str],
    source_table: dict[str, dict],
    work_ids: dict[str, str],
    work_table: dict[str, dict],
) -> dict:
    moved = (*INDEXED_SOURCE_FIELDS, *WORK_FIELDS)
    locator_rows = []
    for row in rows:
        pointers = []
        for pointer in row["pointers"]:
            pointers.append(
                {
                    "source_id": source_ids[id(pointer)],
                    "work_ref_id": work_ids[id(pointer)],
                    **{
                        field: pointer[field]
                        for field in POINTER_FIELDS
                        if field not in moved
                    },
                }
            )
        locator_rows.append(
            {
                "key": row["key"],
                "query_kind": row["query_kind"],
                "pointer_count": row["pointer_count"],
                "pointers": pointers,
            }
        )
    source_table_bytes = sum(
        len(_json_bytes({"source_id": source_id, **source_table[source_id]}))
        for source_id in sorted(source_table)
    )
    work_table_bytes = sum(
        len(_json_bytes({"work_ref_id": work_id, **work_table[work_id]}))
        for work_id in sorted(work_table)
    )
    return {
        "source_table_records": len(source_table),
        "work_table_records": len(work_table),
        "source_table_bytes": source_table_bytes,
        "work_table_bytes": work_table_bytes,
        "simulated_locator_jsonl_bytes": sum(
            len(_json_bytes(row)) for row in locator_rows
        ),
    }


def analyze_pointer_repetition(benchmark_dir: Path) -> dict:
    """Measure metadata repetition without writing or changing a benchmark."""
    benchmark = benchmark_dir.resolve()
    manifest_path = benchmark / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"benchmark manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("artifact_kind") != "pointer_benchmark":
        raise ValueError(f"not a pointer benchmark artifact: {benchmark}")

    rows = _locator_rows(benchmark)
    pointers = [pointer for row in rows for pointer in row["pointers"]]
    groupings = {
        "A_source_file_identity": _reuse_stats(
            _canonical_value(SOURCE_FILE_FIELDS, pointer) for pointer in pointers
        ),
        "B_indexed_source_identity": _reuse_stats(
            _canonical_value(INDEXED_SOURCE_FIELDS, pointer) for pointer in pointers
        ),
        "C_work_identity": _reuse_stats(
            _canonical_value(WORK_FIELDS, pointer) for pointer in pointers
        ),
        "D_source_plus_work": _reuse_stats(
            _canonical_value(SOURCE_WORK_FIELDS, pointer) for pointer in pointers
        ),
        "E_full_static_segment_pointer": _reuse_stats(
            _canonical_value(FULL_STATIC_FIELDS, pointer) for pointer in pointers
        ),
    }
    source_counts = Counter(
        _canonical_value(SOURCE_FILE_FIELDS, pointer) for pointer in pointers
    )
    source_metadata = {
        _canonical_value(SOURCE_FILE_FIELDS, pointer): {
            field: pointer[field] for field in SOURCE_FILE_FIELDS
        }
        for pointer in pointers
    }
    top_sources = [
        {
            "reuse_count": count,
            **source_metadata[key],
        }
        for key, count in sorted(
            source_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:20]
    ]

    source_table, source_ids = _source_file_table(pointers)
    work_table, work_ids = _work_table(pointers)
    source_only = _simulate_source_file_only(rows, source_ids, source_table)
    source_and_work = _simulate_source_file_and_work(
        rows,
        source_ids,
        source_table,
        work_ids,
        work_table,
    )
    total_bytes = _tree_size(benchmark)
    locator_jsonl_bytes = _locator_jsonl_size(benchmark)
    fixed_bytes = total_bytes - locator_jsonl_bytes
    for simulation in (source_only, source_and_work):
        simulation["fixed_non_locator_bytes"] = fixed_bytes
        simulation["estimated_total_bytes"] = (
            fixed_bytes
            + simulation["simulated_locator_jsonl_bytes"]
            + simulation["source_table_bytes"]
            + simulation.get("work_table_bytes", 0)
        )
        simulation["estimated_reduction_percent"] = (
            1 - simulation["estimated_total_bytes"] / total_bytes
        ) * 100

    pointer_object_bytes = sum(len(_json_bytes(pointer)) for pointer in pointers)
    source_fragment_bytes = sum(
        _field_fragment_bytes(pointer, INDEXED_SOURCE_FIELDS)
        for pointer in pointers
    )
    work_segment_fragment_bytes = sum(
        _field_fragment_bytes(pointer, WORK_SEGMENT_FIELDS)
        for pointer in pointers
    )
    query_fragment_bytes = sum(
        _field_fragment_bytes(pointer, QUERY_FIELDS) for pointer in pointers
    )
    fragment_total = (
        source_fragment_bytes
        + work_segment_fragment_bytes
        + query_fragment_bytes
    )
    return {
        "analysis_version": ANALYSIS_VERSION,
        "artifact_kind": "pointer_repetition_analysis",
        "read_only": True,
        "source_benchmark": {
            "path": benchmark.name,
            "query_count": len(rows),
            "pointer_occurrences": len(pointers),
            "total_bytes": total_bytes,
            "locator_jsonl_bytes": locator_jsonl_bytes,
        },
        "groupings": groupings,
        "top_reused_source_files": top_sources,
        "byte_contribution": {
            "method": (
                "UTF-8 bytes of JSON field fragments (`\"field\":value`), "
                "excluding commas/braces; syntax bytes are reported separately"
            ),
            "source_file_field_bytes": source_fragment_bytes,
            "work_segment_field_bytes": work_segment_fragment_bytes,
            "query_specific_field_bytes": query_fragment_bytes,
            "field_fragment_bytes": fragment_total,
            "pointer_object_jsonl_bytes": pointer_object_bytes,
            "pointer_json_syntax_bytes": pointer_object_bytes - fragment_total,
        },
        "hypothetical": {
            "method": (
                "in-memory JSONL simulation using stable 64-hex SHA-256 IDs; "
                "the benchmark's non-locator files are held constant"
            ),
            "A_source_file_only": source_only,
            "B_source_file_plus_work_identity": source_and_work,
        },
    }
