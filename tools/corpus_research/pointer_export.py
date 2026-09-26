"""Deterministic, raw-text-free GitHub Connector pointer-export POC."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .index import connect_readonly
from .model import normalize
from .retrieval import record_rank_key, score_record_match, search


POINTER_EXPORT_VERSION = 2
POINTER_MARKER = ".buddhist-corpus-remote-pointer-export"
POINTER_CANDIDATE_MULTIPLIER = 5
POINTER_FIELDS = (
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
)


def _json_bytes(value: dict) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _bucket(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:2]


def _is_cjk(key: str) -> bool:
    return any(
        0x3400 <= ord(char) <= 0x4DBF
        or 0x4E00 <= ord(char) <= 0x9FFF
        or 0xF900 <= ord(char) <= 0xFAFF
        or 0x20000 <= ord(char) <= 0x2FA1F
        for char in key
    )


def _load_sources(config_path: Path) -> dict[str, dict[str, str]]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    sources: dict[str, dict[str, str]] = {}
    for source in config.get("sources", []):
        corpus = source.get("corpus")
        repository = source.get("github_repository")
        repo_path = source.get("repo")
        if not all(
            isinstance(value, str) and value
            for value in (corpus, repository, repo_path)
        ):
            raise ValueError(
                "each config source must include corpus, repo, and github_repository"
            )
        if corpus in sources:
            raise ValueError(f"duplicate corpus source mapping: {corpus}")
        sources[corpus] = {
            "repository": repository,
            "repo_path": repo_path.rstrip("/"),
        }
    return sources


def _github_source_path(indexed_path: str, repo_path: str) -> str:
    prefix = f"{repo_path}/"
    if not indexed_path.startswith(prefix):
        raise ValueError(
            f"indexed source path is outside mapped repository: {indexed_path}"
        )
    source_path = indexed_path.removeprefix(prefix)
    if not source_path:
        raise ValueError(f"empty source path after repository prefix: {indexed_path}")
    return source_path


def _source_blob_sha(
    root: Path | None,
    source: dict[str, str],
    source_sha: str,
    source_path: str,
    cache: dict[tuple[str, str, str], str | None],
) -> str | None:
    """Return the pinned Git blob ID when the local source object is available."""
    key = (source["repo_path"], source_sha, source_path)
    if key in cache:
        return cache[key]
    if root is None:
        cache[key] = None
        return None
    repo = root / source["repo_path"]
    if not (repo / ".git").exists():
        cache[key] = None
        return None
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{source_sha}:{source_path}"],
        text=True,
        capture_output=True,
        check=False,
    )
    blob_sha = result.stdout.strip()
    cache[key] = blob_sha if result.returncode == 0 and blob_sha else None
    return cache[key]


def _populate_source_blob_cache(
    rows: Iterable[dict],
    sources: dict[str, dict[str, str]],
    root: Path | None,
    cache: dict[tuple[str, str, str], str | None],
) -> None:
    """Resolve uncached source blobs in Git batches without changing pointers."""
    if root is None:
        return
    grouped: dict[tuple[str, str], list[tuple[tuple[str, str, str], str]]] = (
        defaultdict(list)
    )
    for row in rows:
        source = sources.get(row["corpus"])
        if source is None:
            raise ValueError(f"missing GitHub source mapping for {row['corpus']}")
        source_path = _github_source_path(str(row["source_path"]), source["repo_path"])
        source_sha = str(row["source_sha"])
        key = (source["repo_path"], source_sha, source_path)
        if key not in cache:
            grouped[(source["repo_path"], source_sha)].append((key, source_path))
    for (repo_path, source_sha), unresolved in grouped.items():
        repo = root / repo_path
        if not (repo / ".git").exists():
            for key, _ in unresolved:
                cache[key] = None
            continue
        # cat-file resolves all <commit>:<path> expressions in one Git process.
        # It returns only object names, so a failed path is unambiguously null.
        expressions = "".join(f"{source_sha}:{path}\n" for _, path in unresolved)
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "cat-file",
                "--batch-check=%(objectname)",
            ],
            input=expressions,
            text=True,
            capture_output=True,
            check=False,
        )
        lines = result.stdout.splitlines()
        for (key, _), value in zip(unresolved, lines, strict=False):
            cache[key] = (
                value
                if result.returncode == 0
                and len(value) == 40
                and all(char in "0123456789abcdef" for char in value)
                else None
            )
        # A truncated/failed batch must never leave a missing cache entry.
        for key, _ in unresolved[len(lines) :]:
            cache[key] = None


def _pointer(
    row: dict,
    source: dict[str, str],
    rank: int,
    root: Path | None,
    blob_cache: dict[tuple[str, str, str], str | None],
) -> dict:
    indexed_source_path = str(row["source_path"])
    source_path = _github_source_path(indexed_source_path, source["repo_path"])
    pointer = {
        "rank": rank,
        "score": row["score"],
        "match_reasons": row["match_reasons"],
        "record_id": row["id"],
        "corpus": row["corpus"],
        "repository": source["repository"],
        "source_sha": row["source_sha"],
        "source_path": source_path,
        "source_blob_sha": _source_blob_sha(
            root,
            source,
            str(row["source_sha"]),
            source_path,
            blob_cache,
        ),
        "indexed_source_path": indexed_source_path,
        "work_id": row["work_id"],
        "segment_id": row["segment_id"],
        "sequence_no": row["sequence_no"],
        "evidence_class": row["evidence_class"],
        "text_role": row["text_role"],
        "witness": row["witness"],
    }
    assert tuple(pointer) == POINTER_FIELDS
    return pointer


def _identifier_rows(
    db_path: Path,
    identifier: str,
    connection: sqlite3.Connection | None = None,
) -> list[dict]:
    con = connection or connect_readonly(db_path)
    try:
        rows = [
            dict(row)
            for row in con.execute(
                """SELECT * FROM records
                   WHERE work_id=? OR segment_id=?
                   ORDER BY corpus,source_path,sequence_no,id""",
                (identifier, identifier),
            )
        ]
    finally:
        if connection is not None:
            pass
        else:
            con.close()
    ranked = []
    for row in rows:
        score, reasons = score_record_match(
            row,
            identifier,
            match_kind="exact",
            corpus_lemma=False,
        )
        row["score"] = score
        row["match_reasons"] = reasons
        ranked.append(row)
    ranked.sort(key=record_rank_key)
    return ranked


def _select_corpus_candidates(
    rows: Iterable[dict],
    per_corpus_limit: int,
) -> list[dict]:
    """Keep ranked distinct work/source candidates within each corpus."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row["corpus"])].append(row)

    selected: list[dict] = []
    for corpus in sorted(grouped):
        distinct: dict[tuple[object, object], dict] = {}
        for row in sorted(grouped[corpus], key=record_rank_key):
            # Rows from one source file and work differ only in local segment
            # position for this POC. Keep its best existing-ranked candidate.
            key = (row.get("work_id"), row.get("source_path"))
            distinct.setdefault(key, row)
        selected.extend(list(distinct.values())[:per_corpus_limit])
    selected.sort(key=record_rank_key)
    return selected


def _term_rows(
    db_path: Path,
    query: str,
    sources: dict[str, dict[str, str]],
    per_corpus_limit: int,
    connection: sqlite3.Connection | None = None,
) -> list[dict]:
    candidate_limit = per_corpus_limit * POINTER_CANDIDATE_MULTIPLIER
    rows = []
    for corpus in sorted(sources):
        kwargs = {"connection": connection} if connection is not None else {}
        rows.extend(
            search(db_path, query, limit=candidate_limit, corpus=corpus, **kwargs)[
                "results"
            ]
        )
    return _select_corpus_candidates(rows, per_corpus_limit)


def _pointers(
    rows: Iterable[dict],
    sources: dict[str, dict[str, str]],
    root: Path | None,
    blob_cache: dict[tuple[str, str, str], str | None],
) -> list[dict]:
    ordered_rows = list(rows)
    _populate_source_blob_cache(ordered_rows, sources, root, blob_cache)
    pointers = []
    for rank, row in enumerate(ordered_rows, start=1):
        source = sources.get(row["corpus"])
        if source is None:
            raise ValueError(f"missing GitHub source mapping for {row['corpus']}")
        pointers.append(_pointer(row, source, rank, root, blob_cache))
    return pointers


def _replace_pointer_export(stage: Path, output: Path) -> None:
    if output.is_symlink() or output.is_file():
        raise ValueError(f"refusing to replace non-directory output: {output}")
    if output.exists() and not (output / POINTER_MARKER).is_file():
        raise ValueError(
            f"refusing to replace directory without {POINTER_MARKER}: {output}"
        )
    backup = output.parent / f".{output.name}.previous"
    if backup.is_symlink() or backup.is_file():
        backup.unlink()
    elif backup.exists():
        shutil.rmtree(backup)
    if output.exists():
        os.replace(output, backup)
    try:
        os.replace(stage, output)
    except Exception:
        if backup.exists() and not output.exists():
            os.replace(backup, output)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def export_pointer_poc(
    db_path: Path,
    output_dir: Path,
    sources_config: Path,
    queries: Iterable[str],
    identifiers: Iterable[str],
    limit: int = 20,
    root: Path | None = None,
) -> dict:
    """Write a small pointer-only Connector artifact without exporting raw text."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    if not db_path.is_file():
        raise FileNotFoundError(f"index not found at {db_path}")

    source_map = _load_sources(sources_config)
    output = output_dir.resolve()
    stage = output.parent / f".{output.name}.exporting"
    if stage.is_symlink() or stage.is_file():
        stage.unlink()
    elif stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    entries: list[dict] = []
    seen: set[tuple[str, str]] = set()
    blob_cache: dict[tuple[str, str, str], str | None] = {}
    for query in queries:
        key = normalize(query)
        if not key or ("term", key) in seen:
            continue
        seen.add(("term", key))
        namespace = "terms/cjk" if _is_cjk(key) else "terms/latin"
        entries.append(
            {
                "namespace": namespace,
                "key": key,
                "query": query,
                "query_kind": "term",
                "pointers": _pointers(
                    _term_rows(db_path, query, source_map, limit),
                    source_map,
                    root,
                    blob_cache,
                ),
            }
        )
    for identifier in identifiers:
        key = normalize(identifier)
        if not key or ("identifier", key) in seen:
            continue
        seen.add(("identifier", key))
        entries.append(
            {
                "namespace": "ids",
                "key": key,
                "query": identifier,
                "query_kind": "identifier",
                "pointers": _pointers(
                    _select_corpus_candidates(
                        _identifier_rows(db_path, identifier),
                        limit,
                    ),
                    source_map,
                    root,
                    blob_cache,
                ),
            }
        )
    if not entries:
        raise ValueError("provide at least one non-empty query or identifier")

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for entry in entries:
        grouped[(entry["namespace"], _bucket(entry["key"]))].append(entry)
    files = []
    for (namespace, bucket), rows in sorted(grouped.items()):
        relative = Path("locator") / namespace / bucket / "part-000001.jsonl"
        path = stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            _json_bytes(
                {
                    "key": entry["key"],
                    "query_kind": entry["query_kind"],
                    "pointer_count": len(entry["pointers"]),
                    "pointers": entry["pointers"],
                }
            )
            for entry in sorted(rows, key=lambda item: item["key"])
        ]
        path.write_bytes(b"".join(lines))
        files.append(
            {
                "path": relative.as_posix(),
                "byte_size": path.stat().st_size,
                "line_count": len(lines),
            }
        )

    con = connect_readonly(db_path)
    try:
        state_rows = [
            dict(row)
            for row in con.execute("SELECT * FROM source_state ORDER BY corpus")
        ]
    finally:
        con.close()
    source_contract = []
    for state in state_rows:
        source = source_map.get(state["corpus"])
        if source is None:
            raise ValueError(f"missing GitHub source mapping for {state['corpus']}")
        source_contract.append(
            {
                "corpus": state["corpus"],
                "repository": source["repository"],
                "repo_path": source["repo_path"],
                "source_sha": state["source_sha"],
                "evidence_class": state["evidence_class"],
            }
        )
    manifest = {
        "pointer_export_version": POINTER_EXPORT_VERSION,
        "format": "pointer-locator-jsonl",
        "proof_of_concept": True,
        "raw_text_exported": False,
        "runtime": "GitHub Connector -> pinned source repository file",
        "ranking": {
            "implementation": "corpus_research.retrieval.score_record_match",
            "term_queries": "existing local search() ranking",
            "identifier_queries": (
                "exact identifier candidates scored by score_record_match"
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
        "source_blob_sha": {
            "algorithm": "git rev-parse <source_sha>:<source_path>",
            "availability": "null when the local pinned Git object is unavailable",
        },
        "source_mapping_config": sources_config.name,
        "source_contract": source_contract,
        "pointer_fields": list(POINTER_FIELDS),
        "locator": {
            "hash": (
                "SHA-256 of UTF-8 normalized key; first two lowercase hex "
                "characters"
            ),
            "file_pattern": "locator/<namespace>/<bucket>/part-000001.jsonl",
            "files": files,
        },
        "queries": [
            {
                "key": entry["key"],
                "query": entry["query"],
                "query_kind": entry["query_kind"],
                "namespace": entry["namespace"],
                "pointer_count": len(entry["pointers"]),
            }
            for entry in entries
        ],
    }
    locator_manifest = {
        "pointer_export_version": POINTER_EXPORT_VERSION,
        "format": "pointer-locator-jsonl",
        "raw_text_exported": False,
        "hash": manifest["locator"]["hash"],
        "file_pattern": manifest["locator"]["file_pattern"],
        "pointer_fields": list(POINTER_FIELDS),
        "files": files,
    }
    locator_root = stage / "locator"
    (locator_root / "manifest.json").write_text(
        json.dumps(locator_manifest, ensure_ascii=False, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    (stage / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    (stage / "README.md").write_text(
        """# GitHub Connector Pointer POC

This deterministic proof of concept contains ranked provenance pointers only.
It does not contain `raw_text`, copied record shards, a copied corpus, or a
second search engine.

1. Read `manifest.json`.
2. Normalize the POC key, calculate its locator bucket, and fetch that JSONL
   row.
3. Follow pointers in rank order: open `repository` at `source_sha`, then open
   `source_path` directly in GitHub.
4. When available, compare `source_blob_sha` with the Git blob ID reported for
   that pinned source file.
5. Use `work_id`, `segment_id`, and `sequence_no` to locate the passage in the
   original file. Verify wording, context, provenance, text role, and witness
   in that source before making a finding.

Pointers retain the existing shared ranking, but this POC first keeps the best
distinct `(work_id, source_path)` candidate within each corpus. It is not
evidence and does not override user scope, evidence hierarchy, text role,
witness separation, or provenance. GitHub Code Search is not required.

If the listed pointers cannot establish a claim, report:

`không đủ dữ liệu trong remote corpus export hiện tại`
""",
        encoding="utf-8",
    )
    (stage / POINTER_MARKER).write_text(
        f"pointer_export_version={POINTER_EXPORT_VERSION}\n",
        encoding="utf-8",
    )
    _replace_pointer_export(stage, output)
    return {
        "database": str(db_path),
        "output": str(output),
        "query_count": len(entries),
        "pointer_count": sum(len(entry["pointers"]) for entry in entries),
        "raw_text_exported": False,
        "manifest": str(output / "manifest.json"),
    }
