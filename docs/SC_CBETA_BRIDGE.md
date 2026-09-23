# SuttaCentral Āgama → CBETA Identifier Bridge

This bridge uses only pinned local files under:

`suttacentral/sc-data/html_text/lzh/**/*.html`

It does not index the HTML prose as a primary witness. It extracts only:

- the SuttaCentral `<article id>`;
- an explicit local CBETA link;
- local Taishō line anchors such as `t0563a14`.

## Relation types

### `suttacentral_cbeta:work`

Maps a SuttaCentral UID to an explicitly linked normalized CBETA work ID.

Example:

```text
ea9.7 → T02n0125
```

### `suttacentral_cbeta:line_range`

Maps a SuttaCentral UID to the minimum/maximum local Taishō anchors when the
mirror identifies exactly one CBETA work.

Example:

```text
ea9.7 → T02n0125:0563a14..0563a27
```

`details_json` preserves every extracted anchor, the start/end anchors, the
anchor count, and the fact that the mapping came from an explicit local CBETA
link. Both relation types are `metadata_relationship`; neither proves textual
identity.

## Resolution

```bash
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus resolve T02n0125:0563a14..0563a27
```

`resolve ea9.7` follows only explicit indexed bridge relations. A direct CBETA
work/range may also be resolved. Both forms resolve overlap against local
`cbeta-bm` and/or `cbeta-tei` records. The returned CBETA record remains a
separate primary witness with its own source path and pinned source SHA.

## Local coverage and unresolved cases

The pinned `html_text/lzh` tree contains 4,714 HTML mirrors:

- 2,779 contain an article UID, an explicit CBETA link, and Taishō anchors;
- 1,928 contain an article UID and Taishō anchors but no explicit CBETA link;
- 7 contain an article UID but neither an explicit CBETA link nor Taishō
  anchors.

The 1,935 mirrors without an explicit CBETA identifier are deliberately not
mapped. Some filenames resemble Taishō identifiers, but deriving a work ID from
the filename would violate the local-evidence rule. These remain unresolved
until a local file provides an explicit identifier.

If a mirror contains multiple explicit CBETA work links, work mappings are
kept, but one shared Taishō range is not assigned to all of them.

Resolver coverage for the current core index is recorded after the build and
verified in the integration checks:

- 2,648 of 2,779 explicit line ranges overlap a local CBETA BM_u8 core record;
- 129 ranges have no primary record in the core index:
  - 128 belong to five works that have local XML P5 files but are not part of
    the core BM_u8 index: `T02n0150a`, `T22n1422a`, `T22n1422b`,
    `T32n1670a`, and `T32n1670b`;
  - 1 range (`t780b → T17n0780b`) has no matching local CBETA XML filename;
- 2 ranges identify a work present in BM_u8, but the local mirror anchors do
  not overlap that work's BM_u8 range:
  - `lzh-sarv-bu-pm-2 → T23n1436:0200b18..0206b19`;
  - `t511 → T14n0551:0779a03..0781a19`.

The bridge preserves these mappings as metadata but does not invent corrected
work IDs or line ranges. Research using an unresolved bridge must report
**không đủ dữ liệu trong corpus hiện tại** for the missing primary resolution.

CBETA suffix letters are matched case-insensitively because local source IDs
use both forms, for example `T02n0150A` and normalized bridge ID `T02n0150a`.
No work number or line range is inferred when it is absent or inconsistent.
