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

# After all source checkpoints, rebuild the shared FTS index
bin/buddhist-corpus build --profile core

# Search and inspect
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus search "如是我聞" --language lzh
bin/buddhist-corpus context --record-id 123 --window 3
bin/buddhist-corpus work UT22084-001-001
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus compare mn1 T01n0001
bin/buddhist-corpus provenance --record-id 123
```

`core` uses lighter full-text representations where appropriate. For Chinese,
it indexes CBETA BM_u8 for broad retrieval. Use `all`, or open the matching
CBETA XML P5 file directly, when critical apparatus and TEI markup are needed.
Core records are bounded source chunks whose `segment_id` and `relation_ids`
retain the source range for direct verification.

Use another derived database with the global `--db` option:

```bash
bin/buddhist-corpus --db /tmp/corpus.sqlite3 build --profile acceptance
```

Do not place a database inside a source submodule.
