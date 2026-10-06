# Chính sách tài liệu và nguồn chuẩn

> Trạng thái: **HIỆN HÀNH**

Tài liệu này quy định tài liệu nào có thẩm quyền về loại thông tin nào. Nó không
thay thế đặc tả dự án, kiến trúc, cấu hình, schema, mã nguồn hay kiểm thử.

## 1. Nguyên tắc

Không có một thứ tự “file A luôn thắng file B” áp dụng cho mọi câu hỏi.

Thẩm quyền được xác định theo miền thông tin:

| Miền | Nguồn chuẩn |
|---|---|
| Định nghĩa, phạm vi và trạng thái cấp dự án | `docs/PROJECT_SPEC.md` |
| Luật nghiên cứu | `AGENTS.md` |
| Kiến trúc kỹ thuật hiện hành | `docs/ARCHITECTURE.md` |
| 13 nguồn và SHA | `manifest.json` |
| Corpus, vai trò và evidence class | `config/corpus-sources.json` |
| Runtime Connector | `config/remote-corpus.json` |
| Artefact Connector production | production manifest/summary ở remote repo |
| Schema SQLite | `schema/corpus-index.sql` |
| Hành vi truy xuất/xếp hạng | mã trong `tools/corpus_research/` + tests |
| CLI | `docs/CLI.md` + `tools/corpus_research/cli.py` |
| Quy trình AI nghiên cứu | `.codex/skills/buddhist-corpus-research/SKILL.md` |
| Connector chuyên biệt | `docs/REMOTE_AGENT.md` |
| SC ↔ CBETA | `docs/SC_CBETA_BRIDGE.md` + resolver tests |
| Khảo sát ban đầu | `docs/CORPUS_SURVEY.md` |
| Lịch sử phát triển | `progress.md` + lịch sử Git |
| Yêu cầu có mã | `docs/REQUIREMENTS.md` |
| Thiết kế lớp kiểm chứng nghiên cứu MỤC TIÊU | `docs/RESEARCH_VERIFICATION_DESIGN.md` |
| Tiêu chí nghiệm thu | `docs/ACCEPTANCE.md` |
| Lý do quyết định kiến trúc | `docs/adr/` |

## 2. Bốn trạng thái bắt buộc

### HIỆN HÀNH

Đã triển khai và có thể xác nhận bằng code, config, schema, tests hoặc runtime
artefact.

### MỤC TIÊU

Đã được chấp thuận về hướng hoặc đang được đặc tả nhưng chưa triển khai đầy đủ.

### TƯƠNG LAI

Ý tưởng hoặc hướng có điều kiện, chưa thuộc phạm vi triển khai đã cam kết. Không
được xem như requirement v1 cho tới khi được chủ động nâng thành MỤC TIÊU.

### LỊCH SỬ

Mô tả khảo sát, benchmark, POC, quyết định hoặc trạng thái ở một thời điểm trước.

Không được mô tả MỤC TIÊU/TƯƠNG LAI như HIỆN HÀNH. Không được dùng LỊCH SỬ để
phủ định runtime HIỆN HÀNH.

## 3. Một sự thật quan trọng chỉ có một nơi chuẩn

Các tài liệu khác có thể tóm tắt, giải thích hoặc đưa ví dụ, nhưng không nên duy
trì một bản hợp đồng độc lập có khả năng lệch.

Ví dụ:

- `PROJECT_SPEC.md` nói hệ thống dùng 13 nguồn được ghim;
- `manifest.json` quyết định chính xác 13 nguồn nào và SHA nào.

Tương tự, đường dẫn Connector hiện tại phải lấy từ
`config/remote-corpus.json`, không phải từ một bản sao văn xuôi.

## 4. Quy tắc giải quyết mâu thuẫn

Khi hai nguồn nói khác nhau:

1. xác định câu hỏi thuộc miền nào;
2. tìm nguồn chuẩn của miền đó;
3. xác định mỗi tài liệu là HIỆN HÀNH, MỤC TIÊU hay LỊCH SỬ;
4. nếu hỏi hành vi thực tế, kiểm code + tests + runtime artefact;
5. nếu hỏi hệ thống phải làm gì, kiểm Project Spec/Requirements/Acceptance;
6. ghi nhận sai lệch thay vì tự hòa giải.

Ví dụ:

- `progress.md` nói remote còn là POC nhưng
  `config/remote-corpus.json` khai báo `pointer_production_v1`: progress là
  lịch sử, config/runtime là hiện trạng;
- README chỉ dẫn legacy export nhưng CLI/config/production artefact dùng pointer
  v1: README cần sửa;
- đặc tả Atomic Claim tồn tại nhưng code chưa có: đó vẫn là MỤC TIÊU.

## 5. Vai trò của các tài liệu chính

### README

Cửa vào ngắn gọn: dự án là gì, làm gì, cách bắt đầu, đọc gì tiếp theo.

README không phải nơi giữ toàn bộ SHA, pointer protocol, benchmark hay roadmap.

### PROJECT_SPEC

Nguồn chuẩn cấp dự án: mục tiêu, phạm vi, nguyên tắc, kiến trúc cấp cao, năng lực
hiện hành, giới hạn và hướng nâng cấp.

Nó không thay thế nguồn chuyên biệt.

### RESEARCH_VERIFICATION_DESIGN

Nguồn chuẩn cho semantics và data contract của lớp kiểm chứng **MỤC TIÊU**:
Evidence Record, quotation status, Atomic Claim, support status, độc lập nguồn,
phản chứng, Final Claim Gate, Research Run và ranh giới TƯƠNG LAI.

Nó không phải bằng chứng rằng các tính năng đó đã được triển khai.

### AGENTS

Luật nghiên cứu bắt buộc: evidence, provenance, witness separation,
cross-language guardrails, fail-closed.

### ARCHITECTURE

Mô tả hệ thống được xây như thế nào.

### SKILL

Mô tả AI phải hành động thế nào khi nhận một câu hỏi nghiên cứu.

### REMOTE_AGENT

Hướng dẫn vận hành Connector chuyên biệt.

### CORPUS_SURVEY

Hồ sơ khảo sát có mốc thời gian; không phải trạng thái hiện tại.

### progress.md

Hồ sơ lịch sử/bàn giao. Được phép giữ benchmark, POC và trạng thái trung gian,
nhưng không phải CURRENT_STATUS.

## 6. Chống trùng lặp

Không duy trì nhiều bản độc lập của:

- danh sách 13 nguồn và SHA;
- toàn bộ CLI command;
- production key counts;
- pointer fields;
- evidence classes;
- runtime Connector config.

Tóm tắt được phép khi giúp người đọc hiểu; hợp đồng chi tiết phải trỏ về nguồn
chuẩn.

## 7. Quy tắc cho thay đổi về sau

Mỗi thay đổi quan trọng phải tự kiểm:

1. requirement nào thay đổi;
2. nguồn chuẩn nào phải cập nhật;
3. config/schema/code nào thay đổi;
4. test nào chứng minh;
5. tài liệu nào chỉ cần dẫn link;
6. trạng thái là HIỆN HÀNH, MỤC TIÊU, TƯƠNG LAI hay LỊCH SỬ;
7. có cần ADR không.

Một thay đổi chưa hoàn tất nếu implementation đã đổi nhưng nguồn chuẩn liên quan
vẫn mô tả hành vi cũ.

## 8. Prompt tạm

Prompt dùng cho một nhiệm vụ phát triển đã hoàn tất không phải tài liệu sản phẩm
và không nên nằm ở root repository.

`prompt.txt` cũ về đo CJK vocabulary không có giá trị cần giữ và được xóa khỏi
repository.
