# Buddhist Corpus Research 2.0 — Đặc tả yêu cầu sản phẩm (PRD) cho hệ thống nghiên cứu có kiểm chứng

> Trạng thái: **MỤC TIÊU**
>
> Vai trò: tài liệu trung tâm mô tả **đề bài nâng cấp từ hệ hiện hành lên
> Buddhist Corpus Research 2.0**: vì sao cần nâng cấp, 2.0 phải làm được gì,
> những gì phải giữ nguyên, những gì không thuộc 2.0 và khi nào 2.0 được coi là
> thành công.
>
> Tài liệu này **không phải thiết kế mã nguồn**. Chi tiết kỹ thuật nằm trong
> `docs/v2/DESIGN.md`, `docs/v2/REQUIREMENTS.md` và
> `docs/v2/ACCEPTANCE.md`.

## 1. Quy ước phiên bản

Trong chương trình nâng cấp này:

- **Buddhist Corpus Research 1.0** là tên quy ước cho hệ thống hiện hành trước
  lớp kiểm chứng luận điểm;
- **Buddhist Corpus Research 2.0** là phiên bản mục tiêu của lần nâng cấp này.

Đây là quy ước sản phẩm để giúp tài liệu dễ hiểu. Nó không khẳng định kho Git
trước đây đã từng phát hành chính thức phiên bản `1.0` theo quy ước phiên bản
ngữ nghĩa.

### Quy ước thuật ngữ trong tài liệu

**PRD** là viết tắt của *Product Requirements Document*, trong tài liệu này hiểu
là **đặc tả yêu cầu sản phẩm**: tài liệu trả lời vì sao cần nâng cấp, cần đạt gì,
không làm gì và khi nào được coi là thành công.

Tài liệu ưu tiên cách gọi tiếng Việt. Một số thuật ngữ kỹ thuật được giữ tên
tiếng Anh trong ngoặc ở lần xuất hiện đầu tiên để đối chiếu với mã nguồn và tài
liệu kỹ thuật:

- **luận điểm** (`claim`): điều hệ thống muốn khẳng định;
- **bằng chứng** (`evidence`): nội dung đã thực sự được mở, đọc và truy nguyên
  về nguồn;
- **phản chứng** (`counterevidence`): bằng chứng hoặc dữ liệu có thể làm yếu,
  thu hẹp hoặc bác bỏ một luận điểm;
- **cửa kiểm cuối** (`Final Claim Gate`): bước kiểm tra bắt buộc trước khi một
  luận điểm được phép đi vào phần tổng hợp;
- **hồ sơ lần nghiên cứu** (`Research Run`): dấu vết có cấu trúc của một lần
  nghiên cứu;
- **đóng khi thiếu dữ liệu** (`fail-closed`): khi không đủ bằng chứng thì dừng
  và nói rõ giới hạn, không tự điền bằng suy đoán.

Sau phần định nghĩa này, văn xuôi ưu tiên dùng cách gọi tiếng Việt. Tên trường,
mã trạng thái hoặc tên giao diện máy có thể giữ nguyên tiếng Anh khi cần đối
chiếu chính xác với mã nguồn.

## 2. Một câu mô tả 2.0

Buddhist Corpus Research 1.0 đã làm tốt việc:

> **Đưa AI tới đúng nguồn.**

Buddhist Corpus Research 2.0 phải bổ sung khả năng:

> **Không cho AI đi xa hơn những gì nguồn thực sự cho phép kết luận.**

2.0 không nhằm làm repo “biết nhiều Phật học hơn”.

2.0 nhằm làm quá trình nghiên cứu:

- khó suy diễn quá mức hơn;
- khó trích sai hơn;
- khó biến bằng chứng yếu thành kết luận mạnh hơn;
- chủ động tìm dữ liệu làm yếu kết luận;
- truy ngược được vì sao một kết luận được chấp nhận hoặc bị loại.

## 3. Vấn đề cần giải quyết

Hệ 1.0 đã làm tốt chuỗi:

```text
câu hỏi
→ tìm ứng viên
→ mở đúng kho Git
→ đúng commit
→ đúng file/đoạn
→ đọc ngữ cảnh
→ nguồn gốc truy nguyên
```

Khoảng trống còn lại nằm **sau khi nguồn đã được đọc**.

Một nguồn hoàn toàn thật vẫn có thể bị AI dùng sai mức, ví dụ:

- nguồn nói “một số” nhưng AI viết “luôn luôn”;
- siêu dữ liệu song hành bị dùng như bằng chứng câu chữ;
- bản dịch/chú thích bị trình bày như nguyên văn;
- một tuyên bố trong văn bản bị nâng thành sự thật lịch sử;
- nhiều citation phụ thuộc cùng một nguồn bị hiểu là nhiều xác nhận độc lập;
- AI chỉ tìm bằng chứng thuận mà không tìm ngoại lệ;
- phần tổng hợp tự sinh thêm kết luận chưa được kiểm.

Vấn đề trung tâm của 2.0 là:

```text
có bằng chứng thật
≠
luận điểm của AI tự động đúng
```

## 4. Mục tiêu sản phẩm

Sau 2.0, đối với một nghiên cứu đủ sâu, hệ thống phải có khả năng trả lời có cấu
trúc các câu hỏi:

- Kết luận này dựa trên bằng chứng nào?
- Bằng chứng hỗ trợ trực tiếp hay chỉ gián tiếp?
- Câu trích có khớp nguồn thật không?
- Có nhân chứng độc lập nào không?
- Có phản chứng hoặc dữ liệu làm yếu kết luận không?
- luận điểm nào đã bị loại và vì sao?
- Lần nghiên cứu này dùng phiên bản corpus nào?
- Có thể rà soát lại đường từ luận điểm → bằng chứng → nguồn gốc đã ghim không?

## 5. Phương pháp cốt lõi của 2.0

2.0 không chỉ thêm vài trường dữ liệu. Nó thay đổi cách một kết luận được phép đi
từ nguồn tới câu trả lời.

### 5.1. Từ “quy tắc AI nên nhớ” thành “đối tượng + trạng thái + cửa kiểm”

Ở 1.0, nhiều nguyên tắc nghiên cứu đúng đã tồn tại dưới dạng luật mà AI phải tự
tuân thủ.

2.0 phải đưa các điểm quan trọng nhất thành cấu trúc có thể kiểm:

```text
bằng chứng đã đọc
→ có trạng thái

luận điểm
→ có trạng thái

quan hệ luận điểm ↔ bằng chứng
→ có mức hỗ trợ

phản chứng
→ có dấu vết

luận điểm cuối
→ phải qua cửa kiểm
```

Mục tiêu không phải loại AI khỏi nghiên cứu, mà không để một lần suy luận tự do
vừa tạo luận điểm vừa tự xác nhận luận điểm đó.

### 5.2. Giữ bốn tầng dữ liệu riêng

2.0 phải giữ rõ:

```text
con trỏ
→ chỉ nơi cần đọc

bằng chứng
→ điều đã thực sự mở và đọc

luận điểm
→ điều AI muốn khẳng định

tổng hợp
→ cách trình bày các luận điểm đã được kiểm
```

Không gộp bốn tầng này thành một đối tượng chung.

### 5.3. Phân biệt “nguồn mạnh” và “nguồn có hỗ trợ luận điểm này không”

2.0 phải luôn tách hai câu hỏi:

1. **Nguồn này thuộc loại nào, có thẩm quyền ra sao?**
2. **Nguồn này thực sự hỗ trợ luận điểm cụ thể này đến mức nào?**

Một nguồn rất mạnh vẫn có thể không chứng minh luận điểm đang xét.

Ngược lại, điểm truy xuất cao chỉ giúp quyết định nên mở nguồn nào trước; nó
không phải mức xác nhận học thuật.

### 5.4. Việc máy kiểm được thì ưu tiên kiểm bằng máy

Các việc xác định như:

- nguồn/path/SHA có hợp lệ không;
- vị trí có tồn tại không;
- quotation có khớp không;
- nguồn gốc truy nguyên có đủ không;
- luận điểm có bằng chứng không;
- luận điểm bị cấm có lọt qua Cửa kiểm luận điểm cuối không;

nên được kiểm bằng quy tắc máy khi có thể.

AI chỉ nên đảm nhiệm phần thật sự cần suy luận ngôn ngữ như:

- tạo giả thuyết tìm kiếm;
- tách luận điểm;
- đánh giá quan hệ ngữ nghĩa luận điểm ↔ bằng chứng khi quy tắc máy không đủ;
- đề xuất hướng tìm phản chứng;
- tổng hợp câu trả lời.

### 5.5. Truy xuất trước, kiểm chứng sau

Không chạy verifier trên corpus khổng lồ.

Luồng đúng là:

```text
corpus lớn
→ truy xuất hiện hành thu hẹp ứng viên
→ mở một tập bằng chứng nhỏ
→ kiểm chứng trên tập bằng chứng đó
```

Đây là cách giữ 2.0 đơn giản và không phá hiệu năng của 1.0.

### 5.6. Tách nguyên văn, bản dịch và diễn giải

Khi có liên quan, 2.0 phải phân biệt rõ:

```text
VĂN BẢN NGUỒN
BẢN DỊCH ĐÃ XUẤT BẢN
BẢN DỊCH LÀM VIỆC CỦA AI
DIỄN GIẢI
tổng hợp
```

Bản dịch do AI tạo không được trình bày như bản dịch học thuật đã xuất bản.
Diễn giải không được đặt trong ngoặc kép như nguyên văn.

### 5.7. Trạng thái phải do cửa kiểm quyết định

Một bài học quan trọng từ hệ thống trước đây là: **trạng thái không được chỉ là
một nhãn do AI hoặc chương trình gọi tự gán**.

Ví dụ, một luận điểm không được coi là “đã chấp nhận” chỉ vì nơi tạo luận điểm
ghi như vậy. Trạng thái cuối phải là kết quả của các điều kiện kiểm tra thực tế:

```text
luận điểm đề nghị
→ kiểm bằng chứng
→ kiểm mức hỗ trợ
→ kiểm phản chứng
→ kiểm giới hạn
→ cửa kiểm quyết định trạng thái
```

Nguyên tắc bắt buộc:

> **Trạng thái công bố là kết quả của cửa kiểm, không phải ý kiến tự khai của
> AI hay của chương trình gọi.**

### 5.8. Luận điểm phải có lịch sử sửa đổi

Khi một luận điểm bị phản chứng, bị thu hẹp hoặc cần viết lại, hệ thống không
được âm thầm sửa đè rồi làm mất lịch sử.

Phải giữ được ít nhất:

- luận điểm cũ là gì;
- luận điểm mới thay thế nó là gì;
- lý do thay đổi;
- bằng chứng hoặc phản chứng nào dẫn tới thay đổi.

Có thể dùng quan hệ “bản mới thay thế bản cũ” (`supersedes`) trong dữ liệu.
Tên trường cụ thể sẽ do tài liệu thiết kế và mã nguồn quyết định sau.

Mục tiêu là để sau này có thể trả lời:

> “Kết luận này đã thay đổi như thế nào và vì sao?”

### 5.9. Hồ sơ nghiên cứu đã chốt không được sửa âm thầm

Một hồ sơ lần nghiên cứu đã được chốt để làm căn cứ cho câu trả lời không nên bị
sửa đè như chưa từng có phiên bản cũ.

Nếu có bằng chứng mới làm thay đổi kết quả, hệ thống nên tạo bản sửa đổi hoặc
lần nghiên cứu mới có quan hệ rõ với bản trước.

Nguyên tắc này nhằm bảo đảm:

- có thể kiểm toán lại kết quả cũ;
- biết kết luận nào từng được dùng ở thời điểm nào;
- không làm lịch sử nghiên cứu thay đổi âm thầm.

2.0 chưa cần xây một hệ thống quản lý phiên bản phức tạp. Chỉ cần mô hình dữ liệu
không chặn khả năng truy ngược này.

### 5.10. “Chưa xác định” là một kết quả hợp lệ

Khi chưa có bằng chứng đủ để xác định một thông tin, hệ thống phải cho phép giữ
trạng thái:

```text
chưa xác định
không chắc
chưa kiểm
```

thay vì tự điền cho đủ trường.

Nguyên tắc này đặc biệt quan trọng với:

- mức độc lập giữa các nguồn;
- quan hệ giữa các nhân chứng;
- tác giả, niên đại hoặc người dịch khi nguồn không nói rõ;
- tương đương giữa Pāli, Sanskrit, Hán và Tạng;
- loại bằng chứng hoặc loại luận điểm khi chưa đủ căn cứ.

“Chưa xác định” trung thực hơn một giá trị có vẻ đầy đủ nhưng không có nguồn.

### 5.11. Lỗi nghiên cứu thật phải trở thành bài kiểm thử lâu dài

Nếu hệ thống từng cho một lỗi nghiên cứu nghiêm trọng lọt qua, ví dụ:

- câu trích sai vẫn được xuất như nguyên văn;
- chú thích của người dịch bị coi là văn bản gốc;
- luận điểm quá mạnh vẫn được chấp nhận;
- hai nguồn phụ thuộc bị tính như hai xác nhận độc lập;
- luận điểm bị phản chứng vẫn lọt vào kết luận;

thì sau khi sửa, tình huống đó phải trở thành **bài kiểm thử hồi quy**.

> **Kiểm thử hồi quy** là bài kiểm tra được giữ lại để bảo đảm một lỗi đã sửa
> không quay trở lại ở các phiên bản sau.

Các bài kiểm thử nghiên cứu chuẩn nên ưu tiên dùng những lỗi thật từng xảy ra,
không chỉ những tình huống giả định.

## 6. Những gì 2.0 phải giữ nguyên

2.0 là **lớp bổ sung**, không phải dự án viết lại hệ thống.

Các tài sản của 1.0 phải được bảo toàn:

### 6.1. Nguồn và nguồn gốc truy nguyên

- 13 kho nguồn gốc bên ngoài được ghim theo commit SHA;
- đường dẫn nguồn / SHA nguồn / SHA tệp nguồn;
- mã tác phẩm / mã đoạn / thứ tự;
- `evidence_class`;
- `text_role`;
- `witness`.

### 6.2. chế độ cục bộ

```text
SQLite + FTS + CLI
```

Không thay bằng một hạ tầng nặng hơn chỉ vì thêm lớp kiểm chứng.

### 6.3. chế độ GitHub Connector

Giữ đường nhanh hiện tại:

```text
khóa của locator chính thức
→ ô băm SHA-256
→ mảnh locator
→ con trỏ đã xếp hạng
→ nguồn gốc bên ngoài đã ghim
```

Không thay bằng GitHub Code Search.

Không quét toàn kho Git.

Không chép nguyên văn kho ngữ liệu vào locator.

### 6.4. Luật nghiên cứu cốt lõi

Giữ nguyên:

```text
kiến thức mô hình
→ chỉ tạo giả thuyết tìm kiếm

bằng chứng trong kho nguồn
→ mới được xác lập kết luận nghiên cứu
```

Giữ fail-closed khi dữ liệu không đủ.

Giữ nhân chứng riêng; không tự hòa các truyền thống thành một tiếng nói chung.

### 6.5. Tương thích ngược

Các lệnh và hành vi 1.0 đang được dùng như `search`, `context`, `work`,
`parallels`, `resolve`, `variants`, `compare`, `provenance` và
`evidence` không được phá nếu không có lý do bắt buộc và đường chuyển đổi rõ
ràng.

Không thay ranking hiện tại chỉ vì thêm lớp kiểm chứng.

## 7. Năng lực mới của 2.0

2.0 tập trung vào tám năng lực chính.

### 7.1. Bản ghi bằng chứng

Chuẩn hóa bằng chứng **đã thực sự được mở và đọc**, thay vì coi search hit hoặc
con trỏ là bằng chứng.

### 7.2. Cửa kiểm bằng chứng

Kiểm trước khi một kết quả được dùng làm bằng chứng:

- nguồn có mở được không;
- nguồn gốc truy nguyên có đúng không;
- vị trí có khớp không;
- vai trò văn bản có phù hợp không;
- đã đọc đủ ngữ cảnh chưa.

### 7.3. Kiểm chứng câu trích

Phân biệt tối thiểu:

- nguyên văn khớp chính xác;
- khớp sau chuẩn hóa an toàn;
- diễn đạt lại;
- chưa kiểm;
- câu trích không khớp.

Một câu trích sai không được xuất như nguyên văn.

### 7.4. Luận điểm nguyên tử

Kết luận quan trọng được tách thành các luận điểm nhỏ đủ để kiểm độc lập.

Không viết một đoạn tổng hợp dài rồi gắn vài citation ở cuối và coi như toàn bộ
đoạn đã được chứng minh.

### 7.5. Kiểm chứng luận điểm ↔ bằng chứng

Mỗi luận điểm phải được đánh giá quan hệ với bằng chứng, ít nhất theo các mức:

```text
DIRECT
STRONG
WEAK
UNSUPPORTED
CONTRADICTED
```

Khi một luận điểm dựa trên nhiều nguồn, 2.0 cũng phải biểu diễn được các nguồn đó là
độc lập, phụ thuộc một phần, cùng họ nguồn, dẫn xuất từ nhau hay chưa xác định.
Nhiều citation không tự động được tính là nhiều xác nhận độc lập.

Điểm truy xuất/rank không được dùng thay cho đánh giá này.

### 7.6. phản chứng

Trong chế độ nghiên cứu sâu, hệ thống phải chủ động tìm:

- ngoại lệ;
- nhân chứng khác;
- dị bản;
- song hành không khớp;
- nguồn cùng tầng nói khác;
- quan hệ phụ thuộc làm yếu “nhiều nguồn”;
- điều kiện giới hạn phạm vi luận điểm.

Phản chứng phải có khả năng làm luận điểm bị sửa, thu hẹp, hạ mức hoặc loại.

### 7.7. Cửa kiểm luận điểm cuối và kiểm tra cuối

Chỉ luận điểm đủ điều kiện mới được đi vào phần tổng hợp cuối.

`UNSUPPORTED` và `CONTRADICTED` không được trình bày như kết luận đã xác lập.

Nếu tổng hợp cần thêm một luận điểm quan trọng mới, luận điểm đó phải quay lại quy
trình kiểm chứng.

Sau khi tổng hợp, hệ thống phải có một bước kiểm tra cuối để bắt các lỗi kiểu:

- luận điểm quan trọng không có bằng chứng;
- câu trích trực tiếp chưa được kiểm;
- con trỏ/siêu dữ liệu bị trình bày như câu chữ nguồn;
- chú thích của bản dịch bị trình bày như văn bản gốc;
- quan hệ song hành bị biến thành đồng nhất câu chữ;
- tương đương đa ngôn ngữ không có bằng chứng trong kho nguồn;
- phần tổng hợp vô tình làm luận điểm mạnh hơn trạng thái đã được chấp nhận;
- giới hạn phạm vi quan trọng bị bỏ mất.

Nếu kiểm tra cuối thất bại, câu trả lời không được xuất như một kết luận đã xác
lập.

### 7.8. Hồ sơ lần nghiên cứu

Với nghiên cứu sâu, hệ thống lưu đủ dấu vết để biết:

- câu hỏi và phạm vi;
- phiên bản repo/corpus/locator;
- các truy vấn và giả thuyết tìm kiếm;
- bằng chứng đã dùng;
- luận điểm đã tạo;
- luận điểm được chấp nhận hoặc loại;
- phản chứng đã tìm;
- giới hạn của lần nghiên cứu.

Mục tiêu là kiểm toán và tái lập nền bằng chứng, **không phải lưu chain-of-thought
nội bộ của mô hình**.

2.0 phải phân biệt:

- **tái lập truy xuất**: cùng corpus/locator/phạm vi/truy vấn phải lấy lại được
  nền bằng chứng chính tương tự;
- **tái lập nghiên cứu**: biết bằng chứng nào đã dùng, luận điểm nào được chấp nhận hay
  loại, phản chứng nào đã được kiểm và vì sao.

Không đặt mục tiêu bắt AI phải viết lại từng chữ giống hệt lần trước.

## 8. Hai cấp sử dụng

2.0 không được biến mọi câu hỏi thành một quy trình nặng.

### 8.1. Chế độ Nhanh (`Quick`)

Dành cho:

- tra từ;
- tìm đoạn;
- tìm mã tác phẩm;
- xem một quan hệ song hành cụ thể;
- kiểm một câu trích nhỏ.

Luồng tối thiểu:

```text
truy xuất
→ nguồn đã ghim
→ ngữ cảnh / nguồn gốc truy nguyên
→ kiểm câu trích khi cần
→ trả lời
```

### 8.2. Chế độ Nghiên cứu (`Research`)

Dành cho:

- câu hỏi khái niệm;
- nghiên cứu so sánh;
- lịch sử;
- tổng hợp nhiều nguồn;
- nội dung dùng cho sách/bài nghiên cứu;
- câu hỏi có tranh luận hoặc luận điểm tổng quát.

Luồng:

```text
bằng chứng
→ luận điểm
→ kiểm chứng
→ phản chứng
→ Cửa kiểm luận điểm cuối
→ tổng hợp
→ Hồ sơ lần nghiên cứu
```

## 9. Ví dụ cho thấy 2.0 khác 1.0 ở đâu

Giả sử hệ thống mở được ba đoạn thật có `anicca` và `nibbidā`.

AI muốn viết:

> “Trong kinh tạng sớm, quán vô thường **luôn** dẫn tới yếm ly.”

### Với 1.0

Hệ thống có thể xác nhận ba citation đều có thật và nguồn gốc truy nguyên đều đúng.

Nhưng chữ **“luôn”** vẫn có thể vượt quá dữ liệu.

### Với 2.0

Câu đó trở thành một luận điểm riêng.

Hệ thống phải hỏi:

- ba bằng chứng có đủ để chứng minh “luôn” không;
- có trường hợp `anicca` không đi cùng `nibbidā` không;
- nhân chứng khác có cấu trúc khác không;
- phạm vi “kinh tạng sớm” có rộng hơn corpus đã kiểm không.

Kết quả có thể là:

- sửa luận điểm;
- thu hẹp phạm vi;
- hạ xuống `WEAK`;
- hoặc `UNSUPPORTED`.

2.0 chấp nhận một câu trả lời ít mạnh hơn nếu nó trung thực hơn với bằng chứng.

## 10. Loại luận điểm cần phân biệt

2.0 phải ít nhất phân biệt:

- `textual` — văn bản nói gì;
- `historical` — điều gì có thể suy ra về lịch sử;
- `relationship` — các văn bản/ID/nhân chứng liên hệ thế nào;
- `comparative` — các truyền thống/nhân chứng giống và khác gì;
- `interpretive` — cách hiểu từ bằng chứng;
- `empirical` — mệnh đề thực nghiệm;
- `metaphysical` — mệnh đề về thực tại tối hậu.

Mục đích là chặn các bước nhảy tầng như:

```text
văn bản nói X
→ X là sự thật lịch sử
```

hoặc:

```text
văn bản khẳng định tái sinh
→ tái sinh đã được chứng minh thực nghiệm
```

## 11. Trải nghiệm người dùng

Người dùng vẫn chỉ cần hỏi tự nhiên.

Ví dụ:

> “Nghiên cứu vai trò của vô thường trong lập luận vô ngã ở kinh tạng sớm.”

Hệ thống tự xử lý:

```text
phạm vi
→ giả thuyết tìm kiếm
→ truy xuất
→ nguồn
→ bằng chứng
→ luận điểm
→ kiểm chứng
→ phản chứng
→ tổng hợp
```

Không hỏi người dùng về ô băm (`bucket`), không gian tên (`namespace`), kho Git
hay truy vấn kỹ thuật (`query`) trừ khi
phạm vi thực sự không thể suy ra.

Câu trả lời cuối vẫn phải dễ đọc với người nghiên cứu; các cấu trúc kỹ thuật
chỉ hiện ra khi cần kiểm toán hoặc hỏi sâu.

Với chế độ Nghiên cứu, câu trả lời phải thể hiện đủ để người đọc biết:

- kết luận chính;
- bằng chứng theo corpus/nhân chứng;
- phản chứng hoặc giới hạn;
- phần diễn giải của AI;
- phạm vi **đã kiểm** và **chưa kiểm**.

Không được viết một mệnh đề rộng như “trong Phật giáo...” nếu lần nghiên cứu chỉ
kiểm một phạm vi hẹp hơn.

### 11.1. Phải dùng được trên Codex và ChatGPT Work

2.0 không được thiết kế chỉ cho một máy cục bộ hoặc chỉ cho một cách gọi lệnh.

Yêu cầu bắt buộc:

- **Codex** phải có thể làm việc trực tiếp với mã nguồn, chạy các kiểm tra và dùng
  cùng hợp đồng Bản ghi bằng chứng / luận điểm / Hồ sơ lần nghiên cứu;
- **ChatGPT Work** phải có thể thực hiện cùng quy trình nghiên cứu khi làm việc
  với thư mục dự án, tệp được cung cấp hoặc nguồn GitHub đã kết nối;
- dữ liệu trao đổi giữa các bước phải có dạng máy đọc được, ưu tiên đối tượng
  Python có thể chuyển thẳng sang JSON;
- không được để ý nghĩa của một trạng thái chỉ tồn tại trong bộ nhớ của một
  phiên chat hay trong một đường dẫn máy cá nhân.

Đường qua **GitHub plugin** cũng phải được giữ tương thích khi plugin cung cấp đủ
thao tác đọc kho, commit và tệp nguồn. Nếu một phép kiểm chỉ có ở môi trường cục
bộ mà plugin không thực hiện được, hệ thống phải ghi **chưa xác minh** và đóng
khi thiếu dữ liệu; không được tự coi là đã đạt.

Mục tiêu là:

```text
một hợp đồng nghiên cứu
→ nhiều môi trường thực thi
→ cùng ý nghĩa trạng thái
→ cùng nguyên tắc đóng khi thiếu dữ liệu
```

## 12. Những gì không thuộc 2.0 phiên bản đầu

Không đưa vào chỉ để làm kiến trúc “hoành tráng” hơn:

- cơ sở dữ liệu véc-tơ (`vector database`) mới;
- biểu diễn nhúng (`embedding`) cho toàn bộ kho ngữ liệu;
- đồ thị tri thức (`knowledge graph`) toàn diện;
- nền tảng điều phối Kubernetes;
- kiến trúc vi dịch vụ (`microservices`);
- cơ sở dữ liệu phân tán;
- các tác nhân nghiên cứu tự hành;
- tìm kiếm ngữ nghĩa phổ quát;
- điểm tin cậy phần trăm giả như `93.7% đúng`;
- viết lại locator chính thức;
- thay SQLite/FTS cục bộ;
- biến GitHub Actions thành “bộ não nghiên cứu”.

### Đường dự phòng Connector sâu

Một đường truy xuất sâu từ xa cho truy vấn Hán văn tùy ý hoặc các trường hợp locator hữu
hạn không đủ là **TƯƠNG LAI**, không phải phạm vi 2.0 phiên bản đầu.

Chỉ xem xét khi có số liệu thực tế chứng minh cần thiết.

## 13. Tiêu chí thành công của 2.0

2.0 chỉ được coi là thành công khi tối thiểu chứng minh được:

1. truy xuất và CLI hiện tại không bị hồi quy;
2. locator chính thức vẫn tất định;
3. Connector vẫn mở đúng nguồn gốc bên ngoài đã ghim;
4. con trỏ vẫn không bị dùng như bằng chứng;
5. Bản ghi bằng chứng truy nguyên được về nguồn;
6. câu trích sai bị phát hiện;
7. luận điểm không có bằng chứng bị chặn;
8. `UNSUPPORTED` không lọt vào kết luận cuối;
9. `CONTRADICTED` không được trình bày như sự thật đã xác lập;
10. chế độ Nghiên cứu thực sự thực hiện bước tìm phản chứng;
11. luận điểm truy ngược được về bằng chứng;
12. bằng chứng truy ngược được về nguồn đã ghim;
13. một Hồ sơ lần nghiên cứu có thể được xem lại;
14. có thể hỏi “luận điểm này dựa trên bằng chứng nào?” và trả lời được;
15. có thể hỏi “có phản chứng nào cho luận điểm này?” và trả lời được;
16. biết phạm vi nào đã kiểm và chưa kiểm;
17. phân biệt được nguồn độc lập với nguồn dẫn xuất/phụ thuộc;
18. một luận điểm đã sửa có thể truy ngược về bản trước và lý do thay đổi;
19. hồ sơ nghiên cứu đã chốt không bị sửa đè âm thầm;
20. trạng thái chấp nhận luận điểm do cửa kiểm quyết định, không do AI tự khai;
21. lỗi nghiên cứu nghiêm trọng đã phát hiện có bài kiểm thử hồi quy tương ứng;
22. các bài kiểm thử nghiên cứu chuẩn chạy ổn định;
23. khi không đủ dữ liệu, hệ thống vẫn đóng khi thiếu dữ liệu (`fail-closed`).

## 14. Nguyên tắc ưu tiên khi phải lựa chọn

Khi có nhiều phương án triển khai, ưu tiên theo thứ tự:

1. đúng bằng chứng;
2. truy nguyên được;
3. fail-closed;
4. kiểm thử được;
5. tái lập được;
6. không phá 1.0;
7. đơn giản;
8. nhanh;
9. mở rộng được.

Không hy sinh độ tin cậy nghiên cứu để đổi lấy kiến trúc đẹp hoặc phức tạp.

Một nguyên tắc bổ sung:

> **Không thêm một tầng mới nếu tầng đó không giải quyết một rủi ro nghiên cứu
> cụ thể.**

Nếu một thành phần của 1.0 đã giải quyết tốt vấn đề, phải tái sử dụng thay vì
tạo một hệ thống thứ hai song song.

## 15. Ranh giới với các tài liệu khác

Tài liệu này là **PRD của chương trình nâng cấp 2.0**.

Nó trả lời:

> Tại sao nâng cấp? 2.0 phải làm được gì? Không làm gì? Khi nào thành công?

Các tài liệu chuyên biệt:

- `docs/PROJECT_SPEC.md` — đặc tả toàn bộ dự án, bao gồm cả 1.0 và hướng phát
  triển;
- `docs/v2/DESIGN.md` — thiết kế chi tiết của lớp kiểm chứng;
- `docs/v2/REQUIREMENTS.md` — yêu cầu có mã của 2.0;
- `docs/v2/ACCEPTANCE.md` — cách chứng minh yêu cầu 2.0 đã được đáp ứng;
- `docs/ARCHITECTURE.md` — kiến trúc **HIỆN HÀNH**, không phải kiến trúc 2.0 chưa
  triển khai;
- `docs/adr/` — lý do của các quyết định kiến trúc bền vững.

PRD không quyết định lược đồ dữ liệu, tên mô-đun, lớp, giao diện lập trình (API)
hay định dạng lưu trữ cụ thể.
Những quyết định đó chỉ được đưa ra sau khi đọc mã nguồn hiện hành và khi thật sự
cần cho triển khai.

## 16. Điều kiện bắt đầu viết mã

Trước khi viết mã cho 2.0, cần xác nhận ba điều:

1. PRD này đã mô tả đúng đề bài;
2. các điều bất biến của 1.0 cần giữ đã rõ;
3. lát cắt đầu tiên của 2.0 được chọn đủ nhỏ để triển khai và kiểm thử độc lập.

Sau đó phải đọc mã nguồn hiện hành và làm **một bản phân tích triển khai ngắn** trước
khi sửa mã. Bản này chỉ cần trả lời:

- luồng dữ liệu hiện tại thực sự đi qua đâu;
- mô-đun, lược đồ dữ liệu và bài kiểm thử nào liên quan;
- khoảng trống nào cần lấp;
- chỗ nào nên thêm lớp 2.0;
- bài kiểm thử nào phải có trước và sau thay đổi;
- rủi ro hồi quy chính;
- phần nào chưa nên triển khai.

Mục đích là để quyết định triển khai dựa trên mã nguồn thật, không suy đoán từ
PRD.

Không cần thiết kế lại toàn hệ thống trước khi bắt đầu.

## 17. Kết luận

Buddhist Corpus Research 2.0 không phải một hệ thống thứ hai.

Nó là:

```text
Buddhist Corpus Research 1.0
+ lớp kiểm chứng suy luận nghiên cứu
```

Nếu 1.0 trả lời tốt câu hỏi:

> “Nguồn nằm ở đâu và tôi đang đọc phiên bản nào?”

thì 2.0 phải trả lời thêm:

> “Kết luận này có thật sự được nguồn hỗ trợ không, có gì làm nó yếu đi, và tại
> sao nó được phép xuất hiện trong câu trả lời cuối?”
