# Kiến trúc hiện hành của hệ thống nghiên cứu corpus Phật học

> Trạng thái: **HIỆN HÀNH**
>
> Phạm vi: mô tả kiến trúc kỹ thuật đang được triển khai. Tài liệu này không mô
> tả roadmap tương lai và không dùng các benchmark lịch sử làm trạng thái hiện
> tại.

Nguồn chuẩn liên quan:

- đặc tả cấp dự án: `docs/PROJECT_SPEC.md`;
- luật nghiên cứu: `AGENTS.md`;
- yêu cầu: `docs/REQUIREMENTS.md`;
- runtime Connector: `config/remote-corpus.json`;
- schema: `schema/corpus-index.sql`;
- lý do quyết định kiến trúc: `docs/adr/`.

## 1. Tổng quan

Hệ thống có hai đường thực thi dùng chung một hợp đồng bằng chứng:

```text
13 upstream repositories ở pinned SHA
          │
          ▼
deterministic parsers
          │
          ▼
SQLite + FTS + relations + variants + lemmas
          │
          ├──────────────► local CLI research
          │
          └──────────────► production pointer export
                                   │
                                   ▼
                         remote locator repository
                                   │
                                   ▼
                           GitHub Connector
                                   │
                                   ▼
                           pinned upstream source
                                   │
                                   ▼
                      câu trả lời có provenance
```

Local mode và Connector mode khác nhau ở cơ chế truy xuất, nhưng cùng giữ:

- tầng nguồn được ghim;
- phân cấp bằng chứng;
- tách nhân chứng;
- provenance;
- pointer không phải bằng chứng;
- fail-closed khi dữ liệu không đủ.

## 2. Tầng nguồn

Hệ thống quản lý 13 repository/submodule upstream làm nguồn gốc bất biến trong
phạm vi một build/nghiên cứu.

Nguồn chuẩn:

- danh sách repo và commit SHA: `manifest.json`;
- corpus, repository GitHub, `evidence_class`, vai trò và build profile:
  `config/corpus-sources.json`.

Một nguồn thiếu hoặc SHA không khớp là lỗi provenance.

Không sửa dữ liệu bên trong source repository như một phần của pipeline nghiên
cứu.

## 3. Tầng chỉ mục cục bộ

`bin/buddhist-corpus build` tạo database dẫn xuất tại
`derived/corpus.sqlite3`.

Schema hiện có:

- `source_state`;
- `search_index_state`;
- `works`;
- `records`;
- `relations`;
- `variants`;
- `lemmas`;
- `records_fts`;
- `records_cjk_fts`.

Database là artefact dẫn xuất, không phải nguồn chuẩn của câu chữ.

### 3.1. Record và provenance

Record văn bản giữ tối thiểu các trường phục vụ nghiên cứu:

- corpus;
- ngôn ngữ;
- work/segment ID;
- nội dung;
- các dạng normalized/folded/compact khi phù hợp;
- source path;
- source SHA;
- `evidence_class`;
- `text_role`;
- `witness`;
- sequence;
- relation IDs.

### 3.2. Build gia tăng

Trạng thái build gắn với:

- source component;
- pinned source SHA;
- parser version;
- phạm vi build/profile;
- phiên bản chỉ mục tìm kiếm.

Component không đổi được bỏ qua.

Profiles hiện hành:

- `core`: nguồn cốt lõi/thẩm quyền chính và dữ liệu lemma;
- `discovery`: alignment/segmented corpora;
- `all`: toàn bộ 13 nguồn;
- `acceptance`: mẫu thật cố định dùng cho kiểm thử.

## 4. Tầng truy xuất

Hệ thống hiện tại dùng truy xuất từ vựng, không phải vector/embedding semantic
search.

Các tín hiệu chính:

- exact match;
- chuẩn hóa Unicode/case;
- bỏ dấu có chủ đích;
- compact Unicode matching;
- SQLite FTS5;
- lemma do corpus cung cấp;
- evidence-class weighting;
- stable identifiers;
- provenance quality;
- deterministic tie-break.

Logic xếp hạng cốt lõi được dùng chung cho local retrieval và production pointer
generation.

Rank chỉ quyết định ứng viên nào nên mở trước; không quyết định giá trị học
thuật của kết luận.

## 5. Truy xuất CJK

`records_cjk_fts` là FTS5 contentless trigram index cho `lzh`/`zh`.

Mục tiêu:

- sinh ứng viên cho chuỗi con nằm giữa đoạn Hán văn dài;
- tránh phụ thuộc tokenizer theo từ cho CJK;
- vẫn đưa ứng viên qua kiểm tra/xếp hạng chung.

Giới hạn:

- truy vấn cần ít nhất ba ký tự CJK hữu dụng để có đường trigram này;
- không hứa hẹn arbitrary middle-substring coverage cho truy vấn 1–2 ký tự;
- vocabulary trigram là hạ tầng index, không phải từ điển thuật ngữ.

## 6. Mô hình bằng chứng

### 6.1. `evidence_class`

Mô tả thẩm quyền/nguồn gốc của corpus.

Các lớp hiện hành:

1. `canonical_root`;
2. `authoritative_structured`;
3. `metadata_relationship`;
4. `parallel_alignment`;
5. `computational_segmented`;
6. `derived_critical_lemma`;
7. `auxiliary_reference`.

### 6.2. `text_role`

Mô tả bản chất nội dung của record, ví dụ:

- `root_text`;
- `translation_main`;
- `translation_heading`;
- `translator_comment`;
- `translation_note`;
- `alignment_text`;
- `computational_text`;
- `derived_text`;
- `auxiliary_text`.

### 6.3. `witness`

Mô tả edition/nhân chứng cụ thể.

Ba khái niệm trên không được gộp thành một “độ tin cậy” duy nhất.

## 7. Quan hệ, song hành và dị bản

Relations được lưu riêng khỏi text records.

Một relation chỉ chứng minh loại quan hệ mà dữ liệu biểu diễn; nó không tự xác
nhận câu chữ.

Ví dụ SuttaCentral ↔ CBETA:

```text
SuttaCentral parallel relation
→ SuttaCentral-to-CBETA identifier bridge
→ resolved CBETA textual witness
```

Ba bước này phải giữ riêng.

Variants được lưu riêng, có thể mang lemma/reading/witnesses/type/confidence và
provenance của nguồn khảo dị.

## 8. CLI cục bộ

Các lệnh nghiên cứu chính:

- `status`;
- `build`;
- `search`;
- `context`;
- `work`;
- `parallels`;
- `resolve`;
- `variants`;
- `compare`;
- `provenance`;
- `evidence`.

Chi tiết giao diện nằm trong `docs/CLI.md`.

## 9. Tầng GitHub Connector

### 9.1. Vai trò repository

```text
repo chính
quoctran-2608/BuddhismDocuments-for-AI
    │
    │ config/remote-corpus.json
    ▼
repo locator dẫn xuất
quoctran-2608/BuddhismDocuments-for-AI-remote
    │
    │ production pointers
    ▼
pinned upstream source repositories
```

Vai trò:

- repo chính: kiến trúc, phương pháp, config, schema, code, tests, docs;
- repo remote: artefact định tuyến dẫn xuất;
- upstream repos: bằng chứng thực sự.

Repo remote không phải corpus thứ 14.

### 9.2. Runtime

Runtime hiện hành phải được đọc từ `config/remote-corpus.json`.

Đọc `repository`, `branch`, `root_path`, `mode` trực tiếp từ
[config/remote-corpus.json](../config/remote-corpus.json).
Host chốt locator commit cho phiên; không lấy branch/root/SHA từ bản sao văn xuôi.

## 10. Production locator

Production v1 materialize:

```text
terms/latin
ids
```

Không materialize `terms/cjk`.

### 10.1. Term key

```text
Unicode NFC
→ casefold
→ collapse whitespace
```

Không bỏ dấu khi tính bucket.

### 10.2. Identifier key

Giữ nguyên spelling gốc; không casefold.

### 10.3. Bucket

```text
SHA-256(exact UTF-8 production key)
→ hai ký tự hex thường đầu tiên
→ locator/<namespace>/<bucket>/part-000001.jsonl
```

Không phụ thuộc GitHub Code Search để định tuyến.

### 10.4. Pointer

Pointer production giữ metadata cần để mở nguồn, gồm các trường như:

- rank/score/match reasons;
- record/corpus;
- repository;
- source SHA;
- source blob SHA;
- source path;
- indexed source path;
- work/segment/sequence;
- `evidence_class`;
- `text_role`;
- `witness`.

Pointer production không chứa `raw_text`.

## 11. Đường bằng chứng trong Connector

```text
câu hỏi
→ giả thuyết tìm kiếm có căn cứ
→ production locator
→ pointer
→ mở pinned upstream file/blob
→ đọc đủ context
→ provenance / relations / variants khi cần
→ tổng hợp tách nhân chứng
```

Pointer không được dùng như quotation.

Nếu source không thể mở hoặc route không đủ coverage, Connector phải fail-closed
thay vì hoàn thiện câu trả lời bằng trí nhớ mô hình.

## 12. Coverage Connector hiện hành

Production v1 có coverage hữu hạn cho:

- Latin/romanized lemma keys được materialize;
- exact original work IDs.

Nó có thể dẫn tới CBETA hoặc nguồn Hán văn khi source đó xuất hiện trong pointer
của một term/ID được hỗ trợ.

Nó **không** tuyên bố arbitrary exhaustive Chinese-substring lookup.

Lý do không materialize CJK trigram vocabulary được ghi trong
`docs/adr/0008-do-not-materialize-cjk-trigram-vocabulary-in-production.md`.

## 13. Quan hệ với Research Skill

`.codex/skills/buddhist-corpus-research/SKILL.md` là quy trình hành động của AI.

Nó không phải đặc tả kiến trúc thứ hai. Khi cần chi tiết về:

- kiến trúc → tài liệu này;
- luật nghiên cứu → `AGENTS.md`;
- Connector runtime → `docs/REMOTE_AGENT.md`;
- config hiện hành → `config/remote-corpus.json`.

## 14. Lớp kiểm chứng 2.0 và ranh giới tích hợp

Mã A–E đã gộp vào main tại `57db982274e267218594ae5ca463bd2a42d2be02`
(11/10/2026); retrieval/index/ranking/CLI 1.0 giữ nguyên.

| Lớp | Trách nhiệm hiện hành | Ranh giới |
|---|---|---|
| A — verification | Source/pin/blob/location/quote với reader độc lập | VERIFIED chỉ là bằng chứng, không cấp claim assessment |
| B — claims | Claim subject/assessment, final gate, revision history | Assessment cần host; JSON accepted/approved không mang quyền; Research guard đóng |
| C — counterevidence | Per-step scope/receipt/hit–A, dependency và quyết định qua host | SEARCHED không là phản bác ngữ nghĩa; thiếu dependency giữ uncertain |
| D — research_run/store | DB riêng, snapshots/version/history, report và decision | Stored observations cần fresh checks; finalized/RECORDED không cấp publication |
| E — adapters/CLI | LocalHost, LocalResearch, ConnectorHost, ba resolver và CLI riêng | Chỉ nối capability host; không xây nguồn/ranking/approval mới |

LocalHost đọc Git nguồn ghim và giải Bilara/CBETA/84000; LocalResearch tạo draft
và chạy C operations hỗ trợ qua retrieval. Parallels/variants chưa có A resolver
đầy đủ. ConnectorHost không tự gọi mạng/SQLite/shell: ứng dụng nối công cụ được
cấp quyền vào `locator_fetch`/`source_fetch`, pin config/locator, đọc nguồn đầy đủ
và gắn identity/blob. Pointer/range/flags từ transport không chọn capability.

Quick đi đường retrieval → A → bằng chứng/giới hạn, không gọi B/C/D. Research
đi qua candidate/assessment/C/D/review và currentness checks, còn thiếu semantic
approval xác thực; B/D giữ cửa công bố đóng. Lịch sử/hash/report không thay
fresh nguồn/assessment hoặc host authority. Chưa nghiệm thu đủ 13 resolver,
Work, toàn Connector hoặc chất lượng Research học thuật. PRD/DESIGN giữ các
mục tiêu còn thiếu; [USAGE](v2/USAGE.md) mô tả API hiện hành,
[ACCEPTANCE](v2/ACCEPTANCE.md) và [evidence](v2/evidence/README.md) ghi mức kiểm thực.

Bảng môi trường × quy trình và sơ đồ Quick/Research: [AI_ONBOARDING](AI_ONBOARDING.md).

## 15. Luồng dữ liệu nền 1.0 (2.0 nối sau mở nguồn)

```text
Pinned upstream repositories
          │
          ▼
Deterministic local parsers
          │
          ▼
SQLite records + FTS + relations + variants + lemmas
          │
          ├──────── Local CLI
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
            Provenance-first answer
```
