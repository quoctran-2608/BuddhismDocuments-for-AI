# ADR-0009 — Dùng chung xếp hạng truy xuất nhưng không coi rank là thẩm quyền học thuật

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** ranking và lựa chọn candidate
- **Liên quan:** REQ-RET-001, REQ-RET-002, REQ-RET-006, REQ-CON-010

## Bối cảnh

Local search và production pointer generation đều phải quyết định candidate nào
nên được mở trước. Nếu remote tự phát minh một score khác, cùng query có thể dẫn
đến ưu tiên nguồn khác nhau chỉ vì execution mode.

Mặt khác, một score kỹ thuật dù tốt vẫn không thể quyết định câu hỏi học thuật
như witness nào cổ hơn, truyền thống nào đúng hay hai thuật ngữ có thật sự tương
đương.

## Quyết định

Local retrieval và pointer generation dùng chung ngữ nghĩa xếp hạng cốt lõi
(`score_record_match` và quy tắc phá hòa ổn định).

Production selection được phép cân bằng theo corpus và gộp candidate trùng theo
identity đã định nghĩa để một corpus/file không chiếm toàn bộ result set.

Tuy nhiên:

> **Rank chỉ quyết định thứ tự nên mở candidate, không quyết định giá trị học
> thuật của kết luận.**

Claim cuối vẫn phải dựa vào evidence hierarchy, text role, witness, context,
quan hệ nguồn và phạm vi câu hỏi.

## Lý do

- tránh hai hệ xếp hạng khó đồng bộ;
- giữ hành vi local/remote dễ kiểm thử;
- candidate phù hợp hơn được mở trước;
- vẫn bảo vệ ranh giới giữa retrieval quality và scholarly verification;
- cho phép nghiên cứu đa corpus mà không để corpus lớn chiếm hết candidate set.

## Phương án đã không chọn

### Remote có ranking độc lập

Dễ drift và khó giải thích tại sao local/Connector ưu tiên khác nhau.

### Rank quyết định source authority

Sai mô hình: match quality không phải evidence authority và càng không phải
truth score.

### Chỉ lấy top-N toàn cục không cân bằng corpus

Có thể làm nghiên cứu so sánh bỏ mất witness độc lập chỉ vì một corpus nhiều
record hơn hoặc dễ match hơn.

## Hệ quả

- thay scoring cần regression tests cho cả local và pointer generation;
- tài liệu/AI không được mô tả score như confidence học thuật;
- lớp Claim Verification mục tiêu phải hoàn toàn tách khỏi retrieval score.

## Khi nào xem xét lại

Xem xét cách ranking khi test thực tế cho thấy candidate quality kém. Không được
đổi nguyên tắc “rank ≠ scholarly authority” trừ khi khái niệm rank được thay
bằng một mô hình evidence verification khác có hợp đồng rõ ràng.
