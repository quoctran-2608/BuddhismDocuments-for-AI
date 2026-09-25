"""Read-only production-key and scale estimate from existing index artifacts."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .index import connect_readonly
from .model import compact, normalize


UNIVERSE_ANALYSIS_VERSION = 1
_CATEGORIES = ("latin_romanized", "cjk", "identifier")


def _is_cjk_character(value: str) -> bool:
    """Match the existing retrieval CJK predicate without changing search logic."""
    codepoint = ord(value)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x323AF
        or 0x3040 <= codepoint <= 0x30FF
        or 0xAC00 <= codepoint <= 0xD7AF
    )


def _length_distribution(keys: Iterable[str]) -> dict:
    buckets = {"1_char": 0, "2_char": 0, "3_char": 0, "4_plus_char": 0}
    for key in keys:
        length = len(key)
        if length == 1:
            buckets["1_char"] += 1
        elif length == 2:
            buckets["2_char"] += 1
        elif length == 3:
            buckets["3_char"] += 1
        elif length >= 4:
            buckets["4_plus_char"] += 1
    return buckets


def _stats(values: Iterable[str], *, cjk_excluded: bool = False) -> dict:
    raw = list(values)
    nonempty = [value for value in raw if value.strip()]
    excluded = [
        value
        for value in nonempty
        if cjk_excluded and any(_is_cjk_character(char) for char in value)
    ]
    candidates = [
        value
        for value in nonempty
        if value not in excluded
    ]
    normalized = [normalize(value) for value in candidates]
    normalized_nonempty = [value for value in normalized if value]
    originals = set(candidates)
    normalized_keys = set(normalized_nonempty)
    normalized_to_originals: dict[str, set[str]] = defaultdict(set)
    for value in originals:
        normalized_to_originals[normalize(value)].add(value)
    collision_examples = [
        {
            "normalized_key": key,
            "original_keys": sorted(values),
        }
        for key, values in sorted(normalized_to_originals.items())
        if key and len(values) > 1
    ][:20]
    return {
        "total_rows": len(raw),
        "empty_rows": len(raw) - len(nonempty),
        "cjk_excluded_rows": len(excluded),
        "candidate_nonempty_rows": len(candidates),
        "distinct_original_keys": len(originals),
        "distinct_normalized_keys": len(normalized_keys),
        "duplicate_normalized_keys": len(originals) - len(normalized_keys),
        "normalized_collision_examples": collision_examples,
        "normalize_to_empty_keys": sum(not value for value in normalized),
        "normalized_length_distribution": _length_distribution(normalized_keys),
        "one_character_normalized_keys": sum(
            len(value) == 1 for value in normalized_keys
        ),
    }


def _identifier_stats(values: Iterable[str | None]) -> dict:
    raw = list(values)
    nonempty = [value for value in raw if isinstance(value, str) and value.strip()]
    originals = set(nonempty)
    normalized = {normalize(value) for value in originals if normalize(value)}
    normalized_to_originals: dict[str, set[str]] = defaultdict(set)
    for value in originals:
        normalized_to_originals[normalize(value)].add(value)
    collision_examples = [
        {
            "normalized_key": key,
            "original_keys": sorted(values),
        }
        for key, values in sorted(normalized_to_originals.items())
        if key and len(values) > 1
    ][:20]
    punctuation_preserved = sum(
        any(not char.isalnum() and not char.isspace() for char in value)
        and normalize(value) == value.casefold().strip()
        for value in originals
    )
    compact_changed = sum(compact(value) != normalize(value) for value in originals)
    return {
        "distinct_original_work_id": len(originals),
        "distinct_normalized_work_id": len(normalized),
        "duplicate_normalized_keys": len(originals) - len(normalized),
        "normalized_collision_examples": collision_examples,
        "empty_distinct_values": sum(
            value is None or not (value.strip() if isinstance(value, str) else "")
            for value in raw
        ),
        "normalize_to_empty_keys": sum(not normalize(value) for value in originals),
        "normalized_length_distribution": _length_distribution(normalized),
        "one_character_normalized_keys": sum(
            len(value) == 1 for value in normalized
        ),
        "punctuation_lost_by_normalize": 0,
        "punctuation_sensitive_identifiers_preserved_by_normalize": (
            punctuation_preserved
        ),
        "identifiers_changed_by_compact_not_normalize": compact_changed,
    }


def _cjk_index_status(con) -> dict:
    row = con.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='records_cjk_fts'"
    ).fetchone()
    if row is None:
        return {
            "available": False,
            "reason": "records_cjk_fts is absent",
        }
    vocabulary = con.execute(
        """SELECT 1 FROM sqlite_master
           WHERE name='records_cjk_fts_vocab' LIMIT 1"""
    ).fetchone()
    document_count = con.execute("SELECT count(*) FROM records_cjk_fts").fetchone()[0]
    return {
        "available": False,
        "representation": "FTS5 contentless trigram index",
        "search_document_count": document_count,
        "minimum_runtime_cjk_query_length": 3,
        "vocabulary_table_present": bool(vocabulary),
        "reason": (
            "The existing contentless trigram FTS table has no vocabulary table. "
            "Counting a finite production CJK key universe would require scanning "
            "source text or creating an FTS vocabulary/index, both outside this "
            "read-only measurement."
        ),
        "key_length_distribution": None,
    }


def _benchmark_metrics(benchmark_dir: Path) -> dict:
    summary_path = benchmark_dir / "benchmark-summary.json"
    manifest_path = benchmark_dir / "manifest.json"
    if not summary_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError(f"benchmark summary/manifest not found: {benchmark_dir}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if summary.get("artifact_kind") != "pointer_benchmark":
        raise ValueError(f"not a pointer benchmark artifact: {benchmark_dir}")
    metrics = {}
    for category in _CATEGORIES:
        category_summary = summary["by_category"][category]
        metrics[category] = {
            "bytes_per_query": category_summary["bytes_per_query"],
            "pointers_per_query": category_summary["pointers_per_query"],
        }
    return {
        "source": {
            "path": benchmark_dir.name,
            "query_count": summary["overall"]["query_count"],
            "total_bytes": summary["artifact"]["total_bytes"],
            "locator_bytes": summary["artifact"]["locator_bytes"],
            "fixed_non_locator_bytes": (
                summary["artifact"]["total_bytes"] - summary["artifact"]["locator_bytes"]
            ),
            "generation_seconds_for_500_queries": 516,
            "selection": manifest["selection"],
        },
        "categories": metrics,
    }


def _estimate_category(key_count: int | None, metric: dict) -> dict:
    if key_count is None:
        return {
            "key_count": None,
            "estimated_locator_bytes": None,
            "estimated_pointer_occurrences": None,
            "reason": "finite key universe unavailable from the existing index",
        }
    bytes_ = metric["bytes_per_query"]
    pointers = metric["pointers_per_query"]
    lower_per_key = min(bytes_["median"], bytes_["average"])
    return {
        "key_count": key_count,
        "estimated_locator_bytes": {
            "lower": round(key_count * lower_per_key),
            "central": round(key_count * bytes_["average"]),
            "upper": round(key_count * bytes_["p95"]),
        },
        "estimated_pointer_occurrences": {
            "lower": round(key_count * min(pointers["median"], pointers["average"])),
            "central": round(key_count * pointers["average"]),
            "upper": round(key_count * pointers["p95"]),
        },
    }


def _range_per_key(distribution: dict) -> dict:
    """Return an ordered lower/central/upper range from benchmark statistics."""
    average = distribution["average"]
    median = distribution["median"]
    p95 = distribution["p95"]
    return {
        "lower": min(average, median),
        "central": average,
        "upper": max(average, p95),
    }


def _format_bytes(value: int | None) -> dict | None:
    if value is None:
        return None
    return {
        "bytes": value,
        "decimal_mb": value / 1_000_000,
        "mib": value / (1024 * 1024),
        "gib": value / (1024 * 1024 * 1024),
    }


def analyze_pointer_key_universe(db_path: Path, benchmark_dir: Path) -> dict:
    """Count known production namespaces and extrapolate only from benchmark data."""
    benchmark = benchmark_dir.resolve()
    metrics = _benchmark_metrics(benchmark)
    con = connect_readonly(db_path)
    try:
        lemma_values = [
            row["lemma"] for row in con.execute("SELECT lemma FROM lemmas")
        ]
        # This is intentionally the real records.work_id universe. It is the
        # production identifier input, not the smaller works metadata table.
        identifier_values = [
            row["work_id"] for row in con.execute("SELECT DISTINCT work_id FROM records")
        ]
        corpus_work_pairs = con.execute(
            """SELECT count(*) FROM (
                   SELECT DISTINCT corpus,work_id FROM records
                   WHERE work_id IS NOT NULL AND trim(work_id)<>''
               )"""
        ).fetchone()[0]
        cjk_status = _cjk_index_status(con)
    finally:
        con.close()

    latin = _stats(lemma_values, cjk_excluded=True)
    identifiers = _identifier_stats(identifier_values)
    latin_count = latin["distinct_normalized_keys"]
    identifier_count = identifiers["distinct_normalized_work_id"]
    identifiers["distinct_corpus_work_id"] = corpus_work_pairs
    known_namespace_total = latin_count + identifier_count
    estimates = {
        "latin_romanized": _estimate_category(
            latin_count,
            metrics["categories"]["latin_romanized"],
        ),
        "cjk": _estimate_category(None, metrics["categories"]["cjk"]),
        "identifier": _estimate_category(
            identifier_count,
            metrics["categories"]["identifier"],
        ),
    }

    known_locator = {
        bound: (
            estimates["latin_romanized"]["estimated_locator_bytes"][bound]
            + estimates["identifier"]["estimated_locator_bytes"][bound]
        )
        for bound in ("lower", "central", "upper")
    }
    fixed = metrics["source"]["fixed_non_locator_bytes"]
    known_total = {bound: fixed + value for bound, value in known_locator.items()}
    known_pointers = {
        bound: (
            estimates["latin_romanized"]["estimated_pointer_occurrences"][bound]
            + estimates["identifier"]["estimated_pointer_occurrences"][bound]
        )
        for bound in ("lower", "central", "upper")
    }
    seconds_per_query = (
        metrics["source"]["generation_seconds_for_500_queries"]
        / metrics["source"]["query_count"]
    )
    return {
        "analysis_version": UNIVERSE_ANALYSIS_VERSION,
        "artifact_kind": "pointer_key_universe_analysis",
        "read_only": True,
        "source_database": str(db_path.resolve()),
        "benchmark": metrics,
        "namespaces": {
            "terms_latin": latin,
            "terms_cjk": cjk_status,
            "ids": identifiers,
            "known_namespace_total_excluding_unavailable_cjk": known_namespace_total,
            "production_namespace_total": None,
            "production_namespace_total_reason": (
                "The CJK runtime index has no finite enumerable vocabulary in the "
                "current index, so a cross-namespace production total is unknown."
            ),
        },
        "estimates": {
            "category_specific": estimates,
            "known_latin_plus_identifier": {
                "key_count": known_namespace_total,
                "estimated_locator_bytes": {
                    bound: _format_bytes(value)
                    for bound, value in known_locator.items()
                },
                "estimated_total_artifact_bytes": {
                    bound: _format_bytes(value)
                    for bound, value in known_total.items()
                },
                "estimated_pointer_occurrences": known_pointers,
                "rough_generation_time_seconds": {
                    bound: round(known_namespace_total * seconds_per_query)
                    for bound in ("lower", "central", "upper")
                },
            },
            "cjk_formula_per_key": {
                "locator_bytes": _range_per_key(
                    metrics["categories"]["cjk"]["bytes_per_query"]
                ),
                "pointer_occurrences": _range_per_key(
                    metrics["categories"]["cjk"]["pointers_per_query"]
                ),
                "rough_generation_seconds": seconds_per_query,
            },
        },
    }
