# Giao A và nhận bản nộp thật — quy trình chưa thực hiện

PENDING_OWNER_APPROVAL. Chỉ người được chủ dự án chỉ định thực hiện sau phê duyệt riêng; biểu mẫu/JSON tự khai không là thẩm quyền cấp quyền.

1. Duyệt lời hỏi khả năng tham gia không chứa dữ liệu riêng. Xác minh người nhận, năng lực/ngôn ngữ, COI và prior exposure; người đã xem phân tích trước không được tự ghi là blind. Lưu bằng chứng và xử lý role sau duyệt.
2. Trước giao, phải đủ nội dung cho scope, quyền bài và thành phần muốn truyền, đường đọc hợp pháp/đủ ngữ cảnh, người nhận chấp nhận scope, bảo mật/lưu giữ và phê duyệt đúng inventory cuối. Phần AC03/07 thiếu nguồn không được tự chuyển toàn ca thành sẵn sàng.
3. Tạo staging mới đúng ca/người từ allowlist A trong V2. Chỉ trích đoạn cần thiết đã được phép, câu hỏi gốc, biểu mẫu PENDING và nguồn được phép/notices hoặc citation/locator đọc chính thức. Không thay claims hoặc điền quyết định chuyên gia bằng AI. Giữ AC08 survey.
4. Loại B, custodian-analysis, comparison results, historical labels, audit receipts, owner decisions và source-resolution có nhận định trước khỏi A. Không chia sẻ toàn archive folder hoặc toàn owner pack. Kiểm nội dung/inventory cuối rồi lưu hash được duyệt.
5. Giao bằng kênh định danh riêng, hạn chế quyền và thời hạn đã thỏa thuận; không public link/chuyển tiếp. Lưu sự kiện giao thật, xác nhận nhận/thiếu nguồn, điều kiện bảo mật. Không ghi các trường này trước khi có sự kiện.
6. Nhận bản nguyên trạng; xác thực identity và yêu cầu người chấm xác nhận chính bản đã nộp. Lưu file/hash SHA-256, thời điểm có múi giờ, nguồn/version thực đọc và scope. Hash chứng minh bytes, không tự chứng minh identity/chất lượng.
7. Khóa bản nộp trước mở B; nếu có người thứ hai, khóa hai bản độc lập trước trao đổi. Mở B chỉ theo phạm vi được duyệt riêng, ghi sự kiện; giữ bất đồng từng người/dimension. Bản sửa có phiên/hash mới, không ghi đè bản đầu hoặc 259 ô trong hồ sơ khóa.

Mẫu ghi nhận, điền riêng khi có sự kiện thật:

```json
{"case_id":null,"reviewer_verified_identity":null,"identity_confirmation_evidence":null,"received_at":null,"received_file":null,"sha256":null,"review_scope":null,"sources_actually_read":null,"submission_confirmed_by_reviewer":null,"locked_at":null,"locked_by":null,"B_opened_at":null}
```

Intake còn cần: bằng chứng năng lực, ngôn ngữ, COI/prior exposure, scope, chi phí/lịch, kênh và điều kiện confidentiality/retention. Không đăng các câu trả lời lên GitHub. Thời hạn đề xuất phải được owner/người chấm chấp thuận và phù hợp quyền nguồn; thu hồi truy cập khi hết hạn, chỉ ghi việc đã làm thật.

Không tự biến bản nộp thành ground truth, phê duyệt BCR, quyền chia sẻ tiếp hoặc publication approval. HUMAN_ADJUDICATION_PENDING · DISTRIBUTION_CLEARED = 0 · PUBLICATION_NOT_PERMITTED.
