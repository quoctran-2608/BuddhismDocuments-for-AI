# ADR-0008 — Không materialize vocabulary CJK trigram thành namespace production

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** production key universe
- **Liên quan:** REQ-DER-004, REQ-CON-009, REQ-FAIL-004

## Bối cảnh

Local CJK retrieval dùng FTS5 trigram. Một phép đo read-only trên vocabulary FTS
đã cho thấy:

- 45.740.699 hàng vocabulary tổng;
- 45.721.159 token có chứa ký tự CJK;
- toàn bộ token đo được dài đúng 3 code point do tokenizer trigram.

Các sample như chuỗi pha số/ký tự CJK cho thấy vocabulary này là sản phẩm kỹ
thuật của chỉ mục, không phải danh sách thuật ngữ Phật học có nghĩa.

Ngoại suy lịch sử theo benchmark pointer khi đó cho thấy nếu materialize toàn bộ
vocabulary trigram vào format locator tương tự, quy mô có thể ở cỡ khoảng
0,88–1,55 TB và thời gian sinh tuyến tính thô ở cỡ hàng trăm ngày. Đây là phép
đo/ngoại suy để đánh giá thiết kế, không phải production benchmark hiện tại.

## Quyết định

Production v1 **không** materialize `terms/cjk`.

CJK trigram tiếp tục là hạ tầng truy xuất local. Production v1 chỉ materialize
`terms/latin` và `ids`.

Không được quảng bá vocabulary trigram như “từ điển thuật ngữ Phật học CJK”.

## Lý do

- key universe trigram quá lớn cho format locator hiện tại;
- phần lớn token không tương ứng một khái niệm/thuật ngữ nghiên cứu độc lập;
- materialize chúng vừa tốn storage/time vừa tạo semantic contract sai;
- nhu cầu remote CJK hiện vẫn có thể đi qua exact ID hoặc giả thuyết Latin/Indic
  có căn cứ và các quan hệ đã biết.

## Phương án đã không chọn

### Xuất toàn bộ trigram làm `terms/cjk`

Bị loại vì sai về ngữ nghĩa và không thực tế về quy mô.

### Giả định một danh sách CJK key nhỏ mà không có nguồn tạo rõ ràng

Không chọn vì sẽ tạo coverage tùy ý, khó tái tạo và dễ khiến người dùng hiểu nhầm
là exhaustive.

## Hệ quả

- Connector v1 không hỗ trợ arbitrary exhaustive CJK substring lookup;
- khi route hiện có không đủ phải báo giới hạn;
- local CJK retrieval vẫn giữ khả năng trigram riêng;
- một namespace CJK có nghĩa trong tương lai cần một key-generation method khác,
  không được lấy thẳng FTS vocabulary.

## Khi nào xem xét lại

Xem xét nếu dự án có một nguồn thuật ngữ CJK hữu hạn, có nghĩa, tái tạo được;
hoặc có một cơ chế remote retrieval khác chứng minh được coverage/chất lượng tốt
mà không materialize hàng chục triệu trigram.
