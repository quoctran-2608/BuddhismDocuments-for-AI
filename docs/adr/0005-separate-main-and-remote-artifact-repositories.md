# ADR-0005 — Tách repository chính khỏi repository artefact Connector

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** tổ chức repository và runtime từ xa
- **Liên quan:** REQ-CON-001, REQ-CON-002

## Bối cảnh

Repository chính chứa kiến trúc, luật nghiên cứu, parser, schema, CLI, tests và
cấu hình. Artefact phục vụ Connector có thể gồm hàng trăm file locator lớn và
được sinh lại từ local index.

Đặt artefact lớn vào cùng repository mã nguồn làm lịch sử Git nặng hơn và làm mờ
ranh giới giữa “hệ thống điều khiển” với “dữ liệu phân phối dẫn xuất”.

## Quyết định

Duy trì hai repository do dự án quản lý với vai trò khác nhau:

### Repository chính

`quoctran-2608/BuddhismDocuments-for-AI`

Là nơi chuẩn của kiến trúc, phương pháp, config, schema, code, tests và docs.

### Repository artefact từ xa

Được khai báo qua `config/remote-corpus.json`; hiện là
`quoctran-2608/BuddhismDocuments-for-AI-remote`.

Chỉ chứa artefact dẫn xuất phục vụ Connector và không phải corpus Phật học thứ
14 hay nguồn chuẩn của câu chữ.

## Lý do

- giữ repository mã nguồn gọn và dễ review;
- cho phép artefact production thay đổi vòng đời độc lập;
- làm rõ remote repo có thể tái tạo;
- tránh AI hiểu locator/shard là nguồn học thuật;
- Connector có thể tìm runtime hiện hành qua một config máy đọc.

## Phương án đã không chọn

### Đặt toàn bộ artefact vào repository chính

Tăng khối lượng Git và trộn control plane với dữ liệu phân phối.

### Dùng remote repo như mirror đầy đủ của corpus

Tạo corpus thứ hai, tăng chi phí storage và nguy cơ lệch với upstream.

## Hệ quả

- mọi agent Connector phải đọc `config/remote-corpus.json`;
- production manifest/summary ở remote repo mô tả artefact thực tế;
- main repo vẫn là nơi mô tả kiến trúc, còn upstream pinned repositories vẫn là
  nơi chứa evidence.

## Khi nào xem xét lại

Xem xét nếu GitHub không còn là kênh runtime hoặc cơ chế phân phối artefact thay
đổi căn bản. Dù vậy, ranh giới “control/source-of-method” và “derived access
artefact” vẫn nên được giữ.
