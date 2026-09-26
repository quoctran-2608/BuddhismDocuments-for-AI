# GitHub Connector Research Access

This document is the production runtime guide for a ChatGPT/GitHub Connector
agent. Ordinary Connector research should use the production locator declared
by the main repository, not the historical POC or benchmark artifacts.

## 1. Repository roles

### Main repository

`quoctran-2608/BuddhismDocuments-for-AI`

Contains:

- research rules and skill;
- canonical architecture;
- source mappings;
- production locator configuration;
- local build/retrieval/export code.

The main repository is the architecture source-of-truth.

### Remote locator repository

Read `config/remote-corpus.json` in the main repository to discover it.

The current production config declares:

```text
repository: quoctran-2608/BuddhismDocuments-for-AI-remote
branch: main
root_path: remote/pointer-production-v1
mode: pointer_production_v1
```

The remote repository is a deterministic derived access artifact. It is not a
textual source-of-truth.

### Upstream source repositories

Every locator pointer names the original source repository and a pinned
`source_sha`, `source_path`, and normally `source_blob_sha`.

Research evidence comes from these pinned upstream files after they are opened
and read.

## 2. Normal production workflow

A Connector agent should execute this automatically when the user asks a
Buddhist research question:

```text
user question
→ read main skill/config
→ generate supported hypotheses
→ route each key to a production locator shard
→ read ranked pointers
→ select relevant corpora/witnesses
→ open pinned upstream source files
→ read context/provenance
→ inspect relations/variants when needed
→ synthesize
```

Do not ask the user to tell you which of the two project repositories to use.

## 3. Production namespaces

Production v1 materializes:

```text
terms/latin  → 26,547 normalized non-CJK lemma keys
ids          → 32,498 exact original work_id keys
```

Total:

```text
59,045 production keys
```

It intentionally does **not** materialize `terms/cjk`.

The measured local CJK FTS contains tens of millions of low-level trigrams;
those tokens are search-index infrastructure, not a Buddhist terminology
dictionary. Do not construct or assume a remote CJK trigram namespace.

## 4. Key normalization and bucket routing

### Term key

Production term normalization is:

```text
Unicode NFC
→ casefold
→ collapse all whitespace runs to one ASCII space
```

Do not remove diacritics for bucket routing.

### Identifier key

Use the exact original identifier spelling. Do not normalize or casefold it.

### Bucket

For either namespace:

```text
SHA-256(exact UTF-8 production key)
→ first 2 lowercase hexadecimal characters
```

Paths:

```text
<root_path>/locator/terms/latin/<bucket>/part-000001.jsonl
<root_path>/locator/ids/<bucket>/part-000001.jsonl
```

Read the JSONL row whose `key` exactly equals the requested production key.

Verified example:

```text
anicca
→ bucket 45
→ remote/pointer-production-v1/locator/terms/latin/45/part-000001.jsonl
```

Do **not** recursively inspect all 256 buckets.
Do **not** depend on GitHub Code Search; generated locator JSONL may not be
indexed there.

If a shard is too large for the normal file-content endpoint, fetch/read the
shard by its Git blob SHA.

## 5. Locator row and pointer semantics

Each locator row contains a key and an ordered `pointers` list.

Pointers preserve:

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

Production selection reuses the existing local ranking, searches each corpus,
collapses duplicate `(corpus, work_id, source_path)` candidates, keeps a
bounded per-corpus set, then applies the existing stable final order.

This is candidate selection only.

A pointer does **not** prove that its source says anything. Open the source.

## 6. Source verification

For each pointer used in the answer:

1. open the named `repository` at `source_sha`;
2. open `source_path` or use `source_blob_sha` if needed;
3. locate `work_id`, `segment_id`, or the indicated sequence/line;
4. read enough surrounding material for context;
5. preserve `evidence_class`, `text_role`, and `witness`;
6. quote or paraphrase only what was actually read.

When a discovery pointer is computational/alignment data, use it to find a
stronger witness when one is available.

If a compressed/binary source cannot be rendered, do not claim its unseen
wording.

## 7. Research from a short natural-language prompt

The user does not need to supply Pāli/Sanskrit search keys.

For a Vietnamese/English/topic request:

1. infer a small set of plausible Pāli/Sanskrit/romanized hypotheses;
2. normalize each term and try production routing;
3. keep hypotheses distinct from findings;
4. after opening real sources, use terminology actually attested there to
   refine the search;
5. for comparative research, sample relevant corpora separately rather than
   taking only the globally highest pointers.

Where relevant, prioritize canonical/authoritative readable witnesses such as
SuttaCentral Bilara roots, CBETA BM/TEI, and 84000 TEI. Discovery corpora do not
silently replace them.

For an explicit work ID, route directly through `ids`.

## 8. CJK and Chinese-source research

Connector production v1 has no arbitrary Chinese-term namespace.

This does **not** mean CBETA is absent. A supported Latin/Indic hypothesis can
route to CBETA pointers, and an exact CBETA/work identifier can route through
`ids`.

However, do not claim exhaustive Chinese substring search in Connector mode.
If a question requires a Chinese-only term that cannot be reached through a
supported key or identifier, state the coverage limit.

Do not use historical benchmark CJK trigrams as production keys.

## 9. Research modes

### Quick term / exact ID

Start with the highest-priority candidates in the requested scope, open the
strong source files, and verify context.

### Topic / comparative / cross-corpus

Group pointers by relevant corpus and preserve priority within each corpus.
Open a useful sample of independent/strong witnesses before synthesis.

Do not allow one large corpus to consume the entire evidence budget.

### User-restricted scope

If the user asks for CBETA only, one Nikāya, T99, one Vinaya, one language, or
another explicit scope, stay inside it unless permission to broaden is given.

## 10. Evidence hierarchy and scholarly guardrails

Pointer rank is a file-opening priority, not scholarly authority.

Prefer, where applicable:

1. canonical/root textual witnesses;
2. authoritative structured editions;
3. metadata/relationship evidence;
4. parallel/alignment data;
5. computational segmentation;
6. derived critical/lemma data;
7. auxiliary/reference data.

Keep source witnesses separate. Do not treat translator comments/notes as
scriptural root text. Do not infer cross-language identity from model memory.

## 11. Failure behavior

If a key is absent, try other justified supported hypotheses or exact IDs.

Do not:

- scan every locator shard;
- invent a CJK production namespace;
- silently fall back to internet sources;
- turn locator metadata into textual evidence.

If the current remote export cannot establish the requested claim, say:

**không đủ dữ liệu trong remote corpus export hiện tại**

and briefly name the missing coverage.

## 12. Historical and measurement artifacts

The following may remain in the remote repository but are not the normal
runtime when config says `pointer_production_v1`:

- `remote/pointer-poc/` — historical pointer proof of concept;
- `remote/pointer-benchmark/` — deterministic 500-key scale benchmark;
- `remote/pointer-compact-poc/` — serialization experiment.

Use them only when explicitly auditing development history or measurements.

## 13. Local generation reference

Production v1 is generated locally with:

```bash
bin/buddhist-corpus export-pointer-production-v1 \
  --output remote/pointer-production-v1 \
  --limit 20 \
  --workers 4
```

The exporter writes ranked pointers, not copied `raw_text`, and validates the
approved finite production key universe before final publish.
