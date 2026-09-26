"""Resumable production-v1 export for the verified pointer locator pipeline."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .index import connect_readonly
from .model import normalize
from .pointer_benchmark import _distribution, _tree_size, _write_json
from .pointer_export import (
    POINTER_CANDIDATE_MULTIPLIER,
    POINTER_EXPORT_VERSION,
    POINTER_FIELDS,
    POINTER_MARKER,
    _bucket,
    _json_bytes,
    _load_sources,
    _pointers,
    _replace_pointer_export,
    _select_corpus_candidates,
    _term_rows,
    _identifier_rows,
)
from .pointer_universe import _is_cjk_character


PRODUCTION_VERSION = 1
EXPECTED_LATIN_KEY_COUNT = 26_547
EXPECTED_IDENTIFIER_KEY_COUNT = 32_498
PRODUCTION_STAGE_SUFFIX = ".production-v1.staging"
PRODUCTION_STAGE_MARKER = ".buddhist-corpus-pointer-production-v1-stage"
PRODUCTION_STATE = "production-state.json"
PRODUCTION_KEYS = "production-keys.json"
PRODUCTION_BLOB_CACHE = "source-blob-sha-cache.json"
CHECKPOINT_EVERY = 25
MAX_LOCATOR_SHARD_BYTES = 8 * 1024 * 1024
_WORKER_CONNECTION = None


def _source_contract(db_path: Path, sources: dict[str, dict[str, str]]) -> list[dict]:
    con = connect_readonly(db_path)
    try:
        state_rows = [
            dict(row)
            for row in con.execute("SELECT * FROM source_state ORDER BY corpus")
        ]
    finally:
        con.close()
    contract = []
    for state in state_rows:
        source = sources.get(state["corpus"])
        if source is None:
            raise ValueError(f"missing GitHub source mapping for {state['corpus']}")
        contract.append(
            {
                "corpus": state["corpus"],
                "repository": source["repository"],
                "repo_path": source["repo_path"],
                "source_sha": state["source_sha"],
                "evidence_class": state["evidence_class"],
            }
        )
    return contract


def production_key_universe(
    db_path: Path,
    *,
    expected_latin_count: int = EXPECTED_LATIN_KEY_COUNT,
    expected_identifier_count: int = EXPECTED_IDENTIFIER_KEY_COUNT,
) -> list[dict]:
    """Enumerate the fixed production namespaces without sampling or CJK keys."""
    con = connect_readonly(db_path)
    try:
        latin: set[str] = set()
        for row in con.execute("SELECT DISTINCT lemma FROM lemmas WHERE trim(lemma)<>''"):
            key = normalize(row["lemma"])
            if key and not any(_is_cjk_character(char) for char in key):
                latin.add(key)
        identifiers = [
            row["work_id"]
            for row in con.execute(
                """SELECT DISTINCT work_id FROM records
                   WHERE work_id IS NOT NULL AND trim(work_id)<>''
                   ORDER BY work_id"""
            )
        ]
    finally:
        con.close()

    if len(latin) != expected_latin_count:
        raise ValueError(
            "production Latin key count differs from the approved universe: "
            f"{len(latin)} != {expected_latin_count}"
        )
    if len(identifiers) != expected_identifier_count:
        raise ValueError(
            "production original identifier count differs from the approved "
            f"universe: {len(identifiers)} != {expected_identifier_count}"
        )
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("identifier enumeration contains duplicate original work_id")
    if expected_identifier_count >= 2 and {"Dhp", "dhp"} <= set(identifiers):
        # This is expected in the production corpus and documents why IDs retain
        # original spelling rather than normalized locator keys.
        pass
    return [
        *[
            {
                "namespace": "terms/latin",
                "key": key,
                "query": key,
                "query_kind": "term",
                "enumeration_source": "lemmas.lemma normalized non-CJK key",
            }
            for key in sorted(latin)
        ],
        *[
            {
                "namespace": "ids",
                "key": identifier,
                "query": identifier,
                "query_kind": "identifier",
                "enumeration_source": "records.work_id original spelling",
            }
            for identifier in identifiers
        ],
    ]


def _validate_production_keys(
    keys: list[dict],
    expected_latin_count: int,
    expected_identifier_count: int,
) -> None:
    """Validate a persisted approved universe before safely resuming it."""
    latin = [item for item in keys if item.get("namespace") == "terms/latin"]
    identifiers = [item for item in keys if item.get("namespace") == "ids"]
    if len(latin) != expected_latin_count:
        raise ValueError(
            "staged production Latin key count differs from the approved universe: "
            f"{len(latin)} != {expected_latin_count}"
        )
    if len(identifiers) != expected_identifier_count:
        raise ValueError(
            "staged production identifier count differs from the approved universe: "
            f"{len(identifiers)} != {expected_identifier_count}"
        )
    pairs = {(item.get("query_kind"), item.get("key")) for item in keys}
    if len(pairs) != len(keys):
        raise ValueError("staged production key universe contains duplicate keys")
    if not all(
        item.get("query") == item.get("key")
        and item.get("query_kind") in {"term", "identifier"}
        for item in keys
    ):
        raise ValueError("staged production key universe has an invalid key contract")
    identifier_keys = {item["key"] for item in identifiers}
    if expected_identifier_count >= 2 and {"Dhp", "dhp"} <= identifier_keys:
        return
    # Small fixtures may not have this real-corpus collision, but a production
    # stage must never lose either exact spelling.
    if expected_identifier_count == EXPECTED_IDENTIFIER_KEY_COUNT:
        raise ValueError("staged production universe lost Dhp/dhp original IDs")


def _load_staged_keys(
    stage: Path,
    expected_latin_count: int,
    expected_identifier_count: int,
) -> list[dict]:
    keys = json.loads((stage / PRODUCTION_KEYS).read_text(encoding="utf-8"))
    if not isinstance(keys, list):
        raise ValueError("staged production key universe is not a list")
    _validate_production_keys(keys, expected_latin_count, expected_identifier_count)
    return keys


def _stage_path(output: Path) -> Path:
    return output.parent / f".{output.name}{PRODUCTION_STAGE_SUFFIX}"


def _state_path(stage: Path) -> Path:
    return stage / PRODUCTION_STATE


def _iter_locator_rows(root: Path) -> Iterable[dict]:
    """Stream durable locator rows so production resume does not page to C:."""
    for path in sorted((root / "locator").rglob("*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line:
                    yield json.loads(line)


def _existing_locator_keys(stage: Path) -> set[tuple[str, str]]:
    keys = set()
    for row in _iter_locator_rows(stage):
        keys.add((row["query_kind"], row["key"]))
    return keys


def _write_state(stage: Path, state: dict) -> None:
    _write_json(_state_path(stage), state)


def _blob_cache_path(stage: Path) -> Path:
    return stage / PRODUCTION_BLOB_CACHE


def _load_blob_cache(stage: Path) -> dict[tuple[str, str, str], str | None]:
    path = _blob_cache_path(stage)
    if not path.exists():
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {
        (row["repo_path"], row["source_sha"], row["source_path"]): row["blob_sha"]
        for row in rows
    }


def _hydrate_blob_cache_from_locator_rows(
    stage: Path,
    cache: dict[tuple[str, str, str], str | None],
    sources: dict[str, dict[str, str]],
) -> None:
    """Reuse blob IDs already durable in a resumed staging locator."""
    for row in _iter_locator_rows(stage):
        for pointer in row["pointers"]:
            source = sources.get(pointer["corpus"])
            if source is None:
                raise ValueError(
                    f"missing GitHub source mapping for {pointer['corpus']}"
                )
            cache.setdefault(
                (
                    source["repo_path"],
                    pointer["source_sha"],
                    pointer["source_path"],
                ),
                pointer["source_blob_sha"],
            )


def _write_blob_cache(
    stage: Path,
    cache: dict[tuple[str, str, str], str | None],
) -> None:
    _write_json(
        _blob_cache_path(stage),
        [
            {
                "repo_path": repo_path,
                "source_sha": source_sha,
                "source_path": source_path,
                "blob_sha": blob_sha,
            }
            for (repo_path, source_sha, source_path), blob_sha in sorted(cache.items())
        ],
    )


def _new_stage(stage: Path, keys: list[dict]) -> dict:
    if stage.exists():
        if not (stage / PRODUCTION_STAGE_MARKER).is_file():
            raise ValueError(f"refusing to replace unmarked production stage: {stage}")
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    _write_json(stage / PRODUCTION_KEYS, keys)
    _write_blob_cache(stage, {})
    (stage / PRODUCTION_STAGE_MARKER).write_text(
        f"production_version={PRODUCTION_VERSION}\n",
        encoding="utf-8",
    )
    state = {
        "production_version": PRODUCTION_VERSION,
        "complete": False,
        "started_at_unix": time.time(),
        "elapsed_seconds": 0.0,
        "expected_key_count": len(keys),
        "completed_key_count": 0,
    }
    _write_state(stage, state)
    return state


def _resume_stage(stage: Path, keys: list[dict]) -> dict:
    if not (stage / PRODUCTION_STAGE_MARKER).is_file():
        raise ValueError(f"unmarked production stage: {stage}")
    stored = json.loads((stage / PRODUCTION_KEYS).read_text(encoding="utf-8"))
    if stored != keys:
        raise ValueError("production key universe differs from incomplete stage")
    state = json.loads(_state_path(stage).read_text(encoding="utf-8"))
    # A process can be interrupted after all rows and state are durable but
    # before atomic replacement. Re-finalizing this marked staging directory is
    # safe and avoids discarding a completed multi-hour run.
    return state


def _shard_state(stage: Path) -> dict[tuple[str, str], tuple[Path, int]]:
    state = {}
    locator = stage / "locator"
    if not locator.exists():
        return state
    for path in sorted(locator.rglob("part-*.jsonl")):
        relative = path.relative_to(locator)
        namespace = "/".join(relative.parts[:-2])
        bucket = relative.parts[-2]
        state[(namespace, bucket)] = (path, path.stat().st_size)
    return state


def _write_locator_entry(
    stage: Path,
    entry: dict,
    shards: dict[tuple[str, str], tuple[Path, int]],
) -> None:
    bucket = _bucket(entry["key"])
    shard_key = (entry["namespace"], bucket)
    payload = _json_bytes(
        {
            "key": entry["key"],
            "query_kind": entry["query_kind"],
            "pointer_count": len(entry["pointers"]),
            "pointers": entry["pointers"],
        }
    )
    path, size = shards.get(
        shard_key,
        (
            stage
            / "locator"
            / entry["namespace"]
            / bucket
            / "part-000001.jsonl",
            0,
        ),
    )
    if size and size + len(payload) > MAX_LOCATOR_SHARD_BYTES:
        number = int(path.stem.removeprefix("part-")) + 1
        path = path.with_name(f"part-{number:06d}.jsonl")
        size = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    # Closing per row means an interrupted process leaves every prior row
    # complete. Resume derives completed keys from these durable JSONL rows.
    with path.open("ab") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    shards[shard_key] = (path, size + len(payload))


def _query_worker_init(db_path_text: str) -> None:
    """Open one immutable read-only SQLite connection per production worker."""
    global _WORKER_CONNECTION
    _WORKER_CONNECTION = connect_readonly(Path(db_path_text))


def _query_rows(
    job: tuple[Path, dict[str, dict[str, str]], int, str, str],
) -> list[dict]:
    """Run one existing query pipeline in an isolated worker process."""
    db_path, source_map, limit, query_kind, query = job
    if query_kind == "term":
        return _term_rows(
            db_path,
            query,
            source_map,
            limit,
            connection=_WORKER_CONNECTION,
        )
    return _select_corpus_candidates(
        _identifier_rows(db_path, query, connection=_WORKER_CONNECTION),
        limit,
    )


def _query_rows_in_order(
    db_path: Path,
    source_map: dict[str, dict[str, str]],
    limit: int,
    entries: list[dict],
    workers: int,
) -> Iterable[tuple[dict, list[dict]]]:
    """Yield independently retrieved rows in deterministic production-key order."""
    if workers == 1:
        for entry in entries:
            # Keep the default path patchable in unit tests. Production uses
            # workers>1 to retain a readonly connection per child process.
            yield entry, _query_rows(
                (db_path, source_map, limit, entry["query_kind"], entry["query"])
            )
        return
    # Keep at most one future per worker. executor.map() eagerly queues every
    # pending key; for production that can retain tens of thousands of bulky
    # out-of-order query results and force the Windows pagefile on C: to fill.
    # This bounded ordered window retains parallel readonly retrieval while the
    # sole writer emits the identical fixed-key order.
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_query_worker_init,
        initargs=(str(db_path),),
    ) as executor:
        entry_iter = iter(entries)
        in_flight = []
        for _ in range(workers):
            try:
                entry = next(entry_iter)
            except StopIteration:
                break
            job = (db_path, source_map, limit, entry["query_kind"], entry["query"])
            in_flight.append((entry, executor.submit(_query_rows, job)))
        while in_flight:
            entry, future = in_flight.pop(0)
            yield entry, future.result()
            try:
                next_entry = next(entry_iter)
            except StopIteration:
                continue
            job = (
                db_path,
                source_map,
                limit,
                next_entry["query_kind"],
                next_entry["query"],
            )
            in_flight.append((next_entry, executor.submit(_query_rows, job)))


def _locator_files(stage: Path) -> list[dict]:
    files = []
    for path in sorted((stage / "locator").rglob("*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            line_count = sum(1 for _ in handle)
        files.append(
            {
                "path": path.relative_to(stage).as_posix(),
                "byte_size": path.stat().st_size,
                "line_count": line_count,
            }
        )
    return files


def _new_query_stats() -> dict:
    return {
        "query_count": 0,
        "pointer_count": 0,
        "query_bytes": [],
        "pointers_per_query": [],
        "corpora_per_query": [],
        "queries_without_results": 0,
        "source_blob_sha_null_count": 0,
        "raw_text_field_count": 0,
        "duplicate_query_corpus_work_source_count": 0,
    }


def _update_query_stats(stats: dict, row: dict) -> None:
    pointers = row["pointers"]
    stats["query_count"] += 1
    stats["pointer_count"] += len(pointers)
    stats["query_bytes"].append(len(_json_bytes(row)))
    stats["pointers_per_query"].append(len(pointers))
    stats["corpora_per_query"].append(len({pointer["corpus"] for pointer in pointers}))
    stats["queries_without_results"] += int(not pointers)
    stats["source_blob_sha_null_count"] += sum(
        pointer["source_blob_sha"] is None for pointer in pointers
    )
    stats["raw_text_field_count"] += sum("raw_text" in pointer for pointer in pointers)
    duplicate_keys = [
        (row["key"], pointer["corpus"], pointer["work_id"], pointer["source_path"])
        for pointer in pointers
    ]
    stats["duplicate_query_corpus_work_source_count"] += (
        len(duplicate_keys) - len(set(duplicate_keys))
    )


def _finalize_query_stats(stats: dict, distinct_work_file_count: int) -> dict:
    return {
        "query_count": stats["query_count"],
        "pointer_count": stats["pointer_count"],
        "distinct_work_file_count": distinct_work_file_count,
        "corpora_per_query": _distribution(stats["corpora_per_query"]),
        "bytes_per_query": _distribution(stats["query_bytes"]),
        "pointers_per_query": _distribution(stats["pointers_per_query"]),
        "queries_without_results": stats["queries_without_results"],
        "source_blob_sha_null_count": stats["source_blob_sha_null_count"],
        "duplicate_query_corpus_work_source_count": (
            stats["duplicate_query_corpus_work_source_count"]
        ),
        "raw_text_field_count": stats["raw_text_field_count"],
    }


def _stream_production_stats(stage: Path) -> tuple[dict, dict[str, dict]]:
    """Calculate exact summary fields without retaining locator rows in memory."""
    stats_path = stage / ".production-stats.sqlite3"
    stats_path.unlink(missing_ok=True)
    con = sqlite3.connect(stats_path)
    try:
        con.execute(
            """CREATE TABLE distinct_work_files(
               namespace TEXT NOT NULL,
               corpus TEXT NOT NULL,
               work_id_key TEXT NOT NULL,
               source_path TEXT NOT NULL,
               PRIMARY KEY(namespace, corpus, work_id_key, source_path)
            ) WITHOUT ROWID"""
        )
        overall = _new_query_stats()
        by_namespace = {
            "terms/latin": _new_query_stats(),
            "ids": _new_query_stats(),
        }
        for row in _iter_locator_rows(stage):
            namespace = "terms/latin" if row["query_kind"] == "term" else "ids"
            _update_query_stats(overall, row)
            _update_query_stats(by_namespace[namespace], row)
            con.executemany(
                """INSERT OR IGNORE INTO distinct_work_files(
                   namespace,corpus,work_id_key,source_path
                ) VALUES (?,?,?,?)""",
                [
                    (
                        namespace,
                        pointer["corpus"],
                        # JSON makes None and every exact string distinct in the
                        # temporary uniqueness key without changing locator data.
                        json.dumps(pointer["work_id"], ensure_ascii=False),
                        pointer["source_path"],
                    )
                    for pointer in row["pointers"]
                ],
            )
        con.commit()
        namespace_counts = {
            row[0]: row[1]
            for row in con.execute(
                """SELECT namespace,COUNT(*) FROM distinct_work_files
                   GROUP BY namespace"""
            )
        }
        overall_count = con.execute(
            """SELECT COUNT(*) FROM (
                 SELECT DISTINCT corpus,work_id_key,source_path
                 FROM distinct_work_files
               )"""
        ).fetchone()[0]
    finally:
        con.close()
        stats_path.unlink(missing_ok=True)
    return (
        _finalize_query_stats(overall, overall_count),
        {
            namespace: _finalize_query_stats(
                stats, namespace_counts.get(namespace, 0)
            )
            for namespace, stats in by_namespace.items()
        },
    )


def _production_summary(
    overall: dict,
    by_namespace: dict[str, dict],
    manifest: dict,
    stage: Path,
    elapsed_seconds: float,
) -> dict:
    return {
        "production_version": PRODUCTION_VERSION,
        "artifact_kind": "pointer_production_v1",
        "key_counts": {
            "terms_latin_key_count": by_namespace["terms/latin"]["query_count"],
            "identifier_key_count": by_namespace["ids"]["query_count"],
            "total_key_count": overall["query_count"],
        },
        "query_with_results": (
            overall["query_count"] - overall["queries_without_results"]
        ),
        "query_without_results": overall["queries_without_results"],
        "total_pointer_count": overall["pointer_count"],
        "pointers_per_query": overall["pointers_per_query"],
        "source_blob_sha_null_count": overall["source_blob_sha_null_count"],
        "raw_text_field_count": overall["raw_text_field_count"],
        "duplicate_query_corpus_work_source_count": (
            overall["duplicate_query_corpus_work_source_count"]
        ),
        "by_namespace": {
            "terms_latin": by_namespace["terms/latin"],
            "ids": by_namespace["ids"],
        },
        "artifact": {
            "file_count": sum(path.is_file() for path in stage.rglob("*")),
            "total_bytes": _tree_size(stage),
            "locator_bytes": sum(
                item["byte_size"] for item in manifest["locator"]["files"]
            ),
        },
        "generation_elapsed_seconds": elapsed_seconds,
    }


def _finalize_stage(
    stage: Path,
    db_path: Path,
    sources_config: Path,
    source_map: dict[str, dict[str, str]],
    keys: list[dict],
    limit: int,
    elapsed_seconds: float,
) -> dict:
    expected_pairs = {(item["query_kind"], item["key"]) for item in keys}
    actual_pairs: set[tuple[str, str]] = set()
    row_count = 0
    for row in _iter_locator_rows(stage):
        pair = (row["query_kind"], row["key"])
        if pair in actual_pairs:
            raise ValueError("incomplete or duplicate production locator rows")
        actual_pairs.add(pair)
        row_count += 1
    if actual_pairs != expected_pairs or row_count != len(keys):
        raise ValueError("incomplete or duplicate production locator rows")
    files = _locator_files(stage)
    contract = _source_contract(db_path, source_map)
    manifest = {
        "pointer_export_version": POINTER_EXPORT_VERSION,
        "production_version": PRODUCTION_VERSION,
        "artifact_kind": "pointer_production_v1",
        "format": "pointer-locator-jsonl",
        "proof_of_concept": False,
        "raw_text_exported": False,
        "runtime": "GitHub Connector -> pinned source repository file",
        "ranking": {
            "implementation": "corpus_research.retrieval.score_record_match",
            "term_queries": "existing local search() ranking",
            "identifier_queries": (
                "exact original work_id candidates scored by score_record_match"
            ),
            "tie_break": "corpus, source_path, sequence_no",
        },
        "selection": {
            "strategy": "per_corpus_best_distinct_work_source",
            "per_corpus_limit": limit,
            "candidate_fetch_limit_per_corpus": (
                limit * POINTER_CANDIDATE_MULTIPLIER
            ),
            "deduplicate_by": ["corpus", "work_id", "source_path"],
            "final_order": "existing record_rank_key after selection",
        },
        "namespaces": {
            "materialized": ["terms/latin", "ids"],
            "terms_latin": {
                "enumeration": "lemmas.lemma normalized non-empty non-CJK keys",
                "key_count": sum(item["query_kind"] == "term" for item in keys),
            },
            "ids": {
                "enumeration": "records.work_id distinct original spelling",
                "key_count": sum(
                    item["query_kind"] == "identifier" for item in keys
                ),
                "original_spelling_preserved": True,
            },
            "terms_cjk": {
                "materialized": False,
                "limitation": (
                    "terms/cjk full trigram vocabulary is intentionally not "
                    "materialized in production v1"
                ),
                "reason": (
                    "CJK trigram FTS remains build/local retrieval "
                    "infrastructure. The 45.7M trigram vocabulary is not a "
                    "meaningful Buddhist-term vocabulary."
                ),
            },
        },
        "source_blob_sha": {
            "algorithm": "git rev-parse <source_sha>:<source_path>",
            "availability": "null when the local pinned Git object is unavailable",
        },
        "source_mapping_config": sources_config.name,
        "source_contract": contract,
        "pointer_fields": list(POINTER_FIELDS),
        "locator": {
            "hash": "SHA-256 of exact UTF-8 production key; first two lowercase hex characters",
            "file_pattern": "locator/<namespace>/<bucket>/part-000001.jsonl",
            "files": files,
        },
        "production_summary": "production-summary.json",
    }
    locator_manifest = {
        "pointer_export_version": POINTER_EXPORT_VERSION,
        "production_version": PRODUCTION_VERSION,
        "artifact_kind": "pointer_production_v1",
        "format": "pointer-locator-jsonl",
        "raw_text_exported": False,
        "hash": manifest["locator"]["hash"],
        "file_pattern": manifest["locator"]["file_pattern"],
        "pointer_fields": list(POINTER_FIELDS),
        "files": files,
    }
    _write_json(stage / "locator" / "manifest.json", locator_manifest)
    _write_json(stage / "manifest.json", manifest)
    (stage / "README.md").write_text(
        """# Production Pointer Locator v1

This is the raw-text-free production runtime locator for `terms/latin` and
`ids`. It uses the verified existing pointer ranking, corpus balancing, and
provenance fields; it is not a second search engine or scholarly authority.

1. Read `manifest.json` and `production-summary.json`.
2. Look up the exact production key under its SHA-256 bucket.
3. Follow ranked pointers to the pinned upstream source file and verify context,
   provenance, evidence class, text role, and witness before making a finding.

`terms/cjk` full trigram vocabulary is intentionally not materialized in v1.
The local CJK trigram FTS remains build/retrieval infrastructure, not a
Buddhist-term vocabulary. If these pointers cannot establish a claim, report:

`không đủ dữ liệu trong remote corpus export hiện tại`
""",
        encoding="utf-8",
    )
    (stage / POINTER_MARKER).write_text(
        f"pointer_export_version={POINTER_EXPORT_VERSION}\n"
        f"production_version={PRODUCTION_VERSION}\n",
        encoding="utf-8",
    )
    # Staging-only files cannot become part of the Connector runtime artifact.
    # The final marker above is distinct from the stage marker.
    for transient in (
        stage / PRODUCTION_STATE,
        stage / PRODUCTION_KEYS,
        stage / PRODUCTION_BLOB_CACHE,
        stage / PRODUCTION_STAGE_MARKER,
    ):
        transient.unlink(missing_ok=True)
    overall, by_namespace = _stream_production_stats(stage)
    summary = _production_summary(
        overall,
        by_namespace,
        manifest,
        stage,
        elapsed_seconds,
    )
    # Stabilize self-referential file-count/byte summary after every final file
    # except the summary itself is present.
    for _ in range(3):
        _write_json(stage / "production-summary.json", summary)
        summary["artifact"]["file_count"] = sum(
            path.is_file() for path in stage.rglob("*")
        )
        summary["artifact"]["total_bytes"] = _tree_size(stage)
    _write_json(stage / "production-summary.json", summary)
    return summary


def export_pointer_production_v1(
    db_path: Path,
    output_dir: Path,
    sources_config: Path,
    root: Path,
    *,
    limit: int = 20,
    workers: int = 1,
    expected_latin_count: int = EXPECTED_LATIN_KEY_COUNT,
    expected_identifier_count: int = EXPECTED_IDENTIFIER_KEY_COUNT,
) -> dict:
    """Generate or resume the approved two-namespace production locator."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    if workers <= 0:
        raise ValueError("workers must be positive")
    if not db_path.is_file():
        raise FileNotFoundError(f"index not found at {db_path}")
    source_map = _load_sources(sources_config)
    output = output_dir.resolve()
    stage = _stage_path(output)
    if stage.exists():
        # The stage key list was fully enumerated and validated before the first
        # row was written. Reusing it avoids a multi-minute DISTINCT work_id scan
        # on every resume while preserving the approved fixed universe.
        keys = _load_staged_keys(
            stage,
            expected_latin_count,
            expected_identifier_count,
        )
        state = _resume_stage(stage, keys)
    else:
        keys = production_key_universe(
            db_path,
            expected_latin_count=expected_latin_count,
            expected_identifier_count=expected_identifier_count,
        )
        state = _new_stage(stage, keys)
    run_started = time.monotonic()
    completed = _existing_locator_keys(stage)
    shards = _shard_state(stage)
    blob_cache = _load_blob_cache(stage)
    _hydrate_blob_cache_from_locator_rows(stage, blob_cache, source_map)
    pending = [
        key for key in keys if (key["query_kind"], key["key"]) not in completed
    ]
    for index, (key, rows) in enumerate(
        _query_rows_in_order(db_path, source_map, limit, pending, workers),
        start=1,
    ):
        entry = {**key, "pointers": _pointers(rows, source_map, root, blob_cache)}
        _write_locator_entry(stage, entry, shards)
        completed.add((key["query_kind"], key["key"]))
        if index % CHECKPOINT_EVERY == 0:
            state["completed_key_count"] = len(completed)
            state["elapsed_seconds"] += time.monotonic() - run_started
            _write_state(stage, state)
            _write_blob_cache(stage, blob_cache)
            run_started = time.monotonic()

    state["completed_key_count"] = len(completed)
    state["elapsed_seconds"] += time.monotonic() - run_started
    state["complete"] = True
    _write_state(stage, state)
    _write_blob_cache(stage, blob_cache)
    summary = _finalize_stage(
        stage,
        db_path,
        sources_config,
        source_map,
        keys,
        limit,
        state["elapsed_seconds"],
    )
    _replace_pointer_export(stage, output)
    return {
        "output": str(output),
        "terms_latin_key_count": expected_latin_count,
        "identifier_key_count": expected_identifier_count,
        "total_key_count": len(keys),
        "total_pointer_count": summary["total_pointer_count"],
        "total_bytes": summary["artifact"]["total_bytes"],
        "workers": workers,
        "summary": str(output / "production-summary.json"),
        "raw_text_exported": False,
    }
