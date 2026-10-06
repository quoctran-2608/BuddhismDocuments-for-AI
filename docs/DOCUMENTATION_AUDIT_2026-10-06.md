# Biên bản kiểm toán tài liệu — 06/10/2026

> **Trạng thái: LỊCH SỬ / SNAPSHOT KIỂM TOÁN**
>
> Tài liệu này ghi lại kết quả Giai đoạn 8 của vòng chuẩn hóa tài liệu. Nó không
> phải nguồn chuẩn cho runtime về sau. Trạng thái hiện hành phải lấy từ các nguồn
> được quy định trong `docs/DOCUMENTATION_GOVERNANCE.md`.

## 1. Mục tiêu kiểm toán

Kiểm repository theo ba góc nhìn:

1. **Người mới hoàn toàn** — có thể hiểu dự án là gì, vì sao tồn tại, đang làm
   được gì và chưa làm gì hay không;
2. **Lập trình viên tiếp quản** — có xác định được nguồn chuẩn, kiến trúc,
   requirement, test, ADR và nơi thay đổi code/config hay không;
3. **AI researcher** — có biết phải tìm bằng chứng thế nào, mở nguồn nào, giữ
   provenance/witness ra sao và khi nào phải fail-closed hay không.

Mục tiêu thoát của vòng kiểm toán:

- 0 mâu thuẫn quan trọng chưa xử lý;
- 0 trường hợp MỤC TIÊU/TƯƠNG LAI bị mô tả như HIỆN HÀNH;
- 0 kiến trúc POC/legacy bị mô tả như runtime production trong tài liệu hiện hành;
- 0 nhập nhằng quan trọng về nguồn chuẩn theo miền;
- các tài liệu lịch sử phải tự nhận diện rõ là LỊCH SỬ.

## 2. Kết quả theo góc nhìn người mới

**Đạt.**

Đường đọc ngắn nhất:

```text
README.md
→ docs/PROJECT_SPEC.md
```

`README.md` hiện là cửa vào ngắn gọn, giải thích:

- mục tiêu dự án;
- ba vai trò repository chính / remote / upstream;
- Local mode và Connector mode;
- pointer không phải bằng chứng;
- truy xuất hiện hành không phải vector/embedding semantic RAG;
- ranh giới HIỆN HÀNH / MỤC TIÊU / TƯƠNG LAI.

`docs/PROJECT_SPEC.md` có thể đọc độc lập để nắm toàn cảnh:

- bài toán;
- người dùng;
- nguyên tắc bất biến;
- cấu trúc repository;
- hai chế độ thực thi;
- SQLite/FTS;
- production locator;
- evidence hierarchy;
- SC ↔ CBETA;
- năng lực và giới hạn hiện hành;
- lớp kiểm chứng MỤC TIÊU;
- hướng TƯƠNG LAI.

Các dữ kiện máy đọc dễ thay đổi như source SHA, runtime root, schema và production
summary vẫn phải lấy từ nguồn chuyên biệt thay vì coi Project Spec là bản sao cấu
hình.

## 3. Kết quả theo góc nhìn lập trình viên tiếp quản

**Đạt.**

Đường đọc chuẩn:

```text
docs/DOCUMENTATION_GOVERNANCE.md
→ docs/ARCHITECTURE.md
→ docs/REQUIREMENTS.md
→ docs/ACCEPTANCE.md
→ docs/adr/
```

Nguồn chuẩn đã được tách theo miền:

- source + SHA → `manifest.json`;
- corpus/evidence class/profile → `config/corpus-sources.json`;
- runtime Connector → `config/remote-corpus.json`;
- schema → `schema/corpus-index.sql`;
- retrieval/ranking behavior → `tools/corpus_research/` + tests;
- CLI → `docs/CLI.md` + `tools/corpus_research/cli.py`;
- production artefact → manifest/summary trong repo remote;
- luật nghiên cứu → `AGENTS.md`;
- hành vi AI → `SKILL.md`;
- giao thức Connector → `docs/REMOTE_AGENT.md`;
- lý do quyết định kiến trúc → `docs/adr/`.

Bộ ADR hiện có 9 hồ sơ, bao phủ:

1. pinned upstream sources;
2. SQLite là artefact dẫn xuất;
3. truy xuất từ vựng nhạy theo ngôn ngữ;
4. metadata quan hệ khác bằng chứng câu chữ;
5. tách repo chính và repo artefact remote;
6. locator tiền tính toán, không phụ thuộc GitHub Code Search;
7. pointer-only, không sao chép raw text;
8. không materialize `terms/cjk` từ trigram vocabulary;
9. dùng chung retrieval ranking nhưng rank không phải thẩm quyền học thuật.

## 4. Kết quả theo góc nhìn AI researcher

**Đạt.**

Đường đọc chuẩn:

```text
AGENTS.md
→ .codex/skills/buddhist-corpus-research/SKILL.md
→ docs/REMOTE_AGENT.md      # nếu dùng Connector
→ docs/SC_CBETA_BRIDGE.md   # nếu nghiên cứu nhánh SC ↔ CBETA
```

`AGENTS.md` và `docs/SC_CBETA_BRIDGE.md` đã được chuyển sang tiếng Việt trong
vòng kiểm toán cuối, không thay đổi luật hay số liệu kỹ thuật.

Các guardrail chính vẫn giữ nguyên:

- kiến thức mô hình chỉ tạo giả thuyết tìm kiếm;
- pointer không phải textual evidence;
- database dẫn xuất không phải nguồn gốc;
- `evidence_class`, `text_role`, `witness` phải tách riêng;
- relation/bridge không tự chứng minh wording;
- không tự tạo tương đương đa ngôn ngữ từ trí nhớ mô hình;
- discovery corpus không âm thầm thay primary witness;
- không đủ evidence thì fail-closed.

## 5. Trạng thái requirement và nghiệm thu

Tại snapshot này:

- tổng requirement có mã: **69**;
- requirement HIỆN HÀNH: **46**;
- requirement MỤC TIÊU: **23**;
- ID requirement trùng: **0**;
- requirement không có mặt trong `ACCEPTANCE.md`: **0**.

Nhóm MỤC TIÊU gồm:

- Evidence Record;
- quotation verification;
- Atomic Claim + `claim_type`;
- claim–evidence verification;
- source independence;
- counterevidence;
- Final Claim Gate;
- Research Run.

Các năng lực này vẫn **CHƯA TRIỂN KHAI đầy đủ**.

## 6. Test hiện hữu

Bộ test đã kiểm kê gồm 45 test method trong 6 file:

- `tests/test_acceptance.py`: 9;
- `tests/test_cbeta_resolver.py`: 10;
- `tests/test_cjk_substring_search.py`: 1;
- `tests/test_normalization.py`: 7;
- `tests/test_remote_access.py`: 15;
- `tests/test_text_roles.py`: 3.

Tất cả 45 tên là duy nhất. Các tên test được `docs/ACCEPTANCE.md` gọi đích danh
đã được đối chiếu với file test thực tế.

**Lưu ý:** vòng chuẩn hóa/kiểm toán tài liệu này không chạy lại test suite; nó
không thay code/schema/config/tests nên không tuyên bố một lần chạy test mới.

## 7. Runtime Connector đã đối chiếu

`config/remote-corpus.json` tại snapshot khai báo:

```text
repository: quoctran-2608/BuddhismDocuments-for-AI-remote
branch: main
root_path: remote/pointer-production-v1
mode: pointer_production_v1
```

Production manifest xác nhận:

- `artifact_kind = pointer_production_v1`;
- `proof_of_concept = false`;
- `raw_text_exported = false`;
- namespace materialize: `terms/latin`, `ids`;
- `terms/cjk` không materialize.

Production summary tại snapshot:

- Latin keys: 26.547;
- identifier keys: 32.498;
- tổng keys: 59.045;
- query có kết quả: 58.643;
- query không kết quả: 402;
- pointer: 706.011;
- file artefact: 517;
- `raw_text_field_count = 0`;
- `source_blob_sha_null_count = 0`.

Các con số này là snapshot; nguồn chuẩn về sau vẫn là production
manifest/summary ở repo remote.

## 8. Lịch sử và legacy

`progress.md` được giữ nguyên giá trị lịch sử và có cảnh báo ngay đầu file:

- POC;
- benchmark;
- số test cũ;
- branch/root path cũ;
- `prompt.txt` đã bị xóa;
- các cụm “hiện tại” bên trong phải hiểu theo mốc lịch sử.

`docs/CORPUS_SURVEY.md` được giữ là snapshot ngày 22/09/2026 và đã được dịch sang
tiếng Việt trong vòng kiểm toán cuối.

`docs/CLI.md` và `docs/REMOTE_AGENT.md` vẫn nhắc một số path POC/legacy vì cần
phân biệt chúng với production, nhưng các path đó được gắn nhãn lịch sử/legacy và
không được dùng như runtime hiện hành.

## 9. Các sửa lỗi đáng chú ý trước khi chốt

Trong các vòng double-check và Giai đoạn 8 đã sửa các vấn đề sau:

- taxonomy trạng thái từ ba lớp thành bốn lớp thống nhất:
  HIỆN HÀNH / MỤC TIÊU / TƯƠNG LAI / LỊCH SỬ;
- relation/bridge metadata không tự động là Evidence Record, nhưng có thể là
  evidence cho claim `relationship` sau khi source metadata được mở và xác minh;
- `run_id` bắt buộc trong Research mode, có thể trống trong Quick mode nếu chưa
  tạo Research Run;
- tách vòng đời Atomic Claim (`candidate/accepted/rejected`) khỏi mức support
  (`DIRECT/STRONG/WEAK/UNSUPPORTED/CONTRADICTED`);
- bổ sung `claim_type` thành requirement chính thức;
- Việt hóa các tài liệu hiện hành còn lệch ngôn ngữ.

## 10. Kết luận kiểm toán

Tại snapshot 06/10/2026, không còn phát hiện **mâu thuẫn trọng yếu chưa xử lý**
trong hệ tài liệu chuẩn.

Các tiêu chí thoát Giai đoạn 8 được đánh giá:

| Tiêu chí | Kết quả |
|---|---|
| Mâu thuẫn quan trọng chưa xử lý | 0 phát hiện |
| MỤC TIÊU/TƯƠNG LAI bị viết như HIỆN HÀNH | 0 phát hiện |
| POC/legacy bị viết như production hiện hành | 0 phát hiện trong tài liệu chuẩn |
| Nhập nhằng quan trọng về nguồn chuẩn | 0 phát hiện |
| Requirement thiếu ánh xạ Acceptance | 0 |
| ADR thiếu khỏi ADR index | 0 |
| Link nội bộ README/ADR index bị hỏng | 0 tại lúc kiểm |

Những hạn chế **có chủ đích và đã được ghi rõ** không phải lỗi tài liệu:

- production v1 không có arbitrary exhaustive remote CJK substring lookup;
- lớp Evidence/Claim Verification vẫn là MỤC TIÊU;
- Deep Connector fallback chỉ là TƯƠNG LAI;
- `progress.md` và các benchmark/POC cũ là lịch sử.
