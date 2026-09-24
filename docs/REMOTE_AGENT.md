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
5. read `<root_path>/locator/manifest.json`, normalize the query or identifier,
   and calculate the declared bucket;
6. fetch the bucket part file(s), then resolve their zero-based shard indexes
   through the root manifest `shards` array;
7. treat record shard indexes as a full priority-ordered candidate list and
   select shards according to the research mode below;
8. fetch the selected shards and verify actual hits, using only
   `export_role: "primary"` as record hits;
9. read the neighboring overlap rows and record-level provenance;
10. inspect `relations/` or `variants/` under `<root_path>` when needed;
11. apply the existing evidence hierarchy and keep witnesses separate.

`context_overlap` rows preserve two records on each side of a shard boundary.
They duplicate indexed records only for context, so consumers must deduplicate
by record `id`.

The locator maps normalized terms, CJK bigrams, and identifiers to candidate
shards. For a passage, look up a few distinctive terms or CJK bigrams and
intersect or prioritize their paths, then verify the full phrase in
`raw_text`. Locator rows are not evidence. GitHub Code Search is optional only;
the connector workflow does not depend on its indexing.

The record list retains every candidate shard but orders it by the best
matching record in each shard. Priority reuses the local searcher's shared
deterministic final scoring semantics: evidence weight, exact/normalized/
diacritic-folded/compact matching, corpus-lemma evidence, segment quality, and
stable tie-breaking. Locator routing is not a byte-for-byte reproduction of
SQLite FTS/BM25 candidate generation.

Select candidates according to the question:

- For a quick term, passage, work-ID, or source-specific lookup, start with the
  highest-priority candidates within the requested scope.
- For topic, comparative, or cross-corpus research, do not take only the first
  20–50 global candidates. Group the full list by corpus, preserve priority
  within each corpus, and take a useful sample from every relevant corpus,
  commonly about 5–10 shards per corpus. Then verify records and inspect
  context, provenance, relations, variants, and independent witnesses before
  synthesis. The number is guidance, not a fixed quota.
- If the user restricts the question to a Nikāya, CBETA, T99, one Vinaya, or
  another explicit corpus scope, use only candidates in that scope and do not
  expand it without permission.

This corpus-balanced selection prevents one large or highly ranked corpus from
consuming the entire candidate budget. Locator priority decides which files to
open first; it does not decide which corpus matters more, which text is correct,
whether a witness is sufficient, or which source best answers the question.
Those decisions remain governed by user scope, research mode, evidence
hierarchy, text role, witness separation, and provenance.

## Coverage and limits

The export includes every record, relation, and variant in the selected SQLite
database. Coverage is therefore the current index coverage, not all possible
source data. The manifest reports actual table counts and `source_state`
contracts. `shard_fields` names the columns used by each compact row in
`shards`; those rows include path, counts, ID range, and first/last work hints.
The manifest must not be read as claiming unindexed corpora.

The main repository is the canonical research architecture. The remote
repository is a deterministic derived access artifact, not source-of-truth.
Local mode remains offline, while connector mode uses only the declared main
and remote GitHub repositories for repository evidence. Unless the user limits
the corpus, use all data actually present in the current export. Read coverage
from the manifest and never claim all 13 sources when fewer components are
present. Exported records preserve source SHA, evidence class, text role, and
witness.

If the locator or export is missing or cannot establish a claim, report:

**không đủ dữ liệu trong remote corpus export hiện tại**
