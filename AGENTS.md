# Buddhist Corpus Research Rules

This file is the highest-level rule set for every agent and every research task
in this repository.

## Central rule

> Model knowledge may propose a search hypothesis; only repository evidence may establish a research finding.

Nói cách khác: kiến thức sẵn có của AI chỉ được phép gợi ý hướng tìm; chỉ bằng
chứng trong repository này mới được phép xác lập kết luận nghiên cứu.

## Hard offline / local-only mode

Research in this repository is **strictly offline**.

- Do not use Web Search, a browser, `curl`, `wget`, network APIs, or remote
  scholarly sources.
- Do not run `git fetch`, `git pull`, `git clone`, `git submodule update`, or
  any command that can obtain missing data from a remote.
- Do not call the GitHub API as a substitute for local data.
- Do not download models, packages, package data, dictionaries, or corpora.
- Use only files already present in this checkout and standard tools already
  installed locally.
- If a submodule, Git object, LFS object, or expected source file is absent,
  stop that line of inquiry and report: **không đủ dữ liệu trong corpus hiện
  tại**. Never repair the gap by downloading.

## Immutable source layer

The 13 submodule directories listed in `.gitmodules` are immutable
sources-of-origin.

- Never edit, normalize, format, regenerate, or commit inside a source
  submodule.
- Put parsers, indexes, caches, reports, and all other derived artifacts
  outside the submodules.
- Derived artifacts must be reproducible from pinned local source commits.
- Large generated databases belong under `derived/` and are not
  source-of-truth.

Before research, run:

```bash
bin/buddhist-corpus status
```

Treat a missing source or a SHA mismatch as a provenance failure.

## Evidence hierarchy

Use the strongest available witness. A discovery source must not silently
replace a primary witness.

1. **Canonical/root textual witnesses** — source-language root texts and
   identifiable edition witnesses, such as SuttaCentral Bilara roots and
   individual Pāli witnesses.
2. **Authoritative structured editions** — editions preserving stable textual
   structure and apparatus, such as CBETA TEI P5 and 84000 TEI.
3. **Metadata/relationship data** — SuttaCentral parallels and structure,
   84000 RDF/Toh. metadata. These establish relationships, not textual wording.
4. **Parallel/alignment corpora** — 84000 Translation Memory and OpenPecha.
   Use for alignment evidence and discovery; verify wording in an available
   source edition.
5. **Computationally segmented corpora** — BuddhaNexus. Use for candidate
   discovery. Return to CBETA, SuttaCentral, or another appropriate source
   witness whenever one is locally available.
6. **Derived critical/lemmatized data** — `third-party/pali-canon`. Use lemma,
   morphology, collation, and variant data as derived analysis. Name its base
   witnesses and do not present a reconstructed or selected reading as an
   unqualified primary witness.
7. **Auxiliary/reference data** — PTS archive and other noisy reference
   exports. State known quality limits.

When evidence classes conflict, show the conflict. Do not promote the lower
class merely because it is easier to search.

## Required provenance

Every research finding must be traceable to:

- corpus/source name;
- repository-relative source path;
- work/text identifier;
- segment, line, folio, Toh., CBETA, or equivalent identifier when present;
- pinned source commit SHA;
- evidence class, text role, and witness/edition when relevant.

`evidence_class` and `text_role` answer different questions:

- `evidence_class` describes source authority/provenance;
- `text_role` describes what the indexed text is within that source.

Do not quote or synthesize a translator comment or translation note as though
it were root/scriptural text. Comments and notes can be useful authoritative
evidence, but their role must remain explicit.

If variants differ, state which witness says what. If provenance is incomplete,
label the statement as a hypothesis or omit it.

## Cross-language and cross-tradition guardrails

- Do not invent Pāli ↔ Sanskrit ↔ Chinese ↔ Tibetan equivalence from model
  memory.
- A cross-language equation becomes evidence only when a local alignment,
  relationship record, dictionary, shared canonical identifier, or other
  repository record supports it.
- Model knowledge may generate terms to test, but unconfirmed terms must not
  appear as findings.
- Do not harmonize different traditions automatically. Report similarities,
  differences, variants, witness scope, and uncertainty.

## Required research workflow

Use the local CLI before recursively scanning raw files:

```bash
bin/buddhist-corpus search "query"
bin/buddhist-corpus context --record-id ID
bin/buddhist-corpus work WORK_ID
bin/buddhist-corpus parallels WORK_OR_SEGMENT_ID
bin/buddhist-corpus resolve CBETA_WORK_OR_TAISHO_RANGE
bin/buddhist-corpus variants WORK_OR_SEGMENT_ID
bin/buddhist-corpus compare ID1 ID2
bin/buddhist-corpus provenance --record-id ID
```

Read raw files after retrieval when checking context, markup, apparatus, or
source fidelity.

For SuttaCentral Chinese parallels, keep three evidence steps separate:
SuttaCentral parallel relation → local SuttaCentral-to-CBETA identifier bridge
→ resolved CBETA textual witness. A bridge is metadata, not proof of textual
identity.

### Term research

Use this order:

1. exact form;
2. Unicode-normalized/case-normalized form;
3. corpus-provided lemma and morphology;
4. internally attested spelling variants;
5. context around occurrences;
6. local aligned or parallel texts.

Do not infer unattested variants.

### Topic/concept research

Never stop at semantic or keyword search. Iterate:

`seed evidence → internal terminology → occurrences → context → structure →
parallels → variants → independent witnesses → synthesis`

Record which step supplied each claim.

### Candidate discovery

BuddhaNexus, OpenPecha, and Translation Memory normally produce candidates,
not final textual proof. Resolve candidate identifiers back to stronger local
sources when possible. If that resolution is unavailable, state the limit.

## Answer contract

A research answer must:

1. distinguish findings from search hypotheses;
2. cite repository evidence with the required provenance fields;
3. identify variants and independent witnesses rather than flattening them;
4. describe uncertainty and missing coverage;
5. end with **không đủ dữ liệu trong corpus hiện tại** for any claim the local
   repository cannot establish.

Internet knowledge and model memory must never become an implicit fourteenth
source.
