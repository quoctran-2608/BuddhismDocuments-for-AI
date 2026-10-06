# Cầu nối định danh SuttaCentral Āgama → CBETA

> Trạng thái: **HIỆN HÀNH**
>
> Phạm vi: mô tả subsystem ánh xạ định danh SuttaCentral Hán văn sang CBETA và
> cách resolver dùng ánh xạ đó. Đây là metadata quan hệ; không phải bằng chứng
> câu chữ.

Cầu nối chỉ dùng các file local đã ghim dưới:

`suttacentral/sc-data/html_text/lzh/**/*.html`

Nó không lập chỉ mục phần prose HTML như một primary witness. Nó chỉ trích:

- SuttaCentral `<article id>`;
- liên kết CBETA explicit có trong file local;
- Taishō line anchor local như `t0563a14`.

## 1. Loại quan hệ

### `suttacentral_cbeta:work`

Ánh xạ một SuttaCentral UID tới CBETA work ID đã chuẩn hóa khi file local có liên
kết CBETA explicit.

Ví dụ:

```text
ea9.7 → T02n0125
```

### `suttacentral_cbeta:line_range`

Ánh xạ một SuttaCentral UID tới Taishō anchor nhỏ nhất/lớn nhất khi mirror xác
định đúng một CBETA work.

Ví dụ:

```text
ea9.7 → T02n0125:0563a14..0563a27
```

`details_json` giữ toàn bộ anchor đã trích, anchor đầu/cuối, số lượng anchor và
thông tin rằng ánh xạ đến từ liên kết CBETA explicit trong file local.

Cả hai loại relation đều có `evidence_class = metadata_relationship`; không loại
nào tự chứng minh textual identity.

## 2. Resolver

```bash
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus resolve T02n0125:0563a14..0563a27
```

`resolve ea9.7` chỉ đi theo relation cầu nối explicit đã được lập chỉ mục. Một
CBETA work/range trực tiếp cũng có thể được resolve.

Cả hai dạng được kiểm overlap với record local trong `cbeta-bm` và/hoặc
`cbeta-tei`. CBETA record trả về vẫn là một textual witness riêng, có source path
và pinned source SHA riêng.

Resolver hỗ trợ hai dạng index:

1. chunk của `core`/`acceptance` dùng `relation_ids` đầu/cuối hợp lệ;
2. record chi tiết của profile `all` fallback về `segment_id` hợp lệ dạng
   `WORK:START..END` hoặc `WORK:LINE`.

`relation_ids` hợp lệ được ưu tiên.

Không dùng nội dung text để suy hoặc “sửa” locator.

Query record phải duyệt đủ toàn work thay vì cắt ở 5.000 row, để một index `all`
chi tiết không làm mất khả năng resolve range của CBETA work dài.

## 3. Phạm vi local và trường hợp chưa giải được

Tại snapshot khảo sát của subsystem, cây `html_text/lzh` đã ghim có 4.714 HTML
mirror:

- 2.779 có article UID, liên kết CBETA explicit và Taishō anchor;
- 1.928 có article UID và Taishō anchor nhưng không có liên kết CBETA explicit;
- 7 có article UID nhưng không có cả liên kết CBETA explicit lẫn Taishō anchor.

1.935 mirror không có CBETA identifier explicit được **cố ý giữ unresolved**.
Một số filename trông giống Taishō identifier, nhưng suy work ID từ filename sẽ
vi phạm luật bằng chứng local. Chúng chỉ được ánh xạ khi source local cung cấp
identifier explicit.

Nếu một mirror có nhiều liên kết CBETA work explicit, work mapping vẫn được giữ,
nhưng không gán một Taishō range chung cho tất cả các work đó.

## 4. Coverage resolver đã đo

Với core index được dùng khi phép đo này được thực hiện:

- 2.648 / 2.779 explicit line range overlap một CBETA `BM_u8` core record;
- 129 range không có primary record trong core index:
  - 128 thuộc năm work có XML P5 local nhưng không nằm trong core `BM_u8` index:
    `T02n0150a`, `T22n1422a`, `T22n1422b`, `T32n1670a`, `T32n1670b`;
  - 1 range (`t780b → T17n0780b`) không có CBETA XML filename local tương ứng;
- 2 range chỉ tới work có trong `BM_u8` nhưng mirror anchor local không overlap
  range của work đó:
  - `lzh-sarv-bu-pm-2 → T23n1436:0200b18..0206b19`;
  - `t511 → T14n0551:0779a03..0781a19`.

Các số trên là **snapshot đo coverage của subsystem**, không phải nguồn chuẩn cho
trạng thái toàn dự án. Hành vi resolver hiện hành phải được kiểm bằng code/tests;
source contract hiện hành phải lấy từ `manifest.json` và config tương ứng.

Cầu nối vẫn giữ các mapping unresolved như metadata nhưng không tự bịa corrected
work ID hoặc line range.

Khi research dùng một bridge chưa resolve được primary witness, phải báo:

**không đủ dữ liệu trong corpus hiện tại**

## 5. Quy tắc đóng thất bại

CBETA suffix letter được so case-insensitive vì source ID local có thể dùng cả
hai dạng, ví dụ `T02n0150A` và bridge ID đã chuẩn hóa `T02n0150a`.

Không suy work number hoặc line range khi dữ liệu vắng mặt hoặc mâu thuẫn.

Các trường hợp malformed, reversed hoặc non-overlap phải fail-closed; tiêu chí
nghiệm thu nằm trong `docs/ACCEPTANCE.md` và các resolver tests.
