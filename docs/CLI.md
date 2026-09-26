# CLI Guide

All CLI commands are local-only. Build progress/errors go to stderr; primary
results are emitted as JSON to stdout.

## Normal local research

```bash
# Verify 13 local sources and index state
bin/buddhist-corpus status

# Build
bin/buddhist-corpus build --profile core
bin/buddhist-corpus build --profile discovery
bin/buddhist-corpus build --profile all

# Checkpoint one expensive source without rebuilding FTS yet
bin/buddhist-corpus build --profile core --source cbeta-bm --defer-fts

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
```

Without `--context` or `--with-provenance`, `search` keeps its normal output
shape and ranking. Context stays inside the same corpus, work ID, and source
path, ordered by `sequence_no`.

## Production GitHub Connector artifact

Generate/resume production v1 locally:

```bash
bin/buddhist-corpus export-pointer-production-v1 \
  --output remote/pointer-production-v1 \
  --limit 20 \
  --workers 4
```

The exporter validates:

```text
terms/latin: 26,547 normalized non-CJK lemma keys
ids:         32,498 exact original work_id keys
total:       59,045
```

It keeps exact identifier spelling (`Dhp` and `dhp` are distinct), reuses the
existing search/ranking/corpus-balancing/collapse semantics, writes no
`raw_text`, and publishes only after the complete staged artifact is valid.

The production artifact is the normal GitHub Connector runtime. See
[GitHub Connector Research Access](REMOTE_AGENT.md).

### Production bucket protocol

Connector agents should not use this CLI section as a substitute for the skill,
but the storage rule is:

```text
term key:
NFC → casefold → collapse whitespace

identifier:
exact original spelling

bucket:
first 2 lowercase hex chars of SHA-256(exact UTF-8 production key)

paths:
locator/terms/latin/<bucket>/part-000001.jsonl
locator/ids/<bucket>/part-000001.jsonl
```

There is no production `terms/cjk` namespace.

## Historical/development pointer export

The small pointer POC is retained only for development history:

```bash
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
```

Do not use `pointer-poc` for ordinary Connector research when
`config/remote-corpus.json` declares production v1.

## Benchmark and measurement commands

```bash
# Deterministic 500-key measurement
bin/buddhist-corpus export-pointer-benchmark \
  --latin-keys 200 \
  --cjk-keys 200 \
  --identifier-keys 100 \
  --output remote/pointer-benchmark

# Historical compact serialization experiment
bin/buddhist-corpus export-pointer-compact-poc \
  --benchmark remote/pointer-benchmark \
  --output remote/pointer-compact-poc

# Read-only repetition analysis
bin/buddhist-corpus analyze-pointer-repetition \
  --benchmark remote/pointer-benchmark

# Read-only production key-universe measurement
bin/buddhist-corpus analyze-pointer-key-universe \
  --benchmark remote/pointer-benchmark

# Read-only CJK FTS vocabulary measurement
bin/buddhist-corpus analyze-cjk-fts-vocabulary \
  --benchmark remote/pointer-benchmark
```

The CJK vocabulary analyzer uses only a TEMP FTS5 vocabulary view:

```sql
CREATE VIRTUAL TABLE temp.cjk_vocab_measurement
USING fts5vocab(main, records_cjk_fts, 'row');
```

The CJK result is a low-level trigram token universe, not a Buddhist
terminology dictionary. It is not materialized in production v1.

## Legacy export

```bash
bin/buddhist-corpus export-remote --output remote/corpus
```

This full-record export is legacy and is **not** the production Connector path.

## Build/index notes

`core` uses bounded source chunks where appropriate. For Chinese it indexes
CBETA BM_u8 for broad local retrieval. `all` includes the more granular CBETA
XML P5 apparatus and all supported sources.

Normal builds rebuild both the ordinary Unicode FTS index and the versioned CJK
trigram candidate index. Chinese local substring search requires at least three
usable CJK characters. This local behavior must not be confused with Connector
production coverage.

Use another derived database with the global `--db` option:

```bash
bin/buddhist-corpus --db /tmp/corpus.sqlite3 build --profile acceptance
```

Do not place a database inside a source submodule.

## Test suite

```bash
PYTHONPATH=tools python3 -m unittest discover -s tests -v
```
