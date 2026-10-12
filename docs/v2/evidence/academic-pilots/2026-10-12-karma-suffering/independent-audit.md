# KIỂM TOÁN ĐỘC LẬP BCR ACADEMIC PILOT 01

**Ngày:** 12/10/2026  
**Đầu vào:** `BCR_Pilot01_Audit_Package.zip` và bản Word gốc `Nghiệp và khổ đau.docx`.  
**Phạm vi:** Toàn vẹn gói; provenance Git; tái lập thuật toán A ở chế độ offline replay; đối chiếu lựa chọn vị trí kinh; đánh giá giá trị nghiệm thu thực tế. Không đánh giá toàn diện đúng/sai học thuật của bài viết.

## Phán quyết tổng quát

**CHẤP NHẬN CÓ ĐIỀU KIỆN** hồ sơ này như **pilot khám phá về provenance và tầng A**, với hai lỗi/điểm cần sửa trong báo cáo Work. **CHƯA CHẤP NHẬN** là nghiệm thu học thuật, nghiệm thu chất lượng kiểm toán một bài viết hoàn chỉnh, hoặc bằng chứng ưu thế 2.0 so với 1.0. **KHÔNG ĐỀ NGHỊ SỬA MÃ/MERGE** từ pilot này.

| Hạng mục | Kết luận kiểm toán độc lập |
|---|---|
| ZIP, bản Word gốc | PASS: 275 mục `SHA256SUMS.txt` đều khớp; `original.docx` giống hệt bản Word người dùng gửi, SHA-256 `570c4cee4092df7a1343020b5a3d37e98ffca89e1473c362fde732f9625f55d4`. |
| Source provenance | PASS trong bộ 16 tệp: từng SHA-256, Git blob SHA trong gói hợp lệ; GitHub Connector độc lập trả cùng Git blob SHA tại các commit pins cho **cả 16 đường dẫn** (11 Pāli root, 3 bản dịch Anh, 2 CBETA XML). |
| Mã BCR đã sử dụng | PASS kiểm mẫu: năm tệp `verification.py`, `connector_host.py`, `source_resolvers.py`, `local_research.py`, `config/corpus-sources.json` có Git blob SHA khớp remote main `17292ded…`. |
| Raw RPC | Các tệp `rpc/{001..059}.{request,response,tool}.json` đầy đủ; mỗi response có request identity khớp, content có Git blob SHA đúng và tool `structuredContent.content` khớp. 15 locator + 44 source = 59. Đây là audit *tính nhất quán của receipt*, không phải chứng thực chữ ký máy chủ của lịch sử thực thi. |
| Reproduce tầng A | PASS **offline replay**: dùng code snapshot BCR và reader riêng đọc các tệp đã được lưu, tái lập 13 VERIFIED + 2 REJECTED, cùng các trạng thái check ở cả 15/15 lượt. Không trình bày thành một lần kiểm Connector live. |
| Local retrieval và Research | BLOCKED/INCONCLUSIVE: log cho thấy index cùng checkout 13 nguồn thiếu; CLI `search`, `quick`, `run-create` exit 2; không có D Research run thành công. |
| So sánh BCR 1.0 với 2.0 | **CHƯA ĐO** trên bài viết: truy xuất local không chạy, thiếu thiết lập cùng index/query. |
| Chất lượng đánh giá luận điểm Phật học | INCONCLUSIVE: không có semantic ground truth độc lập hay adjudication chuyên gia; A VERIFIED không xác nhận claim đúng. |

## Các phát hiện quan trọng cần sửa hoặc chú giải

### IA-01 (nghiêm trọng): Sai đơn vị kinh ở ca Hán `han-second-witness`

- Work báo một `VERIFIED` tại `T02n0100:0453a01` và dẫn vị trí `0453a01–09` khi so sánh bản **Biệt dịch Tạp A-hàm kinh 211**.
- Trong tệp `T/T02/T02n0100.xml` tại source pin `dbdea41071e1e260ad84b72faefd4587333cf76d`: `<cb:mulu>211</cb:mulu>` xuất hiện tại `0452b04`, kinh 211 kết thúc ở `0452c16`; `<cb:mulu>212</cb:mulu>` mở ở `0452c17`; `0453a01` đã thuộc **kinh 212**.
- Vì vậy A kiểm đúng byte một đoạn trong cùng *tệp TEI* nhưng **đoạn đó không chứng minh nội dung kinh 211**. Đây trước tiên là sai sót **chọn/diễn giải vị trí của harness/Work**, không phải bằng chứng thuật toán A tự nhận sai byte. Nó phơi lộ rủi ro định danh dưới mức `work_id=T02n0100` khi một file TEI chứa nhiều kinh.
- Work có lưu đoạn trích `evidence/T02n0100-211-context.xml` đúng phạm vi kinh 211, trong đó có lời nói về “năm” nhưng liệt kê “貪欲、瞋恚、掉悔、疑” ở `0452c01–02`. Cần sửa trích dẫn chứng cứ cho phát hiện khác biệt H01/H02 từ `0453a` sang `0452b–0452c`; không được dùng gate tại `0453a01` để xác nhận điều về kinh 211.

### IA-02 (quan trọng): Nguyên nhân câu Hán P029 bị từ chối bị giản lược

- Bài gốc trích `一切人所知覺者，皆是本所造因。`.
- Nguồn ghim T99 ở `0253a06–07` có chuỗi `一切人所知覺者皆` + thẻ `<lb>` + `是本所造因，` rồi tiếp tục câu. Không có dấu phẩy ngay sau `者`; kết thúc tiểu cú trong nguồn là `，` chứ không phải `。`.
- Do đó A `QUOTE_MISMATCH` phản ánh **cả** thay đổi dấu câu của đoạn trong bài **lẫn** giới hạn không ghép văn bản qua thẻ/vị trí. Work nhấn vào `lb` như nguyên nhân duy nhất là chưa đủ căn cứ.
- Phép kiểm bổ sung offline: phiên bản không dấu câu `一切人所知覺者皆是本所造因` vẫn `REJECTED` khi đi qua vị trí 0253a06; riêng `一切人所知覺者皆` trong span 0253a06 thì `VERIFIED`. Đây là phép thử *đối chứng bổ sung*, không được tính vào 15 lượt live của Work.

### IA-03 (quan trọng): 13 VERIFIED không phải 13 trích dẫn của bài được xác nhận

- Trong 15 trường hợp `evidence/quick_quotes.json` và `evidence/quick_chinese.json`, **chỉ có hai lượt cung cấp nguyên văn trích dẫn từ bài** (`article-pali-quote`, `article-han-quote`), cả hai đều bị từ chối ở chế độ kiểm nguyên văn đúng contract.
- **13 lượt VERIFIED còn lại sử dụng `quotation_input = null`**. `ConnectorHost.verify_pointer` tự lấy excerpt đúng từ nguồn và đưa làm quotation khi đầu vào rỗng. Chúng là kiểm soát tốt về source locator/blob/span, **không phải phép đo BCR đã phê duyệt 13 câu của bài viết**.
- Work có nêu không đồng nhất source gate với claim; báo cáo công khai tiếp theo nên làm điều này nổi bật ngay cạnh con số 13/15.

### IA-04 (xác nhận, có giới hạn): Định danh SN 35.145

- Bản Bilara ghim ghi `sn35.145:0.3 = Bāhirānattahetusutta`, chủ đề vô ngã của ngoại sắc.
- Bản Bilara ghim ghi `sn35.146:0.3 = Kammanirodhasutta`, chứa các đoạn nghiệp cũ/nghiệp mới.
- Bài AI dẫn SN 35.145 cho nội dung nghiệp cũ/mới. **Sai theo hệ định danh Bilara/SuttaCentral được ghim**; không kết luận mọi hệ đánh số lịch sử đều sai trước khi kiểm nguồn ánh xạ.
- Việc Work phát hiện sai lệch này là **phân tích của tác nhân khi đọc nguồn**, chưa chứng minh BCR tự động phát hiện một claim-to-source mismatch.

### IA-05 (phương pháp): Pilot chưa đo giá trị tăng thêm của Research

- Local 1.0, Quick và Research trên cùng corpus/index đều không chạy thành công do thiếu index/checkout đúng pin.
- Kênh Connector chỉ cho lookup/verify A; chưa có C/D receipts hoặc run store hợp lệ trong phiên.
- Không có expected answer ngữ nghĩa được adjudicate độc lập, không có blindness/preregistration. Vì vậy không thể tính chính xác semantic false acceptance, false rejection hay mức độ cải thiện bài viết.
- Registry có **104** mục với 29 `text_status: PASS`, 3 `FAIL`, 72 `INCONCLUSIVE`; các nhãn này là kiểm kê/phân tích của Work, **không** phải 104 lượt BCR Research có thẩm quyền đánh giá.

## Các điểm làm tốt cần ghi nhận

1. Bảo toàn nguyên byte Word, giữ danh mục nguồn gốc rõ ràng và nguồn được pin.
2. Có raw tool receipts, script harness, logs, mã, source bytes và SHA ledger đủ để người thứ hai tái lập logic A.
3. Work thừa nhận lỗi `source_contract` ban đầu của chính harness; không tính 13 lượt thử ban đầu sai mapping là false rejection của BCR.
4. Không bịa ResearchStore hoặc semantic approval, không lấy mã exit 0 làm PASS; ghi rõ local BLOCKED.
5. Không tự gọi các bài dịch/diễn giải hiện đại không có trong corpus là nguồn kinh thứ 14.
6. Nhận diện khác nhau giữa một câu có trong nguồn và câu ấy hỗ trợ một luận điểm học thuật.

## Khuyến nghị hành động

**Bước 1 — Work thực hiện correction-only, không đổi repository:** Sửa báo cáo/ledger/protocol và nếu cần bổ sung một vòng kiểm chính xác **kinh 211** tại `0452b04–0452c16`; giữ nguyên bản gốc, evidence cũ và receipts, ghi audit delta/phiên bản. Tách mismatch dấu câu với giới hạn XML; tách 13 source-generated controls khỏi hai trích dẫn bài thật; đánh dấu gate 0453a01 là kinh 212. Không ghi lại 15 lượt Work cũ như lượt chạy mới.

**Bước 2 — Tạo môi trường chạy so sánh thực:** Dùng môi trường WSL đã có 13 checkout đúng pin và index kiểm được (nếu còn sẵn), để Codex/chủ quản vận hành cùng danh sách luận điểm và query qua retrieval 1.0, Quick và Research draft A/B/C/D. Không tạo index giả, không chỉnh pins, không phát hành claim. Giao lại log, run snapshots, C receipts và review package cho Work phân tích.

**Bước 3 — Thiết lập đối chứng ngữ nghĩa:** Tách đối chứng do chuyên gia Pāli/Hán lập khỏi câu trả lời Work/Codex; xác nhận luận điểm đúng, sai, bất định; chỉ chấm false acceptance/rejection khi có ground truth đáng tin. Có các trường hợp đúng để phát hiện chặn nhầm.

**Quyết định:** Hoàn thành một **pilot thăm dò kỹ thuật A**, chưa hoàn thành **Academic Pilot 01 nghiệm thu hiệu quả kiểm tra toàn bài**. Không căn cứ gói hiện tại để mở publication, đổi trạng thái toàn BCR 2.0 sang PASS hoặc đề xuất phase mới.

## Tài liệu dùng trong gói

- `BCR_Pilot01_Report.md`, `protocol.json`, `claim_registry.json`, `paragraph_coverage.json`, `article_locked.json`, `SHA256SUMS.txt`.
- `evidence/source_ledger.json`, `evidence/quick_quotes.json`, `evidence/quick_chinese.json`, `evidence/T02n0099-977-context.xml`, `evidence/T02n0100-211-context.xml`.
- `rpc/001…059`, `logs/local_execution.json`, `logs/final_local_recheck.json`, `logs/final_validation.json`.
- `code_snapshot/tools/corpus_research/{connector_host,verification,source_resolvers}.py`.

Nguồn đọc độc lập: [main ghim](https://github.com/quoctran-2608/BuddhismDocuments-for-AI/commit/17292dedf86ba9f732be3e99b40d57f37be03739), [SN 36.21 ghim](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn36/sn36.21_root-pli-ms.json), [SN 35.145](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn35/sn35.145_root-pli-ms.json), [SN 35.146](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn35/sn35.146_root-pli-ms.json), [CBETA T02n0099 ghim](https://github.com/cbeta-org/xml-p5/blob/dbdea41071e1e260ad84b72faefd4587333cf76d/T/T02/T02n0099.xml), [CBETA T02n0100 ghim](https://github.com/cbeta-org/xml-p5/blob/dbdea41071e1e260ad84b72faefd4587333cf76d/T/T02/T02n0100.xml).
