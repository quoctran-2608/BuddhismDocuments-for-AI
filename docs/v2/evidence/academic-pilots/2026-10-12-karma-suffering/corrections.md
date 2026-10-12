# Correction Log — Pilot 01

Ngày hiệu đính: 12/10/2026. Đây là correction/documentation, không sửa BCR code hoặc mở publication. Báo cáo kiểm toán của phiên ChatGPT độc lập được giữ nguyên byte tại [independent-audit.md](independent-audit.md), SHA-256 `b3d161b6829de90497a9a8987bc5e8702e6879a73a695ca28905b6dfdfa38d13`; không phải adjudication chuyên gia con người.

| Finding | Xử lý | Bằng chứng | Nơi đã sửa / bất định còn lại |
|---|---|---|---|
| IA-01 | Đã sửa attribution, AC09 và ledger H02 | TEI mulu 211 ở 0452b04, kết thúc 0452c16; mulu 212 ở 0452c17; 0453a01 thuộc 212 | [Bản corrected](report-corrected.md#ia-01), [case-results](case-results.json), [source-ledger](source-ledger.json). List đúng ở 0452c01–02. Gate cũ không đổi; chưa kết luận bug code/subwork contract. |
| IA-02 | Tách dấu câu khỏi span markup | Nguồn tại 0253a06–07 không có dấu phẩy sau 者, có phẩy sau 因, có lb | [Bản corrected](report-corrected.md#ia-02). Supplementary checks của audit là offline, ngoài 15; raw checks riêng không được cung cấp. Không suy sai nghĩa. |
| IA-03 | Phân loại lại kết quả 15 lượt | 2 article quote inputs đều REJECTED; 13 quotation_input=null là source controls VERIFIED | [Bản corrected](report-corrected.md#ia-03), [execution-matrix](execution-matrix.json). Registry 104 là kiểm kê AI, không BCR Research đánh giá. |
| IA-04 | Giữ kết luận theo pin, xác định người phát hiện | E05/E11 root titles và nội dung | [Bản corrected](report-corrected.md#ia-04). Sai theo Bilara ghim; alias ấn bản khác chưa kiểm. Detector tự động chưa được chứng minh. |
| IA-05 | Giữ nguyên giới hạn nghiệm thu | Local logs exit 2; no D run, no ground truth | [Bản corrected](report-corrected.md#ia-05). Benefit CHƯA ĐO; semantic FA/FR INCONCLUSIVE. |

## Bảo tồn lịch sử và chỉnh lý công khai

Bản Work v1 nguyên byte vẫn ở hồ sơ riêng: SHA-256 `aabd4e58de4564f20220a31abbe5f466a6f82fcaeae6cf8079974ce1f02b6cbe`. [report-work-v1.md](report-work-v1.md) là **public redacted projection**: che cột nguyên đoạn bài trong bảng 104 mục, che đường dẫn workspace; giữ các lỗi/phán quyết cũ. Đây là ngoại lệ có giải thích đối với yêu cầu lưu nguyên byte v1 trên Git: toàn văn bài chưa được cấp quyền công bố. Không dùng projection như bản checksum-equal với v1 gốc.

Bài Word, registry, protocol và 59 RPC triplets không sửa. Correction tạo artifact mới, không tái ghi 15 lượt như live mới. [supplementary-checks.json](supplementary-checks.json) là phép đọc cấu trúc **offline mới**, có thời điểm, inputs/pins/hashes và outputs; không gọi A và không cấp approval. Báo cáo audit giữ riêng offline replay 15 lượt và hai supplementary A checks của chính audit; không có raw receipts của phiên audit trong đầu vào hiện tại.

## Kiểm toán lại

Đọc [evidence-manifest.json](evidence-manifest.json) để biết tệp nào ở Git và tệp nào chưa có nơi archive project-level ổn định. Mở nguồn ghim rồi kiểm mulu/line, không lấy tên file T02n0100 làm định danh của kinh 211. Không biến một giá trị VERIFIED thành semantic approval.

## Kiểm tra whitespace của bản audit nguyên byte

`git diff --cached --check` báo đúng hai dòng có hai khoảng trắng cuối dòng trong `independent-audit.md` (Markdown hard breaks ở Ngày/Đầu vào). Giữ nguyên để bảo toàn SHA-256 của audit, không âm thầm trim. Kiểm lại với `core.whitespace=-blank-at-eol` đạt; các nội dung mới không có warning whitespace. Đây là ngoại lệ bảo tồn đầu vào được ghi rõ, không lỗi hash hoặc source.
