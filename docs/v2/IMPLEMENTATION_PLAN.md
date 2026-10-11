# Buddhist Corpus Research 2.0 — Kế hoạch triển khai ngắn

> Trạng thái: **KẾ HOẠCH MỤC TIÊU / CÓ BỐI CẢNH LỊCH SỬ**
>
> Vai trò: cầu nối ngắn giữa bộ tài liệu 2.0 và mã nguồn hiện hành.
>
> Tài liệu này được viết **sau khi đọc mã nguồn thật**. Nó không thay PRD,
> Design, Requirements hay Acceptance. Các lát cắt/mốc test/việc tiếp theo
> trước A ở mục 1–7, 9–11 là lịch sử lập kế hoạch, không phải việc chưa làm
> tại main hiện nay. Thứ tự năm giai đoạn A–E và các quyết định được giữ nguyên.
>
> Cập nhật 11/10/2026: mã A–E đã gộp tại `57db982274e267218594ae5ca463bd2a42d2be02`.
> Dùng [USAGE](USAGE.md), [ACCEPTANCE](ACCEPTANCE.md) và [evidence](evidence/README.md)
> để đọc hiện trạng; Research publication, Work và nghiệm thu học thuật còn thiếu.

## 1. Kết luận ngắn

Không cần viết lại hệ thống 1.0.

Điểm chèn đơn giản và ít rủi ro nhất là:

```text
truy xuất hiện hành
→ retrieval.evidence()
→ Bản ghi bằng chứng 2.0
→ Cửa kiểm bằng chứng
→ kiểm chứng câu trích
→ các lớp luận điểm ở giai đoạn sau
```

Nói cách khác, **2.0 nên bắt đầu sau khi 1.0 đã tìm và gom được bằng chứng**,
không chen vào bộ phân tích nguồn, FTS, xếp hạng hoặc production locator.

### 1.1. Ràng buộc bắt buộc: chạy được trên Codex và ChatGPT Work

Lõi kiểm chứng không được đồng nghĩa với “một chương trình chỉ chạy trên máy có
SQLite đầy đủ”.

Cách tiếp cận:

```text
Codex / working copy cục bộ ─┐
ChatGPT Work ────────────────┼→ dữ liệu chuẩn JSON → lõi kiểm chứng 2.0
GitHub plugin ───────────────┘
```

**Codex** là đường đầy đủ nhất: có thể làm việc với mã nguồn, chạy Python, kiểm
thử và Git khi working copy có đủ submodule.

**ChatGPT Work** phải dùng cùng hợp đồng dữ liệu. Work có thể lấy dữ liệu từ thư
mục dự án, tệp được cung cấp hoặc nguồn/plugin đã kết nối rồi đưa vào cùng cấu
trúc kiểm chứng.

**ChatGPT qua GitHub plugin** là đường tương thích ưu tiên. Khi plugin đọc được
commit, tệp và nội dung nguồn, nó phải có thể tạo cùng Bản ghi bằng chứng. Nếu
plugin thiếu một phép kiểm mà local Git có, trạng thái phải là **chưa xác minh**
và đóng khi thiếu dữ liệu.

Nguyên tắc cho mã lõi:

- `verification.py` không được cần kết nối SQLite để hiểu một Bản ghi bằng
  chứng đã được tạo;
- không dùng đường dẫn tuyệt đối làm định danh nguồn;
- không buộc lệnh shell vào logic kiểm chứng học thuật;
- đầu vào/đầu ra phải chuyển được sang JSON;
- kiểm tra phụ thuộc môi trường phải đi qua một lớp cung cấp nguồn nhỏ, không
  được trộn vào quy tắc học thuật;
- cùng một dữ liệu phải cho cùng ý nghĩa trạng thái ở Codex, Work và đường
  GitHub plugin.

Ở lát cắt đầu, chưa cần xây một hệ plugin riêng. Chỉ cần **không khóa thiết kế vào
môi trường cục bộ**.

## 2. Mã nguồn hiện hành đã có gì để tái sử dụng

### 2.1. `retrieval.evidence()` là điểm bàn giao tự nhiên

Hàm `tools/corpus_research/retrieval.py::evidence()` hiện đã trả một gói gồm:

- bản ghi chính;
- ngữ cảnh trước/sau;
- nguồn gốc truy nguyên;
- dị bản liên quan.

Đây gần như chính là đầu vào cần thiết để tạo **Bản ghi bằng chứng**
(`Evidence Record`) của 2.0.

Vì vậy không nên tạo một đường đọc SQLite thứ hai chỉ dành cho lớp kiểm chứng.

### 2.2. Nguồn gốc truy nguyên đã có nền tốt

Hệ hiện hành đã giữ:

- corpus;
- đường dẫn nguồn;
- SHA nguồn;
- mã tác phẩm;
- mã đoạn;
- lớp bằng chứng;
- vai trò văn bản;
- nhân chứng;
- ngôn ngữ;
- quan hệ liên quan.

Đây là nền trực tiếp cho Cửa kiểm bằng chứng.

### 2.3. Logic kiểm tệp nguồn đã tồn tại một phần

`pointer_export.py` đã có logic:

- ánh xạ corpus → kho Git;
- chuyển đường dẫn đã lập chỉ mục thành đường dẫn trong kho nguồn;
- lấy Git blob SHA bằng `git rev-parse <source_sha>:<source_path>`.

Không nên viết lại cơ chế SHA khác cho 2.0.

Khi triển khai, nên rút phần dùng chung này thành một hàm/tiện ích chung để:

```text
locator
và
Cửa kiểm bằng chứng
```

cùng hiểu nguồn, đường dẫn và SHA theo một cách.

## 3. Những phần chưa nên sửa

Lát cắt đầu tiên của 2.0 **không cần** sửa:

- các bộ phân tích 13 nguồn trong `index.py`;
- bảng `records`, `works`, `relations`, `variants`, `lemmas`;
- FTS và CJK trigram;
- công thức xếp hạng truy xuất;
- `pointer_production.py`;
- định dạng production locator;
- GitHub Connector routing.

Lý do: các phần này đang giải bài toán **tìm đúng nguồn**. 2.0 giải bài toán
khác: **sau khi đã đọc nguồn, kết luận có vượt quá bằng chứng hay không**.

## 4. Không nên đưa dữ liệu nghiên cứu 2.0 vào corpus SQLite ngay

`schema/corpus-index.sql` hiện là lược đồ của **chỉ mục corpus dẫn xuất**.

Trong khi đó:

- Bản ghi bằng chứng 2.0;
- luận điểm;
- phản chứng;
- Hồ sơ lần nghiên cứu;

là dữ liệu của **một lần nghiên cứu**, có vòng đời và lịch sử sửa đổi riêng.

Vì vậy ở lát cắt đầu tiên:

> **không thêm bảng 2.0 vào corpus SQLite.**

Bản ghi bằng chứng trước hết có thể tồn tại như đối tượng Python và đầu ra JSON
máy đọc.

Khi tới giai đoạn cần lưu Hồ sơ lần nghiên cứu lâu dài, mới quyết định nơi lưu
và tạo ADR nếu quyết định đó ảnh hưởng kiến trúc.

## 5. Lát cắt triển khai đầu tiên

Chỉ làm ba năng lực:

### 5.1. Bản ghi bằng chứng

Tạo cấu trúc dữ liệu từ gói `retrieval.evidence()`.

Nó phải:

- giữ nguồn gốc;
- giữ ngữ cảnh;
- giữ vai trò văn bản và nhân chứng;
- không lấy câu chữ từ con trỏ;
- cho phép trường không áp dụng được để trống thay vì bịa dữ liệu.

### 5.2. Cửa kiểm bằng chứng

Kiểm tối thiểu:

- corpus có ánh xạ nguồn hợp lệ;
- SHA nguồn phù hợp;
- đường dẫn nguồn hợp lệ;
- vị trí bản ghi giải thích được;
- vai trò văn bản/nhân chứng được giữ đúng;
- nếu có thể kiểm Git blob SHA thì dùng cùng logic với locator.

### 5.3. Kiểm chứng câu trích

Hỗ trợ đúng năm trạng thái đã chốt:

- `VERIFIED_EXACT`;
- `VERIFIED_NORMALIZED`;
- `PARAPHRASE`;
- `UNVERIFIED`;
- `QUOTE_MISMATCH`.

Phần này nên là hàm thuần, dễ kiểm thử và không phụ thuộc mô hình AI.

## 6. Tổ chức mã tối thiểu

Không tạo nhiều mô-đun ngay từ đầu.

Đề xuất lát cắt đầu:

```text
tools/corpus_research/
├── retrieval.py        ← giữ nguyên trách nhiệm hiện tại
└── verification.py     ← mới: lõi thuần dữ liệu cho Bản ghi bằng chứng + cửa kiểm + kiểm câu trích

tests/
└── test_verification.py
```

Chưa tạo riêng `claims.py`, `counterevidence.py`, `research_run.py` cho
tới khi bắt đầu đúng giai đoạn đó.

Nếu `verification.py` sau này thực sự lớn, lúc đó mới tách.

## 7. Kiểm thử cho lát cắt đầu

`test_verification.py` nên dùng dữ liệu nhỏ, tạm thời và tất định; không cần
13 submodule để kiểm các quy tắc cốt lõi.

Tối thiểu cần kiểm:

1. con trỏ hoặc kết quả chưa mở không tự trở thành Bản ghi bằng chứng;
2. thiếu nguồn gốc bắt buộc bị từ chối;
3. sai SHA/đường dẫn bị từ chối;
4. câu trích khớp nguyên văn → `VERIFIED_EXACT`;
5. chỉ khác chuẩn hóa Unicode/khoảng trắng → `VERIFIED_NORMALIZED`;
6. đổi một từ → `QUOTE_MISMATCH`;
7. diễn đạt lại không được coi là câu trích nguyên văn;
8. trường không xác định được giữ trống/chưa xác định, không tự điền;
9. cùng một gói JSON cho kết quả kiểm chứng giống nhau không phụ thuộc nguồn dữ
   liệu đến từ SQLite cục bộ hay một bộ đọc GitHub giả lập;
10. thiếu khả năng kiểm nguồn ở môi trường từ xa trả trạng thái chưa xác minh,
    không tự coi là đạt.

Sau khi lát cắt này xanh mới sang lớp luận điểm.

## 8. Thứ tự triển khai 2.0

Không làm tất cả cùng lúc.

**Làm rõ ngày 11/10/2026:** giữ nguyên năm giai đoạn A–E. Hệ 1.0 tiếp tục
tìm và truy nguyên nguồn; 2.0 kiểm những bằng chứng/luận điểm liên quan sau
truy xuất. Hồ sơ xuất/nhập để phản biện độc lập thuộc D, còn kiểm hiệu quả và
tích hợp thuộc E; không cần tách giai đoạn hay thiết kế hệ hai AI tự động.
Mã A–E **ĐÃ TRIỂN KHAI và đã gộp vào main** tại
`57db982274e267218594ae5ca463bd2a42d2be02`. E có tích hợp local, fixture,
nguồn thật và đo mẫu, chưa nghiệm thu đầy đủ. Work, thẩm định độc lập thực
và quyền công bố Research còn thiếu.
Các mô tả lát cắt đầu, mốc 45 test và việc tiếp theo ở mục 5–7, 9, 11 giữ
bối cảnh lập kế hoạch trước A. Kết quả kiểm thử A/B đã thực thi xem
[ACCEPTANCE.md](ACCEPTANCE.md); hiệu quả tích hợp chỉ đã đo mẫu trong [E_REPORT](E_REPORT.md).

### Giai đoạn A — Bằng chứng

```text
Bản ghi bằng chứng
→ Cửa kiểm bằng chứng
→ kiểm chứng câu trích
```

### Giai đoạn B — Luận điểm

```text
Luận điểm nguyên tử
→ mức DIRECT / STRONG / WEAK / UNSUPPORTED / CONTRADICTED
→ Cửa kiểm luận điểm cuối
→ lịch sử sửa luận điểm
```

### Giai đoạn C — Phản chứng

```text
độc lập/phụ thuộc nguồn
→ tìm phản chứng
→ phản chứng làm sửa / hạ mức / loại luận điểm
```

### Giai đoạn D — Hồ sơ lần nghiên cứu

```text
Hồ sơ lần nghiên cứu
→ đã kiểm / chưa kiểm
→ bản đã chốt không sửa đè
→ lịch sử thay thế
```

D cần bổ sung hồ sơ có thể chuyển cho người có chuyên môn hoặc AI trong phiên
riêng, tiếp nhận báo cáo phản biện và lưu quyết định phê duyệt riêng
([REQ-RUN-007](REQUIREMENTS.md#req-run-007--hồ-sơ-phải-hỗ-trợ-xuấtnhập-thẩm-định-độc-lập)).
Có thể xuất/nhập thủ công trước; báo cáo không tự cấp quyền cho các cửa kiểm
A/B. Đây là độc lập của quá trình thẩm định, khác độc lập nguồn tư liệu ở C.

### Giai đoạn E — Tích hợp và kiểm thử nghiên cứu chuẩn

- nối chế độ Nhanh / Nghiên cứu;
- tích hợp CLI khi cần;
- bổ sung 11 tình huống nghiên cứu chuẩn;
- biến sự cố nghiên cứu thật thành kiểm thử hồi quy;
- chỉ sau khi đạt nghiệm thu mới chuyển yêu cầu từ MỤC TIÊU sang HIỆN HÀNH.

E nghiệm thu quy trình thẩm định ở D và đo ba nhóm: E1 bảo toàn kết quả/xếp
hạng/hiệu năng 1.0; E2 chi phí kiểm chứng tăng thêm của Nhanh; E3 chi phí so
với lỗi phát hiện và kết luận có căn cứ bị chặn nhầm trong Nghiên cứu
([REQ-TST-003](REQUIREMENTS.md#req-tst-003--phải-đo-hiệu-quả-trên-nền-so-sánh-được),
[tiêu chí E1–E3](ACCEPTANCE.md#22-đo-hiệu-quả-e1e3-ở-giai-đoạn-e)).
E1–E3 là nhóm đo trong E, không phải giai đoạn mới. E1/E2 đã đo mẫu, E3 đã đo
chi phí draft tại checkpoint trước sửa span; chất lượng học thuật, thẩm định
độc lập và token/chi phí AI **CHƯA ĐO**, ngưỡng chưa chốt. API
thẩm định tự động và hệ nhiều tác nhân vẫn ngoài phạm vi phiên bản đầu.

## 9. Mốc kiểm thử hiện tại

Mã nguồn hiện có **45 phương thức kiểm thử** trong 6 tệp:

- `test_acceptance.py`: 9;
- `test_cbeta_resolver.py`: 10;
- `test_cjk_substring_search.py`: 1;
- `test_normalization.py`: 7;
- `test_remote_access.py`: 15;
- `test_text_roles.py`: 3.

Trong phiên phân tích này, **45 kiểm thử chưa được thực thi**.

Lý do:

- môi trường làm việc không truy cập trực tiếp GitHub để tải 13 Git submodule;
- nhóm acceptance gọi `build_index(..., profile="acceptance")` và cần các
  submodule thật;
- repository hiện không có `.github/workflows/` để chạy bộ kiểm thử qua CI;
- commit đang kiểm tra cũng không có check run tự động.

Vì vậy trạng thái đúng là:

> **đã kiểm kê 45 test từ mã nguồn; chưa xác nhận 45/45 xanh trong phiên này.**

Khi triển khai mã, trước khi chuyển trạng thái yêu cầu 2.0 cần chạy trên một
working copy đầy đủ:

```bash
PYTHONPATH=tools python3 -m unittest discover -s tests -v
```

và giữ kết quả làm baseline.

## 10. Rủi ro hồi quy chính

Chỉ có bốn rủi ro cần canh ngay từ đầu:

1. vô tình thay đổi xếp hạng truy xuất khi thêm kiểm chứng;
2. coi gói `evidence()` là đã được kiểm chứng đầy đủ dù mới chỉ là dữ liệu đầu
   vào;
3. viết lại logic SHA/đường dẫn nguồn theo cách khác locator;
4. đưa trạng thái `accepted` cho AI tự gán thay vì để cửa kiểm quyết định;
5. vô tình viết lõi kiểm chứng phụ thuộc cứng vào SQLite/shell nên không dùng
   được trên ChatGPT Work hoặc đường GitHub plugin.

Nếu giữ được bốn ranh giới này, lát cắt đầu của 2.0 có thể rất nhỏ.

## 11. Việc tiếp theo

Bước viết mã đầu tiên nên là:

> **tạo `verification.py` + `test_verification.py`, chỉ triển khai Bản ghi
> bằng chứng, Cửa kiểm bằng chứng và kiểm chứng câu trích.**

Chưa thêm luận điểm, phản chứng hay Hồ sơ lần nghiên cứu trong cùng bước.
