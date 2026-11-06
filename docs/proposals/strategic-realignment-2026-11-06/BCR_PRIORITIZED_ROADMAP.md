# Roadmap ưu tiên cho hạ tầng chứng cứ nghiên cứu

Ngày 06/11/2026. **ĐỀ XUẤT CHỜ THẨM ĐỊNH; CHƯA TRIỂN KHAI.** Không đặt tên
phiên bản mới. P1–P4 dưới đây là thứ tự công việc, không thay các mốc P0/1–P0/3
hoặc 33 yêu cầu nghiệm thu hiện hành.

Căn cứ: [audit](BCR_CAPABILITY_AUDIT.md),
[target workflow](BCR_TARGET_WORKFLOW.md),
[migration impact](BCR_MIGRATION_IMPACT.md). Mỗi mục triển khai sau này cần
nhánh/PR riêng phù hợp, tiêu chí được thẩm định trước code và raw kết quả.

## 1. Ba thay đổi triển khai đầu tiên

1. **Native candidate preview trước binding (P1-a).** Chặn lỗi chọn key rỗng
   trước khi nó thành yêu cầu bắt buộc. Đây là lỗi vận hành lặp đã có nguồn và
   receipts kiểm lại, tái dùng được source reader/resolver/A.
2. **Đường chọn nguồn rõ ràng và coverage/preflight đúng (P1-b/P1-c, P2-a).**
   Tách parser revision khỏi profile, tách candidate khỏi declared reference,
   giảm cấu hình môi trường lặp. Đây là điều kiện để agent dùng đúng các
   primitives đã có; không “sửa” bằng cách bỏ guard hoặc reference bị lỗi.
3. **Research Evidence Pack + render facts (P2-b rồi P3-a).** Gom dữ liệu
   hiện hữu, giảm gõ lại title/ID và giúp reviewer lần về nguồn. Không chờ có
   semantic truth scoring hoặc một DB khác mới cung cấp hồ sơ hữu ích.

Đây là ba cải tiến sản phẩm; một cải tiến có thể chia thành các PR nhỏ. Không
tự triển khai tất cả vì audit này đã xong; chủ dự án thẩm định thiết kế trước.

## 2. P1 — Truy xuất, lựa chọn và kiểm nguồn

| Mục / căn cứ | Tái sử dụng và thay đổi tối thiểu | Nghiệm thu đo được đề xuất | Regression bắt buộc | Điều kiện quyết định triển khai |
|---|---|---|---|---|
| **P1-a Native preview** — E2/E4/E5/E6, EN MN135 rỗng lặp | `retrieval.work/evidence`, `LocalHost.source_reader`, `source_resolvers`, P0/1. View read-only native key/length/role/witness/span availability; validate-source trước bind | 6/6 keys EN rỗng đã tái hiện được nhận diện đúng; 2/2 positive EN units mở/kiểm được; phân biệt absent/empty/escaped/unsupported bằng source facts. 0 silent substitution; mỗi candidate có pin/path/witness/role và reason. Không tự bind source khác | AC01 SN36.21, AC04 145/146; wrong work/path/pin/witness/segment, ambiguity, no fallback; source span/escape/comment tests | Đầu tiên xác nhận preview hiện có qua verify-source/raw read chưa đáp ứng độ dễ dùng. Chỉ thêm helper/view, không sửa resolver nếu không cần |
| **P1-b Profile/coverage đúng** — E3 cùng-core bị coi mixed | `LocalHost.scope`, `state_parser_version`, source_state. Policy host phân biệt revision/parser mode; nhận diện legacy state không đoán provenance | Fixture cùng `core` khác base parser có kết quả theo policy rõ, không còn báo sai mixed-profile. Stale parser/pin/WAL/scope thiếu vẫn bị chặn. Mọi scope ghi actual components/coverage; state không đủ phân biệt phải báo unknown/needs policy | test_local_integration, declared sources, C exact scope binding, corpus profiles; thêm core/core, core/full, acceptance/core, stale và legacy cases | Thẩm định policy tương thích trước sửa. Không xóa `len(profiles)` guard đơn thuần; không sửa index lịch sử hoặc tự gắn nhãn core cho dữ liệu không chứng minh được |
| **P1-c Chọn candidate rồi khai báo** — query-create khác declared-create | `source-search`, `verify_declared_source`, `create_declared_run`, B/D revision; view phân biệt candidate/DECLARED/EXPANDED | 100% refs bắt buộc giữ nguyên trong audit trail; khi một ref thất bại supporting set của claim vẫn theo all-or-nothing. 0 expanded hit thay declared ngầm. Candidate cần làm rõ phải dừng lựa chọn, không tự top-1 | AC05 valid+empty; thiếu nguồn; work nhiều witness; origin labels, original text/ID, expanded no mutation, gates B–E | Phê duyệt semantics workflow trước API mới. Nếu hướng dẫn+preview đủ thì chưa thêm envelope/schema |
| **P1-d Coverage truy vấn và đối chiếu** — E1/E2, lemma=0, CJK/rows hữu hạn | `search`, `resolve`, `parallels`, `variants`, `compare`; báo route/bound/scope; cân nhắc phân trang opt-in | Bộ query Pāli có/không dấu, Hán >=3 và 1–2, work-ID, parallel bridge: mỗi kết quả/không-hit ghi đúng index/corpus/limit. Tập đối chiếu giữ riêng witness/role; không đánh dấu exhaustive khi bound chạm. Đo recall trong tập đích đã định nghĩa, chưa đặt ngưỡng toàn corpus | retrieval acceptance/CJK/normalization, SC-CBETA bridge, remote routing, provenance, source roles | Chỉ thay search/limit/pagination sau baseline query-set và workload chứng minh bỏ sót. Không build lại corpus chỉ để đẹp số |

P1-a và P1-b đều có căn cứ cụ thể; có thể triển khai thành PR độc lập để kiểm
toán. P1-d không mặc nhiên yêu cầu cải tiến rank hoặc thêm corpus/model.

## 3. P2 — Giảm thao tác kỹ thuật

| Mục / căn cứ | Tái sử dụng và thay đổi tối thiểu | Nghiệm thu đo được đề xuất | Regression bắt buộc | Điều kiện quyết định triển khai |
|---|---|---|---|---|
| **P2-a Preflight và receipts tự ghi** — A/B1/forward root/db/mount/encoding errors | CLI E/LocalHost/context/source_status, logging chuẩn. Một cấu hình host được dùng lại; summary ngắn, raw stdout/stderr/hash được giữ; không framework agent | Cùng môi trường: đo số cấu hình phải gõ, subprocess đã log, bootstrap thiếu log, source reads, wall time. 0 step phụ thuộc chạy tiếp sau run-create lỗi trong smoke scenario. 100% dispatch exit0 nhưng JSON REJECTED/UNVERIFIED được hiển thị đúng. Không hứa giảm thời gian trước phép đo đối chứng | distinct code/source roots; Windows UTF-8/CRLF fallback; missing db/source, WAL, output path, run unknown/stale, CLI defaults | Chuẩn hóa hướng dẫn trước; chỉ thêm orchestration nếu còn nhiều thao tác sau preview. Mount quyền host không bị automation vượt policy |
| **P2-b Evidence Pack local tối thiểu** — dữ liệu đã có nhưng rời | A envelopes + failed bindings/expanded results + D snapshot/trace/export + context; composer/view opt-in, không DB mới | 100% trường trong bảng pack mục 4 workflow có dữ kiện hoặc nhãn chưa có/lý do. Mỗi evidence có identity/gate thật; failed refs không biến mất. Tái mở cùng pin thành công hoặc báo thiếu; 0 cached envelope tự cấp fresh verification. Pack có readable summary và JSON; quyền chia sẻ false | provenance/currentness, metadata vs wording, context span, dependency uncertain, version/reopen/export, fresh output collision, source mất | Prototype bằng compose API hiện hữu trước; chỉ thêm public contract nếu chỉ rõ trường không biểu diễn được. Dữ liệu thật giữ local |

Không lấy số log giảm làm thành công duy nhất. Cần giữ đủ source identity,
status/reason, query/bounds, version và lệnh lỗi. Các helper không được tự
giấu nguồn không kiểm hoặc tạo lịch sử bootstrap không tồn tại.

## 4. P3 — Hồ sơ nghiên cứu và truy vết nhận định

| Mục / căn cứ | Tái sử dụng và thay đổi tối thiểu | Nghiệm thu đo được đề xuất | Regression bắt buộc | Điều kiện quyết định triển khai |
|---|---|---|---|---|
| **P3-a Facts/citation rendering** — title sai chỉ ở prose vẫn lọt, MN/AN title unsupported | `LocalOutputFacts`, `source_identity`, P0/3 và D renderer. Render facts một lần, thêm readers theo collection có selector thật | 0 title/ID/provenance phải gõ lại trong các phần do renderer sinh. Native MN/AN positives, typo negatives và TEI container/subwork được phân biệt; ngoài coverage giữ unavailable. Đo mâu thuẫn giữa prose và fields như lỗi cụ thể, không gọi hết prose CHECKED | Output title/quote/namespace/link/stance tests; N01–N10, stale receipt/render, right source wrong title | Xác minh native heading conventions trên pins trước mở reader. Không fuzzy match, không đổi check syntax thành semantic certificate |
| **P3-b Claim-to-evidence view** — D trace có, narrative còn tách | `trace_claim`, run/history, C results, notes và revision APIs. View “dựa vào đâu/chưa xét gì/đã thay vì sao” | Tập claims khảo sát: từng nhận định quan trọng trong view có claim ID + evidence IDs hoặc UNRESOLVED reason; link đi được tới đúng source/receipt/version. Mọi counter candidate có nhãn đã/chưa xét; sửa claim giữ predecessor. Người audit kiểm đường truy vết mà không phải đọc toàn JSON | B/C/D guards, unsupported/contradicted, scope/condition loss, predecessor/successor, no implicit new claim in synthesis | Thử renderer pack trước. Chỉ thêm dữ liệu nếu D/sidecars hiện hữu thiếu; chưa đổi schema để lưu prose certification |

P3 không thể bảo đảm agent đã nhận diện đủ mọi condition. Tách lỗi identity/
quote/link có thể kiểm máy khỏi lỗi diễn giải cần đánh giá dựa trên nguồn.

## 5. P4 — Kiểm end-to-end trong nhiệm vụ thật

| Mục / căn cứ | Cách thử tối thiểu | Nghiệm thu đo được đề xuất | Regression bắt buộc | Điều kiện quyết định triển khai |
|---|---|---|---|---|
| **P4-a Agent workflow mới** — A/forward contaminated, B1 chưa có đủ đối chứng | Chat mới thật, cùng model/settings được ghi khi khả dụng, baseline/pins/index cố định; tập lookup Pāli/Hán, native-unit rỗng, namespace, cross-witness và conceptual bounded research. Protocol khóa trước; không xem đáp án trước freeze | Ghi từng lần: chọn sai work/witness/key rỗng, sửa locator, dropped required ref, unsupported source, title/prose mismatch, số thao tác, source reads và wall interval cùng clock. Báo số lỗi/mẫu số theo loại; tokens/cost không có giữ NOT_AVAILABLE. 0 nguồn thay ngầm, 0 approval/publication tự cấp là tiêu chí cứng | AC01/04/05/11; output N01–N10; source pins/history/PENDING; Quick/default behavior; negative failure cases | Có P1–P3 baseline so sánh được. Tách nhóm biết regression với nhóm held-out thật; không gọi A/forward cũ là mù hoặc sửa lịch sử thành baseline mới |
| **P4-b Chất lượng và khả năng phản biện** — chưa ground truth độc lập | Reviewer có năng lực phù hợp kiểm cụ thể source/claims khi cần kết luận chất lượng; cơ chế thẩm quyền được xác lập riêng, không recruitment mặc định mỗi run | Đếm lỗi thật được phát hiện/bỏ lọt và phản biện sai trên cùng hồ sơ; phân biệt annotation omission, causal/temporal overreach, mistranslation, false blocking. Không lấy PASS/CHECKED/đồng thuận model làm semantic accuracy | Golden research, B/C/D currentness/authority; claim original và phạm vi giới hạn; rights vẫn đóng | Chỉ thực hiện đánh giá cần nguồn riêng tư khi quyền/capability phù hợp đã có. Thiếu chuẩn thì báo chất lượng chưa xác minh, không trì hoãn mọi draft hữu ích |

Không triển khai model adapter hoặc nhiều agent chỉ để đo P4. Direct Codex
analysis ghi AI_INTERPRETATION ngoài trace P0/2; nếu sau này dùng model host
được phép, ghi trace đó riêng. Không tạo kết quả cho B2/C1–C4 chưa chạy hoặc
gọi khảo sát này là hoàn tất workload experiment.

## 6. Quy tắc đo và quyết định tiếp tục

- Chốt units và mẫu số trước: candidate, native unit, binding, claim, output
  item/document, process record và independent witness là các loại khác nhau.
- Trước thay code, lưu baseline bằng cùng query/input/pin/index và môi trường.
  Đo phần mới với ít nhất một positive, một negative, một ambiguous và một
  thiếu-capability case thích hợp. Không sửa fixture/claim để tránh lỗi.
- Ngưỡng zero silent substitution/false authority là bất biến. Ngưỡng tốc độ/
  source reads/chi phí cần số baseline và quyết định thẩm định; các số 7,007s
  hoặc counts trong audit không phải ngân sách hiệu năng của sản phẩm.
- Giữ toàn bộ regression phù hợp của retrieval/Quick/Research/provenance/
  source reader/A–E/P0/1–P0/3. Lượt full suite tương ứng trước merge code sau
  này; docs-only audit này chỉ chạy 71 tests đã nêu, không nhận phần khác PASS.
- Khi preview/workflow/render giải quyết được blocker, dừng ở thay đổi nhỏ.
  Chỉ thêm resolver/index coverage khi task thật có evidence thiếu; không
  mặc định mở vector RAG, schema/DB hoặc kiến trúc phiên bản mới.

## 7. DEFER có điều kiện

Chưa ưu tiên semantic truth scoring, tự phê duyệt học thuật, agent orchestration,
universal multilingual equivalence, vector DB mới hoặc arbitrary remote CJK.
P0/2 giữ nguyên proposal tùy chọn; Work/Connector cần nghiệm thu riêng nếu có
nhu cầu thực. Những đề xuất này không cho phép xóa Gate A–E hoặc bỏ Final
Claim Gate. Không đổi rights/publication, corpus/pins hoặc lịch sử Pilot.

`HUMAN_ADJUDICATION_PENDING` · `DISTRIBUTION_CLEARED = 0` · `PUBLICATION_NOT_PERMITTED`.
