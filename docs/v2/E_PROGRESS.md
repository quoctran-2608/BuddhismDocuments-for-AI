# Tiến độ E

> **LỊCH SỬ — checkpoint 11/10/2026 tại `1b2d0f010ec2dab8664378516005ed2ad05e4fe6`.**
> Nội dung dưới giữ nguyên 394 tests, main nền D và E chưa merge tại mốc đó.
> Sau đó span fix bổ sung 16 tests; mã A–E gộp tại
> [57db982…](https://github.com/quoctran-2608/BuddhismDocuments-for-AI/commit/57db982274e267218594ae5ca463bd2a42d2be02).
> Trạng thái cuối: [E_REPORT](E_REPORT.md), [ACCEPTANCE](ACCEPTANCE.md),
> [evidence cuối](evidence/README.md). Benchmark ở đây chưa đo lại sau sửa span.


- Nền/main remote vẫn `67eccb4b047365d9ba753de1b0e623542039881d`;
  nhánh `feature/bcr-v2-phase-e`, không PR/merge.
- Hai checkpoint mã đã push: `1d2bf7046f78c6f58f2332f0ab033b8a23f5b5e0`,
  `1b2d0f010ec2dab8664378516005ed2ad05e4fe6` (mã được đo/kiểm cuối).
- E0–E5 phần khả dụng đã làm: 3 resolver nguồn thật, Quick riêng, Research
  draft/D store/C receipts, claim revision mở lại, export/import, portable
  Work/Connector contracts, 11 golden rule cases và benchmark tái sử dụng.
- WSL checkpoint đúng commit: 394/394, không skip/fail/error; A/B/C/D
  44/82/70/77 giữ nguyên. E: 62 portable + 14 corpus thật. Windows A–D và
  E portable đạt; full counted 371 chạy/344 đạt/0 failure/29 error/1 class
  skip, lỗi cũ thiếu nguồn/SQLite cleanup đã đối chiếu baseline.
- E4: lịch sử 1.0 trước A f7415f5; 12/12 retrieval outputs giống, cùng 13 pins
  và index acceptance. Lưu cả 7 và 14 observations, time/CPU/RSS/IO/phases.
  Quick median ~19/74/37 ms cho 1 hit; Research draft ~129 ms, 8 source reads.
- Connector thật: locator b31a1548 → Bilara ghim → hai source fetch → A VERIFIED.
  Work chưa thử. Không có semantic approval xác thực/reviewer hay đáp án học
  thuật độc lập: Research chưa công bố; chất lượng/token/AI cost CHƯA ĐO.
- Tài liệu: E_REPORT, USAGE, evidence raw/logs và ma trận đủ 33 yêu cầu, giữ
  nguyên tiêu chí/số liệu lịch sử A–D. CHỜ CHỐT NGƯỠNG; E chưa nghiệm thu đầy đủ.
- Hoàn tất phần tự thực hiện được; quyết định còn chờ người bảo trì được ghi
  trong E_REPORT. Không tải corpus/package/model, không đổi 1.0/pins/plan A–E.
