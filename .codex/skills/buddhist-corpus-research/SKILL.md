---
name: buddhist-corpus-research
description: Offline, provenance-first research across the 13 local Buddhist corpus sources.
---

# Buddhist Corpus Research

Read and obey the repository root `AGENTS.md` before using this skill.

## Contract

- Input: a term, passage, topic, work ID, relation, variant, or verification
  question.
- Output: findings supported only by local repository evidence, with corpus,
  relative path, work/segment ID, source SHA, evidence class, text role, and
  witness.
- Failure: if local sources/indexes cannot establish the claim, return
  `không đủ dữ liệu trong corpus hiện tại`.
- Side effects: retrieval is read-only. `build` creates/replaces derived data
  under `derived/`; it never edits a submodule.
- Permissions: read the root and submodules; write only outside submodules;
  execute local Python/Git/SQLite tools; no network permission.

## Execution environment

### Local mode

When the local CLI and SQLite index are available, use the existing workflow in
this skill. `evidence --record-id ID --context 2` can bundle a record, context,
provenance, and variants after search.

### GitHub Connector mode

When shell/SQLite access is unavailable but the repositories can be read:

1. read `config/remote-corpus.json` from the main repository;
2. identify the remote corpus repository, branch, and root path;
3. open `<root_path>/manifest.json` in that repository;
4. inspect the exact POC query coverage, source mappings, and pinned source
   SHAs;
5. use `<root_path>/locator/manifest.json` to normalize and route the query or
   identifier to its priority-ordered pointer list;
6. select ranked source pointers according to the research mode below, then
   open the original GitHub repository at each pointer's pinned SHA and path;
7. verify wording, context, provenance, text role, and witness in the source;
8. inspect source relationships and variants when needed;
9. apply the existing research skill, including evidence hierarchy, research
   modes, ranking interpretation, witness separation, and fail-closed behavior.

The generated POC has already selected the best distinct `(work_id, source_path)`
candidate within each available corpus before applying its per-corpus limit.
Pointer `source_blob_sha`, when non-null, is the offline Git blob ID for
`source_sha:source_path`; compare it with the pinned source file when available.

Choose candidates by research mode:

- **Quick or exact lookup:** for a term, passage, work ID, or quick verification
  of a specific source, start with the highest-priority candidates in scope.
- **Topic, comparative, or cross-corpus research:** never spend the whole
  candidate budget on the first 20–50 global entries. Group available pointers
  by corpus, preserve locator priority within each corpus, and open a useful
  sample from every relevant corpus. Verify source text, then inspect context,
  provenance, relations, variants, and independent witnesses before synthesis.
  The POC may not contain enough pointers for exhaustive research; state that
  limit rather than treating it as full query coverage.
- **User-restricted scope:** if the user asks for only a Nikāya, CBETA, T99, one
  Vinaya, or another explicit scope, select only candidates in that scope. Do
  not broaden the corpus set without permission.

Pointer priority decides which source files to open first. It does not decide which
corpus is more important, which text is more correct, whether one witness is
sufficient, or which source best answers the question. Those judgments still
follow user scope, research mode, evidence hierarchy, text role, witness
separation, and provenance. Locator routing is not a byte-for-byte reproduction
of SQLite FTS candidate generation.

GitHub Code Search is optional only. The connector workflow must not depend on
GitHub Code Search indexing. Pointer rows identify candidate original source
files only; they are not evidence and cannot establish a scholarly conclusion.

The pointer POC does not copy `raw_text` or context rows. Use each pointer's
`repository`, `source_sha`, `source_path`, `work_id`, `segment_id`, and
`sequence_no` to inspect the original file directly. Connector mode changes
only the data-access path, not scholarly reasoning. If the export cannot
establish the claim, return
`không đủ dữ liệu trong remote corpus export hiện tại`.

The main repository is the canonical research architecture. The remote
repository is a deterministic derived access artifact, not source-of-truth.
Local mode remains offline. Connector mode uses only the declared main and
remote GitHub repositories plus the pinned original source repositories named
by pointers for repository evidence. Unless the user limits the corpus,
research uses all data actually present in the current pointer POC. Read
coverage from the manifest and never claim all 13 sources when the POC contains
fewer components. Pointers preserve source SHA, evidence class, text role, and
witness.

`remote/pointer-benchmark/`, when present, is a measurement artifact rather than
a research-coverage promise or a production locator. Read its
`benchmark-summary.json` and `benchmark-queries.json` to inspect measured size,
sampling, and limits. Do not treat its 500 sampled keys as a complete vocabulary
or use its linear estimates as evidence for a redesign.

`remote/pointer-compact-poc/`, when present, is a serialization-only comparison
against that exact benchmark. Resolve a locator reference by reading its
`pointer_id` in the pointer table, then merge its ranking fields. Its equivalence
claim is limited to the source benchmark rows; do not infer that it changes
research retrieval, ranking, evidence, or production architecture.

`analyze-pointer-repetition` is read-only measurement over the committed
benchmark. It must not be mistaken for a request to add source/work tables.
Use its byte simulations only to report whether metadata repetition clears the
chosen storage threshold; do not infer a new runtime architecture from them.

`analyze-pointer-key-universe` is also read-only. It reports the finite
Latin/romanized and identifier universe from existing tables. For CJK, do not
scan source text or create a persistent vocabulary index merely to count keys.

When a task explicitly authorizes measuring the already-indexed CJK vocabulary,
use only:

```sql
CREATE VIRTUAL TABLE temp.cjk_vocab_measurement
USING fts5vocab(main, records_cjk_fts, 'row');
```

on a `mode=ro` connection. The TEMP table disappears on close. Treat its output
as the finite indexed trigram token universe, not a dictionary of Buddhist terms,
topic coverage, or a new query parser.

## Start

```bash
bin/buddhist-corpus status
```

If the index is absent:

```bash
bin/buddhist-corpus build --profile core
```

Use `--profile discovery` to add alignment/segmented candidate sources and
`--profile all` for all supported local sources. Builds are incremental by
submodule SHA.

## Research modes

### 1. Term research

1. Search the exact form.
2. Review `match_reasons`: exact, normalized, diacritic-folded, compact, FTS,
   and corpus-lemma.
3. For Pāli, inspect corpus-provided lemma/morphology before proposing variant
   spellings.
4. Read context.
5. Inspect variants.
6. Only then expand through local parallels/alignment.

```bash
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus context --record-id RECORD_ID
bin/buddhist-corpus variants mn1
```

### 2. Passage search

Search a distinctive phrase, rank stronger editions above discovery corpora,
then read context and provenance.

```bash
bin/buddhist-corpus search "如是我聞" --language lzh
bin/buddhist-corpus provenance --record-id RECORD_ID
```

If a BuddhaNexus result identifies a CBETA work/line, query that identifier or
search the phrase in `cbeta-tei`. Cite CBETA as the textual witness and
BuddhaNexus only as discovery evidence.

### 3. Concept/topic research

Do not synthesize from one keyword result. Iterate:

1. seed evidence;
2. collect terminology found in that evidence;
3. search each internally attested term;
4. read context and work structure;
5. inspect parallels and variants;
6. seek independent witnesses;
7. synthesize agreements, differences, and limits.

### 4. Parallel-text research

```bash
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus compare ID1 ID2
```

SuttaCentral `full`/`partial` edges are relationship evidence, not proof that
two passages say the same thing. A `suttacentral_cbeta:*` edge is separate
identifier metadata. Only the resolved `cbeta-bm` or `cbeta-tei` record is the
local CBETA textual witness.

### 5. Variant research

```bash
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus variants mn1
```

Keep lemma, reading, witness sigla, confidence, and source path distinct.
Derived critical selections are editorial outputs; list base witnesses.

### 6. Cross-tradition comparison

Use `compare` to keep witnesses separate. Establish cross-language equivalence
only through local relation/alignment evidence. Never harmonize differences.

### 7. Source verification

```bash
bin/buddhist-corpus provenance --record-id RECORD_ID
bin/buddhist-corpus status
```

Open the returned `source_path` directly when markup, folio, apparatus, or
larger context matters. Confirm that `source_sha` matches the pinned local
submodule SHA.

## Ranking interpretation

Ranking combines:

- exactness and normalization;
- corpus-provided lemma matches;
- evidence class;
- stable segment identifiers and provenance.

It deliberately gives canonical/root and authoritative structured editions
more weight than alignment, computational segmentation, derived analysis, or
auxiliary data. Ranking is a retrieval aid, not a verdict.

`evidence_class` records source authority; `text_role` records whether a result
is root text, main translation, heading, translator comment, translation note,
alignment text, or another explicit role. Do not quote or synthesize
`translator_comment` or `translation_note` records as though they were
root/scriptural text. They remain useful evidence when labeled by role.

## Answer template

1. **Finding** — concise claim.
2. **Evidence by witness** — do not merge witnesses.
3. **Parallels/variants** — relationship type and differences.
4. **Confidence and limits**.
5. **Provenance** for every cited item:
   `corpus | source_path | work_id | segment_id | source_sha | evidence_class | text_role | witness`.
