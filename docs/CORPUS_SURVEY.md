# Local Corpus Survey

Survey date: 2026-09-22. The survey used only the checked-out files and pinned
Git objects. No remote source was consulted.

## Global finding

The repository had no global cross-corpus search index. It contained a few
source-specific indexes and tools, chiefly under `third-party/pali-canon` and
`pts/pts-archive`, but no common record schema or retrieval interface spanning
all 13 submodules.

SQLite 3.45.1 with FTS5 is available locally. The implemented layer therefore
uses Python's standard library and SQLite FTS5; it needs no package download.

## Source observations

| Source | Observed schema/IDs | Role | Limits found locally |
|---|---|---|---|
| SuttaCentral Bilara | JSON maps `segment_id → string`; cognate root, translation, comment, variant files; e.g. `mn1:1.1` | Canonical/root and structured translations | Comments may contain external links; variants use a compact human-readable syntax |
| SuttaCentral sc-data | `new_parallels.json`, structure, language, school, editions, dictionaries | Relationship and metadata graph | A parallel edge does not establish wording; some documented structure files are deprecated |
| CBETA XML P5 | TEI, root `xml:id` such as `T01n0001`, `lb @n`, `pb`, `mulu`, `app/lem/rdg`, witness sigla | Authoritative structured Chinese edition | Large files; gaiji and apparatus require source-aware parsing |
| CBETA BM_u8 | Plain lines beginning with CBETA work/page/line IDs | Fast plain-text witness | Markup is compact legacy syntax; XML P5 is richer for verification |
| 84000 TEI | TEI titles, publication `idno`, `bibl @key=toh...`, milestones and folio metadata | Authoritative structured English translation | Some files are placeholders with little/no body text |
| 84000 RDF | One RDF file per Toh. work; work, instance, translation, sameAs, labels | Metadata/relationship data | Metadata only; not a textual witness |
| 84000 Translation Memory | TMX and JSON `tus`; Tibetan/English, folio, passage ID, creation method | Alignment/discovery | Documented v3 machine alignment is approximate; v4 is manually corrected |
| OpenPecha C0A2DD042 | Line-aligned `WORK-lang.txt` pairs and CSV catalogs | Multilingual Tibetan alignment/discovery | Mixed upstream sources; line alignment is not an independent canonical edition |
| BuddhaNexus Pāli | Segment maps; original and computationally cut forms; SC-compatible IDs for canonical material | Discovery/segmentation | Commentary sources differ; cut segments are computational derivatives |
| BuddhaNexus Chinese | gzipped JSON sentence segments with CBETA-like line IDs | Discovery/segmentation | Derived from CBETA; verify against CBETA XML where available |
| BuddhaNexus Sanskrit | JSON machine segmentation, with a small checked subset | Discovery/segmentation | README explicitly warns of many errors |
| PTS archive | 53 page-marked text exports; optional recovered SQLite and apparatus | Auxiliary/reference | README warns of typos, mojibake, missing/mislabelled volumes, and ROTA-vs-PTS page distinctions |
| pali-canon | Canonical JSON, token lemmas/morphology, five-witness critical apparatus | Derived lemma/critical evidence | Critical text is editorial/derived; lemmatization can contain wrong analyses and must not replace witnesses |

## Tokenization decision

One tokenizer is not enough for all scripts.

- FTS5 `unicode61 remove_diacritics 0` preserves Pāli/Sanskrit diacritics and
  provides token search for space-delimited scripts.
- A diacritic-folded representation supports explicit fallback searches but is
  ranked below exact Unicode matches.
- A compact normalized representation supports substring retrieval for Chinese
  and Tibetan without pretending that Unicode61 performs linguistic word
  segmentation.
- Lemmas are stored in a separate table and copied into a searchable lemma
  representation. Only corpus-provided lemmas count as lemma evidence.
- Relations and alignments live in separate tables; they are not concatenated
  into text.

## Evidence classification

The implementation uses:

- `canonical_root`
- `authoritative_structured`
- `metadata_relationship`
- `parallel_alignment`
- `computational_segmented`
- `derived_critical_lemma`
- `auxiliary_reference`

These names are carried into every indexed record and provenance response.
