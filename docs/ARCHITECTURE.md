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

Ở thời điểm tài liệu này được đồng bộ, config khai báo:

```text
repository: quoctran-2608/BuddhismDocuments-for-AI-remote
branch: main
root_path: remote/pointer-production-v1
mode: pointer_production_v1
```

Nếu config thay đổi, config là nguồn chuẩn chứ không phải giá trị sao chép trong
tài liệu này.

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

## 14. Những gì chưa thuộc kiến trúc hiện hành

Các năng lực sau đang ở trạng thái MỤC TIÊU, chưa được mô tả như implementation
hiện tại:

- Evidence Record chuẩn hóa;
- quote verification có trạng thái;
- Atomic Claim;
- claim–evidence verification;
- counterevidence pass bắt buộc;
- Final Claim Gate;
- Research Run Manifest.

Đặc tả mục tiêu nằm trong `docs/PROJECT_SPEC.md`,
`docs/REQUIREMENTS.md` và `docs/ACCEPTANCE.md`.

## 15. Luồng dữ liệu tổng thể

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
