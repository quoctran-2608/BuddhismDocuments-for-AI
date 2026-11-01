# Academic Pilot 01 — nghiệp và khổ đau (12/10/2026)

Hồ sơ **LỊCH SỬ** về nghiệm thu ứng dụng thực tế: BCR kiểm toán một bài viết Phật giáo do AI tạo. Khác software tests A–E; có kiểm source/provenance trong mẫu, **academic acceptance chưa hoàn thành**, chưa chứng minh 2.0 tốt hơn 1.0 cho toàn bài.

Mã/pin main pilot và base correction: `17292dedf86ba9f732be3e99b40d57f37be03739`. Manifest/config ở commit đó giữ authority pins; [source-ledger.json](source-ledger.json) ghi 16 nguồn đã đọc, không thay manifest. Linux/Python 3.12.14/SQLite 3.53.1; local thiếu index/13 nguồn, Connector chỉ lookup/A.

## Tài liệu và trạng thái

- [Báo cáo hiệu đính](report-corrected.md): IA-01–IA-05, giới hạn và đề xuất.
- [Work v1 public projection](report-work-v1.md): giữ lỗi/phán quyết lịch sử; che cột full article và đường dẫn workspace. V1 nguyên byte SHA-256 `aabd4e58de4564f20220a31abbe5f466a6f82fcaeae6cf8079974ce1f02b6cbe` giữ riêng; đây không phải checksum-equal copy.
- [Audit độc lập](independent-audit.md): nguyên byte; phiên ChatGPT độc lập, không chuyên gia con người. SHA-256 `b3d161b6829de90497a9a8987bc5e8702e6879a73a695ca28905b6dfdfa38d13`.
- [Correction Log](corrections.md), [protocol](protocol.json), [12 case results](case-results.json), [execution matrix](execution-matrix.json).
- [Claim inventory 104 mục (đã che nguyên văn)](claim-inventory-summary.json): nhãn sơ bộ của Work; không phải lượt BCR Research.
- [Source ledger](source-ledger.json), [offline structural correction check](supplementary-checks.json), [evidence manifest](evidence-manifest.json).

15 gate lịch sử = 13 source-generated controls VERIFIED + 2 article quote inputs REJECTED. `0453a01` của T02n0100 thuộc kinh 212; không dùng nó cho kinh 211. Registry 104 là kiểm kê AI, không Research assessment. Local 1.0/Quick/Research BLOCKED; semantic FA/FR INCONCLUSIVE; benefit CHƯA ĐO; publication NOT_PERMITTED.

## Tái lập có giới hạn

Kiểm JSON và hashes file Git theo manifest. Mở upstream repository/path tại source pin, tính SHA-256/Git blob SHA; đối chiếu TEI mulu 211 `0452b04–0452c16`, mulu 212 `0452c17` và line `0453a01`. Danh sách kinh 211 ở `0452c01–02`. Không lấy file work_id làm subwork ID. Đối chiếu dấu câu/lb của T99 tại `0253a06–07`, và hai title Bilara 35.145/35.146.

Để tái lập đủ 15 A checks cần code tại tested commit và raw archived inputs/receipts. Chỉ bản báo cáo audit offline replay được cung cấp, không scripts/raw receipts riêng của auditor. Không replay source cache rồi gọi live. Raw lớn và bài riêng không ở Git; `external_archive_pending` là giới hạn truy cập lâu dài, không tuyên bố lưu đầy đủ trên Git. Xem [USAGE](../../../USAGE.md) và [tiêu chí nghiệm thu](../../../ACCEPTANCE.md) trước lượt chạy WSL; không tự cấp approval.

Giữ nguyên [evidence E lịch sử](../../README.md), không chuyển ma trận dự án sang PASS. PR này chỉ chờ chủ dự án và kiểm toán độc lập review, không tự merge.

## Vòng 2 — thực thi BCR local trên WSL

[Round 2: thực thi WSL và kiểm toán độc lập, 12/10/2026](round2-2026-10-12/README.md).
12/12 ca có retrieval, Quick và Research draft; 25/25 cặp retrieval 1.0 hiện hành/Quick giống nhau.
Bài toán semantic vẫn INCONCLUSIVE, publication đóng; raw ZIP riêng không công khai.
Hồ sơ Round 1 phía trên được giữ nguyên về mặt lịch sử.
