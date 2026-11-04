# P0/2 — Kết quả triển khai, phần đã chạy và giới hạn

Baseline: `11b7d55a7bbadcbfc0f08cf5194947a09da9a06b` sau merge PR #10.
Nhánh mới: `feature/autonomous-evidence-assessment`. Ngày chạy 04/11/2026.

**Pipeline và adapter đã chạy bằng fixture; chưa chạy suy luận model thật.**
`MODEL_INFERENCE_NOT_EXECUTED`. Đây không phải nghiệm thu semantic accuracy,
không có ground truth mới hoặc academic approval. Không dùng nhận định Codex
lịch sử làm đáp án; không gửi Word, claim riêng tư hoặc nguồn tới API ngoài.

## Trước và sau

P0/1 mở được đúng source của claim, nhưng `claims.assess_claim()` chỉ đọc một
assessment **đã được phê duyệt** từ capability B. C cũng dùng approval ấy để
quyết định ý nghĩa phản chứng; D lưu observations/history chứ không sinh AI
analysis. Nối JSON AI vào `assessment_reader` sẽ lẫn proposal với authority.

P0/2 thêm ba module nhỏ và một command E:

- `model_adapter.py`: command transport UTF-8 JSON do host cấu hình, không
  cố định provider, không shell, tối đa hai call/claim, context/output bound,
  timeout, strict JSON, model/version/config hash và thời gian.
- `semantic_assessment.py`: nhận claim, đọc lại A qua capability, kiểm evidence
  IDs/citation/context, gọi support rồi challenge khác mục tiêu và tổng hợp
  riêng. Dùng lại enum support B; UNRESOLVED là status, không enum trùng lặp.
- `semantic_workflow.py`: đọc claim/version của Research Store/P0/1, dùng C
  executor hiện có cho explicit counter queries, xuất JSON/Markdown mới; không
  sửa store hoặc nối proposal thành approval.
- `v2_cli.py`: thêm `semantic-assess`, giữ nguyên command/default cũ.

Không đổi A/B/C/D core, resolver, schema, corpus/index/pins hoặc P0/1. Không
có framework nhiều agent, không cần mời/thuê chuyên gia cho mỗi lần chạy.
Hướng dẫn/API/model contract: [P0_2_USAGE](P0_2_USAGE.md).

## Rào chắn và phản biện

Support nhận nguyên văn claim/type, evidence A hiện hành, quotation/context,
provenance, giới hạn tìm kiếm và nguồn chưa xác minh. Prompt yêu cầu chỉ rõ
phần hỗ trợ/vượt chứng cứ, điều kiện nhân quả/thời gian, thay đổi thuật ngữ,
dịch nghĩa, chú thích/metadata và suy rộng phổ quát; không lấy model memory
làm nguồn hoặc xuất chain-of-thought.

Challenge là call thứ hai với nhiệm vụ chủ động bác bỏ/thu hẹp, thấy support
và toàn bộ evidence/candidate. Có KEEP/LOWER/LIMIT/UNRESOLVED/CONTRADICTION;
không được nâng mức bằng KEEP/LOWER. Phải có rationale/citation cho từng nguồn
được đưa vào, kể cả đề xuất irrelevant; không dùng một phiếu đồng ý thứ hai.
Model không tự khai provenance, independence count, approved, accepted hoặc
publication_authorized. ID và câu trích lạ bị từ chối bằng code.

Synthesis không viết lại một kết luận tự do đã bỏ điều kiện. Nó giữ mức đề
xuất, claim gốc, toàn bộ scope/conditions, citation và issues. Vấn đề quan
trọng/câu hỏi chưa giải quyết, nguồn thiếu, claim blocked hoặc lỗi model buộc
UNRESOLVED, kể cả support ban đầu DIRECT. Đọc lại nguồn trước hai call và cuối;
nguồn đổi/mất giữ current source status UNVERIFIED. Run đổi version/superseded
trong lúc gọi model cũng giữ UNRESOLVED. Nhiều bản dịch có provenance riêng,
không được đếm là nhiều nhân chứng độc lập; independence count null.

Đây là kiểm cấu trúc/căn cứ và rào chắn proposal, không phải thuật toán chứng
minh rationale AI đúng. Prompt injection không có đường chọn tool/command hay
đổi gate; vẫn chưa chứng minh miễn nhiễm thao túng cách hiểu của model thật.

## Kiểm thử thực chạy

Lượt cuối WSL Ubuntu/Python 3.12.3, offline:

| Nhóm | Kết quả |
|---|---|
| Toàn suite | **462 phương thức PASS**, 0 FAIL/ERROR; raw log `Ran 462 tests`, `OK (skipped=2)`. Hai class cần existing Pilot env SKIP ở discover, được chạy riêng. |
| Pilot trên index core có sẵn | **16/16 phương thức PASS**, 0 FAIL/ERROR/SKIP: 9 P0/1 và 7 P0/2; bài blocker có năm subcases. |
| P0/2 phần mềm trong toàn suite | **30 phương thức PASS**, gồm CLI/API, subprocess/JSON/schema, bound/timeout, source currentness, run version và đối kháng. |
| Bảo toàn lịch sử | **62/62 + 239/239** checksum cũ đúng; 12 ca, 37 claim, 259 ô quyết định vẫn PENDING. 13 source HEAD/pin và tracked trees sạch trước/sau. |

Toàn suite dùng workspace Git tạm chứa **byte code/config/tests giống hệt**
worktree triển khai, link tới 13 checkout đã có, acceptance index riêng tạm.
Không đổi tests cũ hoặc monkeypatch assertion/ROOT để làm PASS. Lượt Pilot
chạy trực tiếp code worktree, index lịch sử 12.102.680.576 byte mount
`loop,ro,noload` và SQLite immutable. Không download, build lại hoặc checkpoint
index Pilot. Hết lượt có unmount receipt.

462 gồm 432 phương thức nền (A44/B82/C70/D77, E và retrieval/Connector/golden/
P0/1) cộng 30 mới. Thời gian full process **26,69 giây**, unittest **26,42 giây**;
Pilot process gồm preflight/ví dụ local **9,60 giây**, unittest **6,54 giây**.
Không suy thành benchmark hoặc semantic accuracy. Windows native full suite,
Work/Connector inference và live provider chưa chạy trong nhiệm vụ này.

Đối kháng mới gồm claim sai dùng quote đúng, suy luận nhân quả sai, chữ mọi/
chỉ/luôn luôn; seeded challenge giữ unresolved. Đây là fixture kiểm đường
xử lý, **không phải AI đã tự phát hiện lỗi ấy**. Còn có fake ID/quote, bỏ qua
counter candidate, JSON hỏng/trùng key, approval giả, thiếu nguồn/context,
chú thích bị model định gán lại root và chỉ dẫn độc hại trong **blob Git của
source fixture thật**. Command/config/gate không bị source text điều khiển.

## Các ca Pilot đã dùng

| Ca | Điều đã xác minh bằng phần mềm | Điều chưa được chứng minh |
|---|---|---|
| AC01-C01/C02 | Giữ nguyên text claim trong draft mới; A mở SN36.21; không model → UNRESOLVED. Fixture support DIRECT/challenge LOWER → WEAK. | Model thật phát hiện khái quát quá mức/giới hạn nhân quả của SN36.21. |
| AC04-C01 | SN35.145/146 giữ hai work/path/blob trong cả support và challenge provenance. | Tương đương mọi hệ số hoặc sửa reference lịch sử. |
| AC05-C01 | MN135 root/translation tách riêng, claim/conditions còn nguyên, count độc lập null. | Đánh giá đúng causal scope bằng model thật. |
| AC08-C01 | Hai witness root/EN giữ riêng; fixture issue chưa giải quyết → UNRESOLVED dù action KEEP. | Phát hiện/giải quyết khác biệt dịch thực bằng AI. |
| AC11-C01 | Nguyên văn claim còn nguyên, điều kiện thời gian từ scripted challenge được giữ trong synthesis/report. | Model thực hiểu/giữ đúng điều kiện thời gian của toàn đoạn. |
| AC03-C02 + AC07-C01..C04 | Năm thiếu nguồn/phiên bản **đã biết** được đưa vào draft mới như missing-source inputs; không substitution, không model call, giữ UNRESOLVED. | Không phải bộ tự phát hiện edition thất lạc; không hợp thức hóa bằng nhận định Codex cũ. |

Chỉ đọc một số native units đã chỉ rõ trong test, không tự chuyển full Pilot
alias/range thành unit hoặc tuyên bố đã đọc toàn bộ span. Scope ghi rõ unit
sample. Không đổi 37 mệnh đề gốc hoặc 259 ô; test/report đều ở vùng mới.

Không có **phát hiện học thuật hoặc bất đồng AI thực** trong phiên này.
Các ví dụ local AC01-C02 DIRECT→WEAK và AC08-C01 KEEP nhưng unresolved issue
→ UNRESOLVED là **scripted test outcomes**, không phải nhận định về kinh văn.

## Chạy model, dữ liệu và artifact

Không được cung cấp/phát hiện host model adapter hợp lệ cho lần thử này;
không tự dùng credential hoặc phiên Codex như một API inference của BCR.
**Real model calls = 0.** Token/chi phí provider: chưa đo/không áp dụng cho
phiên inference chưa chạy. Fixture subprocess được ghi mode FIXTURE, phiên
bản và input/output hash; không đánh đồng process execution với AI reasoning.

Raw logs, counts và tested-file hashes:
[evidence P0/2](evidence/p0-2-2026-11-04/README.md). Một báo cáo chạy thật trên
nguồn **phần mềm tổng hợp** được công khai làm ví dụ. Báo cáo JSON/Markdown
AC01/AC08 chứa text/source thật giữ local trong
`D:\WORKING\BuddhismDocuments-for-AI\.m\p02-tools\final-results\private-examples`;
hash có trong receipt. Không gửi chúng qua API hoặc phân phối gói Pilot.
Artifacts xuất binary UTF-8 LF, scoped `.gitattributes` giữ LF; checksum kiểm
trên byte Git/remote, tránh lặp lỗi CRLF/LF của P0/1. Không có ZIP mới.

## Giảm thao tác và phần còn thiếu

Phần mềm đã tự ghép claim/evidence/scope, đọc lại nguồn, chuẩn bị hai request,
kiểm output/citation, giữ bất đồng/điều kiện, tổng hợp và xuất report trong một
command; không cần copy/paste hai phiên phản biện hoặc tự điền JSON approval.
Với fixture chưa đo được mức giảm lao động phân tích ngữ nghĩa thực tế.

Để kiểm một bài nghiên cứu trọn vẹn còn cần: host model được phép dùng dữ liệu
và chạy inference thực; kiểm chất lượng semantic với chuẩn đối chiếu phù hợp;
nguồn/context đầy đủ và giải quyết các blocker phiên bản; kiểm tra phân đoạn
claim/phạm vi bài và prose không tăng kết luận. Chưa có claim extraction từ
Word, planner phản chứng ngữ nghĩa, dependency approval, universal edition/
range resolver hoặc renderer bài hoàn chỉnh; không triển khai P1/3–P1/5.
Các model output vẫn có thể sai dù citation hợp lệ; prompt và hai lượt gọi
không chứng minh đúng, độc lập hoặc đầy đủ.

Quyền academic approval/publication được bảo toàn. Không có accepted claim
mới, không thay `assessment_reader`, Final Claim Gate hoặc publication gate;
không tổ chức giao chuyên gia hay tự cấp quyền chia sẻ. Draft PR dành cho kiểm
toán độc lập, không tự merge.

`HUMAN_ADJUDICATION_PENDING`

`DISTRIBUTION_CLEARED = 0`

`PUBLICATION_NOT_PERMITTED`
