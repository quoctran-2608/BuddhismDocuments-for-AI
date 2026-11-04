# Năng lực BCR quan sát từ code và chạy thật

Các trạng thái dưới áp dụng từng năng lực, không gộp tên module thành nghiệm thu toàn bộ. Đối chiếu24 module code với Git HEAD và các tài liệu bắt buộc trong provenance. Không dùng unit-test PASS để chứng nhận Phật học.

| Thành phần | IMPLEMENTED | PARTIALLY_IMPLEMENTED | DESIGNED_NOT_IMPLEMENTED / BLOCKED |
|---|---|---|---|
| A | evidence_gate, verify_quote, read_local_source; kiểm repository/pin/blob/path/selector/role/witness và đọc độc lập | Ba resolver Bilara/CBETA/84000, quote liên tục trong nguồn; ngữ cảnh được lấy nhưng ý nghĩa cần AI | Chưa đủ13 định dạng, không flatten quote qua markup/entity; paraphrase cần review_reader tin cậy |
| B | make_claim, assess_claim, final_claim_gate;5 mức support và validation basis/presentation/history | Đánh giá gắn đúng claim/evidence phải do assessment_reader đã cấu hình cung cấp | Không có bộ AI tự phân rã/đánh giá lập luận mặc định; không có đường semantic approval thật; Research guard vẫn chặn |
| C | plan, bounded execution receipts, source_independence, assess_counterevidence | Tự gom cùng repository/pin/path/work/witness; search receipts thật, lexical candidates | Độc lập khác họ cần dependency_reader; ý nghĩa limits/contradicts cần assessment_reader; không tự biết query đã đủ |
| D | ResearchStore SQLite riêng, append-only snapshots/triggers, expected_version/CAS, trace, export/import PROPOSED | Native draft/capture chạy thật, bản xuất không có approval | Chốt bị chặn khi thiếu checks; publication luôn false; không xác thực người dùng hay phối hợp side effect ngoài store |
| E | CLI quick/quote/run-create/show/capture/finalize/publication-check và LocalHost | ConnectorHost callback transport,3 resolver; source-root có thể tách code root | Chưa có orchestration AI hỗ trợ–phản biện–tổng hợp tự động, prose-verifier, hoặc uncertainty queue thành sản phẩm |

API/CLI thực: tools/corpus_research/{verification.py,claims.py,counterevidence.py,research_run.py,research_store.py,local_host.py,local_research.py,v2_cli.py}. B final_claim_gate:349+ còn ghi research_conditions=UNVERIFIED dù C/D đã có module; đây là guard cố ý chưa được nối đầy đủ, không phải bằng chứng C/D vắng mặt. verify_synthesis:400+ kiểm danh sách cấu trúc khớp chính xác, không hiểu đoạn văn tự do.

LocalResearch.create:44+ tự sinh literal quotation observations từ hit, không nhập/hiểu37 mệnh đề của bài. Candidate bounds và query có thể chọn nhầm tác phẩm. Thử AC01 query đầu tạo2 literal claims và tìm các work khác SN36.21; phần ngữ nghĩa bài phải làm bằng fallback có ghi nhãn.

| Tầng | Đủ dùng hiện tại | Cần cải thiện / chưa có |
|---|---|---|
| 1 Kiểm nguồn | Pin/blob/path/quote/role/witness cho định dạng đã hỗ trợ khi đủ local data | Binding claim→đúng work/edition; quote qua markup, nhiều hệ số; ngữ cảnh đúng nghĩa không được bảo đảm chỉ bởi hash |
| 2 Kiểm chứng cứ | Contract và provenance của một đánh giá, chống metadata giả primary text | Máy chưa tự tạo mức support, nhận diện phụ thuộc khác họ hoặc phân giải dịch thuật |
| 3 Kiểm lập luận | Giữ links, giới hạn, lịch sử; chặn kết luận thiếu approval | Tự phân tích tiền đề/bước nối/ngoại lệ, phản biện ngữ nghĩa và prose synthesis vẫn cần lớp AI host chưa có |

Runtime chặn thiếu approval là bảo vệ quyền/trust boundary, không là chứng minh logic sai hay đúng. Có thể báo cáo AI research draft có căn cứ riêng mà không gọi accepted hoặc nới gate.

