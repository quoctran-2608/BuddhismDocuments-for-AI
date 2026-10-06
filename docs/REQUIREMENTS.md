# Yêu cầu dự án

> Trạng thái tài liệu: **HIỆN HÀNH**
>
> Vai trò: đặc tả các yêu cầu có mã của dự án.
>
> Nguyên tắc: yêu cầu **HIỆN HÀNH** mô tả những gì hệ thống hiện phải bảo toàn;
> yêu cầu **MỤC TIÊU** mô tả lớp nâng cấp đã được chấp thuận nhưng chưa được
> xem là triển khai xong.

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
- `REQ-DOC`: quản trị tài liệu;
- `REQ-VER`: kiểm chứng claim — MỤC TIÊU;
- `REQ-QTE`: kiểm chứng trích dẫn — MỤC TIÊU;
- `REQ-CTR`: phản chứng — MỤC TIÊU;
- `REQ-RUN`: hồ sơ lần nghiên cứu — MỤC TIÊU.

Trạng thái:

- **HIỆN HÀNH**: đã là yêu cầu của hệ thống đang chạy;
- **MỤC TIÊU**: đã chấp thuận về hướng nhưng chưa triển khai đầy đủ;
- **NGOÀI PHẠM VI V1**: không phải mục tiêu của vòng nâng cấp đầu.

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

### REQ-DOC-002 — Tài liệu phải phân biệt HIỆN HÀNH / MỤC TIÊU / LỊCH SỬ

**Trạng thái:** HIỆN HÀNH.

Một đặc tả chưa triển khai không được trình bày như runtime hiện tại.

### REQ-DOC-003 — README chỉ là cửa vào, không phải nguồn chuẩn mọi chi tiết

**Trạng thái:** HIỆN HÀNH.

README có thể tóm tắt nhưng không được ghi đè config/schema/code.

### REQ-DOC-004 — Tài liệu lịch sử phải giữ đúng bối cảnh lịch sử

**Trạng thái:** HIỆN HÀNH.

`progress.md`, benchmark và corpus survey có thể giữ số liệu cũ nhưng phải được
hiểu là snapshot/hồ sơ lịch sử, không phải trạng thái vận hành hiện tại.

---

# 11. Yêu cầu MỤC TIÊU — lớp kiểm chứng nghiên cứu

> Toàn bộ mục này là **MỤC TIÊU**. Chỉ chuyển sang HIỆN HÀNH khi có code,
> schema/format phù hợp và kiểm thử nghiệm thu.
>
> Semantics và data contract chi tiết của lớp này nằm trong
> `docs/RESEARCH_VERIFICATION_DESIGN.md`.

## 11.1. Evidence Record

### REQ-VER-001 — Chỉ nguồn đã mở và đọc mới được tạo Evidence Record

Pointer, tiêu đề, mục lục, dòng quan hệ, dòng cầu nối hoặc ứng viên khám phá không tự
động là Evidence Record.

### REQ-VER-002 — Evidence Record phải có provenance đầy đủ

Record mục tiêu phải chứa tối thiểu các trường cần để truy ngược nguồn và lần
nghiên cứu, gồm corpus, repository, source SHA/path, work/segment, language,
evidence class, text role, witness, quotation/context và research run ID khi có.

### REQ-VER-003 — Evidence Gate phải kiểm source locator

Trước khi evidence được chấp nhận, hệ thống phải kiểm được source/path/SHA và vị
trí văn bản phù hợp.

## 11.2. Atomic Claim

### REQ-VER-004 — Kết luận quan trọng phải tách thành Atomic Claim

Claim phải đủ nhỏ để đánh giá riêng support/counterevidence.

### REQ-VER-005 — Claim phải nối tới supporting evidence

Claim không có evidence phù hợp không được trở thành kết luận được chấp nhận.

### REQ-VER-006 — Claim verification phải dùng trạng thái định tính

Tối thiểu:

- DIRECT;
- STRONG;
- WEAK;
- UNSUPPORTED;
- CONTRADICTED.

Không dùng một xác suất giả tạo làm thay thế.

### REQ-VER-007 — UNSUPPORTED bị chặn khỏi kết luận cuối

Không được “làm mềm câu chữ” để lén đưa claim thiếu bằng chứng vào kết luận.

### REQ-VER-008 — CONTRADICTED không được trình bày như kết luận đã xác lập

Nếu claim còn được nhắc, phải trình bày đúng là bị phản bác/xung đột trong phạm
vi evidence đã kiểm.

### REQ-VER-009 — Retrieval rank và claim verification phải là hai lớp riêng

Không dùng rank/score của retrieval làm support level của claim.

### REQ-VER-010 — Synthesis chỉ dùng accepted claim set

Phần tổng hợp cuối không được tự thêm một kết luận quan trọng chưa qua claim gate.

### REQ-VER-011 — Atomic Claim phải khai báo loại claim

Mỗi claim quan trọng phải khai báo tối thiểu một `claim_type` thuộc taxonomy v1:

- `textual`;
- `historical`;
- `relationship`;
- `comparative`;
- `interpretive`;
- `empirical`;
- `metaphysical`.

Verifier phải dùng loại claim để tránh coi một loại evidence là đủ cho một mệnh
đề thuộc loại khác.

---

## 11.3. Kiểm chứng trích dẫn

### REQ-QTE-001 — Direct quote phải có trạng thái kiểm chứng

Các trạng thái mục tiêu:

- VERIFIED_EXACT;
- VERIFIED_NORMALIZED;
- PARAPHRASE;
- UNVERIFIED;
- QUOTE_MISMATCH.

### REQ-QTE-002 — QUOTE_MISMATCH không được xuất như direct quote

Nếu khác nguồn, phải sửa quote, hạ thành paraphrase có căn cứ, hoặc loại bỏ.

### REQ-QTE-003 — Paraphrase phải được nhận diện là paraphrase

Không đặt paraphrase trong ngoặc kép như thể là nguyên văn.

---

## 11.4. Phản chứng và độc lập nguồn

### REQ-CTR-001 — Research mode phải có counterevidence pass

Phải chủ động tìm ngoại lệ, witness khác, variant, nguồn cùng cấp xung đột hoặc
điều kiện giới hạn claim.

### REQ-CTR-002 — “Không có phản chứng” phải giới hạn theo phạm vi đã kiểm

Không được chuyển “không tìm thấy trong lần chạy này” thành “không tồn tại phản
chứng”.

### REQ-CTR-003 — Nhiều citation không tự động là nhiều nguồn độc lập

Hệ thống mục tiêu phải có khả năng phân biệt tối thiểu:

- independent;
- partially_dependent;
- same_source_family;
- derived_from;
- uncertain.

### REQ-CTR-004 — Counterevidence phải có thể làm claim bị sửa/hạ/reject

Counterevidence không chỉ là phần trang trí ở cuối answer.

---

## 11.5. Research Run

### REQ-RUN-001 — Research mode phải tạo Research Run Manifest

Manifest phải đủ để biết câu hỏi, thời điểm, mode, scope, commit repo chính,
repo/commit/root của locator khi dùng Connector, source revisions, queries,
evidence IDs, claim IDs, counterevidence status và limitations.

### REQ-RUN-002 — Phải phân biệt reproducibility truy xuất và reproducibility nghiên cứu

Có thể tái tạo retrieval không đồng nghĩa có thể tái tạo toàn bộ reasoning path.

### REQ-RUN-003 — Run phải ghi phần đã kiểm và phần chưa kiểm

Không được để người đọc hiểu phạm vi đã kiểm rộng hơn thực tế.

### REQ-RUN-004 — Run phải cho phép trả lời “claim X dựa vào evidence nào?”

Traceability claim → evidence là yêu cầu bắt buộc.

### REQ-RUN-005 — Run phải cho phép trả lời “đã tìm phản chứng chưa?”

Counterevidence pass phải có trạng thái có thể kiểm.

---

# 12. TƯƠNG LAI — chưa phải requirement v1

Deep Connector fallback, remote retrieval job hoặc GitHub Action để xử lý các
trường hợp locator hữu hạn không đủ chỉ là hướng **TƯƠNG LAI**. Chúng chưa có
mã requirement và không được triển khai như một phần v1 nếu chưa được chủ động
nâng thành MỤC TIÊU.

Nếu được xem xét sau này, worker từ xa chỉ được làm retrieval/test/sinh artefact
có provenance; không được trở thành “AI brain” bỏ qua Evidence/Claim gates.

# 13. Ngoài phạm vi v1 của lớp nâng cấp

Các hạng mục sau **không phải yêu cầu v1**:

- vector database;
- embeddings toàn corpus;
- knowledge graph toàn diện;
- Kubernetes;
- microservices;
- distributed database;
- autonomous multi-agent research;
- semantic search phổ quát;
- universal numeric confidence score.

Chúng chỉ được đưa vào requirement mới khi có nhu cầu và quyết định kiến trúc
riêng.

---

# 14. Quy tắc thay đổi requirement

Một requirement chỉ được sửa khi:

1. lý do thay đổi được ghi rõ;
2. tài liệu cấp dự án liên quan được đối chiếu;
3. acceptance criterion được cập nhật;
4. test/code/config/schema liên quan được xem xét;
5. nếu là quyết định kiến trúc lớn, ADR được tạo hoặc cập nhật.

Không được âm thầm đổi requirement chỉ để hợp thức hóa implementation hiện tại.
