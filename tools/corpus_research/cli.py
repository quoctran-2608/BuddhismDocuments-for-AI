from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .index import PROFILE_SOURCES, SOURCE_BUILDERS, build_index, local_sha
from .remote_export import DEFAULT_SHARD_BYTES, export_remote
from .pointer_export import export_pointer_poc
from .pointer_benchmark import (
    DEFAULT_CJK_KEYS,
    DEFAULT_IDENTIFIER_KEYS,
    DEFAULT_LATIN_KEYS,
    DEFAULT_MAX_TOTAL_BYTES,
    export_pointer_benchmark,
)
from .pointer_compact import export_pointer_compact_poc
from .pointer_repetition import analyze_pointer_repetition
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

    pointer = sub.add_parser(
        "export-remote-pointers",
        help="export a small raw-text-free GitHub Connector pointer POC",
    )
    pointer.add_argument(
        "--output",
        type=Path,
        default=root_dir() / "remote/pointer-poc",
    )
    pointer.add_argument("--query", action="append", default=[])
    pointer.add_argument("--identifier", action="append", default=[])
    pointer.add_argument(
        "--limit",
        type=int,
        default=20,
        help="maximum distinct work/source pointers retained per corpus",
    )
    benchmark = sub.add_parser(
        "export-pointer-benchmark",
        help="measure the existing pointer pipeline on deterministic local keys",
    )
    benchmark.add_argument(
        "--output",
        type=Path,
        default=root_dir() / "remote/pointer-benchmark",
    )
    benchmark.add_argument("--latin-keys", type=int, default=DEFAULT_LATIN_KEYS)
    benchmark.add_argument("--cjk-keys", type=int, default=DEFAULT_CJK_KEYS)
    benchmark.add_argument(
        "--identifier-keys",
        type=int,
        default=DEFAULT_IDENTIFIER_KEYS,
    )
    benchmark.add_argument(
        "--limit",
        type=int,
        default=20,
        help="maximum distinct work/source pointers retained per corpus",
    )
    benchmark.add_argument(
        "--max-total-bytes",
        type=int,
        default=DEFAULT_MAX_TOTAL_BYTES,
        help="stop before replacing output if the artifact exceeds this size",
    )
    compact = sub.add_parser(
        "export-pointer-compact-poc",
        help="compact an existing pointer benchmark without rerunning retrieval",
    )
    compact.add_argument(
        "--benchmark",
        type=Path,
        default=root_dir() / "remote/pointer-benchmark",
    )
    compact.add_argument(
        "--output",
        type=Path,
        default=root_dir() / "remote/pointer-compact-poc",
    )
    repetition = sub.add_parser(
        "analyze-pointer-repetition",
        help="measure metadata repetition in an existing pointer benchmark",
    )
    repetition.add_argument(
        "--benchmark",
        type=Path,
        default=root_dir() / "remote/pointer-benchmark",
    )
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
    elif args.command == "export-remote-pointers":
        try:
            emit(
                export_pointer_poc(
                    args.db,
                    args.output,
                    root / "config/corpus-sources.json",
                    args.query,
                    args.identifier,
                    args.limit,
                    root,
                )
            )
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    elif args.command == "export-pointer-benchmark":
        try:
            emit(
                export_pointer_benchmark(
                    args.db,
                    args.output,
                    root / "config/corpus-sources.json",
                    root,
                    args.latin_keys,
                    args.cjk_keys,
                    args.identifier_keys,
                    args.limit,
                    args.max_total_bytes,
                )
            )
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    elif args.command == "export-pointer-compact-poc":
        try:
            emit(export_pointer_compact_poc(args.benchmark, args.output))
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    elif args.command == "analyze-pointer-repetition":
        try:
            emit(analyze_pointer_repetition(args.benchmark))
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
