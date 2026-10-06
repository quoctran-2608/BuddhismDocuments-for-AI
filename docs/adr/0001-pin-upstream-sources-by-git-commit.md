# ADR-0001 — Ghim nguồn upstream bằng commit Git

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** tầng nguồn
- **Liên quan:** REQ-SRC-001, REQ-SRC-002, REQ-SRC-003

## Bối cảnh

Dự án tổng hợp 13 repository Phật học khác nhau. Nội dung của các repository
upstream có thể tiếp tục thay đổi theo thời gian, trong khi một kết luận nghiên
cứu cần có khả năng trả lời chính xác “đã đọc phiên bản nào”.

Nếu chỉ lưu URL hoặc branch như `main`, cùng một truy vấn có thể cho kết quả
khác ở hai thời điểm mà không biết nguyên nhân.

## Quyết định

Mỗi nguồn upstream được quản lý như một source repository/submodule bất biến
trong phạm vi một lần build/nghiên cứu và được ghim bằng commit SHA.

`manifest.json` là nguồn chuẩn máy đọc cho danh sách nguồn và SHA. Trong local
mode, SHA thực tế phải được so với hợp đồng nguồn trước khi coi dữ liệu là hợp lệ.

Không sửa dữ liệu bên trong các source repository như một phần của pipeline
nghiên cứu.

## Lý do

- tái tạo được corpus đã dùng;
- truy nguyên được câu chữ về đúng phiên bản;
- tránh thay đổi upstream âm thầm làm thay đổi kết quả;
- tách rõ “nguồn gốc” khỏi parser/index/artefact do dự án sinh ra;
- cho phép fail-closed khi source thiếu hoặc sai SHA.

## Phương án đã không chọn

### Chỉ theo dõi branch/tag upstream

Không đủ mạnh vì branch/tag có thể di chuyển.

### Sao chép toàn bộ nội dung vào một corpus mới do dự án sở hữu

Làm mất ranh giới nguồn gốc, tăng chi phí đồng bộ và dễ tạo “nguồn thứ hai”
không còn phản ánh upstream.

## Hệ quả

- cập nhật nguồn là một thay đổi có chủ đích và phải đổi SHA;
- artefact dẫn xuất phải mang provenance về source SHA;
- local checkout thiếu Git object cần thiết không được tự tải để lấp khoảng trống
  trong research mode offline.

## Khi nào xem xét lại

Chỉ xem xét lại nếu Git commit SHA không còn đủ để định danh bất biến nguồn,
hoặc upstream chuyển sang cơ chế phát hành có định danh nội dung mạnh hơn mà vẫn
giữ được tính tái tạo và provenance tương đương.
