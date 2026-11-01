# Kiểm toán độc lập Round 2 — bản lưu GitHub

**Ngày:** 12/10/2026. **Quyết định:** CHẤP NHẬN CÓ ĐIỀU KIỆN cho bằng chứng vận hành local, KHÔNG chấp thuận semantic claims hay publication.

Bản này là biên bản công khai được biên tập từ phiên kiểm toán độc lập, **không phải bản sao nguyên byte** của báo cáo kiểm toán đầy đủ. SHA-256 bản báo cáo độc lập đầy đủ giữ ở ngoài Git: `214ec24ce71d5ddbe090de4ca03accd68e0ba1bec11058ab54e1cdd2fc54ba66`. Không tự nhận đã chạy lại phần mềm trên WSL: đã đọc/kiểm archive độc lập, so stdout JSON và ResearchStore SQLite read-only. Không có oracle chuyên gia học thuật.

## Tính toàn vẹn và provenance

- ZIP gốc `BCR_Pilot01_Round2_WSL_20261012.zip`: **59.202.367 bytes**, SHA-256 `8f035794a659ca045f007d139f2ee8f1270b5c8978e2dacc3a62b5441ee2189a`; khớp `.zip.sha256` do Codex cung cấp.
- ZIP có **1.244 thành viên**, đọc CRC đạt; `SHA256SUMS.txt` chứa **1.243 entries**, toàn bộ 1.243/1.243 hash file còn lại khớp byte thực. `artifact-manifest.json` liệt kê 1.242 payload files, trừ manifest và chính bảng hash.
- 37/37 bản `source-bytes/<sha256>.utf8` khớp tên theo digest. Word gốc có SHA-256 `570c4cee4092df7a1343020b5a3d37e98ffca89e1473c362fde732f9625f55d4`, giữ riêng trong raw.
- 16 đường dẫn nguồn ghim có receipts đối chiếu hash/blob; đây không thay cho phép tái chạy trên toàn bộ 13 checkouts. Commit code chạy thử: `a6707b3ab34e4977cc686a822b726e2bdade8e2c`.
- Ma trận gốc `execution-matrix-locked.json` có SHA-256 `f2887e9f78662df40ef078a6be1de2409deff022154a1994808ee9994f95200c` và dấu thời gian khóa trước main run. `execution-matrix-public.json` chỉ là projection đã bỏ các đoạn bài viết gốc; KHÔNG kiểm hash projection như thể đó là ma trận gốc.

## Kiểm vận hành thực tế

- 12/12 AC01–AC12 có đầu ra retrieval CLI 1.0 hiện hành, Quick 2.0 và Research draft. Trạng thái thực thi không phải verdict ngữ nghĩa.
- **25/25** cặp `commands/ACxx-qN-retrieval.stdout` và `commands/ACxx-qN-quick.stdout` được so JSON trực tiếp: `retrieval == quick.retrieval`. Các cặp có cùng query/corpus/limit và exit code 0. Đây là non-regression so CLI 1.0 tại commit thử, **không phải so với baseline tiền A** `f7415f574ed1510d5854ee00db6baafe2484e355`.
- Các Quick verification array có **45 VERIFIED**, **9 UNVERIFIED**. Hai quote **trực tiếp từ bài**, P013 (AC02) và P029 (AC03), **REJECTED/QUOTE_MISMATCH** theo pinned witness/span; chưa thể suy ra sai nghĩa. 24 targeted source controls: **23 VERIFIED, 1 BLOCKED** (AC11 selector `mn135:5.6`). Source-generated control không phải bài AI trích đúng.
- AC03 có hit ở `Y32n0030` (biên soạn của Ấn Thuận): xuất hiện cùng câu trong nguồn khác **không chứng minh** attribution T99.977; `root_text` kỹ thuật không tự bảo đảm canonical authority.
- AC07 bị chặn ở khâu chứng minh quy thuộc sách/chú giải hiện đại (nguồn chưa được pin), dù thao tác retrieval/draft vẫn chạy.

## Research A/B/C/D

- **12 draft runs, 95 evidence IDs, 57 claim records lịch sử, 56 active candidate IDs**; 1 proposal AC07 bị REJECTED vì thiếu supporting evidence. B assessment: **11 UNVERIFIED + 1 REJECTED**. Không có accepted claims hoặc semantic approval.
- **102 C receipt entries / 57 unique (case, search_id) / 45 duplicated receipt entries.** Tránh diễn đạt 102 lượt tìm kiếm phản chứng độc lập; lexical C retrieval không phải phán quyết semantic counterevidence.
- 12/12 review packages `MATCHED`; 12/12 publication-check không được cấp quyền. `research-store.sqlite3` SHA-256 `a72ee67313c74c2d501c1387cdd6a9a68f3c418f1529ce9cd7cb3c50072ef170`, read-only `PRAGMA integrity_check=ok`, counts: runs=12, snapshots=105, claim_ids=57, packages=12, reports=0, decisions=0.
- Runtime gồm một observation/subprocess, cache hỗn hợp, không phải benchmark: median retrieval ~0.142s, Quick ~0.194s, Research ~13.474s. Không có token/AI money hay CPU/RSS/IO theo ca.

## Tình trạng khoa học và giới hạn

**Vận hành kỹ thuật một phần: được chứng minh qua raw. Nghiệm thu học thuật: INCONCLUSIVE. So sánh 2.0 với retrieval hiện hành cho thấy bổ sung kiểm nguồn/history; so với baseline lịch sử và semantic accuracy: NOT_MEASURED. Publication: NOT_PERMITTED.**

Index được báo có 12.638.217 records và SHA-256 `99da1d7f82b360481568c8458d8bfd2e982b8b7497aaee646912898df82095a2`, nhưng file index gốc ~12.1GB không nằm trong archive; kiểm toán viên không tự hash/rerun 25 query với DB đó. Một sự cố volume/WSL và một lỗi harness đọc khóa trước main run được bảo lưu, không phải kết luận BCR code có lỗi. Nơi lưu raw dài hạn được phê duyệt vẫn **external_archive_pending**, dù bản ZIP hiện có ở Google Drive riêng.

**Cần tiếp theo:** chuyên gia Pāli/Hán đánh giá ground truth AC01–AC12; phân biệt source-presence, quotation, source-attribution, claim-support và phản chứng ngữ nghĩa; sau đó mới được tính tỷ lệ lỗi/chất lượng hoặc yêu cầu sửa mã.
