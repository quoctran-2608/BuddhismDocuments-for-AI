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
| CLI 1.0 | [CLI](CLI.md) + `tools/corpus_research/cli.py` |
| CLI E / Python host APIs | [USAGE](v2/USAGE.md) + `v2_cli.py`, `local_host.py`, `local_research.py`, `connector_host.py`; signatures/validators/tests quyết định thực thi |
| Quy trình AI nghiên cứu | `.codex/skills/buddhist-corpus-research/SKILL.md` |
| Connector chuyên biệt | `docs/REMOTE_AGENT.md` |
| SC ↔ CBETA | `docs/SC_CBETA_BRIDGE.md` + resolver tests |
| Khảo sát ban đầu | `docs/CORPUS_SURVEY.md` |
| Lịch sử phát triển | `progress.md` + lịch sử Git |
| Yêu cầu có mã của nền 1.0 | [REQUIREMENTS](REQUIREMENTS.md) |
| Nghiệm thu nền 1.0 | [ACCEPTANCE](ACCEPTANCE.md) |
| Đề bài nâng cấp Buddhist Corpus Research 2.0 | `docs/v2/PRD.md` |
| Thiết kế Buddhist Corpus Research 2.0 | `docs/v2/DESIGN.md` |
| Yêu cầu có mã của 2.0 | `docs/v2/REQUIREMENTS.md` |
| Nghiệm thu 2.0 | `docs/v2/ACCEPTANCE.md` |
| Báo cáo tích hợp/giới hạn/số đo E có mốc | [E_REPORT](v2/E_REPORT.md); không dùng benchmark cũ làm số đo sau sửa span |
| Bằng chứng thực thi gốc | [evidence README](v2/evidence/README.md) → JSON/raw logs có tested commit và môi trường; phân biệt code commit với evidence-only commit |
| Checkpoint E lịch sử | [E_PROGRESS](v2/E_PROGRESS.md); không là trạng thái nghiệm thu hiện hành |
| Đường đọc và bản đồ tiếp nhận | [AI_ONBOARDING](AI_ONBOARDING.md); tóm tắt và liên kết, không sở hữu policy/contracts |
| Kiểm toán tài liệu theo ngày | [06/10](DOCUMENTATION_AUDIT_2026-10-06.md), [11/10](DOCUMENTATION_AUDIT_2026-10-11.md); snapshot, không là runtime authority |
| Lý do quyết định kiến trúc | `docs/adr/` |

## 2. Bốn trạng thái bắt buộc

### HIỆN HÀNH

Đã triển khai và có thể xác nhận bằng code, config, schema, tests hoặc runtime
artefact.

Phải ghi rõ cấp xác nhận: có mã, software tests, nguồn thật, runtime thực hay
nghiệm thu học thuật. Mã A–E đã gộp không tự làm mọi yêu cầu 2.0 HIỆN HÀNH;
thẩm định ngữ nghĩa, Work/full Connector và publication còn chưa đủ.

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
3. xác định mỗi tài liệu là HIỆN HÀNH, MỤC TIÊU, TƯƠNG LAI hay LỊCH SỬ;
4. nếu hỏi hành vi thực tế, kiểm code + tests + runtime artefact;
5. nếu hỏi hệ thống phải làm gì, kiểm Project Spec/Requirements/Acceptance;
6. ghi nhận sai lệch thay vì tự hòa giải.

Ví dụ:

- `progress.md` nói remote còn là POC nhưng
  `config/remote-corpus.json` khai báo `pointer_production_v1`: progress là
  lịch sử, config/runtime là hiện trạng;
- README chỉ dẫn legacy export nhưng CLI/config/production artefact dùng pointer
  v1: README cần sửa;
- một hợp đồng trong DESIGN là chuẩn tắc; có code/test chưa đủ chứng minh
  runtime hoặc nghiệm thu học thuật. Kiểm ACCEPTANCE trước khi tuyên bố đạt.

## 5. Vai trò của các tài liệu chính

### README

Cửa vào ngắn gọn: dự án là gì, làm gì, cách bắt đầu, đọc gì tiếp theo.

README không phải nơi giữ toàn bộ SHA, pointer protocol, benchmark hay roadmap.

### PROJECT_SPEC

Nguồn chuẩn cấp dự án: mục tiêu, phạm vi, nguyên tắc, kiến trúc cấp cao, năng lực
hiện hành, giới hạn và hướng nâng cấp.

Nó không thay thế nguồn chuyên biệt.

### Bộ tài liệu Buddhist Corpus Research 2.0

`docs/v2/` chứa thiết kế chuẩn tắc, hướng dẫn **HIỆN HÀNH**, nghiệm thu theo
yêu cầu và bằng chứng **LỊCH SỬ** có mốc của 2.0. Mã A–E đã trên main tại
`57db982274e267218594ae5ca463bd2a42d2be02` (11/10/2026); còn tiêu chí chưa đạt:

- `docs/v2/PRD.md` sở hữu đề bài, mục tiêu, phạm vi và tiêu chí thành công;
- `docs/v2/DESIGN.md` sở hữu ngữ nghĩa và hợp đồng dữ liệu của lớp kiểm chứng;
- `docs/v2/REQUIREMENTS.md` sở hữu **31 yêu cầu gốc + 2 bổ sung = 33** mã;
- `docs/v2/ACCEPTANCE.md` sở hữu cách nghiệm thu các yêu cầu 2.0;
- [USAGE](v2/USAGE.md) sở hữu hướng dẫn CLI/API tích hợp, không hợp đồng mới;
- [E_REPORT](v2/E_REPORT.md) dẫn số đo và giới hạn với mốc, [evidence](v2/evidence/README.md)
  sở hữu kết quả/raw logs; [E_PROGRESS](v2/E_PROGRESS.md) chỉ là checkpoint cũ;
- các tài liệu 2.0 bổ sung về sau phải nằm cùng thư mục nếu chúng chỉ áp dụng cho
  chương trình nâng cấp này.

Các tài liệu trong `docs/v2/` không phải bằng chứng rằng tính năng đã được
triển khai. Tài liệu chung/hiện hành tiếp tục nằm ở cấp `docs/`.

**Một nguồn cho một hợp đồng:** DESIGN giữ ngữ nghĩa/hợp đồng chuẩn tắc;
constants/validators và tests ở mã A/B/C/D/E xác định hình dạng dữ liệu thực
hiện tại. USAGE/onboarding chỉ dẫn tới đó, không duy trì schema độc lập.
AGENTS vẫn sở hữu luật nghiên cứu; capability/auth do host xác lập ngoài JSON.
ACCEPTANCE ghi mức đạt; evidence chứng minh đúng lần chạy/commit, không tự
thay tiêu chí hoặc cấp quyền công bố. Các mốc A–E trong ACCEPTANCE và số đo
trước sửa span trong E_REPORT được bảo tồn; đọc trạng thái đầu trang để biết hiện tại.

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
