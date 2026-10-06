# Khảo sát corpus cục bộ — hồ sơ lịch sử

> **Trạng thái: LỊCH SỬ / SNAPSHOT NGÀY 22/09/2026**
>
> Tài liệu này ghi lại tình trạng corpus tại thời điểm khảo sát ban đầu. Những
> câu như “repository chưa có chỉ mục xuyên corpus” mô tả đúng thời điểm
> 22/09/2026, **không phải trạng thái hệ thống hiện tại**.
>
> Muốn biết trạng thái hiện hành, xem `docs/PROJECT_SPEC.md`,
> `docs/ARCHITECTURE.md`, config/schema/code/tests tương ứng.

Khảo sát ngày 22/09/2026 chỉ dùng các file đã checkout và Git object đã ghim;
không dùng nguồn từ xa.

## 1. Kết luận tại thời điểm khảo sát

Tại thời điểm đó, repository chưa có chỉ mục tìm kiếm chung xuyên corpus. Một số
nguồn có chỉ mục/công cụ riêng, chủ yếu dưới `third-party/pali-canon` và
`pts/pts-archive`, nhưng chưa có schema record chung hoặc giao diện truy xuất
thống nhất cho cả 13 submodule.

Môi trường local có SQLite 3.45.1 với FTS5. Vì vậy tầng được triển khai sau khảo
sát chọn Python standard library và SQLite FTS5, không cần tải thêm package.

## 2. Quan sát từng nguồn

| Nguồn | Schema/định danh quan sát được | Vai trò | Giới hạn thấy trong dữ liệu local |
|---|---|---|---|
| SuttaCentral Bilara | JSON map `segment_id → string`; file root, translation, comment, variant cùng họ; ví dụ `mn1:1.1` | Root/canonical và bản dịch có cấu trúc | Comment có thể chứa link ngoài; variant dùng cú pháp compact cho người đọc |
| SuttaCentral sc-data | `new_parallels.json`, structure, language, school, editions, dictionaries | Đồ thị quan hệ và metadata | Một parallel edge không chứng minh câu chữ; một số structure file được tài liệu upstream đánh dấu deprecated |
| CBETA XML P5 | TEI, root `xml:id` như `T01n0001`, `lb @n`, `pb`, `mulu`, `app/lem/rdg`, witness sigla | Ấn bản Hán văn có cấu trúc, thẩm quyền cao | File lớn; gaiji và apparatus cần parser hiểu nguồn |
| CBETA BM_u8 | Dòng plain text mở đầu bằng CBETA work/page/line ID | Nhân chứng plain-text nhanh | Markup là cú pháp legacy compact; XML P5 giàu thông tin hơn khi cần kiểm chứng |
| 84000 TEI | TEI title, publication `idno`, `bibl @key=toh...`, milestone và folio metadata | Bản dịch Anh ngữ có cấu trúc, thẩm quyền cao | Một số file là placeholder, ít hoặc không có body text |
| 84000 RDF | Một RDF file cho mỗi Toh. work; work, instance, translation, sameAs, label | Dữ liệu metadata/quan hệ | Chỉ là metadata; không phải textual witness |
| 84000 Translation Memory | TMX và JSON `tus`; Tibetan/English, folio, passage ID, creation method | Căn chỉnh/khám phá | v3 machine alignment theo tài liệu upstream là gần đúng; v4 được sửa thủ công |
| OpenPecha C0A2DD042 | Cặp `WORK-lang.txt` căn theo dòng và CSV catalog | Căn chỉnh đa ngôn ngữ Tây Tạng/khám phá | Trộn nhiều nguồn upstream; line alignment không phải canonical edition độc lập |
| BuddhaNexus Pāli | Segment map; dạng gốc và dạng cắt bằng tính toán; canonical material có ID tương thích SC | Khám phá/phân đoạn | Commentary source khác nhau; cut segment là dữ liệu dẫn xuất tính toán |
| BuddhaNexus Chinese | JSON gzip chứa sentence segment với CBETA-like line ID | Khám phá/phân đoạn | Dẫn xuất từ CBETA; khi có thể phải kiểm lại bằng CBETA XML |
| BuddhaNexus Sanskrit | JSON machine segmentation, có một tập nhỏ được kiểm thủ công | Khám phá/phân đoạn | README upstream cảnh báo có nhiều lỗi |
| PTS archive | 53 text export có page mark; có thể có SQLite/apparatus khôi phục | Tham khảo phụ trợ | README cảnh báo typo, mojibake, volume thiếu/sai nhãn và khác biệt page ROTA-vs-PTS |
| pali-canon | Canonical JSON, token lemma/morphology, critical apparatus năm witness | Bằng chứng lemma/khảo dị dẫn xuất | Critical text là editorial/derived; lemmatization có thể phân tích sai và không được thay nhân chứng |

## 3. Quyết định tokenization sau khảo sát

Một tokenizer duy nhất không đủ cho mọi hệ chữ.

- FTS5 `unicode61 remove_diacritics 0` giữ dấu Pāli/Sanskrit và cung cấp token
  search cho các hệ chữ phân cách bằng khoảng trắng.
- Một biểu diễn bỏ dấu riêng hỗ trợ fallback search có chủ đích nhưng phải xếp
  thấp hơn exact Unicode match.
- Một FTS5 trigram index riêng trên `compact(raw_text)` sinh ứng viên chuỗi con
  Hán văn cho record `lzh`/`zh`, kể cả CBETA chunk dài mà cột
  normalized/compact được cố ý để trống. Truy vấn ngắn hơn ba ký tự CJK hữu dụng
  không có bảo đảm arbitrary middle-substring coverage. Index này chưa thiết
  lập hành vi substring cho tiếng Tạng.
- Lemma được lưu trong bảng riêng và đưa vào biểu diễn có thể tìm kiếm. Chỉ lemma
  do corpus cung cấp mới được tính là lemma evidence.
- Relation và alignment nằm trong bảng riêng; không nối chúng vào text.

## 4. Phân loại bằng chứng

Implementation sau khảo sát dùng các lớp:

- `canonical_root`;
- `authoritative_structured`;
- `metadata_relationship`;
- `parallel_alignment`;
- `computational_segmented`;
- `derived_critical_lemma`;
- `auxiliary_reference`.

Các tên này được giữ trong indexed record và provenance response.

## 5. Cách đọc tài liệu này hôm nay

Tài liệu này có giá trị vì nó ghi lại **vì sao** dự án đi tới kiến trúc hiện tại,
nhưng không phải nguồn chuẩn cho trạng thái hôm nay.

Nếu cần biết:

- kiến trúc hiện hành → `docs/ARCHITECTURE.md`;
- nguồn/SHA hiện hành → `manifest.json`;
- corpus/evidence class hiện hành → `config/corpus-sources.json`;
- schema hiện hành → `schema/corpus-index.sql`;
- lý do các quyết định kiến trúc đã chưng cất → `docs/adr/`.
