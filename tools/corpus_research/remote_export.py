from __future__ import annotations

import itertools
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from .index import SEARCH_INDEX_COMPONENT, connect_readonly


EXPORT_VERSION = 1
DEFAULT_SHARD_BYTES = 512 * 1024
REMOTE_FAILURE_MESSAGE = "không đủ dữ liệu trong remote corpus export hiện tại"
EXPORT_MARKER = ".buddhist-corpus-remote-export"
SHARD_FIELDS = (
    "kind",
    "corpus",
    "path",
    "byte_size",
    "line_count",
    "item_count",
    "overlap_count",
    "first_id",
    "last_id",
    "work_count",
    "first_work_id",
    "last_work_id",
    "oversized",
)

RECORD_FIELDS = (
    "id",
    "corpus",
    "language",
    "collection_name",
    "work_id",
    "segment_id",
    "title",
    "raw_text",
    "source_path",
    "source_sha",
    "evidence_class",
    "text_role",
    "witness",
    "sequence_no",
    "relation_ids",
)


def _json_bytes(value: dict) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _decoded(value: object, fallback: object) -> object:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return slug or "unknown"


@dataclass(slots=True)
class _PreparedRecord:
    item: dict
    primary: bytes
    overlap: bytes | None = None

    def overlap_bytes(self) -> bytes:
        if self.overlap is None:
            item = dict(self.item)
            item["export_role"] = "context_overlap"
            self.overlap = _json_bytes(item)
        return self.overlap

    def overlap_size(self) -> int:
        # Only the ASCII export-role value changes.
        return len(self.primary) + len("context_overlap") - len("primary")


@dataclass(slots=True)
class _ExportLine:
    data: bytes
    item_id: int
    work_id: str | None = None
    primary: bool = True


def _record_item(row: sqlite3.Row) -> dict:
    item = {key: row[key] for key in RECORD_FIELDS}
    item["relation_ids"] = _decoded(item["relation_ids"], [])
    return item


def _prepare_record(row: sqlite3.Row) -> _PreparedRecord:
    item = _record_item(row)
    primary = dict(item)
    primary["export_role"] = "primary"
    return _PreparedRecord(item, _json_bytes(primary))


def _fill_lookahead(
    rows: Iterator[sqlite3.Row],
    lookahead: deque[_PreparedRecord],
) -> None:
    while len(lookahead) < 3:
        try:
            lookahead.append(_prepare_record(next(rows)))
        except StopIteration:
            return


def _record_blocks(
    rows: Iterable[sqlite3.Row],
    target_bytes: int,
) -> Iterator[list[_ExportLine]]:
    iterator = iter(rows)
    lookahead: deque[_PreparedRecord] = deque()
    _fill_lookahead(iterator, lookahead)
    prefix: list[_PreparedRecord] = []
    primary: list[_PreparedRecord] = []
    block_bytes = 0

    while lookahead:
        current = lookahead[0]
        future = list(lookahead)[1:3]
        projected = block_bytes + len(current.primary) + sum(
            item.overlap_size() for item in future
        )
        if primary and projected > target_bytes:
            suffix = list(lookahead)[:2]
            yield [
                *(
                    _ExportLine(
                        item.overlap_bytes(),
                        item.item["id"],
                        item.item["work_id"],
                        primary=False,
                    )
                    for item in prefix
                ),
                *(
                    _ExportLine(
                        item.primary,
                        item.item["id"],
                        item.item["work_id"],
                    )
                    for item in primary
                ),
                *(
                    _ExportLine(
                        item.overlap_bytes(),
                        item.item["id"],
                        item.item["work_id"],
                        primary=False,
                    )
                    for item in suffix
                ),
            ]
            prefix = primary[-2:]
            primary = []
            block_bytes = sum(item.overlap_size() for item in prefix)
            continue

        primary.append(current)
        block_bytes += len(current.primary)
        lookahead.popleft()
        _fill_lookahead(iterator, lookahead)

    if primary:
        yield [
            *(
                _ExportLine(
                    item.overlap_bytes(),
                    item.item["id"],
                    item.item["work_id"],
                    primary=False,
                )
                for item in prefix
            ),
            *(
                _ExportLine(
                    item.primary,
                    item.item["id"],
                    item.item["work_id"],
                )
                for item in primary
            ),
        ]


class _ShardWriter:
    def __init__(self, root: Path, target_bytes: int):
        self.root = root
        self.target_bytes = target_bytes
        self.shards: list[dict] = []
        self._counters: dict[tuple[str, str], int] = {}
        self._kind: str | None = None
        self._corpus: str | None = None
        self._lines: list[_ExportLine] = []
        self._bytes = 0

    def add(self, kind: str, corpus: str, lines: list[_ExportLine]) -> None:
        block_bytes = sum(len(line.data) for line in lines)
        if (
            self._lines
            and (
                kind != self._kind
                or corpus != self._corpus
                or self._bytes + block_bytes > self.target_bytes
            )
        ):
            self.flush()
        if block_bytes > self.target_bytes and not self._lines:
            self._kind = kind
            self._corpus = corpus
            self._lines = lines
            self._bytes = block_bytes
            self.flush()
            return
        self._kind = kind
        self._corpus = corpus
        self._lines.extend(lines)
        self._bytes += block_bytes

    def flush(self) -> None:
        if not self._lines or self._kind is None or self._corpus is None:
            return
        key = (self._kind, self._corpus)
        number = self._counters.get(key, 0) + 1
        self._counters[key] = number
        relative_path = (
            Path(self._kind) / _slug(self._corpus) / f"part-{number:06d}.jsonl"
        )
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"".join(line.data for line in self._lines))
        primary = [line for line in self._lines if line.primary]
        work_ids = sorted(
            {line.work_id for line in primary if line.work_id is not None}
        )
        entry = {
            "kind": self._kind,
            "corpus": self._corpus,
            "path": relative_path.as_posix(),
            "byte_size": self._bytes,
            "line_count": len(self._lines),
            "item_count": len(primary),
            "overlap_count": len(self._lines) - len(primary),
            "first_id": min((line.item_id for line in primary), default=None),
            "last_id": max((line.item_id for line in primary), default=None),
            "work_count": len(work_ids),
            "first_work_id": work_ids[0] if work_ids else None,
            "last_work_id": work_ids[-1] if work_ids else None,
            "oversized": self._bytes > self.target_bytes,
        }
        self.shards.append(entry)
        self._kind = None
        self._corpus = None
        self._lines = []
        self._bytes = 0


def _table_counts(con: sqlite3.Connection, table: str) -> dict[str, int]:
    return {
        row["corpus"]: row["count"]
        for row in con.execute(
            f"""SELECT corpus,COUNT(*) AS count
                FROM {table} GROUP BY corpus ORDER BY corpus"""
        )
    }


def _source_contract(con: sqlite3.Connection) -> list[dict]:
    return [
        {
            key: row[key]
            for key in (
                "corpus",
                "repo_path",
                "source_sha",
                "parser_version",
                "evidence_class",
            )
        }
        for row in con.execute("SELECT * FROM source_state ORDER BY corpus")
    ]


def _search_index_version(con: sqlite3.Connection) -> str | None:
    try:
        row = con.execute(
            "SELECT version FROM search_index_state WHERE component=?",
            (SEARCH_INDEX_COMPONENT,),
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    return row["version"] if row else None


def _export_records(
    con: sqlite3.Connection,
    writer: _ShardWriter,
) -> None:
    rows = con.execute(
        """SELECT id,corpus,language,collection_name,work_id,segment_id,title,
                  raw_text,source_path,source_sha,evidence_class,text_role,witness,
                  sequence_no,relation_ids
           FROM records
           ORDER BY corpus,work_id,source_path,sequence_no,id"""
    )
    groups = itertools.groupby(
        rows,
        key=lambda row: (row["corpus"], row["work_id"], row["source_path"]),
    )
    for (corpus, _work_id, _source_path), group in groups:
        for block in _record_blocks(group, writer.target_bytes):
            writer.add("records", corpus, block)
    writer.flush()


def _export_simple_table(
    con: sqlite3.Connection,
    writer: _ShardWriter,
    table: str,
) -> None:
    for row in con.execute(f"SELECT * FROM {table} ORDER BY corpus,id"):
        item = dict(row)
        writer.add(
            table,
            item["corpus"],
            [_ExportLine(_json_bytes(item), item["id"])],
        )
    writer.flush()


def _remote_readme() -> str:
    return """# GitHub Connector Corpus Export

This directory is a deterministic, read-only export of the existing SQLite
index. It is an access adapter, not a second research system.

1. Read `manifest.json` and verify actual corpus coverage and pinned SHAs.
2. Search UTF-8 text only under `records/`.
3. Treat `export_role: "primary"` as a hit. Rows marked `context_overlap`
   only preserve two neighboring records across shard boundaries; deduplicate
   all rows by `id`.
4. Read provenance on the record itself.
5. Inspect `relations/` and `variants/` when the research question needs them.
6. Apply the evidence hierarchy and witness separation from the repository
   research skill.

In the manifest, `shard_fields` names the columns used by each compact row in
`shards`.

Files are JSON Lines, ordered and sharded at record boundaries. If the export
does not contain enough evidence, report:

`không đủ dữ liệu trong remote corpus export hiện tại`
"""


def _replace_export(stage: Path, output: Path) -> None:
    if output.is_symlink() or output.is_file():
        raise ValueError(f"refusing to replace non-directory output: {output}")
    if output.exists() and not (output / EXPORT_MARKER).is_file():
        raise ValueError(
            f"refusing to replace directory without {EXPORT_MARKER}: {output}"
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


def _snapshot_database(source_path: Path, target_path: Path) -> None:
    source = sqlite3.connect(
        f"file:{source_path.resolve()}?mode=ro",
        uri=True,
        timeout=30,
    )
    target = sqlite3.connect(target_path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def export_remote(
    db_path: Path,
    output_dir: Path,
    max_shard_bytes: int = DEFAULT_SHARD_BYTES,
    progress: bool = False,
) -> dict:
    if max_shard_bytes <= 0:
        raise ValueError("max_shard_bytes must be positive")
    if not db_path.is_file():
        raise FileNotFoundError(f"index not found at {db_path}")

    output = output_dir.resolve()
    if output == output.parent or not output.name:
        raise ValueError(f"unsafe export output path: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = output.parent / f".{output.name}.exporting"
    if stage.is_symlink() or stage.is_file():
        stage.unlink()
    elif stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    workspace = tempfile.TemporaryDirectory(prefix="buddhist-remote-db-")
    read_db = Path(workspace.name) / db_path.name
    if progress:
        print("[export] copying SQLite snapshot to fast workspace", file=sys.stderr, flush=True)
    _snapshot_database(db_path, read_db)

    con = connect_readonly(read_db)
    try:
        source_contract = _source_contract(con)
        search_index_version = _search_index_version(con)
        record_counts = _table_counts(con, "records")
        work_counts = _table_counts(con, "works")
        relation_counts = _table_counts(con, "relations")
        variant_counts = _table_counts(con, "variants")

        writer = _ShardWriter(stage, max_shard_bytes)
        _export_records(con, writer)
        if progress:
            print("[export] records complete", file=sys.stderr, flush=True)
        _export_simple_table(con, writer, "relations")
        if progress:
            print("[export] relations complete", file=sys.stderr, flush=True)
        _export_simple_table(con, writer, "variants")
        if progress:
            print("[export] variants complete", file=sys.stderr, flush=True)

        indexed_corpora = sorted(
            set(record_counts)
            | set(work_counts)
            | set(relation_counts)
            | set(variant_counts)
            | {source["corpus"] for source in source_contract}
        )
        source_by_corpus = {
            source["corpus"]: source for source in source_contract
        }
        corpora = []
        for corpus in indexed_corpora:
            source = source_by_corpus.get(corpus, {})
            corpora.append(
                {
                    "corpus": corpus,
                    "record_count": record_counts.get(corpus, 0),
                    "work_count": work_counts.get(corpus, 0),
                    "relation_count": relation_counts.get(corpus, 0),
                    "variant_count": variant_counts.get(corpus, 0),
                    "repo_path": source.get("repo_path"),
                    "source_sha": source.get("source_sha"),
                    "parser_version": source.get("parser_version"),
                    "evidence_class": source.get("evidence_class"),
                }
            )

        manifest = {
            "export_version": EXPORT_VERSION,
            "format": "jsonl",
            "index": {
                "record_count": sum(record_counts.values()),
                "work_count": sum(work_counts.values()),
                "relation_count": sum(relation_counts.values()),
                "variant_count": sum(variant_counts.values()),
            },
            "source_contract": {
                "derived_from": "SQLite source_state",
                "sources": source_contract,
            },
            "corpora": corpora,
            "record_count_per_corpus": record_counts,
            "relation_count_per_corpus": relation_counts,
            "variant_count_per_corpus": variant_counts,
            "search_index_version": search_index_version,
            "shard_target_bytes": max_shard_bytes,
            "context": {
                "window": 2,
                "strategy": "overlap",
                "primary_role": "primary",
                "overlap_role": "context_overlap",
                "deduplicate_by": "id",
            },
            "shard_fields": list(SHARD_FIELDS),
            "shards": [
                [shard[field] for field in SHARD_FIELDS]
                for shard in writer.shards
            ],
        }
        (stage / "manifest.json").write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        (stage / "README.md").write_text(_remote_readme(), encoding="utf-8")
        (stage / EXPORT_MARKER).write_text(
            f"export_version={EXPORT_VERSION}\n",
            encoding="utf-8",
        )
    except Exception:
        con.close()
        shutil.rmtree(stage, ignore_errors=True)
        workspace.cleanup()
        raise
    con.close()

    try:
        _replace_export(stage, output)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    finally:
        workspace.cleanup()
    return {
        "database": str(db_path),
        "output": str(output),
        "record_count": manifest["index"]["record_count"],
        "work_count": manifest["index"]["work_count"],
        "relation_count": manifest["index"]["relation_count"],
        "variant_count": manifest["index"]["variant_count"],
        "shard_count": len(manifest["shards"]),
        "manifest": str(output / "manifest.json"),
    }
