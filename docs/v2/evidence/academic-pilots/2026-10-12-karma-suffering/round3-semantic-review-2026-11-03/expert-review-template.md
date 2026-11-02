# Mẫu quyết định thẩm định một luận điểm

Trạng thái hiện tại HUMAN_ADJUDICATION_PENDING. Đây là biểu mẫu ngoài BCR, không JSON approval hoặc host capability. Không điền tên/ngày/chữ ký thay người thật.

## Danh tính và độc lập

- Review ID và case/atomic claim ID:
- Tên người thẩm định:
- Vai trò/cơ quan và năng lực Pāli/Hán/chuyên ngành liên quan:
- Người được ứng dụng/chủ dự án xác thực danh tính, phương pháp và thời điểm xác thực:
- Quan hệ với tác giả/người đề xuất, xung đột lợi ích:
- Đã đọc kết quả AI/vòng trước chưa, ở thời điểm nào:
- Ngày/giờ/múi giờ thực xác nhận:

## Input binding

- SHA-256 giao thức Round3 và review-matrix được đọc:
- Case và đúng mệnh đề được xem xét; trích đoạn chỉ lưu trong hồ sơ riêng:
- Source repository/pin/blob/path/edition/witness/segment hoặc TEI line:
- Nguồn bổ sung (quyền truy cập, phiên bản, URL/locator, ngày đọc thực và hash):
- Đã đọc đủ ngữ cảnh nào; phạm vi nào chưa đọc:

## Đánh giá các tầng riêng

| Tầng | Quyết định/chưa xác định | Chứng cứ vị trí cụ thể | Giới hạn |
|---|---|---|---|
| Source presence | | | |
| Exact quotation / editorial normalization | | | |
| Translation / paraphrase | | | |
| Source attribution / edition / subwork | | | |
| Claim support | | | |
| Counterevidence relevance / adequacy | | | |
| Source dependence / independence | | | |

## Quyết định có lý do

- Đồng ý / sửa / bác / chưa thể phân định đối với nhãn AI nào:
- Nhãn semantic chọn: SUPPORTED / PARTIALLY_SUPPORTED / INSUFFICIENT_SUPPORT / CONTRADICTED / INDETERMINATE / BLOCKED:
- Lập luận, bao gồm điều kiện/ngữ cảnh và liên hệ từng tiền đề với chứng cứ:
- Văn bản gốc / bản dịch / chú giải / tác giả / AI được tách thế nào:
- Phản chứng hoặc cách đọc đối lập và cách xử lý:
- Nội dung/bản dịch/citation đề nghị sửa, phạm vi không được suy rộng:
- Bất đồng với người thẩm định khác; ý kiến thiểu số cần bảo lưu:
- Việc còn thiếu và mức tự tin có lý do (không % giả):
- Chữ ký/xác nhận thật và tài liệu chứng minh quyền xác nhận:

Một quyết định chuyên gia có danh tính thật vẫn cần host tích hợp và kiểm binding/currentness theo BCR nếu muốn dùng trong phần mềm. Biểu mẫu này không tự tạo semantic approval, claim acceptance hoặc Research publication; publication gate giữ nguyên.
