# BCR Academic Pilot 01 — Round 2, thực thi WSL ngày 12/10/2026

Đã đồng bộ checkout chính lên `a6707b3ab34e4977cc686a822b726e2bdade8e2c`, bằng `origin/main` tại lần fetch. Vòng này đã chạy phần mềm thật trên Ubuntu WSL2, dùng nguồn Git local đúng pins. Báo cáo là hồ sơ kiểm thử và kiểm toán AI; **không phải phê duyệt ngữ nghĩa hoặc nghiệm thu học thuật**. Publication gate vẫn đóng.

## Kết quả trả lời yêu cầu

- Môi trường có đủ **13/13 source checkouts** đúng manifest, sạch trước/sau. **16/16 tệp ledger** khớp Git blob và SHA-256. Python 3.12.3, SQLite 3.45.1, FTS5 hoạt động. Bài Word có hash `570c4cee4092df7a1343020b5a3d37e98ffca89e1473c362fde732f9625f55d4`; 150 đoạn và hai bảng khớp archive. 275 checksum lịch sử đều khớp.
- Index acceptance cũ không có cả 12 work IDs cần cho Pilot. Đã tạo index riêng bằng CLI hiện hành, profile `core` với `--source suttacentral-bilara --source cbeta-tei --source suttacentral-relations`. Index mới chứa **12,638,217 records**, 21,123 works, 430,436 relations. Đây là ba corpus được chọn, không tuyên bố đã index đủ cả 13 corpus. Tất cả 16 path/witness trong ledger có records; `required-source-coverage.json` ghi IDs và coverage cụ thể.
- **Retrieval 1.0: 12/12 ca chạy thật; Quick 2.0: 12/12; Research draft: 12/12.** Một ca có thể chạy phần kỹ thuật mà vẫn bị BLOCKED về nguồn hoặc INCONCLUSIVE về học thuật. Có 25 cặp query/corpus/language/limit giống nhau; output retrieval của Quick bằng CLI 1.0 ở 25/25 cặp. Dùng CLI 1.0 **hiện hành**; không gán kết quả này cho baseline lịch sử trước A.
- Hai input nguyên văn thực sự từ bài P013/P029: {'REJECTED': 2}. Đây là từ chối khớp nguyên văn theo nhân chứng/span, không kết luận sai nghĩa. Literal `Kammasutta` từ citation P075 cũng được thử tại work SN 35.145; phép substring/title này tách khỏi kiểm claim-to-source và khỏi hai quote bài.
- Quick A có phân bố {'VERIFIED': 45, 'UNVERIFIED': 9}. Các câu do hệ thống lấy từ nguồn là **source-generated controls**, không tính thành quote của bài được xác nhận. Các đối chứng có selector đích trong Research: 24 lượt, {'VERIFIED': 23, 'BLOCKED': 1}.
- Research lưu 57 candidates, 95 evidence IDs trong snapshots và 102 lượt reader C thực. Mỗi ca có proposal chứa đúng đoạn bài, B assessment attempt, C receipts, history, trace và review package. Đánh giá B cho proposal bài: {'UNVERIFIED': 11, 'REJECTED': 1}; thiếu reader phê duyệt xác thực. Accepted claims và semantic approval đều không được tự tạo.
- Giá trị tăng thêm quan sát được của 2.0: A đọc nguồn Git ghim và kiểm locator/blob/role/witness/span, trả gate riêng; C lưu phép tìm lexical có giới hạn; D lưu candidate/history/snapshot và gói phản biện có binding/hash. **Chưa đo được độ chính xác học thuật, semantic false acceptance/rejection hoặc lợi ích reviewer** vì chưa có ground truth độc lập và kênh thẩm định thật.
- Chưa có bằng chứng đủ để kết luận phải sửa mã cho các quote mismatch, span chưa hỗ trợ, nguồn hiện đại thiếu hoặc approval chưa có. Có quan sát cụ thể cần review về độ chi tiết `text_role` của CBETA: Quick gán `root_text` cho main-body của một sách biên soạn Y32n0030. Header nguồn có tác giả/ấn bản; nhãn kỹ thuật này không tự xác lập canonical authority. `cross-witness-observation.json` giữ bằng chứng cho việc review dữ liệu/role policy; chưa nâng thành semantic false acceptance hoặc regression đã xác nhận. Không sửa code/tests/schema/config/manifest/pins hoặc evidence lịch sử.

## Ma trận kết quả từng ca

PASS ở cột thực thi chỉ nói lệnh/API đã chạy thành công và lưu kết quả. Nó không nhận nhãn PASS/FAIL của Work làm ground truth. FAIL quote chỉ nói không khớp phép trích nguyên văn theo pin. Các status A bên dưới thuộc đối chứng từ nguồn tại selector đã khóa, không phê duyệt bài.

| Ca | Thực thi kỹ thuật / retrieval | A đối chứng nguồn đích | Quote bài / citation literal | Kết luận ngữ nghĩa |
|---|---|---|---|---|
| AC01 | PASS (3/3 hits theo queries) | VERIFIED, VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |
| AC02 | PASS (3/3 hits theo queries) | VERIFIED | REJECTED / QUOTE_MISMATCH | INCONCLUSIVE |
| AC03 | PASS (1/2 hits theo queries) | VERIFIED, VERIFIED | REJECTED / QUOTE_MISMATCH | INCONCLUSIVE |
| AC04 | PASS (0/0/1 hits theo queries) | VERIFIED, VERIFIED, VERIFIED, VERIFIED | title literal: REJECTED | INCONCLUSIVE |
| AC05 | PASS (3/3 hits theo queries) | VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |
| AC06 | PASS (3/0 hits theo queries) | VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |
| AC07 | PASS (0/0 hits theo queries) | chưa có nguồn đích | không phải phép kiểm quote nguyên văn | BLOCKED |
| AC08 | PASS (3/3 hits theo queries) | VERIFIED, VERIFIED, VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |
| AC09 | PASS (3/3 hits theo queries) | VERIFIED, VERIFIED, VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |
| AC10 | PASS (3/3 hits theo queries) | VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |
| AC11 | PASS (3/2 hits theo queries) | BLOCKED, VERIFIED, VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |
| AC12 | PASS (3/3 hits theo queries) | VERIFIED, VERIFIED, VERIFIED | không phải phép kiểm quote nguyên văn | INCONCLUSIVE |

Các câu hỏi, vị trí bài, nguồn/path/pin/witness, query và counterquery nằm trong `execution-matrix-locked.json`. SHA-256 khóa: `f2887e9f78662df40ef078a6be1de2409deff022154a1994808ee9994f95200c`. `case-results-round2.json` tách riêng BCR trả gì, thao tác đọc nguồn thủ công, Codex diễn giải gì, cần chuyên gia gì và phần chưa thể kết luận.

## BCR tự trả về và phần phải đọc/thẩm định

**AC02:** CLI quote nhận đúng chuỗi P013 từ Word/locked article, ở chunk chứa `sn36.21:1.5`. A từ chối nguyên văn; nguồn dùng `ṁ`, chữ thường và dấu thoại/đuôi `ti`, trong khi bài dùng `ṃ`, chữ hoa và dấu chấm. Việc giải thích khác biệt chữ/dấu là kiểm nguồn thủ công, không semantic verdict BCR. Core parser dùng chunk 50 segments; locator evidence có thể là range, selector đoạn gốc được ghi bên cạnh, không giả như index là segment-level.

**AC03:** CLI quote nhận đúng P029. A từ chối câu qua `lb` và khác dấu câu. Đối chứng bỏ dấu câu xuyên hai span trả **REJECTED**; prefix liên tục `一切人所知覺者皆` trả **VERIFIED**. Đối chứng prefix lấy từ nguồn không thay quote bài. Nguồn 977 được resolve đúng range `0252c12..0253a25`; mulu 978 bắt đầu `0253a26`.

Quick query toàn câu P029 trả một hit ở `Y32n0030:0678a10`, path `Y/Y32/Y32n0030.xml`, witness Y, pin `dbdea41071e1e260ad84b72faefd4587333cf76d`; A xác nhận **câu do reader lấy từ nguồn đó**. Header raw xác định `雜阿含經論會編（下）`, tác giả `民國 釋印順著`, edition tháng 10/2011. Đây là quan sát header thủ công; Quick không tự thẩm định lịch sử văn bản. Gate `VERIFIED` ở Y không xác nhận quote nguyên văn hoặc attribution của bài vào T99; main-body `root_text` cũng không bảo đảm loại nguồn canonical. Full bytes/receipts giữ trong `cross-witness-observation.json` và `source-bytes/`.

**AC04:** Đã chạy lexical search riêng với `sn35.145`/`sn35.146` và lệnh `work` riêng để đọc records tại định danh. Số hits theo query nằm trong bảng; search định danh không thay chức năng `work`. Kiểm title literal chỉ kiểm câu chữ. Đọc root source cho thấy 35.145 là `Bāhirānattahetusutta`, 35.146 là `Kammanirodhasutta` có nghiệp cũ/mới. Mismatch citation theo hệ ID ghim là quan sát của Codex trên nguồn. Chưa chứng minh BCR tự thẩm định ý nghĩa của P075 hoặc các hệ đánh số khác.

**AC09:** Đã dùng đúng nguồn 211, lines `0452c01–02`, cùng range `0452b04..0452c16`; không dùng gate lịch sử `0453a01` thuộc 212 để hỗ trợ 211. Mulu 212 bắt đầu `0452c17`. Các nguồn đích được A đọc thật, nhưng giải thích danh sách bốn mục dù nói năm, quan hệ truyền bản và độc lập nhân chứng cần chuyên gia Hán. CLI work/resolve không tự trở thành subwork semantic approval.

**AC01/05/06/08/10/11/12:** Có các lexical hits, nguồn đích và candidate excerpts; B thiếu assessment reader xác thực nên giữ UNVERIFIED. Suy luận hai cấp nhân quả, quy tắc không phán xét nạn nhân, nghĩa `opakkamika`, phạm vi “mọi khổ/bất hạnh”, điều kiện nghiệp/tái sinh và khái niệm cetanā/taṇhā chưa được máy phê duyệt. Không hòa nhân chứng hoặc bản dịch thành ground truth.

Ở AC11, selector bổ sung đã khóa `mn135:5.6` không có trong JSON ghim; giữ BLOCKED, không thay bằng một selector thuận lợi hơn. Hai selector `mn135:7.1` và `mn135:13.1` vẫn VERIFIED theo A. `fixed-selector-blocks.json` ghi giới hạn đối chứng này. Chín gate Quick UNVERIFIED có raw check/locator/limitations riêng trong `quick-pending-gates.json`; BCR giữ retrieval hits nhưng không cấp quyền trích dẫn cho phần chưa giải được.

**AC07:** Discovery queries Gethin/Thanissaro đã chạy, draft vẫn lưu được. Tuy nhiên không có tệp nguồn hiện đại đã khai/pin cho sách và chú giải được quy thuộc. **BLOCKED: không đủ dữ liệu trong corpus hiện tại** cho kiểm lời/phạm vi attribution. Không dùng internet để lấp khoảng trống.

B assessment attempt của AC07 trả `REJECTED` ở check `supporting_evidence=FAIL` vì proposal không có evidence IDs; `approved_binding` vẫn UNVERIFIED. Đây là từ chối hồ sơ thiếu căn cứ, không phải phán quyết semantic UNSUPPORTED cho các tác giả. Cả 57 claims trong store vẫn mang trạng thái candidate; không có accepted claims.

## Research và phương pháp C

`research_case.py` gọi API hiện hành `LocalResearch`/`LocalHost`/`ResearchStore`; lớp audit chỉ lưu các giá trị reader thực trả về. Không sửa package/code. Mỗi run tạo candidates tự lấy câu nguồn và proposal riêng chứa đúng đoạn bài; chỉ gắn evidence đã kiểm từ intended work/path như căn cứ **ứng viên**, không giả định mức hỗ trợ. C chạy truy vấn lexical với host bound 3, fetch 4 để phát hiện cắt; giới hạn/candidate/checked scope/pins và kết quả A giữ đầy đủ trong receipts. Chưa có reviewer xác nhận adequacy hoặc nguồn độc lập; no-hit không chứng minh không tồn tại phản chứng.

`publication-check` API và CLI đã gọi trên version hiện hành. Kết quả publication luôn false. Review packages được export và đối chiếu lại với store; không nhập reviewer giả, không review-decision giả và không tạo approval. Các review packages là dữ liệu thẩm định, không capability hoặc sự cho phép công bố.

## Runtime và sự cố môi trường

Mỗi command có argv/cwd/env chọn lọc, UTC start, stdout/stderr riêng, exit code và wall seconds. `perf_counter` đo một observation mỗi subprocess, gồm startup và ghi output; retrieval chạy trước Quick, cache không flush. Không dùng các số này làm benchmark cold-cache, ngưỡng nghiệm thu hoặc bằng chứng hệ thống nhanh hơn.

| Tầng | Số observations | Median wall giây | Min–max giây |
|---|---:|---:|---:|
| CLI retrieval | 25 | 0.1422 | 0.1143–0.1988 |
| CLI Quick | 25 | 0.1943 | 0.0978–2.6240 |
| Research API (gồm capture/export/check và audit) | 12 | 13.4742 | 0.8255–53.8258 |

CPU/RSS/IO theo ca, token và chi phí AI: **CHƯA ĐO**, giữ null. Không gọi dịch vụ AI trong harness.

Lượt build đầu trên ext4 của WSL làm ổ C: giảm xuống khoảng 4 GB trống, dù `df` WSL báo nhiều dung lượng ảo. Đã dừng build và chuyển sang volume ext4 trên D:. WSL ngắt giữa lúc copy; kiểm prefix không khớp đã chặn dùng bản sao đó. Copy mới đọc lại từng khối, SHA tích lũy khớp, rồi CLI rebuild FTS từ dữ liệu checkpoint. `resource_incident.json`, `build-migration.json`, log build và receipt resumed giữ rõ sự cố. Không có kết quả chính suy ra từ lượt build bị ngắt; sự cố này thuộc môi trường/lưu trữ.

Lượt kiểm tra đầu của harness dừng trước mọi ca AC do đọc sai khóa ledger (`sources` thay vì `entries`). Đã lưu script/manifest/log thất bại trong `harness-attempt-01`, ghi `harness-correction.json`, sửa script ngoài repo và chạy lại. Đây là lỗi harness của Codex, không tính thành lỗi BCR hoặc che khỏi hồ sơ. Direct I/O chỉ bật cho loop volume dẫn xuất mới trong lượt đọc; `temporary-volume-io.json` và receipt ghi cấu hình. Cấu hình/cache này là giới hạn của phép đo runtime, không làm thay đổi câu hỏi, queries, nguồn hoặc code.

Phiên foreground lại kết thúc sau khi cả 12 ca đã lưu outputs, trước marker hash cuối; `main-run-completion.json` ghi bước khôi phục. Chỉ remount volume, đọc hash toàn index và chạy các audit cuối, không chạy lại các ca hoặc tạo run mới. Native Windows Git xác nhận main sạch; WSL Git đọc checkout Windows báo khác biệt CRLF do cấu hình autocrlf khác, còn checkout WSL có 13 type changes do symlink tới nguồn đã ghim. `git-status-interpretation.json` tách các hiện tượng này; không âm thầm chỉnh file để làm sạch log.

## Bàn giao và việc chưa thực hiện

| Loại hạn chế | Quan sát và phạm vi kết luận |
|---|---|
| Code/hợp đồng | Retrieval lexical có bound; A chỉ cấp quote cho span liên tục; chưa tự phê duyệt semantic. CBETA main-body role Y cần review độ chi tiết. Chưa có regression/expected answer độc lập chứng minh phải sửa mã. |
| Dữ liệu | Nguồn modern AC07 chưa khai/pin; index chỉ ba corpus chọn lọc. Không-hit ngoài indexed scope không chứng minh toàn corpus thiếu nguồn. |
| Môi trường | C: chứa WSL VHD thiếu dung lượng; chuyển index sang ext4 D:, remount sau ngắt phiên. SQLite/index hash cuối đã được kiểm lại. |
| Phương pháp/harness | Không ground truth/reviewer độc lập; exploratory và một wall observation. Khóa selector AC11 có một ID không tồn tại; giữ BLOCKED. Lỗi đọc khóa ledger trong harness được bảo lưu và sửa ngoài repo. |

Thư mục này nằm ngoài Git repository và mọi source checkout. `index-main-manifest.json` ghi index SHA `99da1d7f82b360481568c8458d8bfd2e982b8b7497aaee646912898df82095a2`, parser state, counts và FTS state; `index-after.json` đối chiếu hash sau chạy. `old-index-preservation.json` và source audits kiểm bảo toàn index cũ/pins/bytes. `code-snapshot.tar` giữ mã nguyên commit, sources/raw outputs và Research store backup cho kiểm toán. Mọi artifact raw bàn giao có SHA-256 trong `SHA256SUMS.txt` và manifest.

Chưa thực hiện: baseline lịch sử trước A; reviewer độc lập/human Pāli-Hán; semantic assessment/approval; nhập review/approval; Research publication; benchmark nhiều lượt/cold cache/full 13 corpus; chi phí AI và semantic accuracy. Lý do tương ứng: không phải phép baseline trong vòng này, capability/ground truth chưa có, publication đóng, ngoài phép đo hiện hành. Không đổi tiêu chí nghiệm thu và không mở phase phát triển mới.

Raw được giữ local và đóng gói riêng cho bàn giao; **`external_archive_pending`** vì chưa được chỉ định nơi archive dài hạn có quyền truy cập cho reviewer. Gói chứa Word và dữ liệu riêng, không được tự đưa lên GitHub. Không commit vào main, không push/merge. Nếu sau này cần công khai metadata evidence, dùng nhánh evidence riêng và PR để chủ dự án duyệt.
