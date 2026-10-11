# Biên bản kiểm toán tài liệu — 11/10/2026

> **LỊCH SỬ / SNAPSHOT KIỂM TOÁN DOCS** trên baseline
> `57db982274e267218594ae5ca463bd2a42d2be02`, nhánh
> `docs/bcr-v2-ai-onboarding-finalization`. Không là nguồn chuẩn runtime hoặc
> nghiệm thu học thuật. [GOVERNANCE](DOCUMENTATION_GOVERNANCE.md) phân thẩm quyền.

## 1. Phạm vi và kết quả sửa

Kiểm 34 tệp Markdown có sẵn (kể cả skill, 9 ADR, progress và toàn docs/v2),
manifest/config/schema, hai entry points, mã Python/validators và tests liên
quan. Nền main/origin/main đã khớp baseline và working tree sạch trước tạo nhánh.
13 gitlinks/pins không đổi. Sửa 20 tệp có sẵn, tạo 2 tệp mới; tổng 36 Markdown
được kiểm kỹ thuật sau chỉnh sửa. Chỉ Markdown được sửa; hai tài liệu mới là
[AI_ONBOARDING](AI_ONBOARDING.md) và biên bản này.

**Chín nhóm mâu thuẫn trạng thái/kiểm kê đã xử lý** (đếm theo nhóm, không theo
số câu/tệp). BLOCKING làm hiểu sai khả năng/ranh giới; MAJOR sai trạng thái/giao
diện/nguồn chuẩn; MINOR là thiếu điều hướng/diễn đạt. Không đổi tiêu chí để
hợp thức hóa implementation.

| Mã | Mức | Nhận định cũ → cách xử lý có căn cứ |
|---|---|---|
| M1 | BLOCKING | README coi lớp 2.0 là hướng chưa có → cửa vào theo mã A–E, giới hạn còn thiếu |
| M2 | BLOCKING | Spec liệt kê quote status/Research Run như chưa làm → sửa capability đã có, tách semantic approval/publication chưa có |
| M3 | MAJOR | v2 README chỉ là chương trình MỤC TIÊU → cửa vào code/usage/acceptance/evidence/snapshot |
| M4 | MAJOR | Governance 29 mã → đối chiếu 31 gốc + 2 bổ sung = 33, khớp ma trận |
| M5 | MAJOR | Architecture/SKILL/REQ/Plan/Remote nói E ở nhánh chưa gộp → mốc main 57db982, không nâng nghiệm thu toàn 2.0 |
| M6 | MAJOR | PRD/Design nói xuất/nhập review chưa triển khai → D/E đã có mã, còn thiếu thẩm định thực và approval |
| M7 | MAJOR | Plan/PRD nói mọi E1–E3 CHƯA ĐO → mẫu E1/E2 + draft cost E3 đã đo, chất lượng/AI cost và ngưỡng chưa đủ |
| M8 | MAJOR | E_PROGRESS/E_REPORT/mốc ACCEPTANCE dễ bị đọc như hiện trạng trước merge → nhãn lịch sử + link final, giữ nguyên 394/main cũ/bench |
| M9 | MAJOR | Acceptance 1.0 gọi 45 tests là tổng repo → 45 chỉ nhóm 1.0, suite sau E là 410 theo evidence |

Bổ sung các khoảng trống: onboarding ba vai trò/hai trục; API/status/exit và
review authority; liên kết evidence cuối; bỏ các bản sao root/counts runtime
trong prose hiện hành. USAGE làm rõ range resolver là chỉ số ký tự trên chuỗi
nguồn, không byte offset tự khai. Không tạo schema/policy/requirements/roadmap
mới. Không có mâu thuẫn BLOCKING/MAJOR tài liệu còn chưa giải thích tại baseline.

## 2. Ma trận kiểm toán từng tài liệu có sẵn

Cột hiện trạng ghi lỗi/thiếu/trùng hoặc bối cảnh lịch sử; nguồn chuẩn là miền
thẩm quyền cần đối chiếu, không bảng thứ bậc file nào luôn thắng. Relative
links/anchors được kiểm riêng ở mục 3; không phát hiện liên kết Markdown hỏng
ở bộ cũ. Các số/đường trong inline code lịch sử không tự biến thành runtime.

| Tài liệu | Vai trò | Nguồn đối chiếu | Hiện trạng/lỗi/thiếu/trùng | Hành động/bảo tồn |
|---|---|---|---|---|
| [.codex/skills/buddhist-corpus-research/SKILL.md](../.codex/skills/buddhist-corpus-research/SKILL.md) | Quy trình hành động | AGENTS + host/code | MAJOR M5; thiếu hai trục | Sửa bước Quick/Research, approval và liên kết |
| [AGENTS.md](../AGENTS.md) | Luật cao nhất | Luật nguồn/nghiên cứu | MINOR; thiếu lối đọc 2.0 | Bổ sung ngắn; toàn bộ luật cũ giữ nguyên |
| [README.md](../README.md) | Cửa vào dự án | Spec/code/config/acceptance | BLOCKING M1 | Rút gọn, phản ánh A–E, dẫn onboarding |
| [docs/ACCEPTANCE.md](ACCEPTANCE.md) | Tiêu chí nền 1.0 | 46 REQ 1.0 + tests | MAJOR M9; sao chép counts | Ghi 45 là nhóm 1.0; dẫn evidence/production summary |
| [docs/ARCHITECTURE.md](ARCHITECTURE.md) | Kiến trúc hiện hành | Code/config/schema | MAJOR M5; runtime trùng | A–E trên main, trust boundaries, dẫn config |
| [docs/CLI.md](CLI.md) | CLI 1.0 | cli.py/parser/exporter | MAJOR thiếu ranh giới evidence | Phân biệt A; PowerShell, global flags, bỏ counts lặp |
| [docs/CORPUS_SURVEY.md](CORPUS_SURVEY.md) | Khảo sát | Snapshot 22/09/2026 | LỊCH SỬ, đã gắn nhãn | Giữ nguyên; không lấy dung lượng cũ làm runtime |
| [docs/DOCUMENTATION_AUDIT_2026-10-06.md](DOCUMENTATION_AUDIT_2026-10-06.md) | Kiểm toán trước | Snapshot 06/10/2026 | LỊCH SỬ, đã gắn nhãn | Giữ nguyên số 69/45 và nhận định tại mốc cũ |
| [docs/DOCUMENTATION_GOVERNANCE.md](DOCUMENTATION_GOVERNANCE.md) | Phân miền thẩm quyền | Danh mục docs/REQ + code | MAJOR M4; thiếu Usage/evidence | Sửa 33 mã; nguồn chuẩn cho API/evidence/onboarding |
| [docs/PROJECT_SPEC.md](PROJECT_SPEC.md) | Mục tiêu/phạm vi | Bất biến + code/config | BLOCKING M2; copies runtime | Sửa phần khả năng/giới hạn/2.0; giữ mục tiêu và bất biến |
| [docs/REMOTE_AGENT.md](REMOTE_AGENT.md) | Routing Connector | remote config/exporter/ConnectorHost | MAJOR M5; copy root | Config làm chuẩn; A adapter trên main; giữ namespace/bucket |
| [docs/REQUIREMENTS.md](REQUIREMENTS.md) | REQ nền 1.0 | Luật/spec + 46 mã gốc | MINOR phạm vi hiện hành mơ hồ | Nói rõ nền 1.0, không sao chép 33 mã 2.0 |
| [docs/SC_CBETA_BRIDGE.md](SC_CBETA_BRIDGE.md) | Bridge/resolver 1.0 | sc-data + index/retrieval/tests | Hiện hành; coverage có mốc | Giữ nguyên ba bước relation/bridge/witness |
| [docs/adr/0001-pin-upstream-sources-by-git-commit.md](adr/0001-pin-upstream-sources-by-git-commit.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0002-keep-sqlite-as-derived-local-index.md](adr/0002-keep-sqlite-as-derived-local-index.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0003-use-language-sensitive-lexical-retrieval.md](adr/0003-use-language-sensitive-lexical-retrieval.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0004-separate-relationship-metadata-from-textual-evidence.md](adr/0004-separate-relationship-metadata-from-textual-evidence.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0005-separate-main-and-remote-artifact-repositories.md](adr/0005-separate-main-and-remote-artifact-repositories.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0006-use-deterministic-precomputed-connector-locator.md](adr/0006-use-deterministic-precomputed-connector-locator.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0007-export-pointers-not-raw-corpus-text.md](adr/0007-export-pointers-not-raw-corpus-text.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0008-do-not-materialize-cjk-trigram-vocabulary-in-production.md](adr/0008-do-not-materialize-cjk-trigram-vocabulary-in-production.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/0009-share-retrieval-ranking-but-never-treat-rank-as-scholarly-authority.md](adr/0009-share-retrieval-ranking-but-never-treat-rank-as-scholarly-authority.md) | Quyết định kiến trúc | ADR chấp nhận 06/10/2026 | LỊCH SỬ quyết định; nguyên tắc còn áp dụng | Giữ nguyên, không viết lại bối cảnh trước 2.0 |
| [docs/adr/README.md](adr/README.md) | Điều hướng quyết định | ADR có ngày | Danh mục đủ 9 | Giữ nguyên |
| [docs/v2/ACCEPTANCE.md](v2/ACCEPTANCE.md) | Mức đạt/tiêu chí | 33 mã + code/tests/evidence | MAJOR M8; các mốc lịch sử | Thêm trạng thái đầu trang; giữ tiêu chí/bảng/log cũ |
| [docs/v2/DESIGN.md](v2/DESIGN.md) | Ngữ nghĩa/contracts | Thiết kế; validators cho shape thực | MAJOR M6 | Gắn mốc A–E/export-import; chuẩn tắc khác API hiện hành |
| [docs/v2/E_PROGRESS.md](v2/E_PROGRESS.md) | Checkpoint E | 1b2d0f0, 11/10/2026 | MAJOR M8 | Chỉ thêm nhãn/link; thân 394/main D giữ nguyên |
| [docs/v2/E_REPORT.md](v2/E_REPORT.md) | Báo cáo/số đo E | Checkpoint + span fix | MAJOR M8; trước merge | Chỉ thêm trạng thái merge/evidence; không đổi benchmark |
| [docs/v2/IMPLEMENTATION_PLAN.md](v2/IMPLEMENTATION_PLAN.md) | Thứ tự A–E | Kế hoạch trước A + update | MAJOR M5/M7 | Gắn bối cảnh lịch sử và trạng thái/đo hiện nay; giữ 5 phase |
| [docs/v2/PRD.md](v2/PRD.md) | Đề bài chuẩn tắc | Mục tiêu/requirements | MAJOR M6/M7 | Sửa nhận định triển khai/đo; giữ tiêu chí sản phẩm |
| [docs/v2/README.md](v2/README.md) | Cửa vào 2.0 | Code + ACCEPTANCE/evidence | MAJOR M3 | Tách đã có mã, mục tiêu, usage và snapshot |
| [docs/v2/REQUIREMENTS.md](v2/REQUIREMENTS.md) | 33 mã yêu cầu | 31 gốc + RUN-007/TST-003 | MAJOR M5 | Chỉ sửa trạng thái giới thiệu; giữ từng requirement |
| [docs/v2/USAGE.md](v2/USAGE.md) | CLI/API tích hợp | v2_cli + host/store/tests | MAJOR thiếu API/status detail | Thêm signatures/host/report/exit/global flags; range là ký tự |
| [docs/v2/evidence/README.md](v2/evidence/README.md) | Điều hướng evidence | JSON/raw logs gốc | MINOR thiếu final log links | Dẫn ba tệp cuối; phân biệt code/evidence-only HEAD |
| [progress.md](../progress.md) | Lịch sử bàn giao | Snapshot 26/09/2026 | LỊCH SỬ, đã gắn nhãn | Giữ nguyên; không là onboarding hiện hành |

## 3. Ba vòng QA và kiểm kỹ thuật

**Vòng 1 — facts:** đối chiếu config/pins/gitlinks/schema, parser/signatures,
A/B/C/D/E guards, test expected và evidence commit. Phân biệt software tests,
nguồn thật, runtime, approval và scholarly acceptance. Không dùng một ca
Connector hoặc JSON portability để nghiệm thu toàn Connector/Work.

**Vòng 2 — consistency:** README–Spec–Architecture; AGENTS–SKILL;
Architecture–Design; USAGE–CLI/API; Requirements–Acceptance; E_REPORT–evidence;
Governance–danh mục thực. Trạng thái hiện hành và snapshot được ghi riêng;
31 mã gốc + 2 bổ sung khớp hoàn toàn. Mục tiêu sản phẩm/luật nguồn/tiêu chí
chuẩn tắc không bị làm yếu.

Kết quả kiểm kỹ thuật sau khi ổn định diff:

- 275 liên kết Markdown tương đối, 19 anchor, đúng path/case; 0 liên kết hỏng.
  Kiểm thêm 154 tham chiếu inline tới tệp repo hiện hành: 0 tệp thiếu.
- 31 subcommands của hai CLI đối chiếu parser; 33 lần --help (hai root + 31
  subcommands) exit 0; 81 mẫu lệnh trong code fences hiện hành parse được
  sau thay placeholder ID/version bằng giá trị đúng kiểu. Không chạy build/export
  hoặc mutation chỉ để xác nhận cú pháp.
- 24 chữ ký/API bindings khớp AST/signatures: 22 dòng host/store trong USAGE
  và hai mẫu gọi evidence_gate/assess_claim. Ba Python snippets parse được.
- 11 smoke checks trên WSL với index/13 nguồn đã có: status/search 1.0, Quick
  ba corpus, quote đúng/sai, no-hit, lỗi missing index/JSON stderr, thứ tự flags
  và Python LocalHost. Chạy lại toàn suite WSL: 410/410, 0 failure/error/skip,
  pins trước/sau không đổi; không chạy lại Windows full hoặc benchmark.
  Mã native WSL tại baseline được so 47 tệp bảo vệ với working tree/Git trước
  chạy; logs/check results mới giữ tạm ngoài Git, không đổi raw evidence cũ.
- UTF-8, exact-case file paths, fences/headings, anchors theo slug GitHub,
  private-path/token patterns trên Markdown sửa/mới và git diff --check: đạt.
  Chỉ kiểm local anchors/cú pháp, không có lượt render Mermaid tự động.
- Git diff chỉ Markdown; bytes/tree của tools/tests/bin/schema/config/manifest,
  13 gitlinks, Word và mọi evidence/benchmark raw giữ nguyên baseline.

**Vòng 3 — tự mô phỏng AI mới từ tài liệu (không dùng agent hay reviewer độc lập):**

| Vai trò | Bài đi theo đường đọc và câu trả lời tìm được | Kết quả |
|---|---|---|
| Researcher | AGENTS → SKILL → config → USAGE/Remote → source: tìm sutaṃ/ID, mở đúng pin/context, giữ provenance/root-vs-note, no-hit chỉ trong scope; Quick kiểm A, Research giữ draft | ĐẠT |
| Developer | README → onboarding → Architecture → retrieval/A/B/C/D/E → tests: tìm đúng module/entry và expected; source/pins, retrieval 1.0 và authority không tự sửa | ĐẠT |
| Reviewer | Design → 33 Requirements → Acceptance → E_REPORT/evidence → USAGE review + B/D tests: đối chiếu hash/version/history/evidence/C receipts, phát hiện JSON self-approval; finalized/RECORDED không cấp publication | ĐẠT |

ĐẠT nghĩa là các câu hỏi tiếp nhận có câu trả lời và đường kiểm cụ thể trong
docs/code được dẫn; không là đánh giá học thuật độc lập hoặc chỉ kiểm file tồn tại.
Sau vòng mô phỏng đã thêm review contract/troubleshooting và đường đọc ngắn
để không cần mở toàn bộ DESIGN khi chỉ lookup hẹp.

## 4. Bảo tồn và giới hạn còn lại

progress, survey, audit 06/10 và 9 ADR giữ nguyên. Thân E_PROGRESS/E_REPORT,
logs, benchmark 7/14 lượt, 394 tests và main trước merge giữ nguyên; chỉ thêm
header/link trạng thái. Các mốc A–D trong ACCEPTANCE vẫn là lịch sử, 33 tiêu
chí yêu cầu không đổi. Không sửa Word/PDF hoặc package/locator/source.

Hạn chế **phần mềm/nghiệm thu**: ba resolver, semantic approval chưa xác thực,
Research publication đóng, Work chưa phiên thật, toàn Connector chưa nghiệm
thu, thiếu ground truth/reviewer và ngưỡng, Windows full chưa đạt. Chúng đã
được ghi ở các cửa vào, không phải lỗi docs cần che. `final_claim_gate` vẫn
có diagnostic cũ nói C/D chưa triển khai; code thực đã có C/D nhưng guard
Research vẫn đóng. Docs giải thích đúng guard; nhiệm vụ này không sửa mã.

Hạn chế **lưu dấu vết**: final evidence committed ở 57db982 ghi tested code
4986216; lần rerun WSL tại evidence-only HEAD được báo nhưng raw log ngoài Git.
[evidence README](v2/evidence/README.md) ghi rõ; không giả là raw log HEAD đã
được commit. Checks mới của nhiệm vụ docs cũng lưu tạm ngoài Git. Link validator
kiểm local paths/anchors và cú pháp Markdown, không chứng nhận mọi URL ngoài
hoặc render Mermaid trên mọi client. API có thể đổi; cần cập nhật USAGE cùng code.

## 5. Kết luận bàn giao

Mức **1: tài liệu nhất quán, AI onboarding đạt, sẵn sàng rà soát merge** tại
baseline đã nêu. Đây là tự kiểm docs, còn chờ người dùng rà soát độc lập nhánh
trước merge. Không merge main, không mở quyền Research hoặc tuyên bố toàn bộ
BCR 2.0 đã nghiệm thu học thuật.
