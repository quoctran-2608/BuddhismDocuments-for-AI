"""Compact serialization POC for an existing pointer benchmark artifact."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from .pointer_export import POINTER_FIELDS, POINTER_MARKER, _json_bytes, _replace_pointer_export


COMPACT_FORMAT_VERSION = 1
_RANKING_FIELDS = ("rank", "score", "match_reasons")
_POINTER_METADATA_FIELDS = tuple(
    field for field in POINTER_FIELDS if field not in _RANKING_FIELDS
)
_REFERENCE_FIELDS = ("pointer_id", *_RANKING_FIELDS)


def _read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict | list) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _tree_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def _locator_rows(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "locator").rglob("*.jsonl")):
        rows.extend(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
        )
    return rows


def _metadata(pointer: dict) -> dict:
    return {field: pointer[field] for field in _POINTER_METADATA_FIELDS}


def _pointer_id(metadata: dict) -> str:
    """Return a stable full SHA-256 ID for canonical pointer metadata."""
    encoded = json.dumps(
        metadata,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _pointer_table(root: Path) -> dict[str, dict]:
    table = {}
    for path in sorted((root / "pointers").rglob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            pointer_id = row.pop("pointer_id")
            if pointer_id in table:
                raise ValueError(f"duplicate pointer_id in compact table: {pointer_id}")
            if _pointer_id(row) != pointer_id:
                raise ValueError(f"pointer_id does not match metadata: {pointer_id}")
            table[pointer_id] = row
    return table


def reconstruct_compact_rows(root: Path) -> list[dict]:
    """Resolve compact locator references back into benchmark-equivalent pointers."""
    table = _pointer_table(root)
    rows = []
    for row in _locator_rows(root):
        pointers = []
        for reference in row["pointer_refs"]:
            pointer_id = reference["pointer_id"]
            metadata = table.get(pointer_id)
            if metadata is None:
                raise ValueError(f"dangling compact pointer_id: {pointer_id}")
            pointer = {
                **{field: reference[field] for field in _RANKING_FIELDS},
                **metadata,
            }
            if tuple(pointer) != POINTER_FIELDS:
                raise ValueError(
                    f"compact pointer fields differ from contract: {pointer_id}"
                )
            pointers.append(pointer)
        rows.append(
            {
                "key": row["key"],
                "query_kind": row["query_kind"],
                "pointer_count": row["pointer_count"],
                "pointers": pointers,
            }
        )
    return rows


def export_pointer_compact_poc(
    benchmark_dir: Path,
    output_dir: Path,
) -> dict:
    """Serialize an existing benchmark with shared pointer metadata and references."""
    benchmark = benchmark_dir.resolve()
    if not (benchmark / "manifest.json").is_file():
        raise FileNotFoundError(f"benchmark manifest not found: {benchmark}")
    if not (benchmark / "benchmark-queries.json").is_file():
        raise FileNotFoundError(
            f"benchmark query list not found: {benchmark / 'benchmark-queries.json'}"
        )
    benchmark_manifest = _read_json(benchmark / "manifest.json")
    if benchmark_manifest.get("artifact_kind") != "pointer_benchmark":
        raise ValueError(f"not a pointer benchmark artifact: {benchmark}")

    output = output_dir.resolve()
    stage = output.parent / f".{output.name}.compact"
    if stage.exists():
        if not (stage / POINTER_MARKER).is_file():
            raise ValueError(f"refusing to replace unmarked compact stage: {stage}")
        import shutil

        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    source_rows = _locator_rows(benchmark)
    pointers: dict[str, dict] = {}
    compact_rows = []
    for row in source_rows:
        references = []
        for pointer in row["pointers"]:
            metadata = _metadata(pointer)
            pointer_id = _pointer_id(metadata)
            previous = pointers.setdefault(pointer_id, metadata)
            if previous != metadata:
                raise ValueError(f"pointer ID collision: {pointer_id}")
            references.append(
                {
                    "pointer_id": pointer_id,
                    **{field: pointer[field] for field in _RANKING_FIELDS},
                }
            )
        compact_rows.append(
            {
                "key": row["key"],
                "query_kind": row["query_kind"],
                "pointer_count": len(references),
                "pointer_refs": references,
            }
        )

    pointer_path = stage / "pointers" / "part-000001.jsonl"
    pointer_path.parent.mkdir(parents=True)
    pointer_path.write_bytes(
        b"".join(
            _json_bytes({"pointer_id": pointer_id, **pointers[pointer_id]})
            for pointer_id in sorted(pointers)
        )
    )

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    query_by_key = {
        (row["query_kind"], row["key"]): row
        for row in _read_json(benchmark / "benchmark-queries.json")
    }
    for row in compact_rows:
        query = query_by_key[(row["query_kind"], row["key"])]
        namespace = "terms/cjk" if query["category"] == "cjk" else (
            "ids" if row["query_kind"] == "identifier" else "terms/latin"
        )
        bucket = hashlib.sha256(row["key"].encode("utf-8")).hexdigest()[:2]
        grouped[(namespace, bucket)].append(row)

    locator_files = []
    for (namespace, bucket), rows in sorted(grouped.items()):
        relative = Path("locator") / namespace / bucket / "part-000001.jsonl"
        path = stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            b"".join(_json_bytes(row) for row in sorted(rows, key=lambda item: item["key"]))
        )
        locator_files.append(
            {
                "path": relative.as_posix(),
                "byte_size": path.stat().st_size,
                "line_count": len(rows),
            }
        )

    _write_json(stage / "benchmark-queries.json", _read_json(benchmark / "benchmark-queries.json"))
    source_total_bytes = _tree_size(benchmark)
    pointer_bytes = pointer_path.stat().st_size
    locator_bytes = sum(item["byte_size"] for item in locator_files)
    source_occurrences = sum(len(row["pointers"]) for row in source_rows)
    compact_manifest = {
        "compact_format_version": COMPACT_FORMAT_VERSION,
        "artifact_kind": "pointer_compact_poc",
        "proof_of_concept": True,
        "raw_text_exported": False,
        "source_benchmark": {
            "path": benchmark.name,
            "artifact_kind": benchmark_manifest["artifact_kind"],
            "query_count": len(source_rows),
            "pointer_occurrences": source_occurrences,
            "total_bytes": source_total_bytes,
        },
        "pointer_table": {
            "path": "pointers/part-000001.jsonl",
            "pointer_id": "SHA-256 canonical JSON of pointer metadata",
            "fields": list(_POINTER_METADATA_FIELDS),
            "record_count": len(pointers),
            "byte_size": pointer_bytes,
        },
        "locator": {
            "reference_fields": list(_REFERENCE_FIELDS),
            "file_pattern": "locator/<namespace>/<bucket>/part-000001.jsonl",
            "files": locator_files,
            "reference_count": source_occurrences,
            "byte_size": locator_bytes,
        },
        "equivalence": {
            "source_pointer_fields": list(POINTER_FIELDS),
            "preserves": [
                "query",
                "candidate_count",
                "candidate_order",
                "rank",
                "score",
                "match_reasons",
                "source_metadata",
                "source_blob_sha",
            ],
        },
    }
    _write_json(stage / "manifest.json", compact_manifest)
    locator_manifest = {
        "compact_format_version": COMPACT_FORMAT_VERSION,
        "artifact_kind": "pointer_compact_poc",
        "raw_text_exported": False,
        "reference_fields": list(_REFERENCE_FIELDS),
        "files": locator_files,
    }
    _write_json(stage / "locator" / "manifest.json", locator_manifest)
    (stage / "README.md").write_text(
        """# Compact Pointer Serialization POC

This POC serializes the already-generated 500-query pointer benchmark without
running retrieval or changing candidates. `pointers/part-000001.jsonl` stores
each distinct full source/segment metadata record once under a stable
`pointer_id`. Locator rows retain query-specific `rank`, `score`, and
`match_reasons`, then reference that metadata by `pointer_id`.

To reconstruct a benchmark-equivalent pointer result:

1. Read the locator row for the query key.
2. Resolve every `pointer_id` in `pointer_refs` from the pointer table.
3. Merge each reference's `rank`, `score`, and `match_reasons` with metadata.
4. Keep the reference order unchanged.

The artifact contains no `raw_text` and is a serialization measurement only,
not a production locator design.
""",
        encoding="utf-8",
    )
    (stage / POINTER_MARKER).write_text(
        f"compact_format_version={COMPACT_FORMAT_VERSION}\n",
        encoding="utf-8",
    )

    reconstructed = reconstruct_compact_rows(stage)
    if reconstructed != source_rows:
        raise ValueError("compact serialization does not reconstruct benchmark rows")

    summary = {
        "compact_format_version": COMPACT_FORMAT_VERSION,
        "source_benchmark": compact_manifest["source_benchmark"],
        "query_count": len(source_rows),
        "pointer_occurrences": source_occurrences,
        "shared_pointer_records": len(pointers),
        "locator_references": source_occurrences,
        "pointer_table_bytes": pointer_bytes,
        "locator_bytes": locator_bytes,
        "artifact": {
            "file_count": sum(path.is_file() for path in stage.rglob("*")),
            "total_bytes": _tree_size(stage),
        },
        "raw_text_field_count": 0,
        "dangling_pointer_id_count": 0,
        "equivalent_to_source_benchmark": True,
        "scale_estimate_bytes": {},
    }
    summary_path = stage / "compact-summary.json"
    for _ in range(3):
        summary["artifact"]["file_count"] = sum(
            path.is_file() for path in stage.rglob("*")
        )
        summary["artifact"]["total_bytes"] = _tree_size(stage)
        compact_per_query = summary["artifact"]["total_bytes"] / len(source_rows)
        summary["scale_estimate_bytes"] = {
            str(target): round(compact_per_query * target)
            for target in (10_000, 50_000, 100_000)
        }
        summary["size_reduction_percent"] = round(
            (1 - summary["artifact"]["total_bytes"] / source_total_bytes) * 100,
            4,
        )
        _write_json(summary_path, summary)
    _replace_pointer_export(stage, output)
    return {
        "output": str(output),
        "query_count": len(source_rows),
        "pointer_occurrences": source_occurrences,
        "shared_pointer_records": len(pointers),
        "total_bytes": summary["artifact"]["total_bytes"],
        "size_reduction_percent": summary["size_reduction_percent"],
        "summary": str(output / "compact-summary.json"),
        "raw_text_exported": False,
    }
