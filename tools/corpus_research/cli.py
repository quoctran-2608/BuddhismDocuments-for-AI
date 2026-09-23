from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .index import PROFILE_SOURCES, SOURCE_BUILDERS, build_index, local_sha
from .remote_export import DEFAULT_SHARD_BYTES, export_remote
from .retrieval import (
    compare,
    context,
    evidence,
    parallels,
    provenance,
    resolve,
    search,
    status,
    variants,
    work,
)


def root_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def emit(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="buddhist-corpus",
        description="Deterministic offline retrieval for the local Buddhist corpus.",
    )
    p.add_argument("--db", type=Path, default=root_dir() / "derived/corpus.sqlite3")
    sub = p.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="incrementally build a local derived index")
    build.add_argument("--profile", choices=PROFILE_SOURCES, default="core")
    build.add_argument("--force", action="store_true")
    build.add_argument("--source", action="append", choices=sorted(SOURCE_BUILDERS))
    build.add_argument(
        "--defer-fts",
        action="store_true",
        help="checkpoint records now and rebuild FTS in a later build pass",
    )

    sub.add_parser("status", help="report local source and index readiness")

    find = sub.add_parser("search", help="rank exact, normalized, lemma, and FTS candidates")
    find.add_argument("query")
    find.add_argument("--limit", type=int, default=20)
    find.add_argument("--language")
    find.add_argument("--corpus")
    find.add_argument("--context", type=int, default=0)
    find.add_argument("--with-provenance", action="store_true")

    ctx = sub.add_parser("context", help="read neighboring indexed records")
    ctx.add_argument("--record-id", type=int, required=True)
    ctx.add_argument("--window", type=int, default=2)

    wk = sub.add_parser("work", help="show work metadata and indexed witnesses")
    wk.add_argument("identifier")

    par = sub.add_parser("parallels", help="show local relationship/alignment evidence")
    par.add_argument("identifier")

    res = sub.add_parser(
        "resolve",
        help="resolve an indexed SC UID, CBETA work, or Taisho range to local primary records",
    )
    res.add_argument("identifier")
    res.add_argument("--limit", type=int, default=100)

    var = sub.add_parser("variants", help="show local textual variant evidence")
    var.add_argument("identifier")

    cmp_ = sub.add_parser("compare", help="return witnesses without harmonizing them")
    cmp_.add_argument("identifiers", nargs="+")

    prov = sub.add_parser("provenance", help="show the source contract for one record")
    prov.add_argument("--record-id", type=int, required=True)

    ev = sub.add_parser(
        "evidence",
        help="bundle one record with context, provenance, and variants",
    )
    ev.add_argument("--record-id", type=int, required=True)
    ev.add_argument("--context", type=int, default=2)

    export = sub.add_parser(
        "export-remote",
        help="export the current SQLite index for GitHub Connector access",
    )
    export.add_argument("--output", type=Path, default=root_dir() / "remote/corpus")
    export.add_argument("--max-shard-bytes", type=int, default=DEFAULT_SHARD_BYTES)
    return p


def source_status(root: Path) -> list[dict]:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    rows = []
    for item in manifest:
        repo = item["rel_dest"]
        try:
            sha = local_sha(root, repo)
            rows.append(
                {
                    "repo": repo,
                    "present": True,
                    "manifest_sha": item["commit_sha"],
                    "local_sha": sha,
                    "sha_match": sha == item["commit_sha"],
                }
            )
        except (FileNotFoundError, RuntimeError) as exc:
            rows.append(
                {
                    "repo": repo,
                    "present": False,
                    "manifest_sha": item["commit_sha"],
                    "local_sha": None,
                    "sha_match": False,
                    "error": str(exc),
                }
            )
    return rows


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = root_dir()
    if args.command == "build":
        try:
            emit(
                build_index(
                    root,
                    args.db,
                    args.profile,
                    args.force,
                    only_sources=args.source,
                    rebuild_fts=not args.defer_fts,
                )
            )
            return 0
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    if args.command == "status":
        sources = source_status(root)
        result = status(args.db)
        result["local_sources"] = sources
        result["source_contract_ok"] = all(x["present"] and x["sha_match"] for x in sources)
        emit(result)
        return 0 if result["source_contract_ok"] else 2
    if not args.db.exists():
        print(
            f"error: index not found at {args.db}; run `bin/buddhist-corpus build --profile core`",
            file=sys.stderr,
        )
        return 2
    if args.command == "search":
        emit(
            search(
                args.db,
                args.query,
                args.limit,
                args.language,
                args.corpus,
                args.context,
                args.with_provenance,
            )
        )
    elif args.command == "context":
        emit(context(args.db, args.record_id, args.window))
    elif args.command == "work":
        emit(work(args.db, args.identifier))
    elif args.command == "parallels":
        emit(parallels(args.db, args.identifier))
    elif args.command == "resolve":
        emit(resolve(args.db, args.identifier, args.limit))
    elif args.command == "variants":
        emit(variants(args.db, args.identifier))
    elif args.command == "compare":
        emit(compare(args.db, args.identifiers))
    elif args.command == "provenance":
        emit(provenance(args.db, args.record_id))
    elif args.command == "evidence":
        emit(evidence(args.db, args.record_id, args.context))
    elif args.command == "export-remote":
        try:
            emit(
                export_remote(
                    args.db,
                    args.output,
                    args.max_shard_bytes,
                    progress=True,
                )
            )
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
