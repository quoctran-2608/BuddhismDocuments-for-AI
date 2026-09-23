# Offline Buddhist Corpus Research Architecture

## 1. Source Layer

The 13 pinned Git submodules are immutable sources-of-origin. `manifest.json`
and each local submodule `HEAD` form the source contract. A missing source or
SHA mismatch fails closed; the system never fetches.

`config/corpus-sources.json` records source roles and evidence classes.

## 2. Index Layer

`bin/buddhist-corpus build` creates `derived/corpus.sqlite3`.

The committed schema stores:

- text records with corpus, language, collection, work/segment ID, title, raw
  text, normalized/folded/compact representations, path, SHA, evidence class,
  text role, witness, sequence, and relation IDs;
- work metadata;
- relation edges;
- variant readings;
- corpus-provided lemmas and morphology;
- per-source build state;
- separate derived-search-index compatibility state.

The `core` profile chunks source text at stable source boundaries to keep the
global index practical: Bilara uses bounded segment ranges and CBETA BM_u8 uses
bounded line ranges. Returned records retain the first/last source IDs so an
agent can reopen the exact raw file for finer context. The `all` profile keeps
the more granular parsers. Bilara variant entries are likewise grouped into
bounded ranges while retaining their individual segment labels in the reading.

FTS5 `unicode61` handles ordinary Unicode token search. A separate contentless
FTS5 `trigram` index stores `compact(raw_text)` for `lzh`/`zh` records and
generates candidates for Chinese middle-substring queries of at least three
characters. Candidate-scoped exact/normalized/compact checks and the existing
evidence ranking then run on the union. This batch does not establish Tibetan
substring behavior. No generated DB is a source-of-truth.

### Incrementality

The index is incremental.

Each parser is keyed by:

`corpus component + local submodule SHA + parser version + indexing scope`

An unchanged component is skipped. A changed component is deleted and rebuilt
without rebuilding unrelated corpora.

The scope fingerprint prevents a detailed `all` build from mistaking a
chunked `core` state for the same derived representation.

On WSL-mounted storage, the builder checkpoints the temporary fast workspace
back to `derived/` after each completed corpus. An interrupted build can resume
without repeating completed sources.

Expensive sources can also be built explicitly with `--source` and
`--defer-fts`. A final normal `build` pass skips unchanged sources and rebuilds
both the ordinary and CJK substring search indexes once. Rebuilding source
records with `--defer-fts` invalidates the shared search-index compatibility
state until that final pass.

Profiles:

- `core`: SuttaCentral roots/English/variants, CBETA BM_u8 full text,
  84000 TEI/RDF, and Pāli lemma/critical data;
- `discovery`: Translation Memory, OpenPecha, BuddhaNexus;
- `all`: all 13 local sources, including CBETA XML P5 apparatus and every
  Bilara translation/comment;
- `acceptance`: deterministic real local samples for tests.

## 3. Retrieval Layer

The CLI exposes:

- `status`
- `build`
- `search`
- `context`
- `work`
- `parallels`
- `variants`
- `compare`
- `provenance`

Search ranking combines exactness, Unicode normalization, explicit
diacritic-folding, compact-script matching, corpus-provided lemma matches,
evidence class, stable IDs, and provenance quality. Text similarity alone does
not establish a finding.

Relationship tables preserve SuttaCentral parallel types, 84000 work/instance
relationships, and alignment groups without turning them into textual claims.

`evidence_class` describes source authority/provenance. `text_role` independently
describes the indexed content: for example `root_text`, `translation_main`,
`translation_heading`, `translator_comment`, or `translation_note`. An
authoritative note remains authoritative structured evidence without becoming
the translated scripture itself. Nested 84000 body notes are indexed separately
and linked to the containing main segment with `84000:note_of`.

On WSL-mounted paths, builds use a temporary Linux-filesystem SQLite workspace
and copy the completed database back through SQLite's backup API. This avoids
slow per-write NTFS translation while keeping the final artifact under
`derived/`.

## 4. Research Skill

`.codex/skills/buddhist-corpus-research/SKILL.md` translates research intent
into deterministic CLI calls. It requires iterative retrieval for topic
research and requires discovery hits to be checked against stronger witnesses.

The skill supports:

- term research;
- passage search;
- concept/topic research;
- parallel-text research;
- variant research;
- cross-tradition comparison;
- source verification.

## 5. Answer / Provenance Layer

Every returned record contains enough fields to cite:

`corpus | source_path | work_id | segment_id | source_sha | evidence_class | text_role | witness`

Answers keep witnesses separate and state uncertainty. If the local repository
does not establish a claim, the correct output is:

**không đủ dữ liệu trong corpus hiện tại**

## Data flow

```text
Pinned immutable submodules
          │
          ▼
Deterministic local parsers ── source SHA/parser state
          │
          ▼
SQLite records + FTS + relations + variants + lemmas
          │
          ▼
CLI retrieval/ranking/context/provenance
          │
          ▼
Research skill with evidence hierarchy and fail-closed rules
          │
          ▼
Witness-separated answer with repository provenance
```
