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
  relative path, work/segment ID, source SHA, evidence class, and witness.
- Failure: if local sources/indexes cannot establish the claim, return
  `không đủ dữ liệu trong corpus hiện tại`.
- Side effects: retrieval is read-only. `build` creates/replaces derived data
  under `derived/`; it never edits a submodule.
- Permissions: read the root and submodules; write only outside submodules;
  execute local Python/Git/SQLite tools; no network permission.

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
bin/buddhist-corpus work RELATED_ID
bin/buddhist-corpus compare ID1 ID2
```

SuttaCentral `full`/`partial` edges are relationship evidence, not proof that
two passages say the same thing. Open both textual witnesses when local.

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

## Answer template

1. **Finding** — concise claim.
2. **Evidence by witness** — do not merge witnesses.
3. **Parallels/variants** — relationship type and differences.
4. **Confidence and limits**.
5. **Provenance** for every cited item:
   `corpus | source_path | work_id | segment_id | source_sha | evidence_class | witness`.
