"""Read-only vocabulary measurement for the existing CJK FTS5 trigram index."""

from __future__ import annotations

import math
import sqlite3
from pathlib import Path

from .pointer_universe import _benchmark_metrics, _format_bytes, _range_per_key


CJK_VOCAB_ANALYSIS_VERSION = 1
_SAMPLE_SIZE = 20
_TOP_SIZE = 20
_CJK_GLOB_PATTERNS = (
    "*[㐀-䶿]*",
    "*[一-鿿]*",
    "*[豈-﫿]*",
    "*[𠀀-𲎯]*",
    "*[ぁ-ヿ]*",
    "*[가-힣]*",
)
_CJK_WHERE = " OR ".join("term GLOB ?" for _ in _CJK_GLOB_PATTERNS)


def _frequency_percentiles(histogram: list[sqlite3.Row], total: int) -> tuple[int, int]:
    """Compute exact median and P95 from SQL's doc-frequency histogram."""
    median_rank = math.ceil(total * 0.5)
    p95_rank = math.ceil(total * 0.95)
    running = 0
    median = None
    p95 = None
    for row in histogram:
        running += int(row["token_count"])
        if median is None and running >= median_rank:
            median = int(row["document_frequency"])
        if p95 is None and running >= p95_rank:
            p95 = int(row["document_frequency"])
            break
    if median is None or p95 is None:
        raise ValueError("empty CJK vocabulary frequency histogram")
    return median, p95


def _cjk_estimate(key_count: int, benchmark: dict) -> dict:
    metrics = benchmark["categories"]["cjk"]
    byte_range = _range_per_key(metrics["bytes_per_query"])
    pointer_range = _range_per_key(metrics["pointers_per_query"])
    locator = {bound: round(key_count * value) for bound, value in byte_range.items()}
    pointers = {
        bound: round(key_count * value) for bound, value in pointer_range.items()
    }
    return {
        "key_count": key_count,
        "per_key": {
            "locator_bytes": byte_range,
            "pointer_occurrences": pointer_range,
        },
        "estimated_locator_bytes": {
            bound: _format_bytes(value) for bound, value in locator.items()
        },
        "estimated_pointer_occurrences": pointers,
    }


def analyze_cjk_fts_vocabulary(db_path: Path, benchmark_dir: Path) -> dict:
    """Measure the current FTS5 trigram vocabulary using only a TEMP table."""
    benchmark = _benchmark_metrics(benchmark_dir.resolve())
    # `immutable=1` rejects TEMP virtual-table creation. `mode=ro` still
    # prevents persistent writes to the corpus DB while allowing TEMP fts5vocab.
    con = sqlite3.connect(
        f"file:{db_path.resolve()}?mode=ro",
        uri=True,
        timeout=60,
    )
    con.row_factory = sqlite3.Row
    temp_table = "cjk_vocab_measurement"
    try:
        # Three fts5vocab arguments identify an FTS5 table in the main schema.
        # The virtual table itself is TEMP and vanishes when this connection closes.
        con.execute(
            f"CREATE VIRTUAL TABLE temp.{temp_table} "
            "USING fts5vocab(main, records_cjk_fts, 'row')"
        )
        total = con.execute(
            f"""SELECT count(*) AS token_count,
                       min(length(term)) AS minimum_token_length,
                       max(length(term)) AS maximum_token_length
                FROM temp.{temp_table}"""
        ).fetchone()
        total_rows = int(total["token_count"])
        aggregate = con.execute(
            f"""SELECT count(*) AS token_count,
                       min(length(term)) AS minimum_token_length,
                       max(length(term)) AS maximum_token_length,
                       sum(doc) AS total_document_frequency,
                       avg(doc) AS average_document_frequency,
                       max(doc) AS maximum_document_frequency,
                       sum(cnt) AS total_occurrence_frequency
                FROM temp.{temp_table}
                WHERE {_CJK_WHERE}""",
            _CJK_GLOB_PATTERNS,
        ).fetchone()
        cjk_rows = int(aggregate["token_count"])
        lengths = {"1_char": 0, "2_char": 0, "3_char": 0, "4_plus_char": 0}
        # The full FTS vocabulary is all length-3 tokens. Therefore its CJK
        # subset has the same exact length distribution; avoid a second full
        # filtered fts5vocab scan solely to rediscover that fact.
        if (
            total["minimum_token_length"] == 3
            and total["maximum_token_length"] == 3
        ):
            lengths["3_char"] = cjk_rows
        else:
            length_rows = con.execute(
                f"""SELECT length(term) AS token_length, count(*) AS token_count
                    FROM temp.{temp_table}
                    WHERE {_CJK_WHERE}
                    GROUP BY length(term)
                    ORDER BY token_length""",
                _CJK_GLOB_PATTERNS,
            ).fetchall()
            for row in length_rows:
                token_length = int(row["token_length"])
                bucket = (
                    "1_char"
                    if token_length == 1
                    else "2_char"
                    if token_length == 2
                    else "3_char"
                    if token_length == 3
                    else "4_plus_char"
                )
                lengths[bucket] += int(row["token_count"])
        histogram = con.execute(
            f"""SELECT doc AS document_frequency, count(*) AS token_count
                FROM temp.{temp_table}
                WHERE {_CJK_WHERE}
                GROUP BY doc
                ORDER BY doc""",
            _CJK_GLOB_PATTERNS,
        ).fetchall()
        median_document_frequency, p95_document_frequency = _frequency_percentiles(
            histogram,
            cjk_rows,
        )
        top_tokens = [
            {
                "term": row["term"],
                "document_frequency": int(row["doc"]),
                "occurrence_frequency": int(row["cnt"]),
            }
            for row in con.execute(
                f"""SELECT term, doc, cnt FROM temp.{temp_table}
                    WHERE {_CJK_WHERE}
                    ORDER BY doc DESC, term ASC
                    LIMIT ?""",
                (*_CJK_GLOB_PATTERNS, _TOP_SIZE),
            )
        ]
        # Lexical order is deterministic and avoids moving the full vocabulary
        # across the Python boundary solely to calculate stable hashes.
        sample_tokens = [
            {
                "term": row["term"],
                "document_frequency": int(row["doc"]),
                "occurrence_frequency": int(row["cnt"]),
            }
            for row in con.execute(
                f"""SELECT term, doc, cnt FROM temp.{temp_table}
                    WHERE {_CJK_WHERE}
                    ORDER BY term
                    LIMIT ?""",
                (*_CJK_GLOB_PATTERNS, _SAMPLE_SIZE),
            )
        ]
    finally:
        con.close()

    if not cjk_rows:
        raise ValueError("records_cjk_fts contains no CJK vocabulary terms")
    cjk_estimate = _cjk_estimate(cjk_rows, benchmark)
    seconds_per_key = (
        benchmark["source"]["generation_seconds_for_500_queries"]
        / benchmark["source"]["query_count"]
    )
    return {
        "analysis_version": CJK_VOCAB_ANALYSIS_VERSION,
        "artifact_kind": "cjk_fts_vocabulary_analysis",
        "read_only": True,
        "fts5vocab_access": {
            "temporary_virtual_table": (
                "CREATE VIRTUAL TABLE temp.cjk_vocab_measurement "
                "USING fts5vocab(main, records_cjk_fts, 'row')"
            ),
            "persistent_database_changes": False,
            "source_fts_table": "main.records_cjk_fts",
            "mode": "row",
        },
        "vocabulary": {
            "total_vocabulary_rows": total_rows,
            "distinct_cjk_tokens": cjk_rows,
            "token_length_distribution": lengths,
            "minimum_token_length": aggregate["minimum_token_length"],
            "maximum_token_length": aggregate["maximum_token_length"],
            "trigram_check": {
                "all_cjk_tokens_are_three_characters": (
                    lengths["1_char"] == 0
                    and lengths["2_char"] == 0
                    and lengths["4_plus_char"] == 0
                ),
                "note": (
                    "Length is Unicode code-point length of the FTS token. "
                    "A CJK-containing trigram can include non-CJK characters."
                ),
            },
        },
        "frequency": {
            "document_frequency": {
                "average": aggregate["average_document_frequency"],
                "median": median_document_frequency,
                "p95": p95_document_frequency,
                "max": aggregate["maximum_document_frequency"],
            },
            "occurrence_frequency_total": aggregate["total_occurrence_frequency"],
            "top_20_by_document_frequency": top_tokens,
        },
        "deterministic_sample_tokens": sample_tokens,
        "estimates": {
            "cjk": cjk_estimate,
            "rough_generation_seconds_per_key": seconds_per_key,
        },
    }
