# CLI Guide

All commands are local-only and print their main result as JSON to stdout.
Build progress and errors go to stderr.

```bash
# Verify 13 local sources and index state
bin/buddhist-corpus status

# Build an incremental core index
bin/buddhist-corpus build --profile core

# Add discovery/alignment sources to the same database
bin/buddhist-corpus build --profile discovery

# Index all supported local sources
bin/buddhist-corpus build --profile all

# Checkpoint one expensive source without rebuilding FTS yet
bin/buddhist-corpus build --profile core --source cbeta-bm --defer-fts

# After all source checkpoints, rebuild both derived search indexes
bin/buddhist-corpus build --profile core

# Search and inspect
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus search "如是我聞" --language lzh
bin/buddhist-corpus search "anicca" --language pli --context 2 --with-provenance
bin/buddhist-corpus context --record-id 123 --window 3
bin/buddhist-corpus evidence --record-id 123 --context 2
bin/buddhist-corpus work UT22084-001-001
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus resolve T02n0125:0563a14..0563a27
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus compare mn1 T01n0001
bin/buddhist-corpus provenance --record-id 123

# Legacy full-record export; do not use this for the pointer-only connector path
bin/buddhist-corpus export-remote --output remote/corpus

# Small raw-text-free pointer proof of concept for GitHub Connector access
bin/buddhist-corpus export-remote-pointers \
  --query anicca \
  --query dukkha \
  --query jhāna \
  --query nibbāna \
  --query Mahākassapa \
  --query 無常 \
  --query 如是我聞 \
  --query 苦 \
  --query 空 \
  --identifier T02n0099 \
  --identifier T01n0001 \
  --output remote/pointer-poc

# Deterministic 500-key measurement of the same pointer pipeline.
# This creates a separate benchmark artifact; it does not replace the POC.
bin/buddhist-corpus export-pointer-benchmark \
  --latin-keys 200 \
  --cjk-keys 200 \
  --identifier-keys 100 \
  --output remote/pointer-benchmark

# Compact-serialization measurement of the existing 500-query benchmark.
# It reads the benchmark artifact; it does not rerun retrieval or resample keys.
bin/buddhist-corpus export-pointer-compact-poc \
  --benchmark remote/pointer-benchmark \
  --output remote/pointer-compact-poc

# Read-only repetition and byte analysis of the existing benchmark.
# This prints JSON only; it does not create or replace an artifact.
bin/buddhist-corpus analyze-pointer-repetition \
  --benchmark remote/pointer-benchmark

# Read-only key-universe count and production-scale extrapolation.
# It does not generate a production locator or create a remote artifact.
bin/buddhist-corpus analyze-pointer-key-universe \
  --benchmark remote/pointer-benchmark

# Read the existing CJK FTS5 trigram vocabulary through a TEMP fts5vocab table.
# It never persists a vocabulary table, scans raw text, or creates a locator.
bin/buddhist-corpus analyze-cjk-fts-vocabulary \
  --benchmark remote/pointer-benchmark

# Generate or resume the production v1 raw-text-free runtime locator.
# Only terms/latin and exact original ids are materialized; no CJK trigram export.
bin/buddhist-corpus export-pointer-production-v1 \
  --output remote/pointer-production-v1 \
  --limit 20 \
  --workers 4
```

Without `--context` or `--with-provenance`, `search` keeps its previous output
shape and ranking. Context is restricted to the same corpus, work ID, and source
path, ordered by `sequence_no`. `evidence` bundles the target record, neighboring
records, provenance, and locally indexed variants.

`export-remote` is the legacy full-record export and is not the pointer-only
connector path. `export-remote-pointers` reads the existing SQLite database
only during generation. It emits a small deterministic locator whose ranked
pointers identify a GitHub repository, pinned source SHA, repository-relative
source path, Git blob SHA when the pinned local object is available, work/segment
identifiers, evidence class, text role, and witness. It never writes `raw_text`.
For each query, it fetches candidates with the existing ranking, keeps the
best-ranked distinct `(work_id, source_path)` candidate within each corpus, then
retains up to `--limit` candidates per corpus. See
[GitHub Connector Research Access](REMOTE_AGENT.md).

`export-pointer-benchmark` measures this unchanged pointer pipeline on a
deterministic sample of real local index keys: Latin/romanized keys come from
`lemmas.lemma`; CJK keys are trigrams from a stable 5,000-row `lzh`/`zh`
`records.raw_text` sample; identifiers come from stable per-corpus
`records.work_id` row samples. It creates `manifest.json`,
`benchmark-queries.json`, locator JSONL, and `benchmark-summary.json` under a
separate output path. The default safe cap is 32 MiB; it refuses to replace the
target artifact if a generated benchmark exceeds that cap.

`export-pointer-compact-poc` reads the exact existing benchmark query list and
locator rows. It stores full source/segment metadata once in a pointer table
under a stable SHA-256 `pointer_id`; locator rows keep only `pointer_id`,
`rank`, `score`, and `match_reasons`. It verifies that resolving every reference
reconstructs the benchmark rows exactly. This is a serialization POC, not a
production locator change.

`analyze-pointer-repetition` is read-only. It measures the existing benchmark's
metadata repetition for source-file, indexed-source, work, source-plus-work, and
full static segment identities; it also reports byte fragments and in-memory
source-table simulations. It does not call SQLite retrieval, resample queries,
or write under `remote/`.

`analyze-pointer-key-universe` counts the known existing namespaces from the
SQLite index and uses the committed 500-query benchmark's category-specific
bytes/query and pointers/query for extrapolation. It reads Latin/romanized keys
from `lemmas.lemma` and identifiers from `records.work_id`. The current CJK
runtime index is a contentless FTS5 trigram index without a vocabulary table, so
the command reports that its finite CJK key universe is unavailable rather than
scanning text or creating a vocabulary index. It never generates a locator.

`analyze-cjk-fts-vocabulary` uses this SQLite TEMP-only statement:

```sql
CREATE VIRTUAL TABLE temp.cjk_vocab_measurement
USING fts5vocab(main, records_cjk_fts, 'row');
```

The three-argument form addresses the FTS5 table in the `main` schema; the
virtual table itself lives only for the read-only connection. The command
measures the current finite trigram vocabulary, document-frequency distribution,
top tokens, and deterministic lexical sample directly from FTS5. It does not
read `records.raw_text`, rebuild FTS, or create an artifact. “CJK token” means
an indexed trigram containing at least one character in the runtime CJK ranges;
such a trigram can also contain non-CJK characters.

`export-pointer-production-v1` is the production runtime export. It first
validates the approved finite universe: 26,547 normalized non-CJK
`lemmas.lemma` keys and 32,498 **original-spelling** `records.work_id` keys.
It fails before writing output if either count differs. It keeps `Dhp` and `dhp`
as separate exact identifier keys. The command uses the existing term search,
identifier scoring, corpus balancing, collapse, final rank order, pointer
format, and per-corpus limit. It intentionally does not materialize
`terms/cjk`, whose FTS trigrams are local retrieval infrastructure rather than a
Buddhist-term vocabulary.

Generation writes durable JSONL rows to
`remote/.pointer-production-v1.production-v1.staging/`; the final production
path is atomically replaced only after every key is complete and
`manifest.json`/`production-summary.json` are valid. A subsequent command
resumes the marked stage. `--workers` runs independent existing retrieval calls
in separate read-only processes, while the parent writes deterministic locator
rows in production-key order.

Returned records and `provenance` expose both `evidence_class` and `text_role`.
The first describes source authority; the second distinguishes root text, main
translation, heading, translator comment, translation note, and other content
roles. Do not present comments or notes as though they were the main scripture.

`core` uses lighter full-text representations where appropriate. For Chinese,
it indexes CBETA BM_u8 for broad retrieval. Use `all`, or open the matching
CBETA XML P5 file directly, when critical apparatus and TEI markup are needed.
Core records are bounded source chunks whose `segment_id` and `relation_ids`
retain the source range for direct verification.

Normal builds rebuild both the ordinary Unicode FTS index and the versioned CJK
trigram candidate index from existing `records`. An older database reports the
CJK substring index as unavailable until this rebuild completes. Chinese
middle-substring coverage requires at least three usable CJK characters; no
whole-table fallback is used for one- or two-character queries. This does not
claim Tibetan substring coverage.

See [SuttaCentral Āgama → CBETA bridge](SC_CBETA_BRIDGE.md) for the distinction
between parallel evidence, identifier metadata, and a CBETA textual witness.

Use another derived database with the global `--db` option:

```bash
bin/buddhist-corpus --db /tmp/corpus.sqlite3 build --profile acceptance
```

Do not place a database inside a source submodule.
