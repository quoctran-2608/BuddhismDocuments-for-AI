# GitHub Connector Research Access

The pointer export gives GitHub-only agents a read/fetch path into the same
evidence model used by the local SQLite CLI. It does not add a second parser,
index, ranking method, or research methodology.

The main repository contains the code and canonical research architecture.
`config/remote-corpus.json` points to the separate repository that contains the
deterministic generated connector-readable pointer POC. `config/corpus-sources.json`
maps each corpus to the GitHub source repository that a pointer opens.

## Generate the pointer POC

```bash
bin/buddhist-corpus export-remote-pointers \
  --query anicca \
  --query 無常 \
  --identifier T02n0099 \
  --output remote/pointer-poc
```

The command reads only `derived/corpus.sqlite3` and does not use the network or
commit files. It writes ranked pointers, not copied record text. Each pointer
contains the source repository, pinned source SHA, repository-relative path,
work/segment identifiers, evidence class, text role, witness, sequence number,
and the score/reasons used to choose its position. Output ordering and JSON
encoding are deterministic for the same database, source SHAs, code, and
options.

## Local mode and connector mode

Local agents should use `search`, `evidence`, `context`, `provenance`,
`parallels`, `resolve`, and `variants`.

GitHub Connector agents should:

1. read `config/remote-corpus.json` from the main repository;
2. identify the remote repository, branch, and root path;
3. open `<root_path>/manifest.json` in the remote repository;
4. check that the artifact is `pointer-locator-jsonl`, that
   `raw_text_exported` is false, and inspect source repository mappings and
   pinned source SHAs;
5. read `<root_path>/locator/manifest.json`, normalize the query or identifier,
   and calculate the declared bucket;
6. fetch the bucket part file(s), then read its ranked pointer list;
7. select pointers according to the research mode below;
8. open `repository` at `source_sha`, then open `source_path` directly in the
   original GitHub repository;
9. use `work_id`, `segment_id`, and `sequence_no` to locate the passage, then
   verify wording, context, provenance, text role, and witness in the source;
10. inspect source relationships or variants when the research question needs
    them;
11. apply the existing evidence hierarchy and keep witnesses separate.

The pointer locator maps normalized terms, CJK bigrams, and identifiers to
ranked source pointers. For a passage, look up a few distinctive terms or CJK
bigrams, open the indicated pinned source files, and verify the full phrase in
the original source. A pointer includes the repository, pinned source SHA,
repository-relative source path, work ID, segment ID, sequence number,
evidence class, text role, and witness. Pointer rows are not evidence. GitHub
Code Search is optional only; the connector workflow does not depend on its
indexing.

Pointer priority reuses the local searcher's shared deterministic final scoring
semantics: evidence weight, exact/normalized/diacritic-folded/compact matching,
corpus-lemma evidence, segment quality, and stable tie-breaking. The POC uses
the existing `search()` results for term queries and `score_record_match()` for
exact identifier pointers. It is not a byte-for-byte reproduction of SQLite
FTS/BM25 candidate generation.

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
consuming the entire candidate budget. Pointer priority decides which source
files to open first; it does not decide which corpus matters more, which text is correct,
whether a witness is sufficient, or which source best answers the question.
Those decisions remain governed by user scope, research mode, evidence
hierarchy, text role, witness separation, and provenance.

## Coverage and limits

This is a small proof of concept for the explicitly generated query keys; it is
not a complete export of every indexed record. It exports no copied `raw_text`,
record shard, relation shard, variant shard, or second search engine. The
manifest reports the exact query keys, pointer counts, source mappings, and
pinned source contracts. It must not be read as claiming complete query
coverage or all indexed corpora.

The main repository is the canonical research architecture. The remote
repository is a deterministic derived access artifact, not source-of-truth.
Local mode remains offline, while connector mode uses the declared main and
remote repositories plus the pinned original source repositories named by
pointers. Unless the user limits the corpus, use all data actually present in
the current export. Read coverage from the manifest and never claim all 13
sources when fewer components are present. Exported pointers preserve source
SHA, evidence class, text role, and witness.

If the locator or export is missing or cannot establish a claim, report:

**không đủ dữ liệu trong remote corpus export hiện tại**
