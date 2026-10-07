# Buddhist Corpus Research 2.0 — Thiết kế hệ thống nghiên cứu có kiểm chứng

> Trạng thái tài liệu: **MỤC TIÊU**
>
> Vai trò: mô tả **cách Buddhist Corpus Research 2.0 phải hoạt động** để kiểm
> chứng bằng chứng, luận điểm, phản chứng và hồ sơ nghiên cứu.
>
> Đây **không phải mô tả tính năng đã triển khai đầy đủ**. Kiến trúc hiện hành
> nằm trong `docs/ARCHITECTURE.md`. Đề bài sản phẩm của 2.0 nằm trong
> `docs/v2/PRD.md`.
>
> Tài liệu ưu tiên tiếng Việt. Tên trường dữ liệu, mã trạng thái và một số tên
> kỹ thuật được giữ bằng tiếng Anh trong dấu mã để đối chiếu chính xác với mã
> nguồn.

## 1. Ba trạng thái phát triển phải được giữ riêng

### HIỆN HÀNH

Hệ thống hiện đã có:

```text
13 nguồn gốc bên ngoài được ghim theo commit
→ bộ phân tích tất định
→ SQLite / FTS / quan hệ / dị bản / lemma
→ truy xuất cục bộ hoặc locator chính thức
→ mở nguồn gốc bên ngoài đã ghim
→ ngữ cảnh + nguồn gốc
→ câu trả lời theo AGENTS/SKILL
```

### MỤC TIÊU

Buddhist Corpus Research 2.0 bổ sung:

```text
Bản ghi bằng chứng
→ kiểm chứng câu trích
→ luận điểm nguyên tử
→ kiểm chứng luận điểm ↔ bằng chứng
→ phân tích độc lập nguồn
→ tìm phản chứng
→ sửa / hạ mức / loại luận điểm
→ cửa kiểm luận điểm cuối
→ tập luận điểm được chấp nhận
→ tổng hợp
→ kiểm tra cuối
→ hồ sơ lần nghiên cứu
```

### TƯƠNG LAI

Chỉ xem xét sau khi 2.0 ổn định và có nhu cầu thực tế được đo:

- đường truy xuất Connector sâu hơn khi locator hữu hạn không đủ;
- hỗ trợ tìm Hán văn từ xa tùy ý bằng một cơ chế khác với bản chính thức `terms/cjk`;
- tác vụ từ xa tất định để chạy truy xuất nặng rồi trả kết quả có nguồn gốc.

Các ý này **không phải yêu cầu 2.0 phiên bản đầu**.

## 2. Khoảng trống cần giải quyết

Hệ hiện hành đã làm tốt câu hỏi:

> “AI đang đọc đúng nguồn nào?”

Khoảng trống còn lại là:

> “Sau khi đọc đúng nguồn, AI có đang rút ra đúng mức kết luận mà nguồn cho phép
> hay không?”

Một nguồn hoàn toàn thật vẫn có thể bị dùng sai:

- câu trích bị sửa một từ nhưng vẫn trình bày như nguyên văn;
- diễn đạt lại bị đặt trong ngoặc kép;
- chú thích hoặc bản dịch bị trình bày như văn bản gốc;
- quan hệ song hành bị dùng như bằng chứng câu chữ;
- nhiều nguồn dẫn xuất từ cùng một nguồn bị tính như nhiều xác nhận độc lập;
- luận điểm lịch sử, thực nghiệm hoặc siêu hình bị nâng lên từ sai loại bằng chứng;
- phản chứng bị bỏ qua;
- phần tổng hợp tự sinh thêm một kết luận chưa qua kiểm.

Vì vậy phải giữ nguyên tắc:

```text
có bằng chứng thật
≠
luận điểm tự động đúng
```

## 3. Thuật ngữ cốt lõi

- **Con trỏ** (`pointer`): chỉ nơi cần mở; không phải bằng chứng.
- **Bản ghi bằng chứng** (`Evidence Record`): biểu diễn có cấu trúc của nguồn
  đã thực sự được mở và đọc.
- **Luận điểm** (`claim`): điều hệ thống muốn khẳng định.
- **Luận điểm nguyên tử** (`Atomic Claim`): luận điểm đủ nhỏ để kiểm độc lập.
- **Phản chứng** (`counterevidence`): bằng chứng hoặc dữ liệu có thể làm yếu,
  thu hẹp hoặc bác bỏ luận điểm.
- **Cửa kiểm luận điểm cuối** (`Final Claim Gate`): bước quyết định luận điểm
  nào được phép đi vào phần tổng hợp.
- **Hồ sơ lần nghiên cứu** (`Research Run`): dấu vết có cấu trúc của một lần
  nghiên cứu.
- **Đóng khi thiếu dữ liệu** (`fail-closed`): thiếu bằng chứng thì dừng và nói
  rõ giới hạn, không tự điền bằng suy đoán.

Các thuật ngữ kỹ thuật kế thừa từ hệ 1.0:

- **corpus**: kho ngữ liệu có cấu trúc;
- **repository**: kho mã hoặc dữ liệu được quản lý bằng Git; trong văn xuôi gọi là **kho Git**;
- **upstream source**: nguồn gốc bên ngoài mà dự án ghim theo một phiên bản
  cụ thể;
- **SHA**: mã băm dùng để định danh và kiểm tra đúng phiên bản;
- **locator**: chỉ dẫn giúp tìm đúng tệp hoặc đoạn cần mở;
- **metadata**: siêu dữ liệu mô tả văn bản, quan hệ hoặc nguồn;
- **witness**: nhân chứng văn bản, tức một bản/ấn bản/truyền bản cụ thể;
- **FTS** (Full-Text Search): chỉ mục tìm kiếm toàn văn;
- **production**: bản đang được dùng chính thức, phân biệt với bản thử hoặc bản
  đang xây;
- **work / segment**: tác phẩm / đoạn định danh trong nguồn;
- **provenance**: nguồn gốc truy nguyên, tức thông tin đủ để lần ngược về
  kho Git, phiên bản và vị trí nguồn.

## 4. Nguyên tắc thiết kế

### 4.1. Bổ sung, không thay thế

Lớp kiểm chứng nằm **sau** hệ truy xuất và mở nguồn hiện hành.

Không:

- viết lại SQLite/FTS chỉ vì thêm kiểm chứng;
- thay locator chính thức;
- đưa cơ sở dữ liệu véc-tơ vào khi chưa có nhu cầu;
- biến GitHub Actions thành “bộ não suy luận”;
- tạo một điểm số duy nhất giả làm thước đo chân lý học thuật.

### 4.2. Giữ bốn tầng dữ liệu riêng

```text
Con trỏ
→ chỉ nơi cần đọc

Bằng chứng
→ điều đã thực sự mở và đọc

Luận điểm
→ điều muốn khẳng định

Tổng hợp
→ cách trình bày các luận điểm đã được kiểm
```

Không gộp bốn tầng này thành một đối tượng chung.

### 4.3. Tính toàn vẹn dữ liệu không thay thế kiểm chứng học thuật

Phải tách rõ:

```text
kiểm tra dữ liệu
≠
cửa kiểm bằng chứng
≠
kiểm chứng luận điểm
≠
cửa kiểm luận điểm cuối
```

Mã băm đúng, đường dẫn đúng và bản ghi đúng chỉ chứng minh ta đang đọc đúng dữ
liệu. Chúng không tự chứng minh luận điểm học thuật đúng.

### 4.4. Điểm truy xuất không phải mức hỗ trợ luận điểm

Điểm truy xuất trả lời:

> “Ứng viên nào nên mở trước?”

Kiểm chứng luận điểm trả lời:

> “Bằng chứng đã mở hỗ trợ luận điểm này đến mức nào?”

Không ánh xạ trực tiếp điểm truy xuất sang `DIRECT`, `STRONG` hay `WEAK`.

### 4.5. Việc máy kiểm được thì ưu tiên kiểm bằng máy

Ưu tiên quy tắc tất định cho:

- nguồn, đường dẫn và SHA có hợp lệ không;
- vị trí có tồn tại không;
- câu trích có khớp không;
- nguồn gốc có đủ không;
- luận điểm có bằng chứng không;
- trạng thái bị cấm có lọt qua cửa kiểm hay không;
- hồ sơ lần nghiên cứu có đủ trường bắt buộc hay không.

AI chỉ làm phần thật sự cần suy luận ngôn ngữ:

- tạo giả thuyết tìm kiếm;
- tách luận điểm;
- đánh giá quan hệ ngữ nghĩa giữa luận điểm và bằng chứng khi quy tắc máy không
  đủ;
- đề xuất hướng tìm phản chứng;
- tổng hợp câu trả lời.

### 4.6. “Chưa xác định” là một kết quả hợp lệ

Không có căn cứ thì dùng trạng thái như:

- chưa xác định;
- chưa kiểm;
- không chắc.

Không tự điền để dữ liệu trông đầy đủ.

Nguyên tắc này đặc biệt áp dụng cho độc lập nguồn, quan hệ nhân chứng, tác giả,
niên đại, người dịch và tương đương đa ngôn ngữ.

### 4.7. Một lõi kiểm chứng, nhiều môi trường thực thi

Lõi kiểm chứng phải tách khỏi cách lấy dữ liệu.

Nó nhận các đối tượng/dữ liệu máy đọc đã chuẩn hóa và trả kết quả máy đọc, thay
vì tự giả định luôn có:

- SQLite cục bộ;
- lệnh shell;
- một đường dẫn máy cụ thể;
- một phiên ChatGPT cụ thể;
- một công cụ GitHub cụ thể.

Kiến trúc mục tiêu:

```text
                 ┌─ Codex / working copy cục bộ
nguồn dữ liệu ───┼─ ChatGPT Work
                 └─ ChatGPT + GitHub plugin
                         ↓
                hợp đồng dữ liệu chung
                         ↓
                 lõi kiểm chứng 2.0
                         ↓
              trạng thái / kết quả JSON
```

#### Codex

Codex là đường triển khai đầy đủ nhất:

- đọc/sửa repository;
- chạy Python và kiểm thử;
- dùng Git cục bộ để kiểm SHA/tệp khi working copy đầy đủ.

#### ChatGPT Work

Work phải dùng được cùng hợp đồng dữ liệu.

Khi có thư mục dự án cục bộ, có thể dùng đường tương tự Codex. Khi làm việc trên
đám mây hoặc qua nguồn đã kết nối, Work có thể lấy dữ liệu qua plugin/trình
duyệt rồi đưa về cùng cấu trúc Bản ghi bằng chứng.

Không được tạo một loại Bản ghi bằng chứng riêng chỉ dành cho Work.

#### ChatGPT qua GitHub plugin

Đây là đường tương thích ưu tiên.

Nếu plugin đọc được:

- repository;
- commit;
- đường dẫn;
- nội dung tệp;
- và thông tin nguồn cần thiết;

thì quy trình phải có thể tạo cùng Bản ghi bằng chứng và áp dụng cùng các cửa
kiểm không phụ thuộc máy cục bộ.

Những phép kiểm chỉ có thể thực hiện bằng Git cục bộ phải được biểu diễn như một
khả năng của **bộ cung cấp nguồn** chứ không được viết cứng vào logic học thuật.

Nếu môi trường không cung cấp đủ dữ liệu để xác minh một phép kiểm:

```text
không đủ khả năng kiểm
→ UNVERIFIED / chưa xác minh
→ đóng khi thiếu dữ liệu
```

Không được suy từ “không chạy được phép kiểm” thành “phép kiểm đã đạt”.

#### Hợp đồng dữ liệu chung

Các cấu trúc 2.0 phải:

- chuyển được sang JSON mà không mất nghĩa;
- không chứa đối tượng kết nối SQLite hoặc handle tệp đang mở;
- không phụ thuộc đường dẫn tuyệt đối của một máy;
- dùng repository + commit/SHA + source path làm định danh nguồn;
- giữ tên trạng thái giống nhau giữa Codex, Work và GitHub plugin.

## 5. Luồng mục tiêu của 2.0

```text
câu hỏi
→ xác định phạm vi
→ giả thuyết tìm kiếm
→ truy xuất hiện hành
→ locator / FTS cục bộ
→ nguồn đã ghim
→ đọc ngữ cảnh
→ Bản ghi bằng chứng
→ kiểm chứng câu trích
→ Luận điểm nguyên tử
→ kiểm chứng luận điểm ↔ bằng chứng
→ phân tích độc lập nguồn
→ tìm phản chứng
→ sửa / hạ mức / loại
→ Cửa kiểm luận điểm cuối
→ tập luận điểm được chấp nhận
→ tổng hợp
→ kiểm tra cuối
→ Hồ sơ lần nghiên cứu
→ câu trả lời
```

Truy xuất phải thu hẹp corpus lớn thành một tập ứng viên nhỏ trước khi chạy lớp
kiểm chứng. Không chạy bộ kiểm chứng luận điểm trên hàng triệu bản ghi.

## 6. Hai cấp sử dụng

### 6.1. Chế độ Nhanh (`Quick`)

Dùng cho tra cứu hẹp:

- một thuật ngữ;
- một đoạn;
- một mã tác phẩm;
- một quan hệ/song hành cụ thể;
- kiểm một câu trích nhỏ.

Luồng tối thiểu:

```text
truy xuất
→ nguồn
→ ngữ cảnh
→ Bản ghi bằng chứng
→ kiểm câu trích / nguồn gốc khi cần
→ trả lời
```

Không bắt buộc chạy phản chứng đa nguồn cho câu hỏi hẹp, nhưng vẫn phải đóng khi
thiếu dữ liệu.

### 6.2. Chế độ Nghiên cứu (`Research`)

Dùng cho:

- câu hỏi khái niệm;
- so sánh nhiều truyền thống;
- lịch sử;
- tranh luận;
- nội dung phục vụ sách/bài nghiên cứu;
- luận điểm tổng quát;
- câu hỏi cần nhiều nhân chứng văn bản.

Bắt buộc có:

- Bản ghi bằng chứng;
- Luận điểm nguyên tử;
- kiểm chứng luận điểm;
- phân tích độc lập nguồn;
- tìm phản chứng;
- Cửa kiểm luận điểm cuối;
- Hồ sơ lần nghiên cứu.

## 7. Bản ghi bằng chứng (`Evidence Record`)

### 7.1. Ý nghĩa

Bản ghi bằng chứng chỉ được tạo sau khi nguồn thật đã được mở và nội dung liên
quan đã được đọc.

Các thứ sau **không tự động** trở thành bằng chứng:

- con trỏ;
- kết quả tìm kiếm chưa mở;
- tiêu đề/mục lục chưa được kiểm trong nguồn;
- dòng quan hệ;
- dòng cầu nối;
- ứng viên siêu dữ liệu dùng để khám phá.

Quan hệ, cầu nối hoặc siêu dữ liệu **có thể** trở thành bằng chứng cho luận điểm loại
`relationship` nếu nguồn siêu dữ liệu thực sự đã được mở, nguồn gốc được xác minh
và loại bằng chứng được ghi đúng. Chúng không được dùng như bằng chứng câu chữ
cho luận điểm `textual`.

### 7.2. Hợp đồng dữ liệu mục tiêu

Tên trường máy đọc:

```text
evidence_id
run_id
corpus
repository
source_sha
source_blob_sha
source_path
indexed_source_path
work_id
segment_id
sequence_no
language
evidence_class
text_role
witness
quotation
context
quote_verification_status
retrieval_query
match_reasons
relation_ids
limitations
```

Quy tắc:

- `evidence_id`, corpus, kho Git, SHA/đường dẫn và nguồn gốc cốt lõi phải đủ để
  truy ngược nguồn;
- `run_id` bắt buộc trong chế độ Nghiên cứu; chế độ Nhanh có thể để trống nếu
  chưa tạo Hồ sơ lần nghiên cứu;
- `source_blob_sha`, `indexed_source_path`, work/segment/sequence,
  `relation_ids` và `witness` có thể trống khi nguồn không cung cấp hoặc
  không áp dụng;
- `evidence_class` bắt buộc;
- `text_role` và `witness` phải giữ riêng khi áp dụng;
- `quotation` không bắt buộc với bằng chứng chỉ chứng minh siêu dữ liệu/quan hệ;
- nếu dùng trích dẫn nguyên văn hoặc diễn đạt lại, nội dung và ngữ cảnh phải đến
  từ nguồn đã mở;
- không lấy câu trích/ngữ cảnh từ con trỏ.

### 7.3. Cửa kiểm bằng chứng

Trước khi được dùng như bằng chứng đã xác minh:

1. kho Git phải đúng;
2. SHA nguồn/SHA tệp phải phù hợp;
3. đường dẫn nguồn phải tồn tại;
4. vị trí work/segment phải giải thích được khi áp dụng;
5. vai trò văn bản/nhân chứng phải đúng khi áp dụng;
6. trạng thái câu trích phải phù hợp nếu có trích dẫn hoặc diễn đạt lại.

Thất bại ở cửa này thì Bản ghi bằng chứng không được dùng làm bằng chứng đã xác
minh.

## 8. Kiểm chứng câu trích

`quote_verification_status` dùng các mã:

- `VERIFIED_EXACT` — khớp nguyên văn;
- `VERIFIED_NORMALIZED` — khớp sau chuẩn hóa không làm đổi nội dung;
- `PARAPHRASE` — diễn đạt lại có căn cứ, không phải nguyên văn;
- `UNVERIFIED` — chưa kiểm đủ;
- `QUOTE_MISMATCH` — không khớp nguồn.

`VERIFIED_NORMALIZED` chỉ được dùng cho chuẩn hóa bảo toàn nội dung như Unicode
hoặc khoảng trắng. Không dùng để che việc đổi, bỏ, thêm hay đảo từ.

`PARAPHRASE` không được đặt trong ngoặc kép như nguyên văn.

`UNVERIFIED` và `QUOTE_MISMATCH` không được xuất như câu trích đã xác minh.

## 9. Luận điểm nguyên tử (`Atomic Claim`)

### 9.1. Hợp đồng dữ liệu mục tiêu

```text
claim_id
run_id
text
claim_type
status
supporting_evidence_ids
counter_evidence_ids
verification_status
independence_status
limitations
supersedes_claim_id
revision_reason
```

### 9.2. Vòng đời luận điểm

`status` mô tả vòng đời, tối thiểu:

- `candidate` — đang được kiểm;
- `accepted` — đã qua Cửa kiểm luận điểm cuối;
- `rejected` — không được phép vào tập luận điểm được chấp nhận;
- `superseded` — đã được một luận điểm mới thay thế.

`verification_status` là mức bằng chứng hỗ trợ, không phải vòng đời.

### 9.3. Trạng thái cuối phải do cửa kiểm quyết định

Một luận điểm mới chỉ được tạo ở trạng thái `candidate`.

AI hoặc chương trình gọi **không được tự gán** `accepted` để bỏ qua kiểm chứng.

`accepted`, `rejected` hoặc `superseded` phải là kết quả của quy trình kiểm
và quan hệ sửa đổi.

### 9.4. Lịch sử sửa đổi luận điểm

Khi phản chứng làm một luận điểm phải đổi, không sửa đè câu cũ.

Tạo luận điểm mới và giữ:

- `supersedes_claim_id` — luận điểm cũ bị thay thế;
- `revision_reason` — lý do thay đổi;
- bằng chứng/ phản chứng dẫn tới thay đổi.

Luận điểm cũ phải còn truy được để biết lịch sử nghiên cứu.

Phản chứng đã làm luận điểm bị sửa **không được mất** khi tạo bản mới.

### 9.5. Loại luận điểm

`claim_type` tối thiểu:

- `textual` — văn bản nói gì;
- `historical` — mệnh đề về lịch sử;
- `relationship` — quan hệ/song hành/căn chỉnh;
- `comparative` — so sánh nhiều nhân chứng/truyền thống;
- `interpretive` — diễn giải;
- `empirical` — mệnh đề thực nghiệm;
- `metaphysical` — mệnh đề siêu hình.

Loại luận điểm quyết định loại bằng chứng nào có thể hỗ trợ nó. Một đoạn văn
không tự chứng minh một mệnh đề lịch sử, thực nghiệm hay siêu hình chỉ vì nội
dung văn bản khẳng định điều đó.

## 10. Kiểm chứng luận điểm ↔ bằng chứng

### 10.1. Mức hỗ trợ

`verification_status`:

- `DIRECT` — bằng chứng trực tiếp hỗ trợ đúng luận điểm;
- `STRONG` — hỗ trợ mạnh với suy luận hẹp;
- `WEAK` — có liên quan nhưng còn giới hạn đáng kể;
- `UNSUPPORTED` — chưa đủ bằng chứng;
- `CONTRADICTED` — có bằng chứng đáng kể chống lại luận điểm.

### 10.2. Quy tắc sử dụng

- `DIRECT`, `STRONG`: có thể vào tập luận điểm được chấp nhận nếu các cửa
  kiểm khác cũng đạt;
- `WEAK`: chỉ dùng khi câu trả lời giữ đúng mức bất định và giới hạn;
- `UNSUPPORTED`: không được vào tập được chấp nhận;
- `CONTRADICTED`: không được trình bày như kết luận đã xác lập ở dạng ban đầu.

Không được giữ nguyên một luận điểm `UNSUPPORTED` rồi chỉ thêm từ “có lẽ”.

## 11. Phân tích độc lập nguồn

Nhiều trích dẫn không tự động là nhiều nguồn độc lập.

`independence_status` tối thiểu:

- `independent`;
- `partially_dependent`;
- `same_source_family`;
- `derived_from`;
- `uncertain`.

Ví dụ, dữ liệu BuddhaNexus Chinese dẫn xuất từ CBETA không được tính như một
nhân chứng độc lập với chính CBETA chỉ vì nằm ở kho Git khác.

Nếu chưa xác định được quan hệ phụ thuộc, dùng `uncertain`, không tự nâng thành
`independent`.

## 12. Tìm phản chứng

### 12.1. Bắt buộc trong chế độ Nghiên cứu

Với mỗi luận điểm quan trọng, hệ thống phải chủ động tìm các nhóm phù hợp:

- nhân chứng khác;
- dị bản;
- ngoại lệ;
- song hành không khớp;
- nguồn cùng tầng nhưng xung đột;
- quan hệ phụ thuộc làm yếu “nhiều nguồn”;
- điều kiện giới hạn phạm vi.

### 12.2. Phản chứng phải có tác dụng

Kết quả có thể làm luận điểm:

- giữ nguyên;
- viết lại;
- thu hẹp phạm vi;
- hạ `DIRECT` → `STRONG`/`WEAK`;
- chuyển `UNSUPPORTED`;
- chuyển `CONTRADICTED`;
- bị loại;
- được thay bằng một luận điểm mới có lịch sử sửa đổi.

Phản chứng không được chỉ là một đoạn “ý kiến trái chiều” trang trí ở cuối.

### 12.3. Không tìm thấy không có nghĩa là không tồn tại

Chỉ được nói:

> “Không tìm thấy phản chứng trong phạm vi corpus và truy vấn đã kiểm.”

Không được suy thành:

> “Không tồn tại phản chứng.”

## 13. Cửa kiểm luận điểm cuối

Trước phần tổng hợp, hệ thống tạo **tập luận điểm được chấp nhận**.

Một luận điểm chỉ được `accepted` khi:

- có bằng chứng hỗ trợ;
- Bản ghi bằng chứng hợp lệ;
- trạng thái câu trích phù hợp cách trình bày;
- mức hỗ trợ không phải `UNSUPPORTED`/`CONTRADICTED`;
- chế độ Nghiên cứu đã xử lý phản chứng bắt buộc;
- quan hệ độc lập nguồn đã được xem xét khi cần;
- giới hạn quan trọng đã gắn vào luận điểm.

**Chỉ Cửa kiểm luận điểm cuối được phép cấp trạng thái `accepted`.**

Phần tổng hợp chỉ dùng tập luận điểm được chấp nhận và không được tự sinh thêm
luận điểm quan trọng chưa qua cửa kiểm.

## 14. Hồ sơ lần nghiên cứu (`Research Run`)

### 14.1. Mục đích

Hồ sơ lần nghiên cứu ghi lại đủ đường đi để có thể:

- biết phạm vi đã và chưa kiểm;
- biết phiên bản nguồn/locator;
- biết đã dùng bằng chứng nào;
- biết luận điểm nào được chấp nhận, loại hoặc thay thế;
- biết phản chứng nào đã tìm;
- rà soát lại nền bằng chứng.

Không lưu chuỗi suy nghĩ nội bộ của mô hình.

### 14.2. Hợp đồng dữ liệu mục tiêu

```text
run_id
run_status
question
created_at
finalized_at
mode
scope
main_repository
main_repository_commit
remote_repository
remote_repository_commit
remote_root
source_revisions
search_hypotheses
queries
evidence_ids
candidate_claim_ids
accepted_claim_ids
rejected_claim_ids
superseded_claim_ids
counterevidence_performed
counterevidence_summary
limitations
answer_artifact
model_identifier
verification_config
supersedes_run_id
revision_reason
```

`model_identifier` và `verification_config` có thể không bắt buộc trong 2.0
phiên bản đầu nếu môi trường không cung cấp ổn định. Nguồn gốc kho Git,
commit và phiên bản nguồn không được thiếu trong chế độ Nghiên cứu.

### 14.3. Vòng đời hồ sơ nghiên cứu

`run_status` tối thiểu:

- `draft` — đang thực hiện;
- `finalized` — đã chốt làm căn cứ cho câu trả lời;
- `superseded` — đã được một hồ sơ mới thay thế.

Hồ sơ `finalized` **không được sửa đè âm thầm**.

Nếu bằng chứng mới làm thay đổi kết quả, tạo hồ sơ mới và dùng
`supersedes_run_id` + `revision_reason` để nối lịch sử.

Không cần xây hệ quản lý phiên bản phức tạp ở 2.0 phiên bản đầu; chỉ cần bảo đảm
mô hình dữ liệu không làm mất dấu lịch sử.

### 14.4. Hai loại khả năng tái lập

- **Tái lập truy xuất**: cùng phiên bản corpus/locator/phạm vi/truy vấn phải lấy
  lại được nền bằng chứng chính tương tự.
- **Tái lập nghiên cứu**: biết nguồn nào đã mở, luận điểm nào được tạo, bằng
  chứng nào hỗ trợ/chống và luận điểm nào bị loại/thay thế.

Không đặt mục tiêu AI phải viết lại từng chữ giống hệt lần trước.

## 15. Kiểm tra cuối sau khi tổng hợp

Sau khi viết câu trả lời tự nhiên, hệ thống phải kiểm ít nhất:

- mọi kết luận quan trọng có luận điểm tương ứng;
- mọi luận điểm được dùng có bằng chứng;
- không có `UNSUPPORTED` lọt vào;
- không có `CONTRADICTED` được viết như sự thật;
- câu trích trực tiếp đã được kiểm;
- con trỏ/siêu dữ liệu không bị trích như văn bản;
- chú thích bản dịch không bị trình bày như văn bản gốc;
- quan hệ song hành không bị biến thành đồng nhất câu chữ;
- tương đương đa ngôn ngữ có bằng chứng trong kho nguồn;
- không trộn kiến thức mô hình vào kết luận;
- giới hạn phạm vi quan trọng không bị bỏ mất;
- phần tổng hợp không làm luận điểm mạnh hơn trạng thái đã được duyệt.

Thất bại thì không xuất câu trả lời như một kết luận đã xác lập.

## 16. Hợp đồng câu trả lời mục tiêu

Chế độ Nghiên cứu nên trình bày:

1. kết luận chính;
2. bằng chứng theo corpus/nhân chứng;
3. song hành và dị bản;
4. phản chứng hoặc dữ liệu làm yếu;
5. diễn giải;
6. mức chắc chắn và giới hạn;
7. nguồn gốc;
8. mã Hồ sơ lần nghiên cứu nếu có.

Không được viết “trong Phật giáo...” nếu phạm vi thực tế chỉ kiểm một phần nhỏ.

## 17. Tích hợp với hai chế độ thực thi hiện hành

### 17.1. Cục bộ

Không đổi bộ máy truy xuất:

```text
search / context / evidence
→ nguồn + nguồn gốc
→ tạo Bản ghi bằng chứng
→ kiểm chứng
→ lớp luận điểm
```

Tái sử dụng record ID, ngữ cảnh, nguồn gốc, dị bản, quan hệ, path/SHA, vai trò
văn bản và nhân chứng.

### 17.2. GitHub Connector

Không đổi locator chính thức:

```text
production pointer
→ mở nguồn gốc bên ngoài đã ghim
→ Bản ghi bằng chứng
→ kiểm chứng
→ lớp luận điểm
```

Không mở được nguồn thật thì luận điểm cần bằng chứng đó phải đóng khi thiếu dữ
liệu.

## 18. Lưu trữ kết quả kiểm chứng

2.0 cần định dạng máy đọc cho:

- Bản ghi bằng chứng;
- Luận điểm nguyên tử;
- Hồ sơ lần nghiên cứu.

Tài liệu này **không quyết định** dùng SQLite, JSON/JSONL hay thư mục tệp riêng.

Quyết định triển khai phải:

- không sửa nguồn gốc bên ngoài;
- dễ kiểm thử;
- giữ mã định danh ổn định;
- hỗ trợ lịch sử sửa đổi;
- không làm chậm đường Nhanh không cần thiết;
- không sửa đè hồ sơ đã chốt.

Nếu quyết định lưu trữ làm thay đổi kiến trúc đáng kể, phải có ADR riêng.

2.0 phiên bản đầu **không cần** một “sổ mâu thuẫn” riêng. Phản chứng có thể được
giữ dưới dạng bằng chứng liên kết với luận điểm. Chỉ tách thành cấu trúc riêng
khi có nhu cầu thực tế.

## 19. Bộ kiểm thử nghiên cứu chuẩn (`Golden Research Tests`)

Các kiểm thử hiện tại chủ yếu kiểm phần mềm. 2.0 phải bổ sung các tình huống
nghiên cứu cố ý sai.

Tối thiểu 11 trường hợp:

1. câu trích bị đổi một từ;
2. SHA nguồn sai;
3. segment sai;
4. chú thích bản dịch giả làm văn bản gốc;
5. siêu dữ liệu song hành giả làm bằng chứng câu chữ;
6. hai nguồn phụ thuộc giả làm hai nhân chứng độc lập;
7. luận điểm mạnh hơn bằng chứng;
8. luận điểm lịch sử/thực nghiệm/siêu hình bị kiểm bằng sai loại bằng chứng;
9. chế độ Nghiên cứu bỏ bước tìm phản chứng;
10. AI tự tạo tương đương Pāli ↔ Hán không có bằng chứng trong kho nguồn;
11. phần tổng hợp sinh kết luận mới chưa qua cửa kiểm.

Mỗi trường hợp chuẩn phải ghi:

- câu hỏi;
- phạm vi;
- bằng chứng mong đợi;
- nguồn không được dùng như bằng chứng chính;
- phản chứng đã biết;
- luận điểm bị cấm;
- mẫu luận điểm được chấp nhận/bị loại;
- giới hạn phải xuất.

Ưu tiên lấy **lỗi nghiên cứu thật từng xảy ra** làm tình huống kiểm thử hồi quy,
thay vì chỉ dùng ví dụ tưởng tượng.

> **Kiểm thử hồi quy** là bài kiểm tra được giữ lại để bảo đảm một lỗi đã sửa
> không quay trở lại.

Các mẫu chuẩn phải nằm trong kho dự án và chạy được trên mọi máy; không phụ
thuộc đường dẫn cá nhân.

## 20. Tiêu chí hoàn thành 2.0 phiên bản đầu

Chỉ coi lớp kiểm chứng hoàn thành khi:

- truy xuất hiện hành không bị hồi quy;
- locator chính thức vẫn tất định;
- con trỏ vẫn không phải bằng chứng;
- Bản ghi bằng chứng có đủ nguồn gốc;
- câu trích sai bị phát hiện;
- luận điểm không có bằng chứng bị loại;
- trạng thái `accepted` chỉ do cửa kiểm cấp;
- `UNSUPPORTED`/`CONTRADICTED` không lọt vào tập được chấp nhận;
- chế độ Nghiên cứu thực hiện tìm phản chứng;
- quan hệ phụ thuộc giữa nguồn được biểu diễn;
- luận điểm → bằng chứng truy ngược được;
- lịch sử sửa đổi luận điểm truy ngược được;
- Hồ sơ lần nghiên cứu có thể rà soát;
- hồ sơ đã chốt không bị sửa đè;
- phạm vi đã kiểm/chưa kiểm rõ ràng;
- 11 tình huống kiểm thử nghiên cứu chuẩn ổn định;
- lỗi nghiên cứu nghiêm trọng mới phát hiện được bổ sung thành kiểm thử hồi quy;
- đóng khi thiếu dữ liệu vẫn được giữ.

## 21. Tương lai — đường truy xuất Connector sâu

> Trạng thái: **TƯƠNG LAI — không thuộc 2.0 phiên bản đầu**

Nếu locator hữu hạn thực sự trở thành điểm nghẽn, có thể xem xét tác vụ từ xa
tất định:

```text
yêu cầu Connector
→ tác vụ truy xuất từ xa
→ snapshot corpus/index đã ghim
→ kết quả có nguồn gốc
→ Connector đọc kết quả
→ mở nguồn
→ Bản ghi bằng chứng
```

Tác vụ từ xa chỉ làm truy xuất, kiểm thử hoặc tạo tệp kết quả. Nó không tự tổng
hợp kết luận và không được bỏ qua các cửa kiểm.

## 22. Ngoài phạm vi 2.0 phiên bản đầu

Không đưa vào nếu chưa có yêu cầu mới:

- cơ sở dữ liệu véc-tơ;
- embedding toàn corpus;
- đồ thị tri thức toàn diện;
- Kubernetes;
- microservices;
- cơ sở dữ liệu phân tán;
- hệ nhiều tác nhân tự hành;
- tìm kiếm ngữ nghĩa phổ quát;
- điểm tin cậy phần trăm giả như một xác suất đã hiệu chuẩn;
- kiến trúc kho dữ liệu đám mây mới chỉ để phục vụ lớp kiểm chứng.

## 23. Quan hệ với tài liệu khác

- `docs/v2/PRD.md`: đề bài, mục tiêu và ranh giới sản phẩm 2.0;
- `docs/PROJECT_SPEC.md`: đặc tả cấp toàn dự án;
- `docs/v2/REQUIREMENTS.md`: yêu cầu có mã dành riêng cho 2.0;
- `docs/v2/ACCEPTANCE.md`: cách nghiệm thu các yêu cầu 2.0;
- `docs/v2/IMPLEMENTATION_PLAN.md`: kế hoạch triển khai ngắn dựa trên mã nguồn hiện hành;
- `docs/REQUIREMENTS.md` và `docs/ACCEPTANCE.md`: yêu cầu và nghiệm thu của
  hệ thống hiện hành;
- `docs/ARCHITECTURE.md`: kiến trúc đã triển khai;
- `AGENTS.md`: luật nghiên cứu luôn áp dụng;
- `.codex/skills/buddhist-corpus-research/SKILL.md`: hành vi AI hiện hành;
- `docs/REMOTE_AGENT.md`: vận hành Connector hiện hành.

Nếu tài liệu này khác code hiện hành, đó **không tự động là lỗi của code** vì
tài liệu này mô tả MỤC TIÊU. Chỉ khi yêu cầu tương ứng được chuyển sang HIỆN
HÀNH thì mã nguồn mới phải đáp ứng đầy đủ.
