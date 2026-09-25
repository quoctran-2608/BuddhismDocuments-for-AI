"""Deterministic, raw-text-free GitHub Connector pointer-export POC."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .index import connect_readonly
from .model import normalize
from .retrieval import record_rank_key, score_record_match, search


POINTER_EXPORT_VERSION = 1
POINTER_MARKER = ".buddhist-corpus-remote-pointer-export"
POINTER_FIELDS = (
    "rank",
    "score",
    "match_reasons",
    "record_id",
    "corpus",
    "repository",
    "source_sha",
    "source_path",
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


def _pointer(row: dict, source: dict[str, str], rank: int) -> dict:
    indexed_source_path = str(row["source_path"])
    pointer = {
        "rank": rank,
        "score": row["score"],
        "match_reasons": row["match_reasons"],
        "record_id": row["id"],
        "corpus": row["corpus"],
        "repository": source["repository"],
        "source_sha": row["source_sha"],
        "source_path": _github_source_path(
            indexed_source_path,
            source["repo_path"],
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


def _identifier_rows(db_path: Path, identifier: str, limit: int) -> list[dict]:
    con = connect_readonly(db_path)
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
    return ranked[:limit]


def _pointers(
    rows: Iterable[dict],
    sources: dict[str, dict[str, str]],
) -> list[dict]:
    pointers = []
    for rank, row in enumerate(rows, start=1):
        source = sources.get(row["corpus"])
        if source is None:
            raise ValueError(f"missing GitHub source mapping for {row['corpus']}")
        pointers.append(_pointer(row, source, rank))
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
                    search(db_path, query, limit=limit)["results"],
                    source_map,
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
                    _identifier_rows(db_path, identifier, limit),
                    source_map,
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
4. Use `work_id`, `segment_id`, and `sequence_no` to locate the passage in the
   original file. Verify wording, context, provenance, text role, and witness
   in that source before making a finding.

Pointer rank only decides which source file to open first. It is not evidence
and does not override user scope, evidence hierarchy, text role, witness
separation, or provenance. GitHub Code Search is not required.

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
