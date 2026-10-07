# Yêu cầu hiện hành của dự án

> Trạng thái tài liệu: **HIỆN HÀNH**
>
> Vai trò: nguồn chuẩn cho các yêu cầu có mã của **hệ thống hiện hành**.
>
> Yêu cầu riêng của Buddhist Corpus Research 2.0 được tách hoàn toàn sang
> `docs/v2/REQUIREMENTS.md` để tránh lẫn giữa phiên bản đang chạy và phiên bản
> đang nâng cấp.

## 1. Cách đọc mã yêu cầu

Các nhóm mã:

- `REQ-SRC`: nguồn và tính bất biến;
- `REQ-DER`: dữ liệu dẫn xuất;
- `REQ-RET`: truy xuất và xếp hạng;
- `REQ-EVD`: bằng chứng và provenance;
- `REQ-WIT`: nhân chứng và vai trò văn bản;
- `REQ-REL`: quan hệ, song hành và cầu nối;
- `REQ-CON`: GitHub Connector và production locator;
- `REQ-FAIL`: đóng thất bại và giới hạn;
- `REQ-DOC`: quản trị tài liệu.

Tất cả mã trong file này đều là **HIỆN HÀNH**. Các nhóm mã
`REQ-VER`, `REQ-QTE`, `REQ-CTR`, `REQ-RUN`, `REQ-TST` thuộc riêng
Buddhist Corpus Research 2.0 và được quản lý trong `docs/v2/REQUIREMENTS.md`.

---

## 2. Nguồn và tính bất biến

### REQ-SRC-001 — Mười ba nguồn upstream phải được ghim theo commit SHA

**Trạng thái:** HIỆN HÀNH.

Dự án phải duy trì đúng 13 nguồn upstream được quản lý và ghim ở commit SHA xác
định. Danh sách và SHA máy đọc nằm ở `manifest.json`.

**Không đạt** nếu:

- thiếu nguồn;
- SHA local không khớp hợp đồng;
- một nguồn bị thay bằng bản mới không ghi nhận;
- thêm “nguồn thứ 14” ngầm từ web hoặc trí nhớ mô hình.

### REQ-SRC-002 — Nguồn upstream là bất biến trong quá trình nghiên cứu

**Trạng thái:** HIỆN HÀNH.

Không được sửa, normalize, regenerate hoặc commit dữ liệu nghiên cứu vào bên
trong repository/submodule nguồn như một phần của quy trình nghiên cứu.

### REQ-SRC-003 — Nguồn thiếu hoặc sai SHA là lỗi provenance

**Trạng thái:** HIỆN HÀNH.

Local mode phải phát hiện source không có hoặc SHA không khớp và không tiếp tục
như thể dữ liệu hợp lệ.

### REQ-SRC-004 — Mỗi corpus phải có ánh xạ vai trò nguồn rõ ràng

**Trạng thái:** HIỆN HÀNH.

Mỗi corpus được hỗ trợ phải có tối thiểu:

- tên corpus;
- repository;
- evidence class;
- vai trò;
- build profile phù hợp.

Nguồn chuẩn: `config/corpus-sources.json`.

---

## 3. Dữ liệu dẫn xuất

### REQ-DER-001 — SQLite là artefact dẫn xuất, không phải nguồn gốc

**Trạng thái:** HIỆN HÀNH.

`derived/corpus.sqlite3` và các index liên quan phải có thể hiểu là dữ liệu sinh
ra từ các nguồn đã ghim; không được nâng database thành nguồn chuẩn của câu chữ.

### REQ-DER-002 — Artefact dẫn xuất phải có provenance về source SHA

**Trạng thái:** HIỆN HÀNH.

Record/work/relation/variant/lemma phải bảo toàn source path và source SHA phù
hợp với loại dữ liệu.

### REQ-DER-003 — Build phải hỗ trợ tính gia tăng và nhận biết phiên bản parser

**Trạng thái:** HIỆN HÀNH.

Build phải có trạng thái đủ để bỏ qua component không đổi và rebuild khi
source/parser/index version thay đổi.

### REQ-DER-004 — Chỉ mục CJK phải được xem là hạ tầng truy xuất

**Trạng thái:** HIỆN HÀNH.

`records_cjk_fts` dùng trigram phải được coi là chỉ mục sinh ứng viên,
không được mô tả như một từ điển thuật ngữ Phật học.

---

## 4. Truy xuất và xếp hạng

### REQ-RET-001 — Truy xuất phải dùng một ngữ nghĩa xếp hạng chung

**Trạng thái:** HIỆN HÀNH.

Local retrieval và generation của production pointer phải dùng chung logic xếp
hạng cuối, không duy trì hai scholarly ranking độc lập.

### REQ-RET-002 — Xếp hạng phải xác định được và phá hòa ổn định

**Trạng thái:** HIỆN HÀNH.

Với cùng dữ liệu và query, thứ tự cuối phải có quy tắc deterministic đủ để tái
tạo.

### REQ-RET-003 — Tìm kiếm phải phân biệt normalize và bỏ dấu

**Trạng thái:** HIỆN HÀNH.

Primary normalization phải bảo toàn dấu; diacritic folding là bước riêng, không
được hòa thành cùng một phép chuẩn hóa.

### REQ-RET-004 — Lemma do corpus cung cấp phải được dùng như bằng chứng truy xuất

**Trạng thái:** HIỆN HÀNH.

Hệ thống phải có thể dùng lemma/morphology đã được corpus/index cung cấp để mở
rộng tập ứng viên mà không tự bịa biến thể.

### REQ-RET-005 — Truy vấn CJK chuỗi con dài phải có đường sinh ứng viên phù hợp

**Trạng thái:** HIỆN HÀNH.

Đối với `lzh`/`zh`, truy vấn chuỗi con có ít nhất ba ký tự CJK hữu dụng phải
có thể dùng CJK trigram index khi index hiện hành sẵn sàng.

### REQ-RET-006 — Ranking chỉ là ưu tiên mở nguồn

**Trạng thái:** HIỆN HÀNH.

Score/rank không được dùng để tự suy ra:

- độ đúng của truyền thống;
- niên đại;
- độc lập nguồn;
- tương đương đa ngôn ngữ;
- độ đủ của claim.

---

## 5. Bằng chứng và provenance

### REQ-EVD-001 — Pointer không phải textual evidence

**Trạng thái:** HIỆN HÀNH.

Không được trích hoặc tổng hợp câu chữ từ pointer metadata. Trong Connector mode,
phải mở pinned upstream source trước khi dùng wording làm bằng chứng.

### REQ-EVD-002 — Kết luận nghiên cứu phải truy nguyên về nguồn

**Trạng thái:** HIỆN HÀNH.

Mỗi kết luận nghiên cứu quan trọng phải truy được về các trường provenance phù
hợp, gồm:

- corpus/source;
- repository/path;
- work/text identifier;
- segment/line/folio/Toh./CBETA hoặc tương đương khi có;
- pinned source SHA;
- evidence class;
- text role;
- witness khi liên quan.

### REQ-EVD-003 — Bằng chứng phải được đọc trong đủ ngữ cảnh

**Trạng thái:** HIỆN HÀNH.

Một kết quả truy xuất không đủ để trở thành kết luận nghiên cứu. Quy trình phải có khả năng đọc
context trước/sau hoặc mở raw source khi cần để xác minh ý nghĩa.

### REQ-EVD-004 — Discovery source không được âm thầm thay primary witness

**Trạng thái:** HIỆN HÀNH.

BuddhaNexus, corpus căn chỉnh hoặc nguồn phục vụ khám phá tương tự chỉ nên tạo ứng viên
khi có witness mạnh hơn để mở. Nếu không resolve được, phải nêu giới hạn.

### REQ-EVD-005 — Evidence hierarchy phải được giữ khi tổng hợp

**Trạng thái:** HIỆN HÀNH.

Nguồn có evidence class thấp hơn không được tự động được nâng thành primary chỉ
vì dễ tìm hoặc xếp hạng cao.

---

## 6. Nhân chứng và vai trò văn bản

### REQ-WIT-001 — `evidence_class`, `text_role`, `witness` phải tách biệt

**Trạng thái:** HIỆN HÀNH.

Ba trường này biểu diễn ba khái niệm khác nhau và không được gom thành một điểm
“độ tin cậy”.

### REQ-WIT-002 — Ghi chú không được trộn vào bản dịch chính

**Trạng thái:** HIỆN HÀNH.

Khi nguồn hỗ trợ cấu trúc note, note phải có text role riêng hoặc quan hệ riêng,
không được chèn prose của note vào translation_main.

### REQ-WIT-003 — Compare không tự hòa hợp nhân chứng

**Trạng thái:** HIỆN HÀNH.

Kết quả so sánh phải giữ các witness riêng; không tự sinh một bản hợp nhất như
thể đó là original text.

### REQ-WIT-004 — Bản dịch không được trình bày như nguyên ngữ

**Trạng thái:** HIỆN HÀNH.

Một wording trong translation phải được nhận diện đúng text role và không được
dùng như bằng chứng câu chữ của root text.

---

## 7. Quan hệ, song hành và cầu nối

### REQ-REL-001 — Metadata quan hệ không phải textual proof

**Trạng thái:** HIỆN HÀNH.

Parallel relation, RDF relation, alignment hoặc identifier bridge chỉ chứng minh
loại quan hệ mà dữ liệu biểu diễn; không tự chứng minh câu chữ.

### REQ-REL-002 — Luồng SuttaCentral → CBETA phải giữ ba bước riêng

**Trạng thái:** HIỆN HÀNH.

Phải tách:

```text
SuttaCentral parallel relation
→ SuttaCentral-to-CBETA identifier bridge
→ resolved CBETA textual witness
```

### REQ-REL-003 — Resolver CBETA phải fail-closed trên định danh/range sai

**Trạng thái:** HIỆN HÀNH.

Malformed range, reversed range, locator sai hoặc non-overlap không được trả về
textual witness như thể hợp lệ.

### REQ-REL-004 — Cross-language equivalence cần repository evidence

**Trạng thái:** HIỆN HÀNH.

Phương trình Pāli/Sanskrit/Chinese/Tibetan do mô hình đề xuất chỉ là search
hypothesis cho tới khi có alignment, relationship, dictionary, shared canonical
ID hoặc repository evidence khác hỗ trợ.

---

## 8. GitHub Connector và production locator

### REQ-CON-001 — Connector phải đọc runtime config thay vì hard-code repo

**Trạng thái:** HIỆN HÀNH.

Repository, branch, root path và mode của remote runtime phải được lấy từ
`config/remote-corpus.json`.

### REQ-CON-002 — Remote repo là artefact dẫn xuất, không phải corpus thứ 14

**Trạng thái:** HIỆN HÀNH.

`BuddhismDocuments-for-AI-remote` chỉ làm tầng định tuyến/locator; source
evidence nằm ở pinned upstream repositories.

### REQ-CON-003 — Production routing không phụ thuộc GitHub Code Search

**Trạng thái:** HIỆN HÀNH.

Connector phải dùng hash-bucket locator đã định nghĩa, không dùng GitHub Code
Search như cơ chế định tuyến chuẩn.

### REQ-CON-004 — Production pointer không chứa `raw_text`

**Trạng thái:** HIỆN HÀNH.

Artefact production pointer-only không được sao chép nội dung raw corpus vào
pointer row.

### REQ-CON-005 — Pointer phải đủ provenance để mở pinned source

**Trạng thái:** HIỆN HÀNH.

Pointer production phải bảo toàn tối thiểu repository, source SHA, path và các
định danh cần thiết để agent mở đúng source; `source_blob_sha` phải được dùng
khi có.

### REQ-CON-006 — Term bucket dùng normalization chính thức

**Trạng thái:** HIỆN HÀNH.

`terms/latin` dùng:

```text
NFC → casefold → collapse whitespace
```

Không bỏ dấu khi tính bucket.

### REQ-CON-007 — Identifier giữ spelling gốc

**Trạng thái:** HIỆN HÀNH.

`ids` không casefold/normalize key theo cách làm mất phân biệt spelling gốc.

### REQ-CON-008 — Bucket phải xác định bằng SHA-256

**Trạng thái:** HIỆN HÀNH.

Bucket dùng hai ký tự hex thường đầu tiên của SHA-256 trên exact UTF-8 production
key.

### REQ-CON-009 — Production v1 chỉ materialize namespace đã khai báo

**Trạng thái:** HIỆN HÀNH.

Production v1 hiện materialize:

- `terms/latin`;
- `ids`.

Không được giả định tồn tại `terms/cjk`.

### REQ-CON-010 — Ứng viên production phải cân bằng theo corpus và gộp nguồn trùng

**Trạng thái:** HIỆN HÀNH.

Quá trình sinh artefact phải hạn chế việc một corpus/work/source chiếm toàn bộ tập ứng viên,
và phải collapse theo identity được production design định nghĩa.

### REQ-CON-011 — Generation phải deterministic và có thể resume

**Trạng thái:** HIỆN HÀNH.

Một lần generation bị gián đoạn không được làm hỏng artefact production hợp lệ
đã tồn tại; rerun phải có thể tiếp tục/tái tạo ổn định.

---

## 9. Đóng thất bại và giới hạn

### REQ-FAIL-001 — Local mode không được lấp khoảng trống bằng internet

**Trạng thái:** HIỆN HÀNH.

Local research là offline nghiêm ngặt.

### REQ-FAIL-002 — Connector chỉ dùng đường đọc từ xa đã khai báo

**Trạng thái:** HIỆN HÀNH.

Connector mode không phải giấy phép dùng web nói chung làm corpus evidence.

### REQ-FAIL-003 — Không có bằng chứng thì phải trả trạng thái thiếu dữ liệu

**Trạng thái:** HIỆN HÀNH.

Không được biến “không tìm thấy” thành “điều đó không tồn tại”.

### REQ-FAIL-004 — Giới hạn CJK remote phải được nói rõ

**Trạng thái:** HIỆN HÀNH.

Production v1 không được quảng bá như hỗ trợ arbitrary exhaustive CJK substring
lookup.

---

## 10. Quản trị tài liệu

### REQ-DOC-001 — Mỗi loại sự thật phải có nguồn chuẩn theo miền

**Trạng thái:** HIỆN HÀNH.

Quy tắc nằm ở `docs/DOCUMENTATION_GOVERNANCE.md`.

### REQ-DOC-002 — Tài liệu phải phân biệt HIỆN HÀNH / MỤC TIÊU / TƯƠNG LAI / LỊCH SỬ

**Trạng thái:** HIỆN HÀNH.

Một đặc tả MỤC TIÊU hoặc TƯƠNG LAI chưa triển khai không được trình bày như runtime hiện tại.

### REQ-DOC-003 — README chỉ là cửa vào, không phải nguồn chuẩn mọi chi tiết

**Trạng thái:** HIỆN HÀNH.

README có thể tóm tắt nhưng không được ghi đè config/schema/code.

### REQ-DOC-004 — Tài liệu lịch sử phải giữ đúng bối cảnh lịch sử

**Trạng thái:** HIỆN HÀNH.

`progress.md`, benchmark và corpus survey có thể giữ số liệu cũ nhưng phải được
hiểu là snapshot/hồ sơ lịch sử, không phải trạng thái vận hành hiện tại.

---

---

## 11. Quan hệ với Buddhist Corpus Research 2.0

Tài liệu này chỉ sở hữu các yêu cầu **HIỆN HÀNH** của hệ thống đang chạy.

Các yêu cầu riêng của chương trình nâng cấp 2.0 nằm tại:

- `docs/v2/REQUIREMENTS.md` — yêu cầu có mã của 2.0;
- `docs/v2/ACCEPTANCE.md` — cách nghiệm thu các yêu cầu 2.0.

Không sao chép các yêu cầu 2.0 trở lại file này. Khi một năng lực 2.0 thật sự
được triển khai và nghiệm thu, tài liệu hiện hành sẽ được cập nhật theo thay đổi
thực tế lúc đó.

## 12. Quy tắc thay đổi yêu cầu hiện hành

Một yêu cầu hiện hành chỉ được sửa khi:

1. lý do thay đổi được ghi rõ;
2. tài liệu cấp dự án liên quan được đối chiếu;
3. tiêu chí nghiệm thu tương ứng được cập nhật;
4. mã nguồn, cấu hình, schema và kiểm thử liên quan được xem xét;
5. nếu là quyết định kiến trúc bền vững, ADR được tạo hoặc cập nhật.

Không được âm thầm sửa yêu cầu chỉ để hợp thức hóa cách triển khai hiện tại.
