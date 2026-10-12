# BCR Academic Pilot 01 — báo cáo hiệu đính v2

**Phạm vi:** kiểm toán bài AI về nghiệp và khổ đau; correction + evidence archival ngày 12/10/2026. **Kết luận:** có bằng chứng kiểm source/provenance và gate A trong mẫu; nghiệm thu học thuật và so sánh lợi ích 1.0/2.0 chưa hoàn thành. Đây là báo cáo kiểm toán AI, không Research publication hoặc semantic approval.

Main/mã pilot: `17292dedf86ba9f732be3e99b40d57f37be03739`. Source pins giữ nguyên: Bilara `0914c609e49215bb1473199929ee8a2996b423c4`; CBETA `dbdea41071e1e260ad84b72faefd4587333cf76d`. Môi trường lịch sử: Python 3.12.14, SQLite 3.53.1, Linux. Bài gốc khóa SHA-256 `570c4cee4092df7a1343020b5a3d37e98ffca89e1473c362fde732f9625f55d4`, có 150 đoạn và hai bảng; không sửa và không commit toàn văn. Không nhận được packet bàn giao riêng ở lượt đầu.

## IA-01

Lỗi được xác nhận: Work/harness gắn gate `pilot-han-second-witness` ở `T02n0100:0453a01` với Biệt dịch Tạp A-hàm kinh 211. TEI ghim cho thấy mulu 211 bắt đầu ở `0452b04`, kết thúc tại `0452c16`; mulu 212 bắt đầu `0452c17`; `0453a01` thuộc kinh **212**.

A đã xác minh đúng byte tại line được giao trong file T02n0100. Sai ở bước lựa chọn/diễn giải đơn vị kinh của Work. Gate cũ VERIFIED được giữ như lịch sử, **loại khỏi hỗ trợ kinh 211**. Đây là rủi ro định danh dưới mức file TEI, chưa đủ để quy là lỗi code A.

AC09 dùng đúng phạm vi H02 `0452b04–0452c16`, danh sách ở `0452c01–02`: bản ghim nói năm nhưng liệt kê tham dục, sân nhuế, trạo hối, nghi. H01 có mục ngủ ở danh sách tương ứng. Sự khác chữ là quan sát văn bản; nguyên nhân thiếu mục/quan hệ truyền bản cần chuyên gia. Không tự bù từ H01 sang H02. Đây là đọc ngữ cảnh lưu trữ, **không phải gate A mới cho kinh 211**.

[Source-ledger](source-ledger.json), [case-results AC09](case-results.json), [supplementary-checks](supplementary-checks.json) ghi correction. F08 lịch sử và dòng C-T02R05 được thay về mặt dẫn chứng bằng `0452c01–02`; không dùng `0453a01–09` cho kết luận kinh 211.

## IA-02

Câu bài P029 khác nguồn ghim về dấu câu: bài có phẩy sau 者 và chấm sau 因; nguồn không có phẩy sau 者, có phẩy sau 因. Đồng thời chuỗi chữ chạy qua thẻ lb giữa `0253a06` và `0253a07`; resolver hiện chỉ kiểm một span liên tục.

Vì vậy QUOTE_MISMATCH liên quan **cả mismatch dấu câu và giới hạn span**, không là lỗi ngữ nghĩa hoặc chứng minh bịa Hán văn. Audit độc lập báo supplementary offline A: bản không dấu câu xuyên span vẫn REJECTED, riêng prefix trong span VERIFIED. Hai phép đó **ngoài 15 lượt Work**, không live. Báo cáo audit là đầu vào; raw receipts hai phép kiểm riêng không được cung cấp. Correction này chỉ kiểm cấu trúc nguồn archived, không tạo A gate mới.

## IA-03

| Phép kiểm lịch sử | Số lượt | Kết quả | Có nghĩa gì |
|---|---:|---|---|
| Trích trực tiếp từ bài | 2 | 2 REJECTED/QUOTE_MISMATCH | Kiểm nguyên văn P013/P029 theo witness/contract, không phán sai nghĩa |
| quotation_input=null | 13 | 13 VERIFIED | Source-generated quotation controls kiểm locator/blob/span, không 13 câu bài được duyệt |
| Tổng sau sửa lỗi contract harness ban đầu | 15 | 13 VERIFIED + 2 REJECTED | Năng lực source verification trong mẫu |

13 lượt harness ban đầu thiếu repo_path/mapping được ghi riêng, không tính false rejection BCR. Registry **104** mục (29 Work PASS, 3 FAIL, 72 INCONCLUSIVE ở v1) là danh mục và đánh giá sơ bộ của Work; không 104 lượt Research thành công. Các nhãn này chưa được adjudicate và không là ground truth.

Phân biệt bốn tầng: **source verification** đã có gate mẫu; **article quote verification** chỉ hai inputs; **claim support assessment B** chưa chạy; **semantic approval** chưa được cấp. A không thẩm định suy luận hai tầng nhân quả, phạm vi mọi khổ đau, quy thuộc Gethin/Thanissaro hoặc tính độc lập nguồn.

## IA-04

Trong Bilara ghim, Tương Ưng Bộ Kinh 35.145 là `Bāhirānattahetusutta`; Tương Ưng Bộ Kinh 35.146 là `Kammanirodhasutta`, có đoạn nghiệp cũ/nghiệp mới. Citation P075/P142 sai **theo source pin và hệ ID này**. Chưa kiểm alias của mọi ấn bản khác.

Đây là phân tích của Work khi đọc root text, được audit độc lập xác nhận. VERIFIED cho nguồn 35.145 không tự phát hiện claim-to-source mismatch; pilot chưa chứng minh detector BCR tự động bắt sai lệch này.

## IA-05

| Năng lực/tiêu chí | Trạng thái |
|---|---|
| Local retrieval 1.0 | BLOCKED: thiếu index và 13 checkout nguồn; exit 2 |
| Local Quick 2.0 | BLOCKED: không mở được DB; exit 2 |
| Integrated Research A/B/C/D | BLOCKED: run-create exit 2; không có D run thành công |
| Connector lookup/A | Có thực thi mẫu lịch sử; không thay thế pipeline Research |
| Remote Research B/C/D | NOT_RUN; thiếu orchestration/readers xác thực |
| Lợi ích 1.0/2.0 trên toàn bài | CHƯA ĐO |
| Semantic false acceptance/rejection | INCONCLUSIVE |
| Ground truth học thuật độc lập | CHƯA CÓ |
| Research publication | CHƯA ĐƯỢC PHÉP; NOT_RUN |

Không tính 2/15 như false rejection rate hoặc 13/15 như accuracy. Offline replay 15/15 do audit chỉ chứng minh tái lập thuật toán từ archive; receipts nhất quán không là chữ ký máy chủ chứng thực lịch sử.

## Giao thức, kết quả và giá trị thực tế

12 ca từ bài có cả khả năng đúng, sai, chưa đủ bằng chứng và controls, thiết kế exploratory/non-blinded. [case-results.json](case-results.json) giữ từng câu hỏi/vị trí/scope/pin/evidence ID/witness, kết quả máy, phân tích Work, phản biện độc lập và việc cần chuyên gia. Không thay toàn bộ phần AI phân tích thành verdict BCR. [protocol.json](protocol.json) ghi thiết kế và giới hạn; [execution-matrix.json](execution-matrix.json) ghi errors và các bước NOT_RUN.

Giá trị quan sát là định tuyến nguồn, pin/blob/span, lưu receipts và tạo căn cứ đọc ngữ cảnh. Nguồn thực có phần hỗ trợ mệnh đề hẹp phủ nhận quy mọi cảm thọ về nghiệp trước; mở rộng sang mọi khổ/bệnh/bất hạnh và tổng hợp giáo lý vẫn cần scope review chuyên gia. Nguồn hiện đại/bản dịch Việt và quan hệ song hành đủ ba bước chưa xác minh. Không coi các bản dịch Anh hay nhiều repo là nhiều nhân chứng độc lập.

Chi phí: 59 RPC trong harness lịch sử gồm 15 locator/44 source; không tổng mọi setup call. Wall time gồm orchestration, mỗi ca một observation, không benchmark sản phẩm. CPU/RSS/IO/token/tiền AI theo ca chưa đo; không ghi 0. Không có phép so sánh cùng index/query hoặc giá trị tăng thêm của Research.

## Correction Log

[corrections.md](corrections.md) đối chiếu IA-01–IA-05 và từng nơi sửa. V1 nguyên byte và raw receipts được giữ ngoài Git; bản public v1 chỉ che nguyên đoạn bài và đường dẫn private, không sửa phán quyết cũ. Audit giữ nguyên nội dung và hash. Correction mới `COR01-OFFLINE-STRUCTURAL` tách khỏi: harness sai ban đầu; 15 gate hợp lệ; offline replay của audit; supplementary offline A của audit. Không gọi A/B/C/D mới trong correction.

## Hồ sơ công khai và giới hạn tái lập

Git chỉ chứa reports, case/protocol/execution/source metadata, correction record và manifest. Không commit full Word, corpus sources, 59 raw triplets, code snapshot hoặc archives. [evidence-manifest.json](evidence-manifest.json) ghi hashes từng artifact; `external_archive_pending` có nghĩa chưa có địa chỉ project-level ổn định được cấp quyền cho reviewer ngoài phiên. Gói riêng đã bàn giao trong ChatGPT không được biến thành URL công khai giả. Raw offline checks của audit không có trong đầu vào; chỉ giữ audit narrative.

## Đề xuất tiếp theo (chưa thực thi)

P0: chạy cùng câu hỏi/query/scope trên WSL có đủ 13 checkout đúng pins và index kiểm được, tại baseline 1.0 và mã tích hợp được chốt; lưu outputs/rank, A/B/C/D drafts, C receipts và review package. Chuyên gia Pāli/Hán adjudicate corpus-grounded expected answers riêng trước lượt đo. Chỉ sau đó mới đo semantic FA/FR và lợi ích 2.0.

P1: đánh giá subwork binding TEI, nhãn source control/article quote và khả năng quote qua markup/biên tập dấu; đây là đề xuất đánh giá, **không chứng minh bug hoặc yêu cầu sửa code từ pilot**. P2: chốt nơi archive raw có quyền truy cập và đo costs theo phase. Không mở phase mới, thay pins, policy/ACCEPTANCE hoặc publication.
