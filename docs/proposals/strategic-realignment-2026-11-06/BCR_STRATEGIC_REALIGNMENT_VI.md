# BCR — Đề xuất điều chỉnh trọng tâm nghiên cứu

Ngày 06/11/2026, Asia/Bangkok. **ĐỀ XUẤT CHỜ THẨM ĐỊNH**; không thay tài liệu
chuẩn hiện hành, hợp đồng API hoặc quyền của các gate.

## Quyết định định hướng

BCR tập trung làm **hạ tầng dữ liệu, truy xuất và chứng cứ cho AI Research
Agent nghiên cứu Phật học**: tìm đúng nguồn, đọc đúng đoạn và ngữ cảnh, giữ
riêng nhân chứng/bản dịch/chú giải/metadata, kiểm câu trích và provenance, tổ
chức chứng cứ để tái sử dụng và phản biện.

AI Research Agent chịu trách nhiệm đề xuất giả thuyết, phân tích, diễn giải,
lập luận và tìm cách phản bác chính mình. BCR cung cấp dữ kiện và giới hạn có
thể kiểm; BCR không xác nhận toàn bộ lập luận ngữ nghĩa của agent là đúng.
Thẩm định học thuật cần thẩm quyền phù hợp; cơ chế ấy không được sinh ra từ
nhãn của AI, đồng thuận hai lượt model hoặc số test PASS.

Định hướng này phù hợp với phần hạ tầng đã mô tả trong
[PROJECT_SPEC](../../PROJECT_SPEC.md). Thay đổi cần thiết là **ưu tiên sản phẩm
và cách diễn đạt năng lực**: làm đường lấy chứng cứ dễ dùng trước; duy trì
kiểm chứng và lịch sử đã có; không biến mục tiêu đầy đủ trong
[DESIGN](../../v2/DESIGN.md) thành lời hứa phần mềm đã đạt.

## Căn cứ của đề xuất

Đã kiểm remote `main` và tạo nhánh mới từ đúng baseline
`dfdd3cbb79e3dbfb49a855702fa00e4bad3b3410`. Git tree
`f56fd057785c8a5ee35c66b4040027fb0150a208` giống cây triển khai P0/3
`06c497842127e656abfd6a387ac1c254a465a727`. Điều này được xác minh ở lần khảo
sát này, không sửa lại lời khai thiếu merge object của các thí nghiệm cũ.

Khảo sát code, nguồn và hồ sơ cho thấy:

- P0/1 đã mở nguồn được khai báo mà không dùng lexical fallback; nhưng agent
  vẫn có thể khai một native key rỗng trước khi tạo claim binding.
- A, B, C, D, E có trách nhiệm riêng và hữu ích. B/C kiểm hợp đồng và đọc
  assessment qua host; chúng không tự hiểu toàn bộ nghĩa của văn bản.
- P0/3 bảo vệ fields/links đã đưa vào contract. Văn xuôi sai hoặc điều kiện
  bị bỏ sót từ notes vẫn có thể `CHECKED`.
- Nguồn local có đủ 13 pin nhưng index Pilot hiện dùng chỉ có ba corpus.
  Một scope nhiều corpus bị chặn; probe index tạm cùng build profile `core`
  tái hiện sự lẫn giữa phiên bản parser và profile trong `LocalHost.scope`.
- A/B1 và forward test chỉ cho bằng chứng vận hành có giới hạn. A bị nhiễm
  ngữ cảnh, forward test không mù hoàn toàn; không có cơ sở so chất lượng
  4/2/1 claim hoặc tuyên bố AI hiểu giáo lý tốt hơn theo phần trăm.

Chi tiết, mức xác nhận và bằng chứng nằm ở
[kiểm toán năng lực](BCR_CAPABILITY_AUDIT.md). Không đưa raw source, bài riêng
tư, semantic notes hoặc hồ sơ Pilot lên PR đề xuất này.

## Hợp đồng năng lực đề xuất

| BCR chịu trách nhiệm | AI Research Agent chịu trách nhiệm | Chưa được tự cấp |
|---|---|---|
| Lọc/định tuyến ứng viên và công bố phạm vi index | Đặt câu hỏi, chọn hướng tìm có căn cứ | Bao phủ toàn bộ truyền thống/corpus |
| Mở đúng repository/pin/path/unit/witness qua reader | Đọc đủ ngữ cảnh cho vấn đề đang xét | Đúng ngữ nghĩa chỉ từ A VERIFIED |
| Kiểm nguyên văn/chuẩn hóa bảo toàn nội dung | Dịch nghĩa, xác định speaker/stance/điều kiện | Ground truth từ annotations của chính AI |
| Giữ role/class, provenance, relation và phiên bản | Đánh giá giá trị hỗ trợ/phản bác, giữ bất đồng | Nguồn độc lập chỉ từ số citations |
| Lưu snapshot, trace, links và kiểm currentness | Viết proposal có giới hạn, tự phản biện | Academic acceptance hoặc publication |

Ngay cả phép kiểm A cũng có phạm vi: resolver chỉ hỗ trợ ba định dạng hiện
có, quote là span liên tục trong nguồn, không tự nối markup/escaped text.
`PARAPHRASE` cần review capability phù hợp; nó không phải phép so chuỗi tất
định chứng minh diễn đạt đúng. Các trường thiếu không được điền bằng AI.

## Giữ P0/1–P0/3 và Gate A–E

| Thành phần | Vai trò trong định hướng mới |
|---|---|
| P0/1 | Đường kiểm nguồn **đã khai báo**. Giữ fail-closed, nguyên văn claim và phân biệt DECLARED/EXPANDED. Đặt preview ứng viên trước binding; không đổi nguồn bắt buộc thành tùy chọn khi lỗi. |
| P0/2 | Pipeline support/challenge **proposal tùy chọn** khi có model host được phép; thiếu model ghi đúng chưa chạy. Không là điều kiện để mọi lookup có ích và không là semantic approval. |
| P0/3 | Kiểm title/quote/namespace và links đã ghi, ưu tiên render facts từ nguồn để giảm gõ lại. Giữ giới hạn free prose/notes đầu vào. |
| A | Thẩm quyền nguồn/đoạn/câu trích trong capability thực. |
| B | Claim, assessment binding, lịch sử sửa và Final Claim Gate. Không hạ điều kiện nhận `accepted`. |
| C | Kế hoạch/phạm vi/biên nhận tìm phản chứng, quan hệ nguồn và assessment qua host. Hit chưa đọc không là phản chứng đã xét. |
| D | Snapshot/version/history/trace và gói phản biện; dữ liệu lưu không thay fresh reader. |
| E | Tổ chức các capability/CLI/Local/Connector; giữ policy host và cửa công bố. |

## Dự thảo khám phá có thể hữu ích ngay

Có thể tạo hồ sơ dự thảo minh bạch khi chưa hoàn thành nghiệm thu học thuật:
`LocalHost.quick` cung cấp evidence A cho lookup; `LocalResearch`, D và
`export_review` đã hỗ trợ draft/capture/trace. Accepted set có thể rỗng và B/C
còn `UNVERIFIED`. Hồ sơ trình bày những gì đã đọc, proposal, phản biện đã/chưa
xét và các thiếu hụt; không gọi đó là accepted synthesis.

Đây là cách sử dụng trạng thái **draft** sẵn có, không thêm mode, không bỏ qua
Final Claim Gate và không cho phép xuất nguồn riêng tư ra ngoài. Việc tạo
artifact local hoặc PR tài liệu hạ tầng không mở publication gate của Research.
Chi tiết luồng và Research Evidence Pack:
[BCR_TARGET_WORKFLOW](BCR_TARGET_WORKFLOW.md).

## Ba cải tiến nên làm trước

1. **Preview và kiểm ứng viên ở mức native segment trước binding.** Hiển thị
   rỗng/không rỗng, khả năng giải span, role, witness và nguồn thay thế có nhãn.
   Lỗi MN 135 lặp ở nhiều phiên là căn cứ trực tiếp. Tái sử dụng
   `source_resolvers`, `LocalHost.source_reader/verify_pointer`,
   `verify_declared_source`, `retrieval.work/evidence`.
2. **Tách rõ khám phá khỏi nguồn bắt buộc, kèm preflight/coverage dùng chung.**
   Sửa chẩn đoán profile sau khi kiểm toán, giảm cấu hình root/db/mount lặp,
   giữ receipt và yêu cầu làm rõ khi mơ hồ. Tái sử dụng `LocalHost.scope`,
   `state_parser_version`, `source-search`, P0/1 và CLI E; không đổi ranking
   mặc định hoặc tự bỏ reference bị lỗi.
3. **Gom Research Evidence Pack và báo cáo dễ đọc từ dữ liệu đã có.** Một bản
   nhìn nối question → query/candidate → A evidence/context → claim/proposal →
   phản biện/giới hạn; title/ID/citation được render từ fields nguồn. Tái sử
   dụng `retrieval.evidence`, A envelopes, D snapshot/trace/export và P0/3.
   Trước hết cải thiện orchestration/render; chưa có lý do tạo DB/schema mới.

Tiêu chí đo, kiểm hồi quy và điều kiện triển khai từng mục nằm ở
[roadmap](BCR_PRIORITIZED_ROADMAP.md); những thay đổi tài liệu/API có điều kiện
nằm ở [migration impact](BCR_MIGRATION_IMPACT.md). Không đặt tên phiên bản mới.

## Phạm vi bàn giao này

Chỉ thêm tài liệu đề xuất và bằng chứng kiểm toán đã rút gọn. Không sửa code,
tests, skill, AGENTS, schema, index/corpus, pin, hồ sơ lịch sử hay gate. Chạy
kiểm chọn lọc và probes để xác nhận hiện trạng; không triển khai roadmap.
Draft PR dành cho thẩm định thiết kế, không tự merge.

`HUMAN_ADJUDICATION_PENDING` · `DISTRIBUTION_CLEARED = 0` · `PUBLICATION_NOT_PERMITTED`.
