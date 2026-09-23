# GitHub Connector Research Access

The remote corpus export gives GitHub-only agents a read/search/fetch path into
the same evidence model used by the local SQLite CLI. It does not add a second
parser, index, ranking method, or research methodology.

The main repository contains the code and canonical research architecture.
`config/remote-corpus.json` points to the separate repository that contains the
deterministic generated connector-readable export.

## Generate or regenerate

```bash
bin/buddhist-corpus export-remote --output remote/corpus
```

The command reads only `derived/corpus.sqlite3` and does not use the network or
commit files. It replaces only a target directory marked as an earlier corpus
export and fails if the database is absent. Output ordering, names, JSON
encoding, and shard boundaries are deterministic for the same database, source
SHAs, code, and options.

## Local mode and connector mode

Local agents should use `search`, `evidence`, `context`, `provenance`,
`parallels`, `resolve`, and `variants`.

GitHub Connector agents should:

1. read `config/remote-corpus.json` from the main repository;
2. identify the remote repository, branch, and root path;
3. open `<root_path>/manifest.json` in the remote repository;
4. check actual indexed/exported corpora, counts, parser versions, and source
   SHAs;
5. search UTF-8 text under `<root_path>/records/` in the remote repository;
6. fetch matching JSONL shards and use only `export_role: "primary"` as hits;
7. read the neighboring overlap rows and record-level provenance;
8. inspect `relations/` or `variants/` under `<root_path>` when needed;
9. apply the existing evidence hierarchy and keep witnesses separate.

`context_overlap` rows preserve two records on each side of a shard boundary.
They duplicate indexed records only for context, so consumers must deduplicate
by record `id`.

## Coverage and limits

The export includes every record, relation, and variant in the selected SQLite
database. Coverage is therefore the current index coverage, not all possible
source data. The manifest reports actual table counts and `source_state`
contracts. `shard_fields` names the columns used by each compact row in
`shards`; those rows include path, counts, ID range, and first/last work hints.
The manifest must not be read as claiming unindexed corpora.

GitHub code search may tokenize scripts differently, lag after commits, or omit
very broad queries. Search the smallest distinctive exact phrase, then fetch
the shard. If the export is missing or cannot establish a claim, report:

**không đủ dữ liệu trong remote corpus export hiện tại**
