# P0/1 — Receipt kiểm thử mới, 04/11/2026

- [results.json](results.json): kết quả thực chạy, tổng theo module, hash file
  code/test, nguồn trước/sau, mount read-only và đối chứng identity/thời gian.
- [full-suite.stderr](full-suite.stderr): raw unittest log, 432 phương thức OK;
  một class dùng existing-index env SKIP rồi chạy riêng. stdout được thu đầy đủ
  tại [full-suite.stdout](full-suite.stdout), tệp rỗng 0 byte là kết quả thật.
- [pilot-regression.stderr](pilot-regression.stderr): raw log 9 bài Pilot PASS.
- [SHA256SUMS.txt](SHA256SUMS.txt): checksum các tệp trong thư mục này, trừ chính
  danh sách checksum. Chỉ kiểm tính toàn vẹn, không mang thẩm quyền học thuật.

Các JSON raw đầy đủ, stdout/stderr và receipt local mới được giữ dưới
`D:\WORKING\BuddhismDocuments-for-AI\.m\p01-tools\results`; tên/byte/hash nằm
trong `results.json`. Bản công khai bỏ nội dung source/context và nguyên văn
claim pilot từ các observation, chỉ giữ locator/provenance/kết quả đo. Không
phân phối lại hồ sơ pilot khóa hoặc nâng cấp clearance.

Lệnh tái chạy và điều kiện dữ liệu tại [P0_1_USAGE](../../P0_1_USAGE.md).
Full suite dùng temporary exact-byte code copy với link tới 13 checkout ghim,
index acceptance tạm; Pilot dùng index core có sẵn trên image mount
`loop,ro,noload`, unmount sau chạy. Không sửa corpus/index/receipt lịch sử.

Các số liệu chứng minh hành vi phần mềm và định danh nguồn trong phạm vi đã
chạy; không chứng nhận semantic support hoặc nghiệm thu học thuật độc lập.

`HUMAN_ADJUDICATION_PENDING` · `DISTRIBUTION_CLEARED = 0` · `PUBLICATION_NOT_PERMITTED`.
