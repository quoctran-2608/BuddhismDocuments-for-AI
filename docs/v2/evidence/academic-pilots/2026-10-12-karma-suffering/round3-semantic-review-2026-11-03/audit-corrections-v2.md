# Round 3 v2 audit corrections

Hiệu đính theo nhận xét độc lập trên [PR #5](https://github.com/quoctran-2608/BuddhismDocuments-for-AI/pull/5#issuecomment-6590966665), head được kiểm `1a533c1aeb13a4962f877f3f383b59170be3b8e7`. Đây là finalization Round3, không Round4, không chạy lại Round2.

- AC04 giữ nhãn hiển thị CONTRADICTED nhưng giới hạn ngay cạnh nhãn vào **mệnh đề định danh nguồn trong hệ Bilara/SuttaCentral ghim**. semantic_verdict riêng là NOT_ADJUDICATED_AS_DOCTRINAL_CONTRADICTION. Alias lịch sử và nội dung giáo lý chưa bị phán bác bỏ.
- AC01/11/12 bổ sung atomic_claim, supported_claims với vị trí, conditions_or_limits, unconfirmed_parts và verdict_scope. SUPPORTED chỉ cho các báo cáo văn bản hẹp đã liệt kê, không phê duyệt toàn đoạn/toàn bài.
- AC02/03 giữ REJECTED/QUOTE_MISMATCH. Phân tích chữ, chấm câu, markup, edition và ngữ nghĩa không đổi gate sang VERIFIED.
- AC08 giữ câu hỏi lịch sử, thêm question_premise_difference: chữ chỉ ở câu hỏi kiểm toán, không có trong ô bảng gốc. Không quy phát biểu mạnh hơn cho tác giả.
- AC07 giữ BLOCKED_MISSING_SOURCE. AC11 giữ selector5.6 vắng; AC12 giữ6.1 là đề mục và33.3–33.5 là locator bổ sung, không hồi tố sửa nguồn/gate.
- AC05/06/09/10 giữ các kết luận sơ bộ có giới hạn; làm rõ dimension/phạm vi suy luận, không thêm nguồn hoặc phê duyệt học thuật.

Không đổi nhãn hiển thị12 ca; đổi cách trình bày để loại sự mơ hồ về đối tượng được chấm. Không có expert ground truth, accuracy hoặc semantic approval mới.

## Đối chiếu số kiểm tra

81 là bộ kiểm tra nền trước khi thêm3 kiểm tra;84 là bộ cuối được lưu trong validation.json của gói V1. Ba kiểm tra thêm là kiểm17 snapshot đã kèm gói, khớp byte/blob public trên GitHub và phạm vi Draft PR chỉ thêm tài liệu. Mô tả PR cũ81 đã lỗi thời. Không đồng nhất84 boolean checks với9 checksum entries công khai hoặc140 tệp gói riêng.

Hồ sơ gốc có JSON81-check FAIL (scanner nhận nhầm https), JSON83-check FAIL (CRLF/LF) và JSON84-check PASS. Không có standalone81-PASS log được lưu; không dựng lại hoặc gán thời gian giả cho lượt đó.81 checks nền đều PASS trong receipt84 cuối, nhưng điều đó không tái tạo lượt81 lịch sử. [validation-reconciliation-public](validation-reconciliation-public.json) kê tên/nhóm/thời điểm/SHA và mức bằng chứng.

Raw/Word/notes riêng được giữ ngoài Git. Gói V1 và báo cáo gốc được bảo toàn trong lịch sử riêng; bản hiệu đính là V2 có manifest/checksum/ZIP mới. Không thay code/tests/config/pins/index/Research mechanism/publication gate. Giữ Draft, không merge.

SEMANTIC_REVIEW_PROVISIONAL · HUMAN_ADJUDICATION_PENDING · PUBLICATION_NOT_PERMITTED.
