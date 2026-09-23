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
bin/buddhist-corpus context --record-id 123 --window 3
bin/buddhist-corpus work UT22084-001-001
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus resolve T02n0125:0563a14..0563a27
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus compare mn1 T01n0001
bin/buddhist-corpus provenance --record-id 123
```

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
