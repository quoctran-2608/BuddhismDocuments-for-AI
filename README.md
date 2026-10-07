# Hạ tầng nghiên cứu corpus Phật học cho AI

Repository này xây dựng một hạ tầng nghiên cứu Phật học **ưu tiên bằng chứng và
khả năng truy nguyên nguồn** trên 13 repository upstream được ghim bằng commit
SHA.

> Kiến thức sẵn có của mô hình chỉ được dùng để đề xuất giả thuyết tìm kiếm.
> Chỉ bằng chứng trong repository mới được dùng để xác lập kết luận nghiên cứu.

Đây không còn chỉ là một kho “raw data”. Repository hiện gồm:

- tầng nguồn bất biến;
- bộ parser và chỉ mục SQLite/FTS cục bộ;
- CLI nghiên cứu;
- mô hình provenance, nhân chứng, dị bản và quan hệ;
- GitHub Connector dùng production pointer locator;
- hệ tài liệu yêu cầu, nghiệm thu và ADR;
- hướng nâng cấp lớp kiểm chứng claim-by-claim đang được đặc tả nhưng chưa triển
  khai đầy đủ.

## 1. Kiến trúc trong 30 giây

```text
13 repository upstream ở commit SHA đã ghim
        │
        ├── local parsers
        │      ↓
        │   SQLite + FTS + relations + variants + lemmas
        │      ↓
        │   CLI nghiên cứu cục bộ
        │
        └── production pointer export
               ↓
quoctran-2608/BuddhismDocuments-for-AI-remote
               ↓
GitHub Connector
               ↓
mở lại pinned upstream source
               ↓
câu trả lời có provenance
```

Ba vai trò phải được giữ riêng:

- **repo chính** `quoctran-2608/BuddhismDocuments-for-AI`: kiến trúc, luật
  nghiên cứu, config, schema, code, tests và docs;
- **repo remote** `quoctran-2608/BuddhismDocuments-for-AI-remote`: artefact
  dẫn xuất để định tuyến Connector, không phải corpus Phật học thứ 14;
- **13 repo upstream**: nơi chứa bằng chứng văn bản/metadata thực sự.

Runtime Connector hiện hành phải luôn được đọc từ
[`config/remote-corpus.json`](config/remote-corpus.json), không hard-code từ
README.

## 2. Hai chế độ nghiên cứu

### Local mode

Local mode hoạt động offline nghiêm ngặt.

```bash
# Kiểm nguồn và trạng thái chỉ mục
bin/buddhist-corpus status

# Xây chỉ mục
bin/buddhist-corpus build --profile core
bin/buddhist-corpus build --profile discovery
bin/buddhist-corpus build --profile all

# Truy xuất và kiểm nguồn
bin/buddhist-corpus search "anicca" --language pli --context 2 --with-provenance
bin/buddhist-corpus search "如是我聞" --language lzh
bin/buddhist-corpus evidence --record-id RECORD_ID --context 2
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus compare mn1 T01n0001
```

Chi tiết: [Hướng dẫn CLI](docs/CLI.md).

### GitHub Connector mode

Khi AI không có SQLite local:

```text
câu hỏi
→ giả thuyết tìm kiếm có căn cứ
→ production locator
→ pointer đã xếp hạng
→ pinned upstream source
→ ngữ cảnh + provenance
→ quan hệ/dị bản khi cần
→ tổng hợp tách nhân chứng
```

Pointer chỉ là chỉ dẫn mở nguồn, **không phải bằng chứng câu chữ**.

Chi tiết vận hành:
[GitHub Connector Research Access](docs/REMOTE_AGENT.md).

## 3. Truy xuất hiện hành

Hệ thống hiện tại **không phải** vector/embedding semantic RAG.

Truy xuất cục bộ dùng:

- exact match;
- chuẩn hóa Unicode;
- bỏ dấu như một bước fallback riêng;
- SQLite FTS5 `unicode61`;
- lemma/morphology do corpus cung cấp;
- FTS5 trigram riêng cho truy vấn chuỗi con Hán văn `lzh`/`zh`;
- xếp hạng có trọng số theo lớp bằng chứng và phá hòa xác định.

CJK trigram là hạ tầng sinh ứng viên, không phải từ điển thuật ngữ.

## 4. Production Connector hiện hành

Production v1 hiện dùng hai namespace:

```text
terms/latin
ids
```

Không có production `terms/cjk`.

Artefact hiện hành được khai báo trong `config/remote-corpus.json` và nằm ở
repo remote. Con số production, trường pointer và invariant phải lấy từ
production manifest/summary của artefact đó.

Các nguyên tắc quan trọng:

- không phụ thuộc GitHub Code Search để định tuyến;
- pointer production không chứa `raw_text`;
- identifier giữ nguyên spelling gốc;
- bucket dùng SHA-256 trên exact production key;
- rank chỉ là thứ tự ưu tiên mở nguồn, không phải thẩm quyền học thuật.

## 5. 13 nguồn upstream

Danh sách repo, đường dẫn local và commit SHA chuẩn nằm trong
[`manifest.json`](manifest.json).

Vai trò corpus và `evidence_class` nằm trong
[`config/corpus-sources.json`](config/corpus-sources.json).

Các họ nguồn chính gồm:

- SuttaCentral;
- CBETA;
- 84000;
- OpenPecha;
- BuddhaNexus;
- PTS archive;
- dữ liệu Pāli dẫn xuất phục vụ lemma, hình thái học và khảo dị.

Không dùng README làm nguồn chuẩn cho SHA hay kích thước nguồn.

## 6. Tài liệu nên đọc

| Nhu cầu | Tài liệu |
|---|---|
| Hiểu toàn bộ dự án | [PROJECT_SPEC.md](docs/PROJECT_SPEC.md) |
| Biết tài liệu nào có thẩm quyền về việc gì | [DOCUMENTATION_GOVERNANCE.md](docs/DOCUMENTATION_GOVERNANCE.md) |
| Luật nghiên cứu bắt buộc | [AGENTS.md](AGENTS.md) |
| Kiến trúc kỹ thuật hiện hành | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Yêu cầu hiện hành | [REQUIREMENTS.md](docs/REQUIREMENTS.md) |
| Nghiệm thu hiện hành | [ACCEPTANCE.md](docs/ACCEPTANCE.md) |
| Bộ tài liệu nâng cấp 2.0 | [docs/v2/README.md](docs/v2/README.md) |
| Đề bài / PRD 2.0 | [docs/v2/PRD.md](docs/v2/PRD.md) |
| Thiết kế kiểm chứng 2.0 | [docs/v2/DESIGN.md](docs/v2/DESIGN.md) |
| Yêu cầu 2.0 | [docs/v2/REQUIREMENTS.md](docs/v2/REQUIREMENTS.md) |
| Nghiệm thu 2.0 | [docs/v2/ACCEPTANCE.md](docs/v2/ACCEPTANCE.md) |
| Lý do các quyết định kiến trúc | [ADR index](docs/adr/README.md) |
| CLI | [CLI.md](docs/CLI.md) |
| GitHub Connector | [REMOTE_AGENT.md](docs/REMOTE_AGENT.md) |
| Cầu nối SuttaCentral ↔ CBETA | [SC_CBETA_BRIDGE.md](docs/SC_CBETA_BRIDGE.md) |
| Khảo sát corpus tại mốc 22/09/2026 | [CORPUS_SURVEY.md](docs/CORPUS_SURVEY.md) |
| Lịch sử phát triển và benchmark | [progress.md](progress.md) |

## 7. Trạng thái phát triển

### HIỆN HÀNH

Đã có:

- 13 nguồn được ghim;
- SQLite/FTS local;
- truy xuất theo ngôn ngữ;
- provenance;
- `evidence_class`, `text_role`, `witness`;
- quy trình quan hệ/song hành/dị bản;
- GitHub Connector production locator;
- fail-closed khi corpus không đủ dữ liệu.

### MỤC TIÊU — chưa triển khai đầy đủ

Hướng nâng cấp tiếp theo bổ sung:

```text
Evidence Record
→ kiểm chứng trích dẫn
→ Atomic Claim
→ kiểm chứng claim–evidence
→ phản chứng
→ Final Claim Gate
→ Research Run
```

Chi tiết nằm trong
[Bộ tài liệu 2.0](docs/v2/README.md),
[PRD 2.0](docs/v2/PRD.md),
[Thiết kế 2.0](docs/v2/DESIGN.md),
[Yêu cầu 2.0](docs/v2/REQUIREMENTS.md) và
[Nghiệm thu 2.0](docs/v2/ACCEPTANCE.md).

### TƯƠNG LAI — chưa thuộc v1

Chỉ sau v1 mới xem xét deep Connector fallback/job từ xa khi có số liệu chứng
minh locator hiện tại không đủ. Đây không phải runtime hay requirement hiện hành.

## 8. Nguyên tắc không được hiểu sai

- database dẫn xuất không phải nguồn gốc;
- pointer không phải bằng chứng;
- metadata quan hệ không phải câu chữ;
- nhiều citation không tự động là nhiều nguồn độc lập;
- rank cao không đồng nghĩa kết luận đúng hơn;
- AI không được tự suy phương trình Pāli/Sanskrit/Hán/Tạng từ trí nhớ;
- không đủ bằng chứng thì phải nói rõ giới hạn thay vì lấp chỗ trống.

Muốn hiểu kỹ lý do của các nguyên tắc này, xem
[Hồ sơ quyết định kiến trúc](docs/adr/README.md).
