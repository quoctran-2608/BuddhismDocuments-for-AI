# Buddhist Corpus Research 2.0 — PRD nâng cấp hệ thống nghiên cứu có kiểm chứng

> Trạng thái: **MỤC TIÊU**
>
> Vai trò: tài liệu trung tâm mô tả **đề bài nâng cấp từ hệ hiện hành lên
> Buddhist Corpus Research 2.0**: vì sao cần nâng cấp, V2 phải làm được gì,
> những gì phải giữ nguyên, những gì không thuộc V2 và khi nào V2 được coi là
> thành công.
>
> Tài liệu này **không phải thiết kế mã nguồn**. Chi tiết kỹ thuật nằm trong
> `docs/RESEARCH_VERIFICATION_DESIGN.md`, `docs/REQUIREMENTS.md` và
> `docs/ACCEPTANCE.md`.

## 1. Quy ước phiên bản

Trong chương trình nâng cấp này:

- **Buddhist Corpus Research 1.0** là tên quy ước cho hệ thống hiện hành trước
  lớp kiểm chứng luận điểm;
- **Buddhist Corpus Research 2.0** là phiên bản mục tiêu của lần nâng cấp này.

Đây là quy ước sản phẩm để giúp tài liệu dễ hiểu. Nó không khẳng định repository
trước đây đã phát hành một release semantic-version chính thức tên `1.0`.

## 2. Một câu mô tả V2

Buddhist Corpus Research 1.0 đã làm tốt việc:

> **Đưa AI tới đúng nguồn.**

Buddhist Corpus Research 2.0 phải bổ sung khả năng:

> **Không cho AI đi xa hơn những gì nguồn thực sự cho phép kết luận.**

V2 không nhằm làm repo “biết nhiều Phật học hơn”.

V2 nhằm làm quá trình nghiên cứu:

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
→ mở đúng repository
→ đúng commit
→ đúng file/đoạn
→ đọc ngữ cảnh
→ provenance
```

Khoảng trống còn lại nằm **sau khi nguồn đã được đọc**.

Một nguồn hoàn toàn thật vẫn có thể bị AI dùng sai mức, ví dụ:

- nguồn nói “một số” nhưng AI viết “luôn luôn”;
- metadata song hành bị dùng như bằng chứng câu chữ;
- bản dịch/chú thích bị trình bày như nguyên văn;
- một tuyên bố trong văn bản bị nâng thành sự thật lịch sử;
- nhiều citation phụ thuộc cùng một nguồn bị hiểu là nhiều xác nhận độc lập;
- AI chỉ tìm bằng chứng thuận mà không tìm ngoại lệ;
- phần tổng hợp tự sinh thêm kết luận chưa được kiểm.

Vấn đề trung tâm của V2 là:

```text
có bằng chứng thật
≠
luận điểm của AI tự động đúng
```

## 4. Mục tiêu sản phẩm

Sau V2, đối với một nghiên cứu đủ sâu, hệ thống phải có khả năng trả lời có cấu
trúc các câu hỏi:

- Kết luận này dựa trên bằng chứng nào?
- Bằng chứng hỗ trợ trực tiếp hay chỉ gián tiếp?
- Câu trích có khớp nguồn thật không?
- Có nhân chứng độc lập nào không?
- Có phản chứng hoặc dữ liệu làm yếu kết luận không?
- Claim nào đã bị loại và vì sao?
- Lần nghiên cứu này dùng phiên bản corpus nào?
- Có thể rà soát lại đường từ claim → evidence → pinned source không?

## 5. Những gì V2 phải giữ nguyên

V2 là **lớp bổ sung**, không phải dự án viết lại hệ thống.

Các tài sản của 1.0 phải được bảo toàn:

### 5.1. Nguồn và provenance

- 13 upstream repositories được ghim bằng commit SHA;
- source path / source SHA / source blob SHA;
- work ID / segment ID / sequence;
- `evidence_class`;
- `text_role`;
- `witness`.

### 5.2. Local mode

```text
SQLite + FTS + CLI
```

Không thay bằng một hạ tầng nặng hơn chỉ vì thêm verification.

### 5.3. GitHub Connector mode

Giữ đường nhanh hiện tại:

```text
production key
→ SHA-256 bucket
→ locator shard
→ ranked pointer
→ pinned upstream source
```

Không thay bằng GitHub Code Search.

Không quét toàn repository.

Không xuất raw corpus vào locator.

### 5.4. Luật nghiên cứu cốt lõi

Giữ nguyên:

```text
kiến thức mô hình
→ chỉ tạo giả thuyết tìm kiếm

bằng chứng repository
→ mới được xác lập kết luận nghiên cứu
```

Giữ fail-closed khi dữ liệu không đủ.

Giữ nhân chứng riêng; không tự hòa các truyền thống thành một tiếng nói chung.

## 6. Năng lực mới của V2

V2 tập trung vào tám năng lực chính.

### 6.1. Evidence Record

Chuẩn hóa bằng chứng **đã thực sự được mở và đọc**, thay vì coi search hit hoặc
pointer là evidence.

### 6.2. Evidence Gate

Kiểm trước khi một kết quả được dùng làm bằng chứng:

- source có mở được không;
- provenance có đúng không;
- vị trí có khớp không;
- vai trò văn bản có phù hợp không;
- đã đọc đủ ngữ cảnh chưa.

### 6.3. Quote Verification

Phân biệt tối thiểu:

- nguyên văn khớp chính xác;
- khớp sau chuẩn hóa an toàn;
- diễn đạt lại;
- chưa kiểm;
- câu trích không khớp.

Một câu trích sai không được xuất như nguyên văn.

### 6.4. Atomic Claim

Kết luận quan trọng được tách thành các luận điểm nhỏ đủ để kiểm độc lập.

Không viết một đoạn tổng hợp dài rồi gắn vài citation ở cuối và coi như toàn bộ
đoạn đã được chứng minh.

### 6.5. Claim ↔ Evidence Verification

Mỗi claim phải được đánh giá quan hệ với evidence, ít nhất theo các mức:

```text
DIRECT
STRONG
WEAK
UNSUPPORTED
CONTRADICTED
```

Điểm retrieval/rank không được dùng thay cho đánh giá này.

### 6.6. Counterevidence

Trong chế độ nghiên cứu sâu, hệ thống phải chủ động tìm:

- ngoại lệ;
- nhân chứng khác;
- dị bản;
- song hành không khớp;
- nguồn cùng tầng nói khác;
- quan hệ phụ thuộc làm yếu “nhiều nguồn”;
- điều kiện giới hạn phạm vi claim.

Phản chứng phải có khả năng làm claim bị sửa, thu hẹp, hạ mức hoặc loại.

### 6.7. Final Claim Gate

Chỉ claim đủ điều kiện mới được đi vào phần tổng hợp cuối.

`UNSUPPORTED` và `CONTRADICTED` không được trình bày như kết luận đã xác lập.

Nếu synthesis cần thêm một claim quan trọng mới, claim đó phải quay lại quy
trình kiểm chứng.

### 6.8. Research Run

Với nghiên cứu sâu, hệ thống lưu đủ dấu vết để biết:

- câu hỏi và phạm vi;
- phiên bản repo/corpus/locator;
- các truy vấn và giả thuyết tìm kiếm;
- evidence đã dùng;
- claim đã tạo;
- claim được chấp nhận hoặc loại;
- phản chứng đã tìm;
- giới hạn của lần nghiên cứu.

Mục tiêu là kiểm toán và tái lập nền bằng chứng, **không phải lưu chain-of-thought
nội bộ của mô hình**.

## 7. Hai cấp sử dụng

V2 không được biến mọi câu hỏi thành một quy trình nặng.

### 7.1. Quick

Dành cho:

- tra từ;
- tìm đoạn;
- tìm work ID;
- xem một parallel cụ thể;
- kiểm một câu trích nhỏ.

Luồng tối thiểu:

```text
retrieval
→ pinned source
→ context/provenance
→ quote check khi cần
→ answer
```

### 7.2. Research

Dành cho:

- câu hỏi khái niệm;
- nghiên cứu so sánh;
- lịch sử;
- tổng hợp nhiều nguồn;
- nội dung dùng cho sách/bài nghiên cứu;
- câu hỏi có tranh luận hoặc claim tổng quát.

Luồng:

```text
Evidence
→ Claim
→ Verification
→ Counterevidence
→ Final Claim Gate
→ Synthesis
→ Research Run
```

## 8. Ví dụ cho thấy V2 khác 1.0 ở đâu

Giả sử hệ thống mở được ba đoạn thật có `anicca` và `nibbidā`.

AI muốn viết:

> “Trong kinh tạng sớm, quán vô thường **luôn** dẫn tới yếm ly.”

### Với 1.0

Hệ thống có thể xác nhận ba citation đều có thật và provenance đều đúng.

Nhưng chữ **“luôn”** vẫn có thể vượt quá dữ liệu.

### Với 2.0

Câu đó trở thành một claim riêng.

Hệ thống phải hỏi:

- ba evidence có đủ để chứng minh “luôn” không;
- có trường hợp `anicca` không đi cùng `nibbidā` không;
- witness khác có cấu trúc khác không;
- phạm vi “kinh tạng sớm” có rộng hơn corpus đã kiểm không.

Kết quả có thể là:

- sửa claim;
- thu hẹp phạm vi;
- hạ xuống `WEAK`;
- hoặc `UNSUPPORTED`.

V2 chấp nhận một câu trả lời ít mạnh hơn nếu nó trung thực hơn với evidence.

## 9. Loại claim cần phân biệt

V2 phải ít nhất phân biệt:

- `textual` — văn bản nói gì;
- `historical` — điều gì có thể suy ra về lịch sử;
- `relationship` — các văn bản/ID/witness liên hệ thế nào;
- `comparative` — các truyền thống/witness giống và khác gì;
- `interpretive` — cách hiểu từ evidence;
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

## 10. Trải nghiệm người dùng

Người dùng vẫn chỉ cần hỏi tự nhiên.

Ví dụ:

> “Nghiên cứu vai trò của vô thường trong lập luận vô ngã ở kinh tạng sớm.”

Hệ thống tự xử lý:

```text
phạm vi
→ giả thuyết tìm kiếm
→ retrieval
→ source
→ evidence
→ claim
→ verification
→ counterevidence
→ synthesis
```

Không hỏi người dùng về bucket, namespace, repository hay query kỹ thuật trừ khi
phạm vi thực sự không thể suy ra.

Câu trả lời cuối vẫn phải dễ đọc với người nghiên cứu; các cấu trúc kỹ thuật
chỉ hiện ra khi cần kiểm toán hoặc hỏi sâu.

## 11. Những gì không thuộc V2 phiên bản đầu

Không đưa vào chỉ để làm kiến trúc “hoành tráng” hơn:

- vector database mới;
- embeddings toàn corpus;
- knowledge graph toàn diện;
- Kubernetes;
- microservices;
- distributed database;
- autonomous research agents;
- universal semantic search;
- điểm tin cậy phần trăm giả như `93.7% đúng`;
- viết lại production locator;
- thay local SQLite/FTS;
- biến GitHub Actions thành “bộ não nghiên cứu”.

### Deep Connector fallback

Một đường truy xuất sâu từ xa cho arbitrary CJK hoặc các trường hợp locator hữu
hạn không đủ là **TƯƠNG LAI**, không phải phạm vi V2 v1.

Chỉ xem xét khi có số liệu thực tế chứng minh cần thiết.

## 12. Tiêu chí thành công của V2

V2 chỉ được coi là thành công khi tối thiểu chứng minh được:

1. retrieval và CLI hiện tại không bị hồi quy;
2. production locator vẫn deterministic;
3. Connector vẫn mở pinned upstream source;
4. pointer vẫn không bị dùng như evidence;
5. Evidence Record truy nguyên được về source;
6. câu trích sai bị phát hiện;
7. claim không có evidence bị chặn;
8. `UNSUPPORTED` không lọt vào kết luận cuối;
9. `CONTRADICTED` không được trình bày như fact;
10. Research mode thực sự thực hiện counterevidence pass;
11. claim truy ngược được về evidence;
12. evidence truy ngược được về pinned source;
13. một Research Run có thể được xem lại;
14. biết phạm vi nào đã kiểm và chưa kiểm;
15. Golden Research Tests chạy ổn định;
16. khi không đủ dữ liệu, hệ thống vẫn fail-closed.

## 13. Nguyên tắc ưu tiên khi phải lựa chọn

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

## 14. Ranh giới với các tài liệu khác

Tài liệu này là **PRD của chương trình nâng cấp 2.0**.

Nó trả lời:

> Tại sao nâng cấp? V2 phải làm được gì? Không làm gì? Khi nào thành công?

Các tài liệu chuyên biệt:

- `docs/PROJECT_SPEC.md` — đặc tả toàn bộ dự án, bao gồm cả 1.0 và hướng phát
  triển;
- `docs/RESEARCH_VERIFICATION_DESIGN.md` — thiết kế chi tiết của lớp kiểm chứng;
- `docs/REQUIREMENTS.md` — requirement có mã;
- `docs/ACCEPTANCE.md` — cách chứng minh requirement đã được đáp ứng;
- `docs/ARCHITECTURE.md` — kiến trúc **HIỆN HÀNH**, không phải kiến trúc V2 chưa
  triển khai;
- `docs/adr/` — lý do của các quyết định kiến trúc bền vững.

PRD không sở hữu schema, tên module, class, API hay format lưu trữ cụ thể.
Những quyết định đó chỉ được đưa ra sau khi đọc code hiện hành và khi thật sự
cần cho implementation.

## 15. Điều kiện bắt đầu viết mã

Trước khi code V2, nhóm triển khai chỉ cần xác nhận ba điều:

1. PRD này đã mô tả đúng đề bài;
2. các invariants của 1.0 cần giữ đã rõ;
3. lát cắt đầu tiên của V2 được chọn đủ nhỏ để triển khai và kiểm thử độc lập.

Sau đó mới đọc code để chọn vị trí triển khai phù hợp.

Không cần thiết kế lại toàn hệ thống trước khi bắt đầu.

## 16. Kết luận

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
