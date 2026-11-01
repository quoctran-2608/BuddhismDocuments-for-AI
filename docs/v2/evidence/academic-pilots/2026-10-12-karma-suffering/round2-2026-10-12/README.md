# Academic Pilot 01 — Round 2 (WSL, 12/10/2026)

## Trạng thái nghiệm thu

**CHẤP NHẬN CÓ ĐIỀU KIỆN** như bằng chứng vận hành local của BCR 1.0/Quick 2.0/Research draft. **Học thuật INCONCLUSIVE; publication NOT_PERMITTED.** Đây là bằng chứng lịch sử, không phải software release, benchmark chuẩn, review của chuyên gia hoặc quyền công bố kết luận.

**Kết quả then chốt:** 12/12 ca chạy ở cả 3 luồng; 25/25 phần retrieval 1.0 hiện hành/Quick giống nguyên JSON; Quick A có 45 VERIFIED và 9 UNVERIFIED; P013/P029 được REJECTED/QUOTE_MISMATCH; Research tạo 12 draft, 95 evidence IDs; 57 claim records nhưng chỉ 56 active candidates; 102 C entries nhưng 57 unique search IDs. Semantic approval: 0. Nguyên các số liệu Codex được bảo lưu cùng bản hiệu đính, không viết lại lịch sử.

## Tài liệu và khả năng đối chiếu

- [Báo cáo Round 2 nguyên byte](report-vi.md) — do Codex viết; xem [corrections.md](corrections.md) trước khi diễn giải 102 và 57.
- [Kiểm toán độc lập — public summary](independent-audit.md) và [số liệu đã hiệu đính](corrected-metrics.json): phân biệt cái máy trả về với điều kiểm toán viên suy luận.
- [12 trường hợp](case-results-round2.json), [ma trận truy vấn công khai](execution-matrix-public.json) (đã bỏ nguyên văn bài riêng), [execution policy](execution-policy.json), [main run summary](main-run-summary.json), [unexecuted operations](unexecuted-operations.json).
- [Raw Codex summary chưa chỉnh](round2-summary-original.json), [thời gian đo](runtime-measurements.json), [index manifest đã ẩn path máy](index-manifest-public.json), [source ledger](source-ledger-bindings.json).
- [Danh mục 1.242 artifact](artifact-manifest.json), [SHA-256 toàn bộ 1.243 thành viên khác bảng hash](SHA256SUMS.txt), và [archive integrity/retention](archive-integrity.json).

### Cách kiểm lại khi có raw riêng

1. Lấy ZIP chính xác có SHA-256 `8f035794a659ca045f007d139f2ee8f1270b5c8978e2dacc3a62b5441ee2189a` (59.202.367 bytes); kiểm `sha256sum` trước khi giải nén.
2. Với 1.243 file không kể `SHA256SUMS.txt`, kiểm SHA-256 từng byte theo bảng trong hồ sơ này; kiểm CRC ZIP. Danh mục raw giữ file gốc Word, receipts và SQLite, nhưng **không được đưa các byte riêng tư lên Git**.
3. So `retrieval.stdout` với `quick.stdout.retrieval` cho 25 cặp; đếm 45/9 gate status, kiểm P013/P029 và 24 target controls. Dùng cùng locked matrix gốc, không thay bằng projection.
4. Mở ResearchStore read-only, kiểm integrity, 12 runs/105 snapshots/57 claims/12 packages, 0 reports/0 decisions; phân biệt entries với distinct C search IDs.
5. Để **tái thực thi** cần code `a6707b3...`, đúng source pins, index có scope/FTS tương ứng, ma trận gốc, runtime/harness ngoài repo. Index 12.1GB không ở ZIP: đừng coi việc kiểm hash ZIP là chạy lại đầy đủ.

### Quyền riêng tư và bảo quản

Kho Git công khai chỉ chứa báo cáo/metadata, truy vấn nguồn, checksums và phép chiếu đã che đoạn bài AI. **Không chứa bản Word, quote nguyên văn riêng, source bytes đóng gói, ResearchStore SQLite hay ZIP 59MB.** Tệp ZIP/giải nén hiện thuộc thư mục riêng Google Drive của chủ dự án; đây không phải một archive cấp dự án có chính sách giữ lâu dài. `external_archive_pending` và việc lưu raw dài hạn vẫn là nhiệm vụ chưa đóng. Không đưa link Drive riêng vào Git công khai.

[Trở lại hồ sơ Round 1](../README.md). Mọi kết quả Round 1 giữ nguyên và không bị kết luận Round 2 ghi đè.
