# BCR Academic Pilot 01 — verified-evidence bootstrap

**Trạng thái:** LỊCH SỬ / kiểm toán sơ bộ; **chưa nghiệm thu học thuật**.

**Bài đầu vào:** “Nghiệp và khổ đau: Có phải mọi khổ đau đều do nghiệp quá khứ?” (bản Word do chủ dự án cung cấp). Mục đích là khảo sát khả năng BCR hỗ trợ kiểm tra nguồn kinh, câu trích, dẫn chứng và lập luận trong bài viết Phật giáo do AI tạo ra.

**Mốc mã:** `quoctran-2608/BuddhismDocuments-for-AI` tại `17292dedf86ba9f732be3e99b40d57f37be03739` (mốc nền, không phải mã được chạy lại tại thời điểm commit hồ sơ). Production locator tham chiếu: `b31a154863c347f150a3bbb2df8bf269b50aeade`. Source pins phải lấy từ `manifest.json` đúng commit; không dùng thông tin văn xuôi làm nguồn chuẩn.

## Kết quả có bằng chứng đến ngày 12/10/2026

- Manifest bên trong gói Work có **275/275 mục SHA-256 khớp** khi kiểm lại trên bản gói được cung cấp.
- Mười sáu source artifacts trong source ledger đã được đối chiếu với Git blob SHA tương ứng ở upstream ghim trong lần kiểm toán độc lập; đây là kiểm chứng provenance, không phải thẩm định ngữ nghĩa.
- Bộ **15 phép kiểm A** trong gói có 13 `VERIFIED` và 2 `REJECTED`; một lượt **offline replay** riêng tái lập 15/15 trạng thái. Đây **không phải** 15 lần Connector live mới.
- **Chỉ 2 lượt** cung cấp trực tiếp câu trích từ bài viết; cả hai bị từ chối về quote-verification theo hợp đồng hiện hành. **13 `VERIFIED` là source-generated controls**, không phải 13 trích dẫn của bài được phê duyệt.
- Local 1.0, Quick local và Research A/B/C/D trong môi trường Work thiếu checkout nguồn/index: `BLOCKED`. Chưa có so sánh thực nghiệm 1.0–2.0 trên cùng corpus/index, chưa có ground truth chuyên gia cho độ đúng luận điểm, chưa đo semantic false acceptance/false rejection.
- Vấn đề đối chiếu Hán kinh **211/212** và mismatch do dấu câu/cắt span được mô tả tại [independent-audit-summary.md](independent-audit-summary.md). Kết luận bản Work v1 cần hiệu đính, không được dùng như approval.

## Tệp đã lưu và các tệp còn chờ

- [independent-audit-summary.md](independent-audit-summary.md): kết luận kiểm toán và điều phải hiệu đính (bản tóm lược, không thay thế báo cáo kiểm toán đầy đủ).
- [integrity-and-status.json](integrity-and-status.json): hashes, số lượng được kiểm và ma trận khả năng nghiệm thu, có mốc.
- **Chưa commit:** Word đầu vào; `BCR_Pilot01_Audit_Package.zip`, `BCR_Pilot01_Evidence.tar.xz`, 59 bộ RPC receipts và toàn bộ raw corpus/mã nguồn snapshot. Xem SHA-256 trong integrity index; các hash không tương đương việc có nơi lưu trữ ngoài Git ổn định.

## Phối hợp với ChatGPT Work

Thư mục được tạo từ nhánh **bootstrap riêng** để không xung đột với đợt Work đang tạo bản báo cáo `report-corrected.md`, `case-results.json`, `source-ledger.json` và README chính thức. Sau khi Work bàn giao branch/PR, đối chiếu và hợp nhất các nội dung không trùng bằng review; không merge hai PR một cách máy móc.

**Không sửa mã, không đổi corpus/source pins, không phát hành Research, không coi kết quả kiểm toán AI là thẩm định chuyên gia.** Nội dung bootstrap này không thay thế `docs/v2/ACCEPTANCE.md`, `docs/v2/evidence/README.md` hay tài liệu thẩm quyền hiện hành.
