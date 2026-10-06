# Hồ sơ quyết định kiến trúc

Thư mục này lưu các ADR (Architecture Decision Record — hồ sơ quyết định kiến
trúc) của dự án.

ADR trả lời **tại sao một quyết định kiến trúc được chọn**. Nó không thay thế:

- `docs/PROJECT_SPEC.md` — dự án là gì và phạm vi nào;
- `docs/ARCHITECTURE.md` — hệ thống hiện đang được xây như thế nào;
- `docs/REQUIREMENTS.md` — hệ thống phải đáp ứng yêu cầu gì;
- config/schema/code/tests — trạng thái máy đọc và hành vi thực thi.

Các ADR hiện hành:

1. [ADR-0001 — Ghim nguồn upstream bằng commit Git](0001-pin-upstream-sources-by-git-commit.md)
2. [ADR-0002 — Giữ SQLite là chỉ mục cục bộ dẫn xuất](0002-keep-sqlite-as-derived-local-index.md)
3. [ADR-0003 — Dùng truy xuất từ vựng nhạy theo ngôn ngữ](0003-use-language-sensitive-lexical-retrieval.md)
4. [ADR-0004 — Tách metadata quan hệ khỏi bằng chứng câu chữ](0004-separate-relationship-metadata-from-textual-evidence.md)
5. [ADR-0005 — Tách repository chính khỏi repository artefact Connector](0005-separate-main-and-remote-artifact-repositories.md)
6. [ADR-0006 — Dùng locator tiền tính toán và xác định cho GitHub Connector](0006-use-deterministic-precomputed-connector-locator.md)
7. [ADR-0007 — Remote production chỉ xuất con trỏ, không sao chép raw text](0007-export-pointers-not-raw-corpus-text.md)
8. [ADR-0008 — Không materialize vocabulary CJK trigram thành namespace production](0008-do-not-materialize-cjk-trigram-vocabulary-in-production.md)
9. [ADR-0009 — Dùng chung xếp hạng truy xuất nhưng không coi rank là thẩm quyền học thuật](0009-share-retrieval-ranking-but-never-treat-rank-as-scholarly-authority.md)

## Quy ước

Mỗi ADR gồm:

- trạng thái;
- bối cảnh;
- quyết định;
- lý do;
- phương án đã không chọn;
- hệ quả;
- điều kiện xem xét lại.

ADR ghi lại quyết định bền vững. Số liệu benchmark chỉ được giữ khi chúng giải
thích quyết định; trạng thái runtime hiện tại phải lấy từ config/manifest/code
tương ứng.

Nếu một quyết định bị thay thế, không xóa ADR cũ. Đổi trạng thái và tạo ADR mới
để giữ được lịch sử lý do.
