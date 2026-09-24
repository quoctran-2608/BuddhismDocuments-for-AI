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
4. inspect actual coverage, counts, and pinned source SHAs;
5. use `<root_path>/locator/manifest.json` to normalize and route the query or
   identifier to candidate shard paths;
6. fetch candidate JSONL shards and verify the actual hit in exported content;
7. inspect primary-hit context and provenance;
8. inspect `relations/` and `variants/` under `<root_path>` when needed;
9. apply the existing research skill, including evidence hierarchy, research
   modes, ranking interpretation, witness separation, and fail-closed behavior.

GitHub Code Search is optional only. The connector workflow must not depend on
GitHub Code Search indexing. Locator rows identify candidate files only; they
are not evidence and cannot establish a scholarly conclusion.

Rows marked `context_overlap` exist only to preserve shard-boundary context.
Deduplicate by record `id` and treat only `export_role: "primary"` as a hit.
Connector mode changes only the data-access path, not scholarly reasoning. If
the export cannot establish the claim, return
`không đủ dữ liệu trong remote corpus export hiện tại`.

The main repository is the canonical research architecture. The remote
repository is a deterministic derived access artifact, not source-of-truth.
Local mode remains offline. Connector mode uses only the declared main and
remote GitHub repositories for repository evidence. Unless the user limits the
corpus, research uses all data actually present in the current index/export.
Read coverage from the manifest and never claim all 13 sources when the export
contains fewer components. Remote records preserve source SHA, evidence class,
text role, and witness.

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
