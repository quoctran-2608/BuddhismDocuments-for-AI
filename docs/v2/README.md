# Buddhist Corpus Research 2.0

Mã A–E đã gộp vào `main` tại
[57db982274e267218594ae5ca463bd2a42d2be02](https://github.com/quoctran-2608/BuddhismDocuments-for-AI/commit/57db982274e267218594ae5ca463bd2a42d2be02).
Đây là lớp bổ sung sau retrieval 1.0, giữ nguyên pins/index/ranking/CLI cũ:
A kiểm bằng chứng/câu trích, B kiểm luận điểm, C phản chứng/độc lập nguồn,
D hồ sơ/lịch sử/phản biện, E host adapters/CLI/tích hợp.

Quick kiểm nguồn ghim qua Bilara JSON, CBETA TEI, 84000 TEI. Research local tạo
draft, candidate claims, C receipts, version/history và package review. Một ca
GitHub Connector thật đạt A VERIFIED. **Research publication vẫn đóng**: chưa
có semantic approval xác thực, ground truth hay phản biện độc lập thực tế.
Work chưa thử phiên thực; toàn Connector và các định dạng ngoài ba resolver
chưa nghiệm thu. Hoàn thành mã không đồng nghĩa hoàn thành nghiệm thu 2.0.

## Chọn tài liệu

| Nhu cầu | Tài liệu và vai trò |
|---|---|
| AI mới | [AI_ONBOARDING](../AI_ONBOARDING.md): hai trục môi trường/quy trình, module và trust boundaries |
| Chạy CLI/Python/Connector | [USAGE](USAGE.md): giao diện hiện hành, callback host và lỗi thường gặp |
| Kết quả/giới hạn kỹ thuật | [E_REPORT](E_REPORT.md): báo cáo có mốc; [evidence](evidence/README.md): raw logs/JSON và provenance commit |
| Yêu cầu sản phẩm | [PRD](PRD.md): chuẩn tắc, còn tiêu chí chưa đạt |
| Ngữ nghĩa/hợp đồng dữ liệu | [DESIGN](DESIGN.md): nguồn chuẩn thiết kế; code validators/tests quyết định hình dạng API thực tế |
| Bộ yêu cầu | [REQUIREMENTS](REQUIREMENTS.md): 31 gốc + 2 bổ sung = 33 mã, giữ nguyên tiêu chí |
| Đạt tới đâu | [ACCEPTANCE](ACCEPTANCE.md): trạng thái từng yêu cầu, bằng chứng phần mềm khác nghiệm thu học thuật |
| Lý do/thứ tự triển khai | [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md): kế hoạch năm giai đoạn A–E, giữ bối cảnh trước A và có cập nhật trạng thái |
| Checkpoint cũ | [E_PROGRESS](E_PROGRESS.md): lịch sử 1b2d0f0, 394 tests và benchmark trước sửa span |

[Evidence cuối](evidence/README.md) ghi WSL 410/410 và Windows E portable 78/78;
Windows full chưa đạt. Benchmark E1/E2 mẫu và E3 draft cost thuộc checkpoint
trước sửa span; chất lượng học thuật/token/chi phí AI chưa đo, ngưỡng chưa chốt.

PRD/DESIGN/REQUIREMENTS vẫn mang tiêu chí **MỤC TIÊU** ở phần chưa đủ nghiệm
thu; không đổi đồng loạt thành HIỆN HÀNH chỉ vì có code/fixture. Các phần A–E
trong ACCEPTANCE chứa mốc lịch sử riêng; dùng trạng thái đầu trang và ma trận
để đọc hiện trạng, không lấy câu “chưa triển khai” tại mốc A làm hiện trạng E.

Luật: [AGENTS](../../AGENTS.md) → [SKILL](../../.codex/skills/buddhist-corpus-research/SKILL.md).
Nền 1.0: [CLI](../CLI.md), [ARCHITECTURE](../ARCHITECTURE.md),
[REQUIREMENTS](../REQUIREMENTS.md), [ACCEPTANCE](../ACCEPTANCE.md).
Nguồn thẩm quyền tài liệu: [GOVERNANCE](../DOCUMENTATION_GOVERNANCE.md).
