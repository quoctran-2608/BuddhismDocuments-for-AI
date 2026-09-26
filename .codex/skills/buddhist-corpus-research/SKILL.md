---
name: buddhist-corpus-research
description: Provenance-first Buddhist corpus research in local SQLite mode or GitHub Connector production mode.
---

# Buddhist Corpus Research

Read and obey the repository root `AGENTS.md` before using this skill.

## Goal

Turn a short user request about a Buddhist term, passage, work ID, or topic into
a repository-evidenced answer without requiring the user to know the corpus
layout.

The core contract is:

```text
model knowledge → search hypothesis only
repository evidence → research finding
```

A locator pointer is never evidence by itself.

## Choose the execution mode automatically

### Local mode

Use local mode when the CLI and SQLite index are available.

Start with:

```bash
bin/buddhist-corpus status
```

Then use the CLI workflow documented below.

### GitHub Connector mode

Use Connector mode when GitHub repositories are connected but local
shell/SQLite access is unavailable.

Do **not** ask the user to explain how the two project repositories fit
together. Discover the runtime from the repository:

1. open `config/remote-corpus.json` in
   `quoctran-2608/BuddhismDocuments-for-AI`;
2. use its `repository`, `branch`, `root_path`, and `mode`;
3. open `<root_path>/manifest.json` and
   `<root_path>/locator/manifest.json` in the declared remote repository;
4. use the production locator to find candidate source pointers;
5. open the original upstream repository named by each pointer at the pinned
   `source_sha` / `source_blob_sha`;
6. read the relevant source context before making a finding.

The current production config points to:

```text
main repo:
quoctran-2608/BuddhismDocuments-for-AI

remote locator repo:
quoctran-2608/BuddhismDocuments-for-AI-remote

production root:
remote/pointer-production-v1
```

Always read the config rather than hardcoding these values in case a later
version changes them.

## Production Connector routing protocol

Production v1 materializes exactly two namespaces:

```text
terms/latin  → normalized non-CJK lemma keys
ids          → exact original work_id spelling
```

It does **not** materialize a general `terms/cjk` namespace. The local CJK
FTS trigram index is build/retrieval infrastructure, not a production dictionary
of Buddhist terms.

### 1. Decide whether the lookup is an identifier or a term

Use `ids` for an exact work/text identifier such as a canonical work ID.
Preserve its original spelling exactly. Do not casefold identifiers; e.g.
`Dhp` and `dhp` are distinct production keys.

Use `terms/latin` for Pāli, Sanskrit, romanized, and other non-CJK term
hypotheses that can be expressed as production lemma keys.

For Vietnamese/English/CJK topic questions, the model may propose likely
Pāli/Sanskrit/romanized terms as **search hypotheses only**. Do not present
those cross-language equations as findings until repository evidence supports
them.

### 2. Normalize a term key exactly

For `terms/latin`, apply the production normalization used by
`corpus_research.model.normalize()`:

```text
Unicode NFC
→ Unicode casefold
→ split on whitespace
→ join with one ASCII space
```

Do not strip diacritics for bucket routing.

For `ids`, use the exact original identifier string with no normalization.

### 3. Calculate the bucket

The manifest declares:

```text
SHA-256 of exact UTF-8 production key
→ first two lowercase hex characters
```

Then open:

```text
<root_path>/locator/terms/latin/<bucket>/part-000001.jsonl
```

or:

```text
<root_path>/locator/ids/<bucket>/part-000001.jsonl
```

Find the JSONL row whose `key` exactly equals the production key.

Do not recursively scan all locator shards. Do not depend on GitHub Code Search;
generated JSONL may not be indexed there.

Verified production example:

```text
key: anicca
SHA-256 bucket prefix: 45

remote/pointer-production-v1/
  locator/terms/latin/45/part-000001.jsonl
```

### 4. If a shard is too large for a normal file fetch

Use the Git blob for that shard when the Connector exposes its blob SHA.
This is normal for production JSONL files and does not change the research
method.

### 5. Read the locator row

A row contains:

```text
key
query_kind
pointer_count
pointers[]
```

Each pointer includes ranking fields plus source provenance such as:

```text
rank
score
match_reasons
record_id
corpus
repository
source_sha
source_blob_sha
source_path
indexed_source_path
work_id
segment_id
sequence_no
evidence_class
text_role
witness
```

The production exporter already balances candidates by corpus and collapses
duplicate `(corpus, work_id, source_path)` groups. Preserve pointer order
within each corpus when selecting files to open.

### 6. Open source evidence, not just the pointer

For every claim you want to use:

1. open `repository` at the pointer's `source_sha`;
2. open `source_path`, or fetch `source_blob_sha` when appropriate;
3. locate `work_id` / `segment_id` / `sequence_no`;
4. read enough surrounding source context to interpret the passage;
5. check `evidence_class`, `text_role`, and `witness`;
6. only then treat the wording as evidence.

If a compressed or binary discovery source cannot be rendered in Connector
mode, do not claim unseen wording from it. Prefer a stronger readable witness
when available.

### 7. Topic and comparative research

For a topic, do not stop at one hypothesis or one corpus.

Use this loop:

```text
user topic
→ 2–6 plausible supported hypotheses
→ production locator rows
→ group pointers by relevant corpus
→ open strong source witnesses
→ collect terminology actually attested in source
→ test additional supported hypotheses when useful
→ inspect parallels/variants/independent witnesses
→ synthesize agreements, differences, and limits
```

Do not spend the entire candidate budget on the first globally ranked corpus.

Where relevant, prefer primary/authoritative witnesses such as SuttaCentral
Bilara roots, CBETA BM/TEI, and 84000 TEI over discovery-only corpora. Use
BuddhaNexus, Translation Memory, OpenPecha, and similar corpora mainly to locate
or relate evidence, then return to a stronger source witness when possible.

### 8. User-restricted scope

If the user asks for only a Nikāya, CBETA, T99, one Vinaya, one language, or
another explicit scope, respect that scope. Do not broaden it without
permission.

### 9. Unsupported or missing production key

If a production key is absent:

- try other justified supported hypotheses;
- use terminology found in already-opened evidence to refine hypotheses;
- do not scan all shards;
- do not invent a CJK production namespace;
- do not silently switch to general internet research.

If the available production locator cannot establish the requested claim,
state:

**không đủ dữ liệu trong remote corpus export hiện tại**

and explain the coverage limitation briefly.

## Ranking interpretation

Pointer rank decides which source files to open first. It does not decide:

- which tradition is correct;
- which witness is historically earlier;
- which source is doctrinally authoritative;
- whether one witness is enough;
- whether a cross-language equation is true.

Those judgments follow evidence hierarchy, user scope, source context, text
role, witness separation, and explicit repository relationships.

GitHub Connector routing is not a byte-for-byte reproduction of SQLite FTS
candidate generation. It is a deterministic production access path to selected
source candidates.

## Research modes

### Term research

Local mode:

```bash
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus context --record-id RECORD_ID
bin/buddhist-corpus variants mn1
```

Connector mode follows the production routing protocol above.

In either mode:

1. exact/normalized form;
2. corpus-provided lemma or attested spelling;
3. context;
4. variants;
5. parallels/alignment only after evidence is anchored.

### Passage research

Local mode:

```bash
bin/buddhist-corpus search "如是我聞" --language lzh
bin/buddhist-corpus provenance --record-id RECORD_ID
```

In Connector mode, there is no arbitrary CJK production locator. Use a supported
identifier or justified romanized/Indic hypothesis to reach candidate sources.
If that route cannot establish the passage, state the production coverage
limit instead of pretending exhaustive Chinese search.

### Concept/topic research

Never synthesize from one keyword hit. Iterate:

```text
seed evidence
→ internally attested terminology
→ occurrences
→ context/work structure
→ parallels
→ variants
→ independent witnesses
→ synthesis
```

### Parallel-text research

Local mode:

```bash
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus compare ID1 ID2
```

Keep SuttaCentral relation evidence, identifier bridges, and resolved CBETA
textual witnesses separate.

### Variant research

Local mode:

```bash
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus variants mn1
```

Keep lemma, reading, witness sigla, confidence, and source path distinct.

### Cross-tradition comparison

Keep witnesses separate. Establish cross-language equivalence only from
repository alignment/relationship evidence; model-generated equivalents remain
hypotheses until confirmed.

## Local CLI quick reference

If the index is absent:

```bash
bin/buddhist-corpus build --profile core
```

Use `--profile discovery` for alignment/segmented sources and `--profile all`
for all supported sources.

Useful commands:

```bash
bin/buddhist-corpus search "anicca" --language pli --context 2 --with-provenance
bin/buddhist-corpus evidence --record-id RECORD_ID --context 2
bin/buddhist-corpus context --record-id RECORD_ID --window 3
bin/buddhist-corpus work WORK_ID
bin/buddhist-corpus parallels WORK_OR_SEGMENT_ID
bin/buddhist-corpus resolve CBETA_WORK_OR_TAISHO_RANGE
bin/buddhist-corpus variants WORK_OR_SEGMENT_ID
bin/buddhist-corpus compare ID1 ID2
bin/buddhist-corpus provenance --record-id RECORD_ID
```

## Historical/measurement artifacts

These are not the normal Connector runtime:

- `remote/pointer-poc/` — historical proof of concept;
- `remote/pointer-benchmark/` — 500-key scale measurement;
- `remote/pointer-compact-poc/` — serialization experiment.

Do not route ordinary research through them when
`config/remote-corpus.json` declares `pointer_production_v1`.

## Answer contract

Answer in the user's requested language and clearly separate:

1. **Finding** — what the source evidence supports.
2. **Evidence by witness/corpus** — do not merge independent witnesses.
3. **Parallels/variants** — relationship type and meaningful differences.
4. **Interpretation** — your synthesis, clearly distinguished from quotation.
5. **Confidence and limits**.
6. **Provenance** for every cited item:
   `corpus | repository | source_path | work_id | segment_id | source_sha | evidence_class | text_role | witness`.

Do not present pointer metadata as a quotation. Quote only text actually opened
in the original source. If the source evidence cannot establish a claim, fail
closed rather than completing it from model memory.
