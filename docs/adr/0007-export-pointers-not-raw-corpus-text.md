# ADR-0007 — Remote production chỉ xuất con trỏ, không sao chép raw text

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** artefact Connector
- **Liên quan:** REQ-EVD-001, REQ-CON-004, REQ-CON-005

## Bối cảnh

Thiết kế remote ban đầu từng thử shard chứa bản sao record/text. Khi local corpus
đã lên khoảng hàng chục triệu record, hướng này tạo một corpus thứ hai cần lưu,
đồng bộ và kiểm provenance.

Mục tiêu Connector thực sự chỉ cần biết file nguồn nào nên mở trước; wording cuối
cùng phải được đọc từ upstream source đã ghim.

## Quyết định

Production remote là **pointer-only**.

Pointer được phép chứa metadata định tuyến và provenance như:

- repository;
- source SHA;
- source blob SHA;
- source path;
- work/segment/sequence;
- evidence class;
- text role;
- witness;
- rank/score/match reasons.

Pointer production không chứa trường `raw_text`.

Sau khi chọn pointer, agent phải mở pinned upstream source và đọc context trước
khi dùng wording làm bằng chứng.

## Lý do

- không sao chép khoảng 50 triệu record sang remote;
- không duy trì corpus thứ hai;
- giảm nguy cơ nội dung remote lệch khỏi source đã ghim;
- buộc runtime giữ nguyên nguyên tắc “pointer không phải evidence”;
- lưu trữ remote dành cho định tuyến, không dành cho nhân bản corpus.

## Phương án đã không chọn

### Full-record remote export làm production

Đã có dưới dạng legacy nhưng không được chọn làm runtime production vì quá nặng
và làm mờ provenance.

### Nhúng trích đoạn ngắn vào pointer

Tiện cho hiển thị nhưng dễ khiến agent dùng excerpt như evidence mà không mở
nguồn và làm xuất hiện thêm một bản sao wording cần đồng bộ.

## Hệ quả

- Connector cần thêm bước mở upstream file/blob;
- source locator phải đủ mạnh để tìm đúng vị trí;
- file upstream quá lớn có thể cần dùng `source_blob_sha`;
- production summary phải có thể kiểm invariant không xuất `raw_text`.

## Khi nào xem xét lại

Chỉ xem xét nếu một yêu cầu runtime có bằng chứng đo lường rõ rằng việc mở source
gốc không đáp ứng được, và giải pháp mới vẫn không làm mất provenance hoặc biến
artefact remote thành corpus thứ hai.
