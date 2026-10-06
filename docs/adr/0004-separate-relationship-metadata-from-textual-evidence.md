# ADR-0004 — Tách metadata quan hệ khỏi bằng chứng câu chữ

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** mô hình bằng chứng
- **Liên quan:** REQ-REL-001, REQ-REL-002, REQ-REL-003, REQ-EVD-001

## Bối cảnh

Một số corpus cung cấp parallel graph, RDF relation, alignment hoặc cầu nối định
danh. Những dữ liệu này rất hữu ích để đi từ tác phẩm này sang tác phẩm khác,
nhưng chúng không tự chứa hoặc xác nhận toàn bộ wording của văn bản đích.

Nếu AI coi “có quan hệ song hành” là “hai đoạn có cùng câu chữ”, hệ thống sẽ
tạo kết luận mạnh hơn dữ liệu.

## Quyết định

Metadata quan hệ và bằng chứng câu chữ là hai lớp khác nhau.

Đặc biệt với SuttaCentral ↔ CBETA, phải giữ ba bước:

```text
SuttaCentral parallel relation
→ SuttaCentral-to-CBETA identifier bridge
→ resolved CBETA textual witness
```

Chỉ bước cuối, sau khi mở và đọc nguồn CBETA thích hợp, mới có thể cung cấp
bằng chứng câu chữ.

Resolver phải fail-closed với định danh/range sai, đảo chiều, malformed hoặc
không giao nhau.

## Lý do

- giữ đúng nghĩa của từng loại dữ liệu;
- tránh biến metadata thành trích dẫn giả;
- cho phép quan hệ hữu ích trong discovery mà không hạ chuẩn evidence;
- làm rõ nơi xảy ra lỗi khi bridge đúng nhưng source resolution thất bại.

## Phương án đã không chọn

### Gộp relation và text vào một khái niệm “evidence”

Dễ dùng nhưng mất khả năng phân biệt “quan hệ tồn tại” với “câu chữ tồn tại”.

### Tự suy nội dung văn bản đích từ ID bridge

Không có cơ sở và vi phạm provenance-first research.

## Hệ quả

- data model phải giữ relation riêng khỏi record text;
- tài liệu và AI workflow phải mô tả đúng loại bằng chứng;
- compare/parallel output không được tự tuyên bố textual identity.

## Khi nào xem xét lại

Chỉ xem xét nếu một nguồn relationship cụ thể về sau cung cấp cả textual witness
đã định vị và kiểm chứng trong cùng artefact; ngay cả khi đó vẫn phải giữ rõ loại
claim mà nguồn đó hỗ trợ.
