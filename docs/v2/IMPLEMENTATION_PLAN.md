# Buddhist Corpus Research 2.0 — Kế hoạch triển khai ngắn

> Trạng thái: **MỤC TIÊU**
>
> Vai trò: cầu nối ngắn giữa bộ tài liệu 2.0 và mã nguồn hiện hành.
>
> Tài liệu này được viết **sau khi đọc mã nguồn thật**. Nó không thay PRD,
> Design, Requirements hay Acceptance và không mô tả tính năng đã triển khai.

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
└── verification.py     ← mới: Bản ghi bằng chứng + cửa kiểm + kiểm câu trích

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
8. trường không xác định được giữ trống/chưa xác định, không tự điền.

Sau khi lát cắt này xanh mới sang lớp luận điểm.

## 8. Thứ tự triển khai 2.0

Không làm tất cả cùng lúc.

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

### Giai đoạn E — Tích hợp và kiểm thử nghiên cứu chuẩn

- nối chế độ Nhanh / Nghiên cứu;
- tích hợp CLI khi cần;
- bổ sung 11 tình huống nghiên cứu chuẩn;
- biến sự cố nghiên cứu thật thành kiểm thử hồi quy;
- chỉ sau khi đạt nghiệm thu mới chuyển yêu cầu từ MỤC TIÊU sang HIỆN HÀNH.

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
4. đưa trạng thái `accepted` cho AI tự gán thay vì để cửa kiểm quyết định.

Nếu giữ được bốn ranh giới này, lát cắt đầu của 2.0 có thể rất nhỏ.

## 11. Việc tiếp theo

Bước viết mã đầu tiên nên là:

> **tạo `verification.py` + `test_verification.py`, chỉ triển khai Bản ghi
> bằng chứng, Cửa kiểm bằng chứng và kiểm chứng câu trích.**

Chưa thêm luận điểm, phản chứng hay Hồ sơ lần nghiên cứu trong cùng bước.
