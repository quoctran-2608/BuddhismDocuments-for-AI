# Buddhist Corpus Research 2.0 — Tiêu chí nghiệm thu

> Trạng thái tài liệu: **MỤC TIÊU**
>
> Vai trò: quy định cách chứng minh từng yêu cầu trong
> `docs/v2/REQUIREMENTS.md` đã thật sự được triển khai.
>
> Toàn bộ 2.0 hiện đang **CHƯA TRIỂN KHAI ĐẦY ĐỦ**. Có tài liệu thiết kế không
> đồng nghĩa yêu cầu đã đạt.
>
> Nghiệm thu hệ hiện hành nằm riêng trong `docs/ACCEPTANCE.md`.

## 1. Nguyên tắc nghiệm thu

Mỗi yêu cầu 2.0 chỉ được chuyển từ **MỤC TIÊU** sang **HIỆN HÀNH** khi có đủ bằng
chứng phù hợp.

Các mức bằng chứng có thể dùng:

- **TỰ ĐỘNG**: có bài kiểm thử chạy bằng máy;
- **CẤU TRÚC**: có thể kiểm bằng lược đồ dữ liệu, định dạng, cấu hình hoặc mã;
- **TÍCH HỢP**: có kiểm thử qua nhiều lớp của hệ thống;
- **NGHIÊN CỨU CHUẨN**: có tình huống nghiên cứu cố định kiểm hành vi học thuật;
- **RÀ SOÁT**: cần kiểm thủ công có chủ đích cho phần chưa thể tự động hoàn toàn.

Không được chuyển trạng thái chỉ vì đã có lớp, hàm hoặc trường dữ liệu mang đúng
tên.

### Bằng chứng triển khai Giai đoạn A — 11/10/2026

`tools/corpus_research/verification.py` đã có lõi Bản ghi bằng chứng, Cửa kiểm
bằng chứng và năm trạng thái kiểm câu trích. `tests/test_verification.py` có
44 bài kiểm thử độc lập với 13 submodule: giữ 32 phương thức ban đầu và bổ sung
12 phương thức về ranh giới tin cậy. Có tích hợp `retrieval.evidence()` trên
SQLite nhỏ, đọc blob Git thật ghim trong repo tạm và kiểm dữ liệu JSON kiểu
GitHub với cùng lõi. Mẫu thử nhỏ là dữ liệu phần mềm, không phải chứng cứ corpus.

Sau rà soát, `opened_source` và `paraphrase_review` đều là dữ liệu chưa tin cậy.
`source_contract` phải lấy từ config/manifest do ứng dụng kiểm soát, không từ
ứng viên. `source_reader(request)` là khả năng thực thi do ứng dụng cấu hình
riêng: nhận định danh kho/commit/path và bộ chọn work/segment/sequence, tự đọc
đúng phiên bản đã ghim, giải vị trí/vai trò/nhân chứng và phạm vi từ chính nguồn.
Cửa kiểm đối chiếu nội dung đầy đủ, định danh, vị trí và phạm vi với lần đọc độc
lập này. SHA blob tự tính chỉ kiểm tính nhất quán của byte; mã băm hay các trường
tự khai khớp nhau không chứng minh quan hệ commit/path → blob. Chính cấu hình
nguồn và lần đọc độc lập thiết lập quan hệ đó. Git cục bộ vẫn dùng `rev-parse`
và `cat-file`, không đọc nội dung working tree thay cho blob ghim.

Ứng dụng nối `read_local_source()` và bộ giải vị trí theo định dạng nguồn bên
trong `source_reader`; callback không được chỉ trả lại `opened_source`. Phần
giải vị trí 13 nguồn và tích hợp CLI chưa được bổ sung trong lát cắt này. Tệp
đã đọc đưa vào dưới dạng JSON, kể cả JSON do adapter Git từng trả ra, không tự
mang quyền xác minh. Con trỏ chưa mở vẫn là `CANDIDATE`; có nội dung mà thiếu
khả năng đọc độc lập giữ `UNVERIFIED`; đủ nguồn độc lập và các phép kiểm khác
mới đạt `VERIFIED`. Mâu thuẫn với căn cứ độc lập bị `REJECTED`.

`paraphrase_review` là đề xuất, nay cần thêm `review_id`. Khả năng thực thi
`review_reader(review_id)` do ứng dụng nối vào kênh người kiểm/phê duyệt đã xác
thực, trả bản đánh giá đã được chấp thuận gồm `review_id`, `quotation`,
`source_text`, `supported`, `reviewer`, `rationale`. Callback chỉ nhận mã tra
cứu, không nhận nội dung đề xuất để tự xác nhận. Tất cả trường trên phải khớp
chính xác, gồm kiểu boolean và người kiểm. Thay câu diễn đạt lại, văn bản nguồn
cần kiểm hoặc danh tính người kiểm làm đánh giá cũ mất hiệu lực. Thiếu đánh giá
đã xác thực giữ `UNVERIFIED`; đánh giá hợp lệ đồng ý trả `PARAPHRASE`, phản đối
trả `QUOTE_MISMATCH`. Diễn đạt lại luôn không có quyền trích nguyên văn. Máy
không tự xét đúng sai ngữ nghĩa; chưa có kênh phê duyệt thật tích hợp sẵn.

Hai callback nằm ngoài dữ liệu JSON, không được chọn bởi JSON hoặc mã do AI
sinh từ đề xuất. Các cờ `trusted`, `verified`, `attested`, `approved` không cấp
quyền; tệp JSON đánh giá tự tạo không phải kênh phê duyệt đã xác thực. Lõi không
thực hiện I/O trực tiếp và không bắt buộc SQLite/shell; callback tùy môi trường
có thể thực hiện I/O. Dữ liệu đầu vào/đầu ra vẫn chuyển được sang JSON. Thay đổi
tương thích có chủ ý: lời gọi cũ chỉ truyền dữ liệu sẽ giữ `UNVERIFIED`, dù
trước đây các trường tự khai khớp nhau đã cho qua. Các kỳ vọng thiếu an toàn ở
kiểm thử nguồn JSON, diễn đạt lại và tiến trình cô lập đã được siết lại; các
trường hợp hợp lệ dùng căn cứ độc lập do host kiểm thử cấu hình.

`VERIFIED` chỉ xác nhận nguồn/vị trí và phép kiểm câu trích áp dụng. Nó không
cấp mức hỗ trợ luận điểm, không xác nhận kết luận học thuật và không nâng
`computational_segmented` hoặc `parallel_alignment` thành nhân chứng chính.
`evidence_class`, `text_role`, `witness` được giữ riêng. Chưa có lớp luận điểm.

Kết quả Windows/Python 3.14: 44/44 bài A đạt (mốc trước 32/32). Baseline 1.0
chạy 36 bài với 29 lỗi, chặn 9 bài acceptance ở `setUpClass`; mốc A trước chạy
68 bài với 29 lỗi; sau rà soát chạy 80 bài với cùng 29 lỗi. Đối chiếu danh sách
`ERROR:` không có chênh lệch. Nhóm lỗi vẫn là thiếu submodule/tệp/Git object và
khóa SQLite khi dọn thư mục tạm. Không sửa hoặc bỏ qua lỗi 1.0; toàn suite chưa
xanh. Ở lần rà soát mã này chưa xác nhận trên checkout đủ nguồn, phiên Work thật hoặc GitHub plugin
thật. Chưa có adapter remote xác minh phiên bản tích hợp: chỉ dữ liệu plugin
tự khai phải giữ `UNVERIFIED`; chỉ host đã nối công cụ đọc đúng phiên bản mới
có thể cung cấp khả năng tương đương đường Git cho cùng lõi.

Các mục A dưới đây ghi **đã có lõi, chờ nghiệm thu**, không chuyển toàn bộ yêu
cầu sang HIỆN HÀNH. Tại mốc rà soát A này, Giai đoạn B–E chưa triển khai.

### Nghiệm thu cuối mã lõi A — 11/10/2026

Đã fetch và xác nhận `main` tại `f7415f574ed1510d5854ee00db6baafe2484e355`
chưa chứa Giai đoạn A; mã A được kiểm tại
`60873fbe55fe4b2061fba8c0e0050afbb5b07f2f`. Hai phiên bản chạy trong worktree
riêng trên Ubuntu WSL2/Linux 6.6.87.2, Python 3.12.3, SQLite 3.45.1. Đã tải đủ
13 submodule bằng `submodule update --init --recursive --depth 1`, đối chiếu
HEAD với Gitlink/manifest và xác nhận nguồn không bị sửa. Baseline dùng liên
kết tới chính các checkout nguồn đã ghim của nhánh A, bảo đảm cùng byte nguồn.
Môi trường được giữ tại `/home/tranquoc/bcr-phase-a-final-20261011`; checkout
Windows gốc vẫn chưa khởi tạo nguồn. Không sửa Gitlink, manifest hay cấu hình.

| Môi trường và bộ nguồn | Phiên bản | Bài chạy | Bài đạt | Error records | Assertion failures | Bài acceptance bị chặn |
|---|---|---:|---:|---:|---:|---:|
| WSL/Python 3.12.3, đủ 13 nguồn ghim | main | 45 | 45 | 0 | 0 | 0 |
| WSL/Python 3.12.3, cùng 13 nguồn ghim | A | 89 | 89 | 0 | 0 | 0 |
| Windows/Python 3.14, thiếu nguồn | main | 36 | 9 | 29 | 0 | 9 |
| Windows/Python 3.14, cùng tình trạng thiếu nguồn | A | 80 | 53 | 29 | 0 | 9 |

44/44 phương thức A đạt riêng trên cả Windows và WSL; không bài nào bị bỏ qua.
29 error records Windows giống nhau cả tên bài và loại exception: 26
`PermissionError` khóa SQLite, 2 `FileNotFoundError`, 1
`subprocess.CalledProcessError` do nguồn Git thiếu. Một bài có thể báo cả lỗi
thân bài và cleanup; lỗi `setUpClass` không được tính vào số bài đã chạy.
Không kết luận A sửa lỗi nền Windows từ việc suite Linux xanh. Đối chiếu cùng
môi trường không phát hiện lỗi mới hoặc lỗi thuộc A; hàm đường dẫn chuyển từ
`pointer_export.py` có phần thực thi AST giống bản main, các tệp 1.0 khác giữ
nguyên. Kết quả này nghiệm thu mã lõi trong phạm vi suite hiện có, không thay
cho kiểm toàn bộ dữ liệu/hiệu năng hoặc nghiệm thu toàn bộ 2.0.

Chưa thử phiên Work/GitHub plugin thật, chưa tích hợp adapter remote, bộ giải
vị trí 13 nguồn hay kênh phê duyệt diễn đạt lại vào CLI. `REQ-ENV-001/002` vẫn
chưa được nghiệm thu đầy đủ. Không có sửa mã A được yêu cầu bởi kết quả kiểm
thử này; PR giữ Draft chờ người bảo trì rà soát và chấp thuận phạm vi/giới hạn.

---

### Bằng chứng triển khai mã lõi Giai đoạn B — 11/10/2026

Nền là `main` tại merge commit A
`5880d260e7afccde67b56e1c85f504ec52ecf376`. Đã fetch, xác nhận không có thay
đổi nền và tạo nhánh `feature/bcr-v2-phase-b`. Chỉ bổ sung `claims.py`,
`test_claims.py` và cập nhật tài liệu này; không sửa A, 13 nguồn, parser,
SQLite/schema, FTS, ranking, locator hay CLI. Các mô tả Draft/chờ chấp thuận
trong báo cáo A phía trên là lịch sử trước khi PR #1 được merge.

`make_claim()` tạo đủ 13 trường theo Design mục 9, luôn `candidate`, mức hỗ trợ
null và độc lập nguồn `uncertain`. Trường chưa có căn cứ giữ null/danh sách rỗng.
Có thêm `presentation` (certainty và quotations) và `revision_evidence_ids` để
kiểm cách công bố và giữ bằng chứng dẫn tới sửa đổi. Thiếu mã/nội dung/loại,
dữ liệu sai kiểu hoặc loại ngoài bảy loại quy định bị từ chối. AI chỉ đề xuất
luận điểm, phân tách, mức hỗ trợ và cách trình bày; không dùng dấu câu hay cờ
JSON để tự xác nhận tính nguyên tử.

#### Hợp đồng đánh giá và ranh giới với A

Hai capability cho đánh giá do **ứng dụng** nối bên ngoài JSON/mã AI sinh;
công bố còn bắt buộc `history_reader` theo hợp đồng gia cố bên dưới:

- `evidence_reader(evidence_id)` lấy kết quả **thật sự qua cửa kiểm A** từ kho
  do ứng dụng kiểm soát, hoặc kiểm lại qua A. Trả envelope A gồm `status`,
  `source_opened`, `checks`, `quote`, `evidence`; B kiểm envelope, mã yêu cầu,
  trạng thái và dữ liệu nguồn/ngữ cảnh. JSON ứng viên có `state=VERIFIED`
  không cấp quyền. Cache phải vô hiệu hóa kết quả cũ khi bằng chứng đổi;
  file JSON tùy ý không phải kho đã xác thực.
- `assessment_reader(review_id)` lấy đánh giá đã phê duyệt qua kênh xác thực.
  Chỉ nhận mã tra cứu, không nhận đề xuất để tự xác nhận. Thiếu/hỏng capability
  hoặc đánh giá hợp lệ giữ chờ kiểm, khác với `UNSUPPORTED` đã được đánh giá.
  Chưa xây kênh phê duyệt thật.

Đánh giá được phê duyệt cần đủ:

```text
review_id
claim                 # đúng claim_subject(), không chứa nhãn tự phong
evidence              # Evidence Records hiện tại, theo thứ tự mã support/counter
atomic                # boolean, quyết định ngữ nghĩa của người kiểm
support_level         # DIRECT / STRONG / WEAK / UNSUPPORTED / CONTRADICTED
scope                 # narrow_lookup / research
evidence_uses         # evidence_id + basis + justification cho từng bằng chứng
required_limitations
max_certainty         # tentative / asserted
reviewer
rationale
```

`claim_subject()` gắn mã/run/nội dung/loại, mã bằng chứng/phản chứng, giới hạn,
cách trình bày và thông tin sửa đổi. Ảnh chụp bằng chứng giữ toàn bộ trường A,
gồm repository/path/SHA, quotation/context, vai trò và nhân chứng. So sánh JSON
chính xác, phân biệt boolean/số; nội dung/provenance đổi làm phê duyệt cũ mất
hiệu lực. Hash/nhãn tự khai không xác nhận quyền phê duyệt. Người kiểm chịu
trách nhiệm xác nhận nguyên tử, đúng loại/phạm vi, quan hệ ngữ nghĩa và căn cứ
phù hợp; máy kiểm liên kết dữ liệu và các quy tắc tất định.

`evidence_uses.basis` phân biệt `textual_report`, `primary_text`, `relationship`,
`historical_corroboration`, `comparison`, `interpretation`,
`empirical_observation`, `metaphysical_argument`. Một tên basis đúng không làm
luận điểm đạt: phải có đánh giá đã phê duyệt gắn đúng dữ liệu. Metadata chỉ
dùng cho relationship; textual_report không chứng minh sự thật lịch sử/thực
nghiệm/siêu hình. Primary text cần lớp canonical/structured, root_text và
witness; bản dịch/note/discovery không được nâng thành bản gốc. Discovery vẫn
có thể phục vụ tra cứu hẹp về chính dữ liệu ấy với lớp/vai trò/witness giữ
nguyên và giới hạn `discovery_source:<evidence_id>:<class>`. Điểm tìm kiếm và
số citation không quyết định mức hỗ trợ hay độc lập nguồn.

#### Cửa kiểm, tổng hợp và lịch sử

`assess_claim()` trả ASSESSED/UNVERIFIED/REJECTED riêng với vòng đời luận điểm.
`final_claim_gate()` là nơi cấp accepted: cần bằng chứng A hợp lệ, đánh giá
nguyên tử/hỗ trợ đã phê duyệt, loại/cách dùng nguồn phù hợp, quotation đúng
wording/vai trò/witness, đủ giới hạn và cách trình bày không vượt đánh giá.
DIRECT/STRONG không tự vượt điều kiện khác. WEAK cần certainty=tentative và
giới hạn rõ. UNSUPPORTED/CONTRADICTED bị rejected dù thêm câu chữ giảm nhẹ.
Thiếu approval thì không gán mức hỗ trợ suy đoán.

B chỉ cho chốt tra cứu hẹp textual/relationship ở quick với scope=narrow_lookup
đã phê duyệt. Mọi research, phạm vi rộng và năm loại còn lại giữ chờ điều kiện
C/D (hoặc rejected nếu có lỗi khác). Có thể đánh giá hỗ trợ đủ bảy loại nhưng
chưa cấp quyền chốt nghiên cứu. Cờ tự khai không hoàn thành phản chứng, độc
lập nguồn hoặc Research Run.

`accepted_claim_set()` chạy lại gate để xuất tập được phép. `verify_synthesis()`
cũng chạy lại với reader hiện tại, chỉ nhận danh sách chính xác claim_id, text,
verification_status, limitations, presentation. Mã lạ, câu mới/đổi, nâng mức,
bỏ giới hạn, mục trùng hoặc trường prose thêm bị từ chối. Accepted đã serialize
không tự mang quyền. Chưa xác minh ngữ nghĩa đoạn văn tự do; phần đó chờ E.

`append_claim()`/`revise_claim()` tạo bản sao lịch sử JSON, không sửa đè snapshot
cũ. Bản sửa cần mã mới, predecessor còn hiệu lực, lý do và bằng chứng dẫn tới
sửa vẫn nằm trong liên kết support/counter. Giữ phản chứng cũ, không đổi run,
không cho chu trình, ghi đè mã hay nhánh thay thế mơ hồ. Bản sửa bắt đầu candidate
và cần đánh giá mới. `history_claim()` chiếu superseded nhưng giữ snapshot gốc.
Mọi gate/export phải đọc lịch sử hiện hành qua capability của host, gồm cả
luận điểm đầu tiên. Danh sách caller gửi không xác nhận lịch sử đầy đủ; bản cũ
bị loại dù approval cũ còn tồn tại. Hàm thuần không phải cơ chế quyền truy cập
chống ứng dụng tự ghi đè dữ liệu hay bỏ qua gate.

#### Kiểm thử tại mốc triển khai B trước gia cố lịch sử

Ubuntu WSL/Python 3.12.3/SQLite 3.45.1 dùng đủ 13 checkout nguồn ghim, cùng byte
nguồn với baseline qua liên kết trong worktree B. Đối chiếu Gitlink/HEAD và kiểm
nguồn không bị sửa trước/sau chạy. Tệp B được chép nguyên byte từ nhánh Windows
sang worktree Linux riêng, giữ hash kiểm tra; không cập nhật pin.

| Bộ kiểm và môi trường | Chạy/đạt | Error/failure/skip |
|---|---:|---:|
| Baseline main sau A, WSL đủ nguồn, chạy mới trước sửa mã | 89/89 | 0/0/0 |
| Riêng B, WSL | 66/66 | 0/0/0 |
| Toàn suite sau B, cùng môi trường/nguồn WSL | 155/155 | 0/0/0 |
| Riêng B, Windows/Python 3.14 | 66/66 | 0/0/0 |
| Riêng A, Windows/Python 3.14 | 44/44 | 0/0/0 |

Lệnh: `PYTHONPATH=tools python3 -m unittest discover -s tests -p test_claims.py -v`
và `PYTHONPATH=tools python3 -m unittest discover -s tests -v` (Windows dùng
python). Không sửa/bỏ qua test cũ. 89 bài cũ vẫn đạt; không có hồi quy mới trong
WSL đối chiếu. Toàn suite Windows chưa chạy lại ở mốc B; lỗi nền Windows ghi
ở báo cáo A, không tuyên bố đã sửa. Không có GitHub CI thực thi suite.

66 phương thức B dùng mẫu phần mềm nhỏ, tất định, độc lập submodule, có kết quả
thật từ cửa kiểm A cho fixture. Bao phủ tự phong trạng thái, thiếu/hỏng capability,
binding, sai loại/basis/vai trò/witness, năm mức hỗ trợ, giới hạn/WEAK, đóng research,
tổng hợp có cấu trúc, lịch sử/supersession và JSON. Tiến trình riêng chặn import
SQLite/subprocess vẫn chạy gate hợp lệ. Đây không phải chứng cứ Phật học hoặc
bộ nghiên cứu chuẩn thật.

Đã có mã lõi B và kiểm tự động, **chờ rà soát/nghiệm thu độc lập**. Chưa tích hợp
CLI, nguồn thật với resolver A, kênh phê duyệt ngữ nghĩa/diễn đạt lại, phiên Work
hoặc GitHub plugin thật. REQ-ENV-001/002 chưa nghiệm thu đầy đủ. C/D/E và bộ golden
research đầy đủ chưa triển khai; không chuyển toàn bộ 31 yêu cầu sang HIỆN HÀNH.
Chỉ commit/push nhánh B; chưa tạo PR hoặc merge.

#### Gia cố ranh giới lịch sử công bố — 11/10/2026

Mốc trước sửa là `3900236d58e1e08aa3adabd2a949db4a9201b9b5` trên
`feature/bcr-v2-phase-b`. Gate cũ chỉ bắt buộc lịch sử khi ứng viên có predecessor;
C1 không có predecessor vẫn được accepted khi bỏ lịch sử sau khi C2 thay thế.
Batch cũ mặc định lấy `claims` làm lịch sử đầy đủ, nên subset `[C1]` che mất C2.
Synthesis kế thừa lỗ hổng đó dù phê duyệt ngữ nghĩa C1 vẫn hợp lệ.

`final_claim_gate()` nay luôn gọi `history_reader`, không nhận quyền hiện hành
từ `history` JSON. `accepted_claim_set()` bỏ fallback `history=claims` và gọi
lại gate cho từng đề xuất. `verify_synthesis()` gọi lại batch với các reader
hiện tại, từ chối mục C1 đã từng accepted nếu lịch sử host nay có C2.
Tham số `history` cũ được giữ tương thích nhưng bỏ qua khi xét quyền công bố;
thiếu, cắt ngắn hay gắn nhãn trusted/complete vào JSON không thay thế capability.

Hợp đồng tối thiểu:

```text
history_reader({claim_id, run_id})
  -> {claim_id, run_id, complete: true, history: [immutable snapshots]}
```

Request chỉ chứa mã luận điểm và run (run có thể null trong quick), không gửi
nội dung, đề xuất lịch sử, trạng thái hay cờ hiện hành. Host tự cấu hình kho
lịch sử có thẩm quyền và phạm vi project/phiên/tài khoản bên ngoài JSON hoặc
mã AI sinh. Trả toàn bộ lịch sử áp dụng trong phạm vi ấy, gồm predecessor và
mọi successor hiện có, kể cả khi đang hỏi mã cũ; không chỉ trả các tổ tiên.
Envelope phải khớp claim/run, từng snapshot thuộc cùng run và nội dung luận
điểm phải khớp chính xác `claim_subject()` trong kho. Các kiểm append-only,
chu trình, trùng mã, run và giữ phản chứng tiếp tục áp dụng.

`complete: true` là cam kết của capability đã được host cấu hình tin cậy,
không phải chứng minh bằng JSON. Có callback chưa đủ: callback không được
echo dữ liệu caller, tự suy hiện hành từ ứng viên, chọn kho theo JSON hay trả
cache cũ. Lõi không thể phát hiện host cố ý nói sai về tính đầy đủ. Store trả
thiếu mà gắn complete=true vi phạm hợp đồng, không thuộc bảo đảm của lõi.

- `accepted`: snapshot đã đăng ký khớp lịch sử host đầy đủ/hiện hành, chưa
  bị thay thế và mọi điều kiện bằng chứng/đánh giá/cách trình bày đều đạt.
- `candidate`: thiếu/hỏng capability hoặc thiếu dữ liệu, complete không phải
  boolean true, hoặc còn phép kiểm UNVERIFIED (gồm điều kiện C/D).
- `rejected`: có FAIL, như sai scope, snapshot bị sửa, mã không có trong lịch
  sử được host xác nhận đầy đủ, lịch sử mâu thuẫn hoặc lỗi gate khác.
- `superseded`: lịch sử hợp lệ xác nhận snapshot đã bị thay thế, không có
  FAIL khác; ưu tiên hơn trạng thái chờ. Trường hợp có FAIL vẫn rejected.

| Bộ kiểm tại mốc gia cố | Chạy/đạt | Error/failure/skip |
|---|---:|---:|
| Baseline B trước sửa, WSL đủ 13 nguồn ghim | 155/155 | 0/0/0 |
| Riêng B sau sửa, Windows và WSL | 82/82 mỗi môi trường | 0/0/0 |
| Toàn suite sau sửa, WSL cùng nguồn ghim | 171/171 | 0/0/0 |

Giữ cả 66 phương thức B cũ; siết kỳ vọng khi dữ liệu khác snapshot host và
thiết lập kho fixture độc lập với tham số công bố. Thêm 16 bài, gồm hồi quy
C1 qua cả ba đường, subset/lịch sử bị cắt, tự khai accepted/current/trusted,
thiếu/lỗi/incomplete reader, request chỉ có mã, sai scope, đổi snapshot dù có
approval mới, C2 cần approval riêng, hai luận điểm độc lập và lịch sử mâu thuẫn.
Tiến trình chặn SQLite/shell vẫn chạy gate với capability host cấu hình.
89 bài A/legacy vẫn đạt, không skip hay hồi quy trong môi trường đối chiếu.
Không đổi pin, mã A hoặc các thành phần truy xuất hiện hành.

Đây vẫn là lõi thuần và fixture phần mềm, **chưa nghiệm thu B hoàn toàn**.
Chưa có kho lịch sử/adapter thực, xác thực chủ thể, quyền ghi hay transaction.
Host phải bảo vệ snapshot chỉ nối thêm, đọc mới và phối hợp công bố với thay
đổi lịch sử để tránh khoảng thời gian giữa đọc và ghi. Giai đoạn D cần tích
hợp phạm vi Research Run/quick, lưu vết phiên bản, kho có thẩm quyền và cơ chế
phối hợp đó. Chưa triển khai C/D/E, chưa xác minh Work/plugin thực hoặc golden
research đầy đủ; REQ-ENV-001/002 và ma trận nghiệm thu không được nâng trạng thái.

---

### Bằng chứng triển khai mã lõi Giai đoạn C — 11/10/2026

Nền `main` đã fetch và xác minh tại
`adf2daf3103bc8c6b963dc5687a2739fefad946d`; nhánh triển khai là
`feature/bcr-v2-phase-c`. Chỉ thêm `tools/corpus_research/counterevidence.py`,
`tests/test_counterevidence.py` và cập nhật tài liệu này. Mã và bài kiểm A/B,
13 Gitlink nguồn, parser, SQLite/schema, FTS, ranking, locator và CLI 1.0 giữ
nguyên. Các nhận xét “chưa triển khai C” phía trên là lịch sử tại mốc A/B.
Kế hoạch vẫn có năm giai đoạn A–E; chưa triển khai D/E.

#### Quan hệ nguồn và cách đếm bảo thủ

`source_independence()` đọc các Evidence Records hiện tại qua `evidence_reader`
của B/A, giữ nguyên nguồn ghim, ngữ cảnh, lớp nguồn, vai trò và nhân chứng.
Hai bản ghi có cùng repository/SHA/path/work/witness được gom một họ nguồn,
không tính hai citation thành hai xác nhận độc lập. Các quan hệ khác lấy qua
`dependency_reader({'evidence_ids': [left, right]})` do host cấu hình, gắn đúng
hai snapshot bằng chứng đầy đủ, căn cứ, người kiểm và lý do:

| Quan hệ | Ý nghĩa và cách xử lý |
|---|---|
| `independent` | Có căn cứ được host chấp thuận rằng hai nguồn là xác nhận độc lập; chỉ đếm riêng khi mọi cặp giữa các nhóm đều đã xác định độc lập |
| `partially_dependent` | Có phần phụ thuộc; giữ quan hệ nhưng không suy ra số nguồn độc lập chính xác |
| `same_source_family` | Cùng họ nguồn; gom nhóm để không đếm lặp |
| `derived_from` | Có căn cứ dẫn xuất, ghi rõ bản ghi dẫn xuất và gom với nguồn gốc |
| `uncertain` | Thiếu bằng chứng, thiếu reader hoặc đánh giá sai snapshot; không tự nâng thành độc lập |

`independent_source_count` là null khi còn quan hệ giữa các nhóm chưa biết
hoặc chỉ phụ thuộc một phần. Các cạnh độc lập mâu thuẫn với chuỗi cùng họ/
dẫn xuất và chu trình dẫn xuất bị từ chối. Một đánh giá không chắc không xóa
được định danh cùng nguồn đã quan sát. Không có bảng kết luận hard-code theo
tên repository, so câu chữ, điểm retrieval hoặc số citation. Tính độc lập
nguồn tư liệu không phải tính độc lập của người/AI phản biện. Reader phải đọc
metadata/provenance hoặc phân tích đã chấp thuận thực; một callback trả JSON
tự tạo không chứng minh quan hệ nguồn. Chưa có adapter quan hệ cho 13 nguồn.

#### Kế hoạch, thực thi và giới hạn tìm phản chứng

`make_counterevidence_plan()` chỉ tạo `PLANNED`, gắn snapshot luận điểm,
corpora, repository/SHA nguồn, giới hạn truy xuất, phạm vi quan trọng chưa kiểm
và các bước có mã. Biểu diễn đủ bảy hướng: ngoại lệ, nhân chứng khác, dị bản,
song hành không khớp, xung đột cùng tầng, phụ thuộc nguồn và giới hạn phạm vi.
Mỗi bước yêu cầu một thao tác hiện hành: search, context, evidence, parallels,
variants, resolve hoặc work. Kế hoạch không quyết định độ đầy đủ học thuật;
host phải phê duyệt các hướng phù hợp với luận điểm và ghi phần chưa kiểm.

`search_counterevidence()` gọi `search_reader(search_id)` ngoài dữ liệu đề xuất.
Host phải nối công cụ 1.0 hoặc đọc biên nhận thực thi thật, trả đúng kế hoạch
đã phê duyệt cùng các bước executed/failed/not_run, complete kiểu boolean,
phạm vi thực kiểm, ứng viên và giới hạn. Lõi kiểm liên kết chính xác kế hoạch,
truy vấn, corpus/pin và biên nhận; thiếu bước, lỗi, cắt kết quả, phạm vi kiểm
một phần hoặc ứng viên chưa mở giữ `UNVERIFIED`. Sai pin/phạm vi, mã bước hoặc
định danh ứng viên mâu thuẫn bị từ chối. Các cờ completed/verified trong JSON
đề xuất không cấp quyền. `execution_complete` chỉ nói thao tác hữu hạn đã
chạy đủ, không chứng minh đã tìm hết corpus hoặc hoàn thành Research.

Kết quả giữ riêng kế hoạch, attempts, candidates và verified_evidence.
Ứng viên phải qua reader A và thuộc phạm vi nguồn thực kiểm mới đủ điều kiện
cho bước sau; `VERIFIED` vẫn chỉ xác minh bằng chứng, chưa xác định phản bác
ngữ nghĩa. Không có hit chỉ cho phép câu “không tìm thấy ứng viên phản chứng
trong các truy vấn và phạm vi đã kiểm”, không kết luận phản chứng không tồn
tại. Phạm vi chưa kiểm không bị xóa khi thao tác hoàn tất.

**Chưa tích hợp truy xuất corpus thật vào C.** Các biên nhận trong test được
host fixture cấu hình độc lập với JSON đề xuất; chúng mô phỏng thao tác phần
mềm, không chứng minh một lần nghiên cứu corpus đã chạy. Không có search
engine thứ hai hoặc adapter Connector mới. Hợp đồng có thể dùng ở cục bộ và
Work; chưa thử phiên Work/GitHub plugin thực.

#### Tác động qua đánh giá và lịch sử B

`assess_counterevidence()` đọc lại kết quả tìm và các bằng chứng hiện tại,
đưa mã bằng chứng tìm thấy vào tập phản chứng tiềm năng, rồi gọi
`assess_claim()` của B. `assessment_reader(review_id)` hiện có phải cung cấp
đánh giá ngữ nghĩa được phê duyệt cho đúng snapshot luận điểm đã bổ sung mã
bằng chứng. Phần `counterevidence_review` trong cùng đánh giá gắn chính xác
kết quả search/independence, findings cho từng phản chứng (supports, irrelevant,
limits, contradicts), quyết định và lý do. Không suy ra ngữ nghĩa từ từ khóa.
Thay luận điểm, nguồn, kết quả thực thi hoặc quan hệ nguồn làm đánh giá cũ
mất hiệu lực; các lần đọc bằng chứng mâu thuẫn bị từ chối.

Quyết định cho phép giữ nguyên, hạ hỗ trợ, thu hẹp, viết lại, UNSUPPORTED,
CONTRADICTED hoặc loại. Mọi thay đổi cần căn cứ limits/contradicts; hạ hỗ trợ
còn phải đọc được phê duyệt B trước đó và chứng minh mức mới thấp hơn mức cũ.
Quan hệ nguồn chưa rõ được giữ uncertain/null trong đánh giá, không bị biến
thành độc lập để cấp mức hỗ trợ. Phê duyệt có thể vẫn xác nhận một giới hạn
câu chữ trong phạm vi hẹp; không cần bịa số nguồn độc lập.

Thu hẹp/viết lại trả `REVISION_REQUIRED` và một đề xuất `candidate` có mã mới,
supersedes_claim_id, lý do và mã bằng chứng dẫn tới sửa; không ghi đè bản cũ,
không thừa kế mức hỗ trợ/phê duyệt. Host chuyển đề xuất qua `revise_claim()`,
lưu lịch sử, lấy phê duyệt B riêng cho bản mới và chạy lại gate với
`history_reader`. C không cấp accepted hoặc tạo cửa công bố thứ hai.
UNSUPPORTED/CONTRADICTED vẫn bị gate B từ chối. Research vẫn chờ D; đường
Quick và cả ba đường gate/accepted_claim_set/verify_synthesis giữ quy tắc B
chặn công bố lại bản superseded. Chưa có kho lịch sử hoặc cơ chế phối hợp
đọc/ghi có thẩm quyền của D.

Ví dụ tích hợp fixture: luận điểm “mọi báo cáo fixture mô tả đèn xanh” có
bằng chứng hỗ trợ; tìm được báo cáo về đèn đỏ, kiểm qua A, rồi phê duyệt ngữ
nghĩa xác nhận giới hạn. C đề nghị đổi thành “một báo cáo fixture mô tả đèn
xanh”; B tạo bản thay thế, giữ phản chứng/lý do, cần đánh giá mới và chặn bản
cũ ở cả ba đường công bố. Fixture này kiểm quy tắc phần mềm, không chứng minh
chân lý Phật học.

#### Đối chiếu bốn yêu cầu C và bằng chứng kiểm

| Yêu cầu | Mã lõi và test tương ứng | Phần còn chờ D/E, chưa nghiệm thu |
|---|---|---|
| REQ-CTR-001 | Plan bảy hướng, search receipts có nguồn ghim; test plan-only, missing/failed/not_run/truncated, capability hỏng, giả cờ và Research vẫn chờ | D nối chính sách bắt buộc tìm với Research Run/gate; E nối truy xuất thật và kiểm bỏ bước trên ca nghiên cứu chuẩn |
| REQ-CTR-002 | Lưu claim/corpus/pin/query/checked/unchecked scope, hits và failures; test no-hit hữu hạn, partial/missing scope, sai pin, JSON roundtrip | D lưu/truy vấn hồ sơ và buộc câu trả lời giữ phạm vi; E kiểm trên corpus và Work/Connector thực |
| REQ-CTR-003 | Năm quan hệ, snapshot binding, gom họ/dẫn xuất, count null khi thiếu căn cứ; test cùng nguồn, derived, partial/uncertain, khác repo/cùng chữ, chu trình và mâu thuẫn | E nối metadata/provenance thực và mẫu nghiên cứu nguồn phụ thuộc; chưa có bộ phân giải quan hệ 13 nguồn |
| REQ-CTR-004 | Reuse assessment B, bảy quyết định và đề xuất sửa; test hạ mức cần approval cũ, mới cần approval riêng, counter giữ lại, chuỗi sửa/lịch sử và ba đường chặn superseded | D lưu lịch sử có thẩm quyền/transaction và Research Run; E nối kênh phê duyệt thực, golden research và kiểm tích hợp |

#### Kết quả tự động

| Bộ kiểm | Chạy/đạt | Error/failure/skip |
|---|---:|---:|
| Baseline main adf2daf, WSL đủ 13 nguồn ghim | 171/171 | 0/0/0 |
| Riêng C, Windows/Python 3.14 và WSL/Python 3.12.3 | 56/56 mỗi môi trường | 0/0/0 |
| Riêng A, Windows và WSL | 44/44 mỗi môi trường | 0/0/0 |
| Riêng B, Windows và WSL | 82/82 mỗi môi trường | 0/0/0 |
| Toàn suite với C, WSL cùng 13 nguồn ghim | 227/227 | 0/0/0 |

WSL dùng checkout riêng ở nền adf2daf và chính 13 checkout nguồn đã ghim từ
lần nghiệm thu A/B, đối chiếu HEAD/Gitlink và diff nguồn trước/sau. Không tải
corpus hoặc dependency mới. Hai tệp mã/test C được chép nguyên byte sang
checkout WSL; không sửa suite A/B/legacy để đạt. Không phát hiện hồi quy trong
suite đã chạy; không suy ra toàn corpus/hiệu năng đã được nghiệm thu.

56 test C gồm các trường hợp đúng/sai và chuỗi A→C→B có lịch sử. Tiến trình
cô lập chặn import SQLite, subprocess và retrieval vẫn chạy đánh giá thu hẹp
hợp lệ với reader fixture; lõi không I/O và không phụ thuộc shell/DB. Reader
host có thể thực hiện I/O; host phải bảo vệ cấu hình capability, quyền phê
duyệt, snapshot, độ mới và phối hợp giữa đọc/ghi/công bố.

Đây là **mã lõi C có kiểm thử, chờ nghiệm thu tích hợp**, không chuyển toàn bộ
C hoặc 2.0 sang HIỆN HÀNH. D còn kho lịch sử/Research Run và chính sách công
bố; E còn adapter thật, 11 ca nghiên cứu chuẩn, kiểm Work/Connector và phép
đo E1–E3 (**CHƯA ĐO**). Luồng xuất/nhập thẩm định REQ-RUN-007 chưa triển khai;
không xây hệ AI phản biện thứ hai, không triển khai D/E trong nhánh này.

---

### Gia cố C: phạm vi nhiều corpus và liên kết hit–A — 11/10/2026

Rà soát commit `b0720b0edfa04a79f6a810c9f34e5ecad4148d8e` xác nhận hai lỗi:
một bước hoàn tất bị yêu cầu phủ toàn bộ plan.scope, khiến kế hoạch nhiều
corpus hợp lệ bị từ chối; pointer trỏ đoạn khác vẫn có thể nhận evidence_id
đã qua A trong cùng corpus/pin. Chỉ sửa mô-đun C, bài kiểm C và tài liệu này.

Phạm vi một bước nay là phần chiếu plan.scope theo step.corpus: đúng một
corpus, repository/SHA đã ghim tương ứng và constraints của kế hoạch giữ
nguyên. Một biên nhận không được nhận đã kiểm corpus khác hoặc toàn kế hoạch.
Để execution_complete=true, mọi bước đã giao phải hoàn tất và tập corpus từ
các bước hoàn tất phải phủ đủ corpora của kế hoạch. Corpus có trong kế hoạch
nhưng không có bước, thiếu biên nhận hoặc bước chưa hoàn tất giữ UNVERIFIED,
không có tóm tắt “không tìm thấy”. Sai pin, corpus hoặc constraints bị từ chối.
Complete vẫn chỉ là thực thi thao tác hữu hạn trong các constraints đã được
host phê duyệt; không chứng minh đã kiểm hết corpus hoặc hoàn thành Research.

Pointer do search_reader cung cấp từ hit thực phải có corpus, repository,
source_sha, source_path tương đối trong repository, work_id (null tường minh
khi không áp dụng) và segment_id hoặc sequence_no đủ xác định vị trí. C kiểm
các trường này với snapshot A, so chính xác cả kiểu dữ liệu; những định danh
nguồn/vị trí bổ sung hiện diện cũng phải khớp. Sai nguồn, work hoặc đoạn trả
REJECTED; thiếu dữ liệu đối chiếu trả UNVERIFIED. Bằng chứng không liên kết
được không được đưa vào verified_evidence, mã phản chứng tìm thấy hoặc đề
xuất sửa. evidence_id đơn lẻ hoặc cờ verified không chứng minh liên kết hit.

Pointer opaque như record_id/locator ID chưa đủ để đối chiếu. Host phải dùng
công cụ/nguồn ghim hiện có để giải chính hit đó, chuẩn hóa các định danh rồi
đưa vào biên nhận search_reader. Không được chép định danh từ một bằng chứng
do JSON đề xuất chọn để tự tạo liên kết. C không bịa mapping hoặc dựng thêm
reader/adapter; pointer chưa giải giữ UNVERIFIED. Lõi chỉ kiểm liên kết dữ liệu,
trách nhiệm về tính xác thực của hit và phép giải vẫn thuộc capability host.

Giữ đủ 56 phương thức test C cũ, thêm 14 phương thức cho hai vấn đề này. Có
hai bước/hai corpus với hit đã qua A, thiếu bước/biên nhận, giả hoàn tất khi
phạm vi hẹp, sai SHA/vượt scope, biên nhận nhầm corpus và hồi quy một corpus;
pointer đúng/sai đoạn/sai nguồn, thiếu định danh/opaque, vị trí sequence, host
chuẩn hóa hit và ngăn hit không liên kết đi vào sửa luận điểm. Điều chỉnh một
kỳ vọng cũ: bước kiểm một corpus hoàn tất hợp lệ nhưng corpus còn lại thiếu
bước nay là UNVERIFIED thay vì REJECTED, execution_complete vẫn false. Fixture
chung cung cấp pointer đầy đủ; hai fixture đổi nguồn/đoạn cập nhật pointer
tương ứng để tiếp tục kiểm loại bằng chứng/quan hệ chưa biết, không né cửa A.

| Bộ kiểm sau gia cố | Chạy/đạt | Error/failure/skip |
|---|---:|---:|
| Riêng C, Windows và WSL | 70/70 mỗi môi trường | 0/0/0 |
| Riêng A, Windows và WSL | 44/44 mỗi môi trường | 0/0/0 |
| Riêng B, Windows và WSL | 82/82 mỗi môi trường | 0/0/0 |
| Toàn suite, WSL cùng 13 nguồn ghim | 241/241 | 0/0/0 |

Số liệu 56/227 và lịch sử A/B phía trên giữ nguyên theo mốc trước gia cố.
Không sửa A/B, 13 nguồn ghim hoặc truy xuất 1.0; không tải thêm dữ liệu.
Giới hạn mã lõi/fixture và phần chờ D/E vẫn giữ nguyên; chưa tích hợp corpus
thật, kho lịch sử, Research Run hoặc adapter mới. Chưa nghiệm thu toàn bộ C.

---

### Bằng chứng triển khai mã lõi Giai đoạn D — 11/10/2026

Nền `main` được fetch và xác nhận tại commit C đã duyệt
`361ccf2874fd35b2de68991aa9319b398e3218b5`; nhánh triển khai là
`feature/bcr-v2-phase-d`. Thêm `research_run.py`, `research_store.py` và
`test_research_run.py`; chỉ cập nhật tài liệu này. Không sửa mã/test A/B/C,
13 nguồn ghim, corpus SQLite/schema, parser/index, FTS, ranking, locator hoặc
CLI. Kế hoạch vẫn gồm năm giai đoạn A–E; không triển khai E. Các câu “chưa
triển khai D” và số liệu A/B/C phía trên giữ nguyên theo mốc lịch sử.

#### Hồ sơ, thông tin host và truy nguyên

`make_research_run()` giữ đủ 28 trường trong Design mục 14.2 và luôn tạo draft.
Host cấu hình `context_reader(run_id)` bên ngoài JSON, cung cấp kho/commit chính,
environment local/connector, pins và locator khi áp dụng. `ResearchStore` dùng
clock host (mặc định UTC) để lập thời điểm; không lấy thời điểm, finalized,
accepted IDs hoặc counterevidence_performed tự khai làm căn cứ. SHA hợp lệ về
định dạng chưa chứng minh nguồn tồn tại: host phải xác lập phiên bản từ cấu
hình/Git/Connector thực. Không có adapter tự khám phá phiên bản trong D.

Scope phải hợp lệ theo hợp đồng C, pins phải thuộc cấu hình host. Local không
cần locator và giữ ba trường remote null; Connector cần repository/commit/root
hợp lệ. model_identifier và verification_config được phép null. Trường riêng
không được tự thêm vào proposal; các trường chain-of-thought/private reasoning
và credential đã biết bị chặn. Host phải loại bí mật khỏi dữ liệu được cung
cấp; kiểm tên trường không phải dịch vụ nhận diện/redact mọi bí mật trong prose.

`capture()` và `finalize()` đọc hiện hành qua evidence_reader, assessment_reader
và các capability C, dùng nguyên assess_claim/final_claim_gate/
assess_counterevidence. Lưu đầy đủ history luận điểm, Evidence Records A, đánh
giá B, kết quả gate, search attempts/candidates/verified_evidence, quan hệ nguồn,
findings và đề nghị sửa C. JSON đầu ra hoặc cache lịch sử không được nối ngược
thành reader nguồn/phê duyệt mới. Thiếu nguồn hoặc approval có thể ghi nhận
trong draft với UNVERIFIED, nhưng không chốt hồ sơ kiểm chứng đầy đủ.

Hai cấu trúc retrieval/research phân biệt truy xuất với nghiên cứu: queries
do AI đề xuất là planned_queries; actual_countersearches lấy từ C đã đọc qua
host, giữ nguyên truy vấn, pin, phạm vi thực kiểm, bước lỗi/chưa chạy và phần
chưa kiểm. evidence/assessments/history giữ đường nghiên cứu; không yêu cầu
viết lại câu trả lời từng chữ hoặc lưu chuỗi suy nghĩ nội bộ. Chưa có biên nhận
tích hợp cho mọi thao tác truy xuất ngoài C; planned query không tự thành
query đã chạy. Hướng tìm phù hợp và ý nghĩa constraints vẫn do host phê duyệt.

`trace_claim(run_id, claim_id)` trả nội dung/loại, hỗ trợ/phản chứng, nguồn ghim,
vị trí/ngữ cảnh/vai trò/nhân chứng, đánh giá đã lưu, mã bằng chứng thiếu và
quan hệ thay thế. Kết quả ghi rõ version và historical_observation_only; không
cấp quyền công bố. `run_history()` đọc mọi snapshot lưu trước đây, gồm các
quan sát C cũ. Yêu cầu C đã ghi được giữ qua sửa draft/luận điểm và tự kiểm lại
khi chốt; truyền danh sách rỗng không xóa một yêu cầu sửa C đang còn hiệu lực.

#### Kho thực, lịch sử và ranh giới giao dịch

`ResearchStore(path, ...)` là adapter SQLite riêng bằng thư viện chuẩn Python.
Đường dẫn và capability chỉ cấu hình từ host, không nhận từ proposal/report.
Kho lưu qua nhiều lần chạy chương trình; marker application_id từ chối DB
khác, gồm corpus index. Không có DB cố định hoặc dữ liệu sinh trong repo.

Mỗi thao tác ghi dùng BEGIN IMMEDIATE và expected_version: SQLite khóa writer
giữa các tiến trình, kiểm phiên bản hiện hành rồi ghi snapshot mới/cập nhật
con trỏ phiên bản trong cùng giao dịch. Mã run/claim/report/decision có ràng
buộc duy nhất; claim ID không tái sử dụng giữa các run. Draft cũng lưu phiên
bản mới, không xóa bản trước. Trigger chặn UPDATE/DELETE các snapshot và bản
ghi lịch sử/thẩm định; API không cho sửa, append, revise hoặc capture lại run
finalized. Đây là bảo vệ qua adapter/SQLite, không chống chủ sở hữu máy sửa
schema, thay file DB hoặc cấu hình reader giả. Host chịu trách nhiệm quyền file.

Run mới thay run finalized bằng supersedes_run_id + revision_reason, phải dùng
claim ID và approval phù hợp run mới. Hai draft có thể đề nghị thay cùng run,
nhưng chỉ một successor được chốt; quan hệ được ghi nguyên tử khi chốt và có
ràng buộc duy nhất. Trạng thái superseded là hình chiếu từ quan hệ, không sửa
byte snapshot cũ. Chu trình/tái sử dụng ID/thiếu lý do bị từ chối. Các phép
append/revise luận điểm vẫn gọi B và giữ quy tắc cùng run_id/phản chứng.

`history_reader({'claim_id', 'run_id'})` đọc đầy đủ lịch sử hiện hành trong kho,
gồm mọi predecessor/successor cùng run. Caller không cắt lịch sử bằng JSON.
Run bị thay thế không còn trả complete=true cho công bố; lưu trữ cũ vẫn đọc
được để kiểm toán. Giữ nguyên cả ba đường B chặn công bố lại luận điểm cũ.

`check_publication()` kiểm expected_version, run còn hiện hành và chạy lại
verify_synthesis của B dưới khóa kho. Lịch sử đổi sau lần kiểm trước gây
ConflictError hoặc bị gate chặn. **Kết quả luôn publication_authorized=false**:
D chưa phối hợp được side effect xuất bản thực với mọi nguồn/approval bên
ngoài. E phải nối quyết định công bố và độ mới của các provider với host có
thẩm quyền. Khóa SQLite bảo vệ sửa/chốt lịch sử trong kho, không tuyên bố bảo
đảm công bố nguyên tử qua mạng hoặc ứng dụng ngoài.

Finalized xác nhận một hồ sơ kiểm toán đủ các phép kiểm áp dụng, không đồng
nghĩa mọi luận điểm accepted. Quick hẹp vẫn qua gate B như cũ; Research cần
phản chứng C đã kiểm/phê duyệt cho mọi luận điểm hiện hành để chốt hồ sơ,
nhưng gate B vẫn giữ candidate do điều kiện tích hợp chưa hoàn thành. Không
sửa hoặc mở rào chắn Research của B chỉ vì đã có run finalized.

#### Xuất/nhập và quyết định phê duyệt tách riêng

`export_review()` lấy snapshot đã capture từ kho, gắn package_id, version và
SHA-256, câu hỏi thẩm định; trả JSON và Markdown. Gói có snapshot đầy đủ,
lịch sử phiên bản của run và snapshot run tiền nhiệm khi áp dụng để giữ căn
cứ sửa, kể cả các lần tìm C trước. Draft chưa đầy đủ vẫn có thể xuất để nhờ
kiểm, với trạng thái/giới hạn UNVERIFIED giữ nguyên; không thành hồ sơ đã duyệt.
verify_review_package đối chiếu toàn bộ gói với bản lưu có thẩm quyền, không
chỉ tin hash do người gửi tính lại. Snapshot/version đổi khiến gói bị stale.

`import_review()` kiểm gói/snapshot hiện hành, danh tính/vai trò khai báo,
thời điểm/session, quan hệ với bên đề xuất, nhận xét từng claim, căn cứ,
giới hạn, đề nghị keep/rewrite/narrow/reject và phần chưa xác minh. Mã claim
phải có trong gói; citation phải vừa liên kết claim vừa có Evidence Record A
trong snapshot. Gợi ý ngoài/thiếu corpus chỉ ghi phần chưa kiểm, không thành
bằng chứng mới. Báo cáo gốc được lưu bất biến, thời điểm nhập lấy từ host.
Các cờ approved/trusted/accepted trong báo cáo vẫn là dữ liệu đề xuất;
import trả PROPOSED, không sửa run/claim hoặc tự cấp approval cho B.

`record_review_decision(report_id, review_id=...)` lưu đối tượng quyết định
riêng qua **assessment_reader B hiện có**. Đánh giá host cần có phần
review_report_decision gắn report/package/claim, disposition approve/reject và
lý do; B vẫn kiểm subject/evidence hiện hành. Quyết định sai snapshot hoặc
nguồn đổi không được ghi như đã duyệt. Nhãn RECORDED chỉ nói quyết định được
lưu; không công bố và không thay assessment_reader bằng báo cáo nhập. Sửa
luận điểm tiếp tục qua revise_claim với ID mới và approval riêng.

**Chưa tích hợp kênh xác thực/phê duyệt thực**. Test dùng oracle host cấu hình
độc lập với proposal/report; danh tính AI tự khai hoặc khác tên model không
chứng minh độc lập thẩm định và không thay tính độc lập nguồn của C.

#### Đối chiếu yêu cầu và kiểm thử

| Yêu cầu | Mã lõi/lưu trữ thật và bằng chứng tự động | Phần còn chờ E |
|---|---|---|
| REQ-RUN-001 | Đủ trường, context/clock host, local/connector, scope/pins; test thiếu định danh/phiên bản/locator, tự khai trạng thái và JSON roundtrip | Nối cấu hình/Git/Connector thực và điều phối tạo run trong nghiên cứu |
| REQ-RUN-002 | retrieval/research riêng, A/B/C snapshots và lịch sử; test planned/actual, trace và chặn private reasoning | Adapter các thao tác truy xuất thực, kiểm khả năng tái lập trên corpus |
| REQ-RUN-003 | Giữ checked/unchecked scope và failures C; test partial scope, nguồn/pin sai, failed search và không bỏ C đã ghi | Chính sách phạm vi/câu trả lời và truy xuất Work/Connector thực |
| REQ-RUN-004 | Trace claim→support/counter→A/provenance/approval/successors; test missing/orphan evidence, wrong run và kiểu nguồn giữ nguyên | Truy nguyên qua giao diện tích hợp và dữ liệu nghiên cứu chuẩn |
| REQ-RUN-005 | Lưu/replay C requests, search/semantics/decisions/revisions và phiên bản cũ; fixture A→C→B→D xuyên suốt | Nối executor/kênh phê duyệt thật, quy trình nghiên cứu đầy đủ |
| REQ-RUN-006 | SQLite thật, snapshot bất biến, CAS/transaction, successor duy nhất, history_reader hiện hành; test mở lại, trigger, hai tiến trình ghi cùng version và lịch sử đổi sau kiểm | Phối hợp công bố ngoài kho với provider/host, giao diện vận hành và xác thực quyền |
| REQ-RUN-007 | Xuất JSON/Markdown từ kho, nhập PROPOSED, giữ báo cáo gốc và quyết định host riêng; test tampering/stale, fake approval, thiếu capability, nguồn đổi và không sửa finalized | Phiên phản biện thực, kênh xác thực/phê duyệt, sử dụng trên Work/Connector |

| Bộ kiểm D | Chạy/đạt | Error/failure/skip |
|---|---:|---:|
| Baseline main 361ccf2, WSL đủ 13 nguồn ghim | 241/241 | 0/0/0 |
| Riêng D, Windows/Python 3.14 và WSL/Python 3.12.3 | 69/69 mỗi môi trường | 0/0/0 |
| Riêng A, Windows và WSL | 44/44 mỗi môi trường | 0/0/0 |
| Riêng B, Windows và WSL | 82/82 mỗi môi trường | 0/0/0 |
| Riêng C, Windows và WSL | 70/70 mỗi môi trường | 0/0/0 |
| Toàn suite với D, WSL cùng 13 nguồn ghim | 310/310 | 0/0/0 |

Các DB test nằm trong thư mục tạm, connection được đóng trước cleanup trên
Windows. Hai tiến trình Python thật cùng barrier/version ghi một thắng/một
ConflictError; snapshot không mất dữ liệu. Fixture xuyên suốt giữ C phản chứng,
B claim cũ/mới, D finalized và run thay thế, rồi xuất hồ sơ; không tuyên bố
fixture là nghiên cứu Phật học. Lõi JSON chạy trong tiến trình chặn SQLite/
shell; adapter lưu trữ cần SQLite chuẩn. WSL dùng checkout riêng tại nền C và
chính 13 checkout nguồn bất biến đã có, kiểm SHA/diff trước/sau. Không tải
corpus/package và không sửa test A/B/C/legacy để đạt.

Đây là **mã lõi D có kho lưu trữ thật và fixture, chờ nghiệm thu tích hợp**,
không chuyển toàn bộ D/2.0 sang HIỆN HÀNH. E còn adapter corpus thực, luồng
Quick/Research, phối hợp công bố/xác thực, 11 ca nghiên cứu chuẩn, Work/
Connector và phép đo E1–E3 (**CHƯA ĐO**). Không xây dịch vụ AI phản biện, web,
API, kho vector hoặc hạ tầng phân tán.

---

## 2. Ma trận nghiệm thu 31 yêu cầu

| Yêu cầu | Trạng thái hiện tại | Bằng chứng tối thiểu cần có |
|---|---|---|
| REQ-VER-001 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động: con trỏ/kết quả chưa mở không tạo được Bản ghi bằng chứng; siêu dữ liệu quan hệ chỉ được dùng đúng loại luận điểm |
| REQ-VER-002 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động + cấu trúc: thiếu nguồn gốc bắt buộc bị từ chối; trường không áp dụng được phép để trống, không tạo dữ liệu giả |
| REQ-VER-003 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động: sai kho nguồn/SHA/đường dẫn/đoạn làm Cửa kiểm bằng chứng thất bại |
| REQ-VER-004 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: kết luận phức hợp phải được tách thành các luận điểm có thể kiểm độc lập |
| REQ-VER-005 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Tự động: luận điểm thiếu bằng chứng hỗ trợ không thể được chấp nhận |
| REQ-VER-006 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Cấu trúc + tự động: chỉ chấp nhận các mức DIRECT/STRONG/WEAK/UNSUPPORTED/CONTRADICTED đã định nghĩa |
| REQ-VER-007 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Tự động + nghiên cứu chuẩn: UNSUPPORTED không qua Cửa kiểm luận điểm cuối |
| REQ-VER-008 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Tự động + nghiên cứu chuẩn: CONTRADICTED không được xuất như kết luận đã xác lập |
| REQ-VER-009 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Tự động: thay đổi điểm truy xuất không tự thay đổi mức hỗ trợ của luận điểm |
| REQ-VER-010 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: phần tổng hợp sinh luận điểm mới ngoài tập đã chấp nhận phải thất bại kiểm tra cuối |
| REQ-VER-011 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Tự động + nghiên cứu chuẩn: thiếu loại luận điểm bị từ chối; dùng sai loại bằng chứng không được nâng mức hỗ trợ |
| REQ-VER-012 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Tự động: AI hoặc chương trình gọi không thể tự ghi trạng thái `accepted`; chỉ Cửa kiểm luận điểm cuối được cấp trạng thái này |
| REQ-VER-013 | ĐÃ CÓ LÕI B; CHỜ NGHIỆM THU | Tự động: sửa luận điểm tạo lịch sử thay thế, giữ bản cũ, lý do sửa và phản chứng liên quan |
| REQ-VER-014 | MỘT PHẦN: LÕI A/B | Tự động + nghiên cứu chuẩn: thông tin chưa đủ căn cứ phải giữ trạng thái chưa xác định/chưa kiểm/không chắc; không tự suy đoán thành giá trị xác định |
| REQ-QTE-001 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động: phân loại đúng các trạng thái khớp nguyên văn, khớp sau chuẩn hóa, diễn đạt lại, chưa kiểm và không khớp |
| REQ-QTE-002 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: câu trích sai một từ không được xuất như nguyên văn |
| REQ-QTE-003 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: diễn đạt lại không được trình bày như câu trích trực tiếp |
| REQ-CTR-001 | ĐÃ CÓ LÕI C; CHỜ NGHIỆM THU | Tích hợp: chế độ Nghiên cứu thiếu bước tìm phản chứng phải không đạt |
| REQ-CTR-002 | ĐÃ CÓ LÕI C; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: “không tìm thấy phản chứng” phải kèm corpus/truy vấn/phạm vi đã kiểm |
| REQ-CTR-003 | ĐÃ CÓ LÕI C; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: nguồn phụ thuộc không được tính như xác nhận độc lập; chưa rõ phải giữ uncertain |
| REQ-CTR-004 | ĐÃ CÓ LÕI C; CHỜ NGHIỆM THU | Tích hợp: phản chứng có thể làm luận điểm bị thu hẹp/hạ mức/loại/thay thế |
| REQ-RUN-001 | ĐÃ CÓ LÕI D; CHỜ NGHIỆM THU | Tự động: chế độ Nghiên cứu thiếu commit kho chính, kho/commit/thư mục gốc của locator, phiên bản nguồn hoặc trường bắt buộc phải không đạt |
| REQ-RUN-002 | ĐÃ CÓ LÕI D; CHỜ NGHIỆM THU | Cấu trúc: dữ liệu tách được tái lập truy xuất và tái lập nghiên cứu; không yêu cầu lưu chuỗi suy nghĩ nội bộ |
| REQ-RUN-003 | ĐÃ CÓ LÕI D; CHỜ NGHIỆM THU | Tự động + nghiên cứu chuẩn: hồ sơ phải có phạm vi đã kiểm/chưa kiểm và câu trả lời không được mở rộng quá phạm vi |
| REQ-RUN-004 | ĐÃ CÓ LÕI D; CHỜ NGHIỆM THU | Tự động: từ mã luận điểm truy ra được toàn bộ mã bằng chứng liên quan |
| REQ-RUN-005 | ĐÃ CÓ LÕI D; CHỜ NGHIỆM THU | Tự động: trạng thái tìm phản chứng và tóm tắt kết quả có thể truy vấn |
| REQ-RUN-006 | ĐÃ CÓ LÕI D; CHỜ NGHIỆM THU | Tự động: hồ sơ đã chốt (`finalized`) không được sửa đè; thay đổi phải tạo bản mới có quan hệ thay thế và lý do |
| REQ-TST-001 | CHƯA TRIỂN KHAI | Tự động: 11 mẫu nghiên cứu chuẩn nằm trong repo/nguồn ghim và chạy được trên môi trường sạch, không phụ thuộc đường dẫn cá nhân |
| REQ-TST-002 | CHƯA TRIỂN KHAI | Quy trình + tự động: mỗi sự cố nghiên cứu nghiêm trọng đã sửa có bài kiểm thử hồi quy tương ứng |
| REQ-ENV-001 | MỘT PHẦN: LÕI A/B; CHƯA THỬ WORK | Tự động + tích hợp: lõi kiểm chứng nhận/trả dữ liệu JSON tương đương trên Codex và ChatGPT Work; không yêu cầu SQLite, shell hay đường dẫn tuyệt đối để hiểu đúng trạng thái |
| REQ-ENV-002 | MỘT PHẦN: LÕI A/B GIẢ LẬP; CHƯA THỬ PLUGIN | Tích hợp + rà soát: cùng một mẫu bằng chứng từ GitHub có thể đi qua đường plugin khi đủ dữ liệu; thiếu phép kiểm bắt buộc phải trả chưa xác minh và đóng khi thiếu dữ liệu |

---

### 2.1. Yêu cầu bổ sung cho D/E

Làm rõ ngày 11/10/2026: kế hoạch vẫn có năm giai đoạn A–E. A/B đã được
nghiệm thu **phần mã lõi** và gộp vào main tại
`494f8584dbc7fb104466c7e0b656e2370dd6b027`; các báo cáo và số liệu phía trên
giữ nguyên theo thời điểm ghi nhận. Điều này không nghiệm thu toàn bộ 2.0,
không tự nâng trạng thái 31 yêu cầu gốc trong ma trận. Hai yêu cầu dưới đây
là phần bổ sung, **CHƯA TRIỂN KHAI**, không thay hoặc làm yếu yêu cầu cũ.
Nghiệm thu toàn bộ ở mục 6 còn phải đáp ứng hai yêu cầu bổ sung này.

| Yêu cầu | Trạng thái hiện tại | Bằng chứng nghiệm thu cần có |
|---|---|---|
| REQ-RUN-007 | ĐÃ CÓ LÕI D; CHỜ TÍCH HỢP E | Tích hợp + rà soát: xuất/nhập thủ công đủ snapshot và căn cứ; lưu báo cáo khác quyết định phê duyệt; báo cáo chưa phê duyệt/sai snapshot không cấp quyền; đánh giá đã phê duyệt dùng capability host và cửa kiểm hiện có |
| REQ-TST-003 | CHƯA ĐO; MỤC TIÊU E | Báo cáo E1–E3 có baseline so sánh được, kết quả thô, chi phí và lỗi bỏ lọt/chặn nhầm; phần thẩm định độc lập có phép đo giá trị tăng thêm khi sử dụng |

Nghiệm thu REQ-RUN-007 phải đi hết một vòng xuất → phản biện → nhập → quyết
định theo chính sách → kiểm qua gate. Gói chuyển đi phải giữ luận điểm, bằng
chứng, nguồn/ngữ cảnh, giới hạn, phiên bản và phạm vi; có nhận xét có căn cứ
và đề nghị sửa/loại, không chỉ một nhãn đồng ý. Ghi bên đề xuất, bên phản
biện và căn cứ phân biệt quá trình thẩm định; không lấy khác tên mô hình làm
chứng minh độc lập nguồn tư liệu hoặc độ đúng.

Cần có trường hợp thuận: snapshot còn hiện hành, đánh giá được host phê duyệt
và đủ điều kiện của mode đi qua các gate áp dụng. Trường hợp đối nghịch gồm
báo cáo chưa phê duyệt nhưng tự khai accepted/trusted, thiếu căn cứ nguồn,
sai/đổi snapshot, dùng approval C1 cho C2 hoặc tái công bố C1 đã bị thay thế.
Chúng không được cấp quyền công bố; giữ candidate/UNVERIFIED khi thiếu khả
năng kiểm, rejected/superseded theo kết quả gate hiện có. Việc nhập không
được chọn capability, bỏ `history_reader` hoặc sửa đè lịch sử. Thủ công vẫn
phải có dấu vết quyết định; không cần xây API hay hệ hai AI tự động.

### 2.2. Đo hiệu quả E1–E3 ở Giai đoạn E

E1–E3 là nhóm nghiệm thu trong E, không phải giai đoạn mới. Cả ba hiện
**CHƯA ĐO**. Bộ test A/B xanh chỉ chứng minh hành vi trong phạm vi đã chạy,
không chứng minh hiệu năng hay giá trị của hệ 2.0 tích hợp.

| Nhóm | Đối chiếu và phép đo | Kết quả phải ghi |
|---|---|---|
| E1 — Bảo toàn 1.0 | Cùng bộ truy vấn trên commit nền 1.0 và 2.0 tích hợp; cùng 13 nguồn ghim, cấu hình index/ranking/locator và điều kiện máy/cache. Chạy các lệnh search, context, work, parallels, resolve, variants, compare, provenance, evidence | Định danh/nội dung kết quả và thứ tự xếp hạng, chênh lệch ngoài chủ đích, thời gian phản hồi, CPU/bộ nhớ/I/O khi đo được; dấu vết cho thấy lệnh cũ không gọi nghiên cứu sâu |
| E2 — Nhanh | Câu hỏi tra từ, tìm đoạn, xem nguồn, đọc ngữ cảnh và kiểm câu trích; đối chiếu cùng tác vụ với đường truy xuất nền và đường Nhanh có các phép kiểm áp dụng | Thời gian tổng và tăng thêm, thời gian từng bước đọc nguồn/kiểm chứng, số lần đọc và lượt xử lý AI, tài nguyên; truy nguyên bước gây chậm, không quét corpus hay gọi quy trình sâu ngoài nhu cầu |
| E3 — Nghiên cứu | Cùng câu hỏi, phạm vi và nguồn trên đường nền, 2.0 Nghiên cứu, và cùng hồ sơ trước/sau thẩm định độc lập nếu dùng | Thời gian, số lần đọc nguồn, lượt xử lý/token và chi phí khi có dữ liệu thực; lỗi bỏ lọt, kết luận có căn cứ bị chặn nhầm; thẩm định phát hiện thêm bao nhiêu lỗi thật và đưa ra bao nhiêu phản biện sai |

Mỗi báo cáo ghi commit nền/tích hợp, nguồn/cấu hình/môi trường, bộ truy vấn,
điều kiện cache, số lần chạy và kết quả thô. Tách chi phí xây index/chuẩn bị
khỏi thời gian trả lời; báo cáo phân bố thời gian thay vì chọn một lượt nhanh
nhất. So sánh trên cùng phạm vi; khác dữ liệu hay điều kiện phải được ghi rõ,
không gộp thành kết luận hiệu quả. E2 không được bỏ phép kiểm nguồn, approval
hay lịch sử áp dụng để đạt thời gian đẹp; việc kiểm tất định dùng chương trình.

E3 dùng mẫu có kết quả mong đợi được rà soát độc lập với AI bị đánh giá, gồm
cả lỗi cố ý và luận điểm hợp lệ. Giữ 11 tình huống chuẩn ở mục 3, thêm đối
chứng hợp lệ để phát hiện chặn nhầm. Ghi số lỗi bỏ lọt trên tổng lỗi đã biết
và số luận điểm hợp lệ bị chặn trên tổng luận điểm hợp lệ. Với phản biện,
ghi lỗi thật phát hiện thêm và phản biện sai trên tổng nhận xét kiểm được;
phần còn tranh luận hoặc chưa kiểm phải tách riêng, không tính thành đúng.
Một AI thứ hai đồng ý không được dùng làm đáp án chuẩn cho chính nó.

Người bảo trì phải chốt mức chấp nhận hiệu năng/chi phí từ baseline trước
nghiệm thu E, ghi lý do và điều kiện đo; tài liệu này không tự tạo ngưỡng số.
Khi có suy giảm, phải chỉ ra bước gây ra và quyết định xử lý, không chỉ ghi
test đạt. Không có số liệu thời gian/tài nguyên/token/chi phí thì ghi
**CHƯA ĐO** cho phần đó và giới hạn; không được tuyên bố nhóm đo đã đạt khi
còn thiếu phép đo bắt buộc hoặc mức chấp nhận chưa được chốt.

---

## 3. Bộ kiểm thử nghiên cứu chuẩn

Mỗi tình huống chuẩn phải có tối thiểu:

- câu hỏi;
- phạm vi được phép;
- bằng chứng mong đợi;
- nguồn không được dùng như bằng chứng chính;
- phản chứng đã biết;
- luận điểm bị cấm;
- mẫu luận điểm được chấp nhận/bị loại;
- giới hạn bắt buộc phải xuất.

Bộ tối thiểu gồm 11 trường hợp:

1. **Câu trích đổi một từ** — phải phát hiện không khớp.
2. **Sai SHA nguồn** — Bản ghi bằng chứng phải bị từ chối.
3. **Sai đoạn nguồn** — vị trí không hợp lệ phải làm cửa kiểm thất bại.
4. **Chú thích giả làm văn bản gốc** — phải chặn sai vai trò văn bản.
5. **Siêu dữ liệu song hành giả làm bằng chứng câu chữ** — phải chặn.
6. **Hai nguồn phụ thuộc giả làm hai nhân chứng độc lập** — phải nhận ra quan hệ phụ thuộc.
7. **Luận điểm mạnh hơn bằng chứng** — phải thu hẹp, hạ mức hoặc loại.
8. **Sai loại bằng chứng** — luận điểm lịch sử/thực nghiệm/siêu hình không được xác nhận chỉ vì văn bản nói như vậy.
9. **Bỏ tìm phản chứng** — chế độ Nghiên cứu phải không đạt.
10. **Tự tạo tương đương Pāli ↔ Hán** — không có bằng chứng trong kho nguồn thì không được xác lập.
11. **Phần tổng hợp sinh luận điểm mới** — luận điểm chưa qua cửa kiểm phải bị phát hiện.

Các mẫu phải nhỏ, ổn định và có thể chạy trên mọi máy. Không dùng một đường dẫn
cá nhân làm điều kiện để bài kiểm thử quan trọng được chạy.

---

## 4. Kiểm thử hồi quy từ sự cố thật

Một **sự cố toàn vẹn nghiên cứu** là trường hợp hệ thống từng cho một kết luận,
câu trích, quan hệ nguồn hoặc trạng thái nghiên cứu sai lọt qua các cửa kiểm.

Khi sửa một sự cố như vậy:

```text
sự cố thật
→ xác định nguyên nhân
→ sửa mã/quy tắc
→ thêm kiểm thử hồi quy
→ giữ kiểm thử lâu dài
```

Không cần tạo thủ tục hành chính nặng. Mục tiêu duy nhất là biến lỗi đã biết
thành thứ hệ thống không được phép lặp lại.

---

## 5. Điều kiện chuyển một yêu cầu 2.0 sang HIỆN HÀNH

Một yêu cầu chỉ được chuyển trạng thái khi:

1. có triển khai thực;
2. hợp đồng dữ liệu/định dạng liên quan đã được chốt nếu cần;
3. có bài kiểm thử phù hợp;
4. có tình huống nghiên cứu chuẩn nếu yêu cầu liên quan hành vi nghiên cứu;
5. không làm hồi quy truy xuất/Connector hiện hành;
6. `docs/v2/REQUIREMENTS.md` và file này được cập nhật;
7. tài liệu cấp toàn dự án được cập nhật nếu trạng thái thực tế thay đổi.

Không chuyển trạng thái vì có mã khung, bản mô phỏng hoặc tài liệu.

## 6. Điều kiện nghiệm thu toàn bộ 2.0 phiên bản đầu

Chỉ coi 2.0 phiên bản đầu hoàn thành khi tối thiểu:

- 31 yêu cầu trong tài liệu này đã có bằng chứng nghiệm thu phù hợp;
- truy xuất và CLI hiện hành không hồi quy;
- locator chính thức vẫn tất định;
- Connector vẫn mở nguồn gốc bên ngoài đã ghim;
- con trỏ vẫn không phải bằng chứng;
- Bản ghi bằng chứng truy nguyên được;
- câu trích sai bị phát hiện;
- luận điểm không bằng chứng bị chặn;
- trạng thái `accepted` chỉ do cửa kiểm cấp;
- lịch sử sửa luận điểm được giữ;
- `UNSUPPORTED`/`CONTRADICTED` không lọt vào kết luận như sự thật;
- chế độ Nghiên cứu thực hiện tìm phản chứng;
- độc lập/phụ thuộc nguồn được biểu diễn;
- Hồ sơ lần nghiên cứu truy nguyên được;
- hồ sơ đã chốt không bị sửa đè;
- biết phạm vi đã kiểm/chưa kiểm;
- 11 tình huống nghiên cứu chuẩn chạy ổn định;
- sự cố nghiên cứu đã sửa có kiểm thử hồi quy;
- lõi kiểm chứng dùng cùng hợp đồng dữ liệu trên Codex và ChatGPT Work;
- đường GitHub plugin không bị thiết kế chặn và đóng khi thiếu khả năng xác minh;
- khi thiếu dữ liệu, hệ thống vẫn đóng và nêu giới hạn.

Đây là tiêu chí **MỤC TIÊU**, không phải tuyên bố trạng thái hiện tại.
