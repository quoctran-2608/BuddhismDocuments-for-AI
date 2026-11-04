# P0/1 — Báo cáo triển khai và hồi quy nguồn khai báo

Ngày chạy: 04/11/2026. Baseline chính xác:
`bdff78ad83d0f56c676155555b063d52f12634d5` (main sau PR #9).
Nhánh: `feature/claim-work-constrained-retrieval`.
Phạm vi: Claim/Work-Constrained Retrieval local, không triển khai P0/2–P1/5.

## Chẩn đoán trước sửa

Đã đọc AGENTS, skill BCR, PROJECT_SPEC, PRD, DESIGN, ACCEPTANCE, USAGE và lần
theo `claims`, `local_research`, `local_host`, `retrieval`, source resolvers,
verification, counterevidence, ResearchStore/run và CLI E.

Pilot có claim ID và `source_refs`, nhưng `LocalResearch.create()` chỉ nhận
question/query/corpus. Hàm tìm theo query, lấy hit, kiểm A rồi tạo claim mới
mô tả câu trích với ID sinh mới. Nó không nhận claim gốc hay source reference
của claim. Vì vậy định danh nguồn không được truyền vào truy xuất ở đường tạo
Research theo query. Đây là thiếu đường nối, không phải resolver không mở được
SN 36.21. `work`/source reader/A vốn đã có phần lớn locator cần thiết.

## Thay đổi tối thiểu

Thêm `tools/corpus_research/declared_sources.py`, các lệnh E riêng
`verify-source`, `claim-run-create`, `source-search` và kiểm thử. Không đổi SQL
schema, schema Claim/Evidence, resolver, retrieval 1.0 hay gate A/B/C/D/E.

Đường mới:

```text
claim ID + nguyên văn claim
→ source_references[claim_id] (locator native đã đối chiếu)
→ lọc chính xác corpus/work/path và kiểm manifest pin/repository
→ đọc nguồn ghim, giải segment/witness thật
→ một nguồn phù hợp duy nhất → A kiểm nguồn độc lập lần nữa
→ link evidence vào draft mới → B/C/D/E giữ kiểm tra hiện có
```

Giữ source reference nguyên bản trong sidecar audit, cùng `claim_id`, nhãn
`DECLARED`, gate và provenance đầy đủ. Segment nằm trong chunk được giải từ
nguồn thật, không suy sequence/offset từ caller. Thiếu nguồn, sai pin/witness,
segment không có, quá giới hạn candidate hoặc nhiều nguồn phù hợp đều báo rõ,
không gọi lexical search thay thế. Một claim có nhiều reference chỉ nhận
supporting IDs khi tất cả đã kiểm A thành công.

Nguồn bổ sung qua `source-search` có nhãn `EXPANDED` và
`replaces_declared_source=false`; không sửa run/claim. Kế hoạch phản chứng C
vẫn chạy qua API hiện có và nằm riêng trong `counterevidence`. Không tự chuyển
discovery hit thành bằng chứng hỗ trợ hay phản chứng ngữ nghĩa.

Đây là envelope API/input **mới, opt-in** ánh xạ các trường đã có, không thêm
trường vào hợp đồng B/D hoặc migration SQLite. `claim_id` là association do
caller khai, không tự xác thực rằng đó là claim đã được phê duyệt. Hướng dẫn
input/CLI/API và cách xử lý reason: [P0_1_USAGE.md](P0_1_USAGE.md).

## Đối chứng trước/sau trên dữ liệu thật

Index Pilot core hiện có: 12.102.680.576 byte, mount `loop,ro,noload`, SQLite
immutable/read-only, không build lại hay checkpoint index lịch sử. Nguồn là
các checkout local đã có; cả 13 HEAD khớp manifest và tracked tree sạch trước/
sau. Không dùng mạng để lấp dữ liệu corpus. GitHub Connector chỉ phục vụ đồng
bộ metadata/tài liệu dự án và bàn giao code/PR.

| Ca | Đường mặc định/trước nâng cấp | Đường bật ràng buộc |
|---|---|---|
| AC01 | `pubbekatahetu`, limit 1 chọn `an3.61`; hit có thể đúng query nhưng sai tác phẩm claim viện dẫn. Ranking này vẫn giữ nguyên. | Reference SN 36.21 mở `sn36.21:2.1`, pin `0914c609…`, witness `root:root-pli-ms`, blob `1bdd992d…`; A VERIFIED, không tìm từ khóa để thay nguồn. |
| AC04 | Lookup work chính xác đã tồn tại, nhưng đường claim/query không mang ràng buộc. | Mở riêng `sn35.145:0.2` và `sn35.146:0.2`; work/path/blob/câu trích khác nhau tại Bilara pin này. Ghép work 145 với path 146 bị báo `DECLARED_SOURCE_NOT_INDEXED`; không tự đổi số. |
| Sai work/path/pin/witness/segment | Lexical retrieval không có hợp đồng bind claim → reference. | Từng mutation không được VERIFIED; trả reason/failure, không thay nguồn. |
| Thiếu source checkout/blob | Index wording không đủ thẩm quyền làm nguồn. | UNVERIFIED; thiếu Git source không được bù bằng index hoặc nguồn mở rộng. |
| Nhiều nhân chứng | Xếp hạng discovery có thể chọn một hit. | Chỉ work SN 36.21 chưa đủ chọn root/bản dịch: `AMBIGUOUS_DECLARED_SOURCE`. |

Một bài kiểm đọc **nguyên văn AC01-C01 từ register pilot khóa**, đưa bản sao
vào draft mới và xác nhận text/ID giữ nguyên, nguồn đã bind, accepted set rỗng;
register nguyên bản không đổi byte. Các bài khác kiểm identity và mutation,
không tạo ground truth ngữ nghĩa. Việc mở riêng SN 35.145/146 không xác lập
quan hệ tương đương giữa mọi hệ đánh số hay sửa quyết định/claim AC04 lịch sử.

## Kiểm thử thực sự đã chạy

Raw log và receipt có checksum tại
[evidence P0/1](evidence/p0-1-2026-11-04/README.md).

| Lượt cuối | Kết quả |
|---|---|
| Full `unittest discover -s tests -v`, Python 3.12.3/Ubuntu WSL, bản sao tạm byte-identical của code với link tới 13 checkout local | **432 phương thức PASS, 0 FAIL, 0 ERROR**; log `Ran 432 tests`, `OK (skipped=1)`. Một **class** P0/1 cần existing-index env được SKIP ở lượt discover và chạy riêng ngay dưới, không tính SKIP thành PASS. |
| `test_declared_sources_corpus.PilotDeclaredSourceTests` trên index Pilot chỉ đọc, có `BCR_P01_CLAIMS` | **9/9 PASS, 0 FAIL/ERROR/SKIP**. |
| Kiểm inventory lịch sử | **62/62** checksum hồ sơ autonomous cũ và **239/239** checksum gói preparation đúng; 37 claim còn PENDING, 259 ô quyết định còn PENDING. |

Full suite bao gồm: A verification 44; B claims 82; C counterevidence 70;
D research_run/store 77; E local integration 40, corpus thật 14 và span 16;
golden research 11; connector contract 11; nhóm retrieval/normalization/roles/
remote/resolver/acceptance 45; P0/1 mới 22. Tổng 432. Log liệt kê từng tên bài
và `results.json` có tổng theo module. Các bài mới kiểm CLI, mapping claim/ref,
provenance, pin do host quản lý khi caller bỏ trường SHA, không fallback, không
partial substitution, đọc lại nguồn khi reopen run, expansion riêng và gate
công bố đóng.

Full suite dùng workspace Git tạm trên Linux với byte code/config/tests giống
worktree triển khai; chỉ workspace tạm có source links và index acceptance mới.
Không sửa file test cũ hoặc monkeypatch ROOT để làm chúng PASS. Lượt Pilot
chạy trực tiếp code worktree tại baseline nói trên. Receipt ghi SHA-256 bốn
file code/test đã chạy, thời điểm, môi trường và mount. Chưa chạy full suite
trên Windows native hoặc nghiệm thu Connector/Work thực trong nhiệm vụ này.

Số đo thực của lượt cuối: full suite khoảng **25,78 giây**; nhóm Pilot khoảng
**1,38 giây**. Một cặp quan sát cùng phiên: Quick query khoảng **84,94 ms**
(1 retrieval call, 2 source reads); declared-source khoảng **24,31 ms**
(0 retrieval calls, 3 source reads). Chỉ là một lần đo local, có ảnh hưởng cache
và tải đồng thời; không suy thành benchmark tốc độ. Chưa đo token/chi phí tiền
hoặc semantic accuracy. Không gọi model để cấp semantic approval.

## Bảo toàn

Baseline được đồng bộ bằng Git objects/tài liệu dự án qua Connector và xác
minh hash trước khi đặt nhánh mới tại đúng `bdff78ad…`; không tải corpus hay
đổi main. Product/config/schema/tests gốc có Git tree SHA trùng baseline.
Diff bàn giao chỉ gồm module/CLI P0/1, tests, hướng dẫn và evidence mới.

Không thay 13 gitlink/pin, corpus, index Pilot, claim gốc, 259 ô quyết định,
các ZIP Round 3/A/B hay quyết định lịch sử. Hai inventory đã khóa được kiểm lại
theo checksum có sẵn, không tái sinh receipt lịch sử. Không gửi tài liệu cho
chuyên gia hoặc cấp quyền chia sẻ. A VERIFIED không tạo B approval, accepted
claim hoặc quyền công bố.

## Hạn chế còn lại

- Nguồn phải có work/path trong index hiện tại; nguồn ngoài coverage vẫn báo
  thiếu, kể cả blob có thể tồn tại trong checkout. Không tự bổ sung corpus.
- Resolver vẫn chỉ hỗ trợ các định dạng Bilara/CBETA/84000 hiện có. Không
  tuyên bố đã hỗ trợ đầy đủ mọi source/edition của 13 corpus.
- Không có field edition thống nhất: input `edition` bị từ chối. Alias nguồn
  Pilot/range và tương đương hệ số chưa được tự động chuyển đổi. Caller cần
  cung cấp locator native đã đối chiếu; không dùng số giống nhau làm identity.
- Work nhiều file/unit cần ràng buộc rõ hơn. Có giới hạn candidate do host
  quản lý; nguồn không mở được trong tập ứng viên có thể khiến kết quả giữ
  mơ hồ. Cách đóng thận trọng này có thể bỏ sót nguồn hợp lệ thay vì tự chọn.
- Đường default/EXPANDED vẫn có thể chọn hit lệch tác phẩm. Các bài ràng buộc
  đã chạy không quan sát chọn nhầm; không có chứng minh bao phủ mọi corpus.
- Ràng buộc định danh không xác minh suy luận, dịch nghĩa, tính đầy đủ của
  ngữ cảnh, độc lập nguồn hay mức hỗ trợ claim. Full unit/range không được tự
  ghép thành câu trích. Semantic support/counterevidence assessment còn pending.
- Sidecar là audit data; không phải policy engine ngăn host/caller cố ý thay
  đổi claim bằng thao tác revision riêng. Các thao tác ấy vẫn phải qua B–E.

`HUMAN_ADJUDICATION_PENDING`

`DISTRIBUTION_CLEARED = 0`

`PUBLICATION_NOT_PERMITTED`
