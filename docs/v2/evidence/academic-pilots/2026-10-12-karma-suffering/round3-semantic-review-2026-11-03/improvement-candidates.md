# Các hướng nâng cấp cần nghiên cứu theo bằng chứng

Đây là candidate cho chủ dự án đánh giá sau adjudication, không yêu cầu phải sửa code hoặc chấp nhận phase mới. Không có code/index/pin/schema/policy change trong Round3.

| Candidate | Bằng chứng quan sát | Thử nghiệm có thể thiết kế | Giới hạn quyết định hiện tại |
|---|---|---|---|
| Kiểm locator–claim trước khi ghi source control | R3-F15/F17:5.6 vắng;6.1 là đề mục,33.3 mới định nghĩa | Dùng bộ case chuyên gia lập có locator đúng/sai, kiểm selected unit chứa mệnh đề cần đánh giá; giữ lịch sử khi đề xuất sửa | A không hứa phê duyệt nghĩa; chưa chứng minh bug core |
| Binding tiểu kinh trong TEI | R3-F03/F13 và IA-01 lịch sử: file có nhiều kinh | Thử boundary mulu và citation211/212 với ca đúng/sai có expected độc lập | Có thể thuộc metadata/harness; không đổi resolver vội |
| Tách work type/edition/author khỏi text_role | R3-F04/F05: Y main-body root_text nhưng header là biên soạn | Chuyên gia phân loại mẫu CBETA collections; UI/API hiển thị collection/work type và role riêng | root_text không tự sai trong main-body; không nâng thành false acceptance |
| Trích dẫn biên tập và markup minh bạch | R3-F01/F02/F03/F06 | Prototype lớp đọc đã chuẩn hóa kèm map về original spans; ghi rõ exact/editorial/paraphrase và test adversarial attribution | Giữ nguyên gate verbatim hiện hành, không nối span ngầm |
| Tra ngữ cảnh từ vựng theo corpus | R3-F12: cùng opakkamikā ở SN/MN, một bản dịch khác gloss | Dữ liệu lexicon/chú giải có quyền và provenance; chuyên gia đánh nghĩa theo context, không tự đồng nhất ngôn ngữ | Chưa có lexical ground truth, không chọn một gloss từ AI |
| Rubric atomic claim–evidence và phạm vi | R3-F08/F09/F14/F18 | Chuyên gia tách textual/normative/historical, ghi điều kiện và đối chứng; sau đó mới đo semantic false rates | Không dùng nhãn AI làm đáp án rồi tự chấm BCR |
| Nguồn học giả hiện đại có quyền | R3-F10/F11 | Ingestion supplemental có bản quyền/edition/page/hash và tách pin cohort; thử attribution bằng full context | Không tải sách hoặc snippets trái policy; không biến thành nguồn14 ngầm |
| Phân loại độc lập nguồn/counterevidence | C lexical có bound; Y và bản dịch không tự độc lập | Expert dependency evidence, known counterexamples, adequate scope; kiểm negative kết quả và stale bindings | Chưa có authenticated reviewer hoặc độc lập nguồn đã xác nhận |
| Chỉ số receipt và audit UX | 102 entries/57 unique/45 bản trùng ở raw | Hiển thị entries/executions/unique IDs, bound và unverified scope khác nhau; schema tự kiểm liên kết | Không thay historical metrics; không coi duplicate là bug khi snapshot lặp có chủ đích |

Mọi thử nghiệm sau phải có tiêu chí trước khi chạy, source pins/rights và reviewer authority rõ ràng. Duy trì fail-closed, source immutability, dữ liệu riêng và publication guard.
