# Hướng dẫn chuyên gia — đọc độc lập

Đây là hồ sơ chuẩn bị, không có quyết định chuyên gia sẵn. Người chuẩn bị đã tiếp xúc kết quả AI trước đó; chỉ các kết quả trước bị giữ riêng. Danh mục luận điểm và nguồn được chọn không phải mẫu ngẫu nhiên hoặc thiết kế mù hoàn toàn.

1. Người quản lý xác nhận quyền truy cập tài liệu, đồng ý chia sẻ bài riêng, danh tính/năng lực thật và xung đột lợi ích. Người thẩm định khai rõ đã đọc kết quả AI hay quyết định người khác chưa. Không gửi hồ sơ B trước khi khóa bản nộp.
2. Nhận riêng hồ sơ A. Kiểm SHA256SUMS và manifest của A; chọn đúng case được giao. Ghi tệp, phiên bản, SHA-256 và những phần thực sự đã đọc. Không coi một tệp có trong gói là đã được người chấm đọc.
3. Đọc câu bài gốc cùng ngữ cảnh tối thiểu, mệnh đề nguyên tử và nguồn. Đoạn tiếng Việt là lời tác giả hoặc bản tạm dịch của tác giả; không là bản dịch độc lập. Có ba bản dịch Anh Sujato đã lưu trữ; những nguồn khác yêu cầu đủ năng lực Pāli/Hán. Không tạo bản dịch AI thay phần thiếu. Nếu không đủ năng lực, ghi BLOCKED cho phương diện cần kỹ năng đó.
4. Đối chiếu source SHA/path/locator/witness/edition. JSON values giữ nguyên chữ; TEI line records giữ markup và char offsets, không âm thầm nối/chuẩn hóa. Full nguồn được kèm để kiểm ranh tiểu kinh, header và apparatus. Y32n0030 là tác phẩm biên soạn hiện đại, không tự tính là nhân chứng kinh độc lập. Không hòa hợp các bản khác nhau.
5. Ghi riêng từng claim_id × dimension: SOURCE_IDENTITY (quy thuộc nguồn), VERBATIM (chữ trích), TRANSLATION (dịch), CONTEXT (ngữ cảnh), CLAIM_SUPPORT (hỗ trợ nghĩa), ALTERNATIVES (phản chứng/cách đọc khác), INFERENCE_SCOPE (phạm vi suy luận). Khi một dimension không áp dụng, để label=null, status=NOT_APPLICABLE và giải thích vì sao; không gán nhãn hỗ trợ cho việc không áp dụng.
6. Chọn một nhãn trong rubric dưới, kèm scope, nguồn/vị trí và lập luận. Không dùng một phán quyết toàn ca thay các phương diện khác nhau. Giữ bất định và phản chứng, không ép ra đúng/sai. Không suy chẩn đoán ngược hoặc khái quát toàn truyền thống nếu nguồn không đủ.
7. Nộp bản mới có danh tính, năng lực, xác nhận thực tế và ngày/phương thức xác nhận. Mẫu trống vẫn giữ nguyên. Người quản lý kiểm chứng danh tính ngoài biểu mẫu, lưu chứng cứ xác nhận và SHA bản nộp; một trường JSON tự ghi authenticated không đủ xác thực.
8. Khóa bản nộp rồi mới cho phép đối chiếu hồ sơ B. Người thứ hai làm độc lập trước khi nhìn kết quả của người thứ nhất. Bảo lưu cả bản nộp, SHA, bất đồng và quyết định xử lý sau đó; không sửa đè để tạo đồng thuận giả. Chưa được dùng các biểu mẫu này làm BCR semantic approval hoặc quyền publication.

| Nhãn | Khi dùng |
|---|---|
| SUPPORTED | Chứng cứ đủ cho đúng mệnh đề/phương diện/phạm vi, nêu điều kiện. |
| PARTIALLY_SUPPORTED | Kê rõ phần được và chưa được hỗ trợ. |
| INSUFFICIENT_SUPPORT | Chứng cứ hiện có không đủ, không đồng nghĩa bị phản bác. |
| CONTRADICTED | Có chứng cứ đối lập trực tiếp cho đúng mệnh đề/phương diện. |
| INDETERMINATE | Có những cách đọc hợp lý chưa phân định được. |
| BLOCKED | Thiếu đầu vào bắt buộc hoặc năng lực cần thiết; ghi điều kiện gỡ chặn. |

Các ca có thiếu đầu vào có thể đọc phần đã có để đặt yêu cầu bổ sung, nhưng không được ghi đã thẩm định hoàn tất. Mọi quyết định hiện PENDING. Nguồn mới phải có bản gốc hợp lệ, edition, vị trí, ngữ cảnh, rights và checksum riêng; bổ sung bằng amendment có ngày, không thay protocol đã khóa.
