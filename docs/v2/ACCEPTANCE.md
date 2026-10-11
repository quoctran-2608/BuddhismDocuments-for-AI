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
| REQ-CTR-001 | CHƯA TRIỂN KHAI | Tích hợp: chế độ Nghiên cứu thiếu bước tìm phản chứng phải không đạt |
| REQ-CTR-002 | CHƯA TRIỂN KHAI | Nghiên cứu chuẩn: “không tìm thấy phản chứng” phải kèm corpus/truy vấn/phạm vi đã kiểm |
| REQ-CTR-003 | CHƯA TRIỂN KHAI | Nghiên cứu chuẩn: nguồn phụ thuộc không được tính như xác nhận độc lập; chưa rõ phải giữ uncertain |
| REQ-CTR-004 | CHƯA TRIỂN KHAI | Tích hợp: phản chứng có thể làm luận điểm bị thu hẹp/hạ mức/loại/thay thế |
| REQ-RUN-001 | CHƯA TRIỂN KHAI | Tự động: chế độ Nghiên cứu thiếu commit kho chính, kho/commit/thư mục gốc của locator, phiên bản nguồn hoặc trường bắt buộc phải không đạt |
| REQ-RUN-002 | CHƯA TRIỂN KHAI | Cấu trúc: dữ liệu tách được tái lập truy xuất và tái lập nghiên cứu; không yêu cầu lưu chuỗi suy nghĩ nội bộ |
| REQ-RUN-003 | CHƯA TRIỂN KHAI | Tự động + nghiên cứu chuẩn: hồ sơ phải có phạm vi đã kiểm/chưa kiểm và câu trả lời không được mở rộng quá phạm vi |
| REQ-RUN-004 | CHƯA TRIỂN KHAI | Tự động: từ mã luận điểm truy ra được toàn bộ mã bằng chứng liên quan |
| REQ-RUN-005 | CHƯA TRIỂN KHAI | Tự động: trạng thái tìm phản chứng và tóm tắt kết quả có thể truy vấn |
| REQ-RUN-006 | CHƯA TRIỂN KHAI | Tự động: hồ sơ đã chốt (`finalized`) không được sửa đè; thay đổi phải tạo bản mới có quan hệ thay thế và lý do |
| REQ-TST-001 | CHƯA TRIỂN KHAI | Tự động: 11 mẫu nghiên cứu chuẩn nằm trong repo/nguồn ghim và chạy được trên môi trường sạch, không phụ thuộc đường dẫn cá nhân |
| REQ-TST-002 | CHƯA TRIỂN KHAI | Quy trình + tự động: mỗi sự cố nghiên cứu nghiêm trọng đã sửa có bài kiểm thử hồi quy tương ứng |
| REQ-ENV-001 | MỘT PHẦN: LÕI A/B; CHƯA THỬ WORK | Tự động + tích hợp: lõi kiểm chứng nhận/trả dữ liệu JSON tương đương trên Codex và ChatGPT Work; không yêu cầu SQLite, shell hay đường dẫn tuyệt đối để hiểu đúng trạng thái |
| REQ-ENV-002 | MỘT PHẦN: LÕI A/B GIẢ LẬP; CHƯA THỬ PLUGIN | Tích hợp + rà soát: cùng một mẫu bằng chứng từ GitHub có thể đi qua đường plugin khi đủ dữ liệu; thiếu phép kiểm bắt buộc phải trả chưa xác minh và đóng khi thiếu dữ liệu |

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
