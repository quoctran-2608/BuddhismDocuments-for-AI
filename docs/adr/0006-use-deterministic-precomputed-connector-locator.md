# ADR-0006 — Dùng locator tiền tính toán và xác định cho GitHub Connector

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** định tuyến Connector
- **Liên quan:** REQ-CON-003, REQ-CON-006, REQ-CON-007, REQ-CON-008

## Bối cảnh

GitHub Connector không có SQLite local để chạy FTS như CLI. Nếu agent phải tìm
ứng viên bằng cách duyệt repository hoặc GitHub Code Search thì độ bao phủ và độ
ổn định phụ thuộc vào việc GitHub đã index file nào, vào thời điểm nào.

GitHub Code Search không phải một hợp đồng runtime đảm bảo toàn bộ artefact sinh
ra được index đầy đủ hoặc ngay lập tức.

## Quyết định

Production Connector dùng locator được tiền tính toán từ local index.

Hai namespace production v1 hiện hành:

- `terms/latin`: khóa thuật ngữ non-CJK đã chuẩn hóa;
- `ids`: work ID giữ nguyên spelling gốc.

Định tuyến:

```text
production key
→ SHA-256(exact UTF-8 key)
→ hai ký tự hex thường đầu tiên
→ locator/<namespace>/<bucket>/part-000001.jsonl
→ tìm dòng có key khớp chính xác
```

GitHub Code Search không phải cơ chế định tuyến chuẩn.

## Lý do

- đường dẫn từ key tới shard xác định được;
- không phụ thuộc chỉ mục tìm kiếm của GitHub;
- agent không phải quét 256 bucket;
- dễ kiểm thử deterministic;
- có thể thay artefact remote mà không đổi phương pháp nghiên cứu;
- cho phép Connector hoạt động như tầng định tuyến, không thành search engine thứ hai.

## Phương án đã không chọn

### GitHub Code Search làm router

Không có bảo đảm đủ/nhanh cho file sinh tự động và khó coi là dependency runtime
ổn định.

### Duyệt tuần tự các shard

Tốn request, chậm và phá ý nghĩa của locator.

### Chạy SQLite từ xa trong Connector

Không phù hợp capability runtime hiện tại và biến deployment thành dịch vụ
database riêng.

## Hệ quả

- normalization của production key trở thành một phần hợp đồng lưu trữ;
- identifier phải giữ spelling gốc;
- thay hash/namespace/path là thay đổi phiên bản locator;
- config và production manifest phải mô tả runtime đang active.

## Khi nào xem xét lại

Xem xét khi Connector có một cơ chế query ổn định hơn với hợp đồng coverage rõ
ràng, hoặc khi production key space thay đổi đến mức hash-bucket locator không
còn phù hợp. Không thay đổi chỉ vì Code Search tình cờ hoạt động ở một thời điểm.
