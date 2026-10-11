# Buddhist Corpus Research

Hệ thống đưa AI tới đúng văn bản Phật học, đúng phiên bản và đúng nhân chứng,
rồi kiểm nguồn/câu trích và lưu dấu vết nghiên cứu. Kiến thức mô hình chỉ giúp
đề xuất truy vấn; kết luận phải dựa vào nguồn đã đọc theo [AGENTS.md](AGENTS.md).

## Hệ thống gồm gì?

- **Repo chính** `quoctran-2608/BuddhismDocuments-for-AI`: luật, mã Python,
  cấu hình, schema, tests và tài liệu.
- **13 upstream**: nguồn bất biến ghim trong [manifest.json](manifest.json).
  [Corpus mapping](config/corpus-sources.json) phân biệt nguồn chính, bản dịch,
  metadata, alignment và dữ liệu dẫn xuất; mỗi record giữ provenance và witness.
- **Index local**: SQLite/FTS dẫn xuất dưới `derived/`; có thể dựng lại từ pins,
  giúp tìm ứng viên và ngữ cảnh, không sở hữu câu chữ nguồn.
- **Repo hỗ trợ** `BuddhismDocuments-for-AI-remote`: locator pointer-only để
  Connector tìm đường tới upstream. Runtime đọc [remote config](config/remote-corpus.json),
  không dùng GitHub Code Search làm router. Remote không phải nguồn thứ 14.

## 1.0 và 2.0 hiện làm được gì?

**1.0** cung cấp retrieval tất định: search/context/work/parallels/resolve/
variants/compare/provenance/evidence; xếp hạng ứng viên, giữ riêng nhân chứng.
CLI, index và ranking 1.0 được giữ nguyên khi bổ sung 2.0.

**2.0** đã gộp mã A–E vào `main` tại
[57db982…](https://github.com/quoctran-2608/BuddhismDocuments-for-AI/commit/57db982274e267218594ae5ca463bd2a42d2be02):
A kiểm nguồn/câu trích, B quản lý và đánh giá luận điểm, C kiểm phạm vi tìm
phản chứng/quan hệ nguồn, D lưu hồ sơ có version/lịch sử, E nối host adapter
và CLI riêng. **Quick** tìm và kiểm bằng chứng hẹp; **Research** tạo dự thảo,
candidate claims, biên nhận C và gói phản biện, cần thẩm định để đi tiếp.
Local/Connector/Work là trục môi trường, khác trục Quick/Research.

Quick đã kiểm nguồn thật qua **Bilara JSON, CBETA TEI, 84000 TEI**; ba resolver
không bao phủ mọi định dạng của 13 nguồn. Một ca GitHub Connector thật đạt A
`VERIFIED`; Work chưa kiểm phiên thực và toàn luồng Connector chưa nghiệm thu.

Research **chưa có semantic approval xác thực và chưa được phép công bố**.
Report nhập `PROPOSED`, assessment `ASSESSED` và run `finalized` không tự cấp
quyền công bố. Mã A–E đã có không có nghĩa toàn bộ 2.0 đạt nghiệm thu học thuật.
Đáp án/reviewer độc lập, hiệu quả Research học thuật, token/chi phí AI và ngưỡng
hiệu năng còn thiếu; Windows full suite chưa đạt. Xem [trạng thái nghiệm thu](docs/v2/ACCEPTANCE.md),
[báo cáo E](docs/v2/E_REPORT.md) và [evidence cuối](docs/v2/evidence/README.md).

## Bắt đầu sử dụng

Chỉ dùng nguồn và công cụ đã có, không tự tải corpus/package/model. Chạy từ
root repo chính. WSL/Linux có Python, Git và SQLite FTS5:

```sh
bin/buddhist-corpus status
bin/buddhist-corpus search 'sutaṃ' --language pli --context 2 --with-provenance
bin/buddhist-research quick 'sutaṃ' --corpus suttacentral-bilara --limit 1
```

`status` kiểm pins và báo trạng thái index; thiếu nguồn/SHA sai thì dừng nhánh
nghiên cứu. Nếu nguồn đủ nhưng thiếu index, xem [build profiles](docs/CLI.md#2-build-profile).
Search hit và gói `evidence` 1.0 vẫn cần mở nguồn; Quick chỉ trả bằng chứng
đã qua A trong `verified_evidence`. Luôn đọc giới hạn của kết quả.

PowerShell dùng module Python thay wrapper Bash 1.0:

```powershell
$env:PYTHONPATH = 'tools'
python -m corpus_research.cli status
python -m corpus_research.v2_cli quick 'sutaṃ' --corpus suttacentral-bilara --limit 1
```

Giao diện Python dành cho host đã có; callback có thẩm quyền do ứng dụng nối,
không lấy từ JSON của AI. Cú pháp, điều kiện index/store và ví dụ Research xem
[USAGE](docs/v2/USAGE.md). Repo cung cấp CLI/Python/Connector contracts.

## Đọc gì tiếp?

| Nhu cầu | Cửa vào |
|---|---|
| AI mới hoặc lập trình viên tiếp quản | [AI_ONBOARDING](docs/AI_ONBOARDING.md): kiến trúc, module, giao diện, trạng thái và xử lý lỗi |
| Nghiên cứu đúng luật | [AGENTS](AGENTS.md) → [SKILL](.codex/skills/buddhist-corpus-research/SKILL.md) |
| Mục tiêu/phạm vi/bất biến | [PROJECT_SPEC](docs/PROJECT_SPEC.md) |
| Kiến trúc và nguồn thẩm quyền | [ARCHITECTURE](docs/ARCHITECTURE.md), [GOVERNANCE](docs/DOCUMENTATION_GOVERNANCE.md) |
| Dùng retrieval 1.0 | [CLI](docs/CLI.md) |
| GitHub Connector | [REMOTE_AGENT](docs/REMOTE_AGENT.md) + [runtime config](config/remote-corpus.json) |
| Thiết kế, sử dụng và nghiệm thu 2.0 | [docs/v2](docs/v2/README.md) |
| Quyết định và lịch sử | [ADR](docs/adr/README.md), [progress](progress.md), [khảo sát](docs/CORPUS_SURVEY.md) |

Kiểm thử kỹ thuật cuối E ghi WSL 410/410 và E portable Windows 78/78; xem
[nguồn bằng chứng và commit được chạy](docs/v2/evidence/README.md), không dùng
số test làm chứng nhận học thuật. [Biên bản docs 11/10/2026](docs/DOCUMENTATION_AUDIT_2026-10-11.md)
ghi phạm vi nâng cấp tài liệu và các phép kiểm bàn giao.
