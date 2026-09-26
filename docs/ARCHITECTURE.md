# Offline Buddhist Corpus Research Architecture

## 1. Source Layer

The 13 pinned source repositories/submodules are immutable sources-of-origin.
Pinned SHAs and local source state form the source contract. A missing source
or SHA mismatch fails closed.

`config/corpus-sources.json` records source roles and evidence classes.

## 2. Index Layer

`bin/buddhist-corpus build` creates `derived/corpus.sqlite3`.

The schema stores:

- text records with corpus, language, collection, work/segment ID, text,
  normalized/folded/compact representations, source path/SHA, evidence class,
  text role, witness, sequence, and relation IDs;
- work metadata;
- relation edges;
- variant readings;
- corpus-provided lemmas and morphology;
- per-source build state;
- derived-search-index compatibility state.

FTS5 `unicode61` handles ordinary Unicode token search. A separate contentless
FTS5 `trigram` index stores compact Chinese text for `lzh`/`zh` candidate
generation. The CJK trigram index is local search infrastructure and is not a
remote terminology dictionary.

Generated databases are derived artifacts, never source-of-truth.

### Incrementality

Each parser/build component is keyed by source component, pinned SHA, parser
version, and indexing scope. Unchanged components are skipped.

Profiles:

- `core`: primary/authoritative core sources and lemma data;
- `discovery`: alignment/segmented candidate sources;
- `all`: all 13 supported sources;
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
- `evidence`
- pointer export/measurement commands

Search ranking combines exactness, Unicode normalization, explicit
diacritic-folding, compact matching, corpus-provided lemma matches, evidence
class, stable IDs, and provenance quality.

The shared ranking implementation is reused by production pointer generation.
The Connector does not invent a second scholarly ranking.

`evidence_class` describes source authority/provenance.
`text_role` describes what the indexed content is, such as root text, main
translation, heading, translator comment, translation note, alignment text, or
another explicit role.

## 4. Research Skill

`.codex/skills/buddhist-corpus-research/SKILL.md` maps a user's research
question to either:

- local CLI/SQLite research; or
- GitHub Connector production routing.

The same evidence hierarchy, witness separation, provenance contract, and
fail-closed behavior apply in both modes.

## 5. GitHub Connector Production Access Layer

### Repository roles

```text
main repo
quoctran-2608/BuddhismDocuments-for-AI
    │
    │ config/remote-corpus.json
    ▼
remote locator repo
quoctran-2608/BuddhismDocuments-for-AI-remote
    │
    │ production pointers
    ▼
pinned upstream source repositories
```

The current production root is discovered from config and is presently:

```text
remote/pointer-production-v1/
```

The main repo is canonical architecture.
The remote repo is a derived locator artifact.
The upstream pinned repositories contain the source evidence.

### Production namespaces

Production v1 contains:

```text
terms/latin  → normalized non-CJK lemma keys
ids          → exact original work_id spelling
```

Counts at production-v1 generation:

```text
terms/latin  26,547
ids          32,498
total        59,045
```

`Dhp` and `dhp` remain distinct exact identifier keys.

There is no production `terms/cjk` namespace. The measured local CJK FTS
vocabulary contains tens of millions of low-level trigram tokens; exporting
them as if they were Buddhist concepts was rejected as both semantically wrong
and impractical.

### Deterministic routing

For a term, use the same normalization as
`corpus_research.model.normalize()`:

```text
NFC → casefold → collapse whitespace
```

For identifiers, preserve the exact original spelling.

For either production key:

```text
SHA-256(exact UTF-8 key)
→ first 2 lowercase hex chars
→ locator/<namespace>/<bucket>/part-000001.jsonl
→ exact JSONL key row
```

GitHub Code Search is not required and should not be the routing mechanism.

Verified example:

```text
anicca
→ bucket 45
→ locator/terms/latin/45/part-000001.jsonl
```

### Pointer selection

Generation reuses the existing retrieval/ranking semantics. For each key it
collects ranked candidates per corpus, collapses
`(corpus, work_id, source_path)`, keeps a bounded per-corpus set, and applies
the existing stable final order.

This prevents one corpus or one source file from monopolizing a result set
without creating a second score.

Each pointer preserves:

```text
repository
source_sha
source_blob_sha
source_path
work_id
segment_id
sequence_no
evidence_class
text_role
witness
rank / score / match_reasons
```

### Evidence path

```text
question
→ supported hypotheses
→ production locator
→ source pointers
→ open pinned upstream file/blob
→ read context
→ provenance / relations / variants
→ witness-separated synthesis
```

The pointer itself is not evidence.

If a source file is too large for a normal Connector file fetch, the agent can
use the pointer's `source_blob_sha` or the shard/source Git blob when supported.

### Coverage

Connector production v1 gives broad finite routing for Latin/romanized lemma
keys and exact work identifiers. It can still reach CBETA and other Chinese
sources when those sources are pointers for a supported term or exact ID.

It does not claim exhaustive arbitrary Chinese-substring lookup. Missing remote
coverage must be reported rather than filled from model memory.

## 6. Historical measurement artifacts

These remain for reproducibility/auditing, not ordinary production routing:

- `remote/pointer-poc/` — historical proof of concept;
- `remote/pointer-benchmark/` — 500-query scale benchmark;
- `remote/pointer-compact-poc/` — compact-serialization experiment.

Measurements established that:

- full-pointer compact dedup was larger than the benchmark;
- source/work metadata tables did not clear the project's storage-benefit
  threshold;
- exporting the full CJK trigram vocabulary would be impractical and
  semantically inappropriate.

Those experiments are closed unless a future real acceptance failure justifies
reopening them.

## 7. Answer / Provenance Layer

Every research finding should carry:

`corpus | repository | source_path | work_id | segment_id | source_sha |
evidence_class | text_role | witness`

Answers keep witnesses separate, distinguish quotation from interpretation, and
state uncertainty.

Local failure:

**không đủ dữ liệu trong corpus hiện tại**

Connector failure:

**không đủ dữ liệu trong remote corpus export hiện tại**

## Data flow

```text
Pinned immutable source repositories
          │
          ▼
Deterministic local parsers
          │
          ▼
SQLite records + FTS + relations + variants + lemmas
          │
          ├──────── Local CLI research
          │
          └──────── Production pointer export
                         │
                         ▼
                Remote locator repository
                         │
                         ▼
                  GitHub Connector
                         │
                         ▼
              Pinned upstream source
                         │
                         ▼
          Provenance-first research answer
```
