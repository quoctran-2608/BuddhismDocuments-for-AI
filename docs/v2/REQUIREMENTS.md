# Buddhist Corpus Research 2.0 — Yêu cầu có mã

> Trạng thái tài liệu: **MỤC TIÊU**
>
> Vai trò: nguồn chuẩn cho các yêu cầu có mã **chỉ áp dụng cho chương trình nâng
> cấp Buddhist Corpus Research 2.0**.
>
> Đề bài sản phẩm nằm trong `docs/v2/PRD.md`; thiết kế nằm trong
> `docs/v2/DESIGN.md`; cách nghiệm thu từng yêu cầu nằm trong
> `docs/v2/ACCEPTANCE.md`.
>
> Các yêu cầu hiện hành của hệ 1.0 nằm riêng trong `docs/REQUIREMENTS.md`.

## 1. Cách đọc tài liệu

Tài liệu giữ nguyên các mã đã được dùng từ trước để không làm đứt lịch sử:

- `REQ-VER`: kiểm chứng bằng chứng và luận điểm;
- `REQ-QTE`: kiểm chứng câu trích;
- `REQ-CTR`: phản chứng và độc lập nguồn;
- `REQ-RUN`: hồ sơ lần nghiên cứu;
- `REQ-TST`: kiểm thử chất lượng nghiên cứu.

Toàn bộ yêu cầu trong file này đang là **MỤC TIÊU** cho tới khi có mã nguồn và
bằng chứng nghiệm thu tương ứng.

Một số tên trường và mã trạng thái được giữ bằng tiếng Anh vì chúng là hợp đồng
máy đọc. Ý nghĩa tiếng Việt được giải thích trong `docs/v2/DESIGN.md`.

---

## 2. Bản ghi bằng chứng và cửa kiểm

### REQ-VER-001 — Chỉ nguồn đã mở và đọc mới được tạo Bản ghi bằng chứng

Con trỏ, kết quả tìm kiếm chưa mở, tiêu đề, mục lục, dòng quan hệ, dòng cầu nối
hoặc ứng viên khám phá không tự động trở thành Bản ghi bằng chứng
(`Evidence Record`).

Quan hệ hoặc siêu dữ liệu chỉ có thể trở thành bằng chứng cho luận điểm về
**quan hệ** khi chính nguồn đó đã được mở, nguồn gốc được xác minh và loại bằng
chứng được ghi đúng. Chúng không được dùng như bằng chứng câu chữ cho luận điểm
về **văn bản**.

### REQ-VER-002 — Bản ghi bằng chứng phải đủ để truy ngược về nguồn

Bản ghi bằng chứng phải chứa các thông tin nguồn gốc cần thiết để truy ngược về
nguồn đã đọc, tối thiểu theo khả năng nguồn cung cấp:

- corpus;
- repository;
- source SHA và đường dẫn;
- vị trí tác phẩm/đoạn;
- ngôn ngữ;
- `evidence_class`;
- `text_role`;
- `witness` khi áp dụng;
- câu trích/ngữ cảnh khi dùng câu chữ;
- mã hồ sơ lần nghiên cứu trong chế độ Nghiên cứu.

Không bắt buộc một trường không tồn tại hoặc không áp dụng ở nguồn phải có giá
trị giả.

### REQ-VER-003 — Cửa kiểm bằng chứng phải xác minh vị trí nguồn

Trước khi một Bản ghi bằng chứng được dùng như bằng chứng đã xác minh, hệ thống
phải kiểm các thông tin có thể kiểm bằng máy, gồm repository, SHA/blob, đường
dẫn và vị trí đoạn khi áp dụng.

Sai nguồn, sai SHA, sai đường dẫn hoặc sai vị trí phải làm cửa kiểm thất bại.

---

## 3. Luận điểm và mức hỗ trợ

### REQ-VER-004 — Kết luận quan trọng phải được tách thành Luận điểm nguyên tử

Một kết luận quan trọng phải được tách thành luận điểm đủ nhỏ để có thể:

- nối với bằng chứng;
- đánh giá mức hỗ trợ;
- tìm phản chứng;
- chấp nhận, sửa, hạ mức hoặc loại độc lập.

Không được coi một đoạn tổng hợp dài có vài trích dẫn ở cuối là đã kiểm chứng
từng kết luận trong đoạn.

### REQ-VER-005 — Luận điểm phải nối được tới bằng chứng hỗ trợ

Luận điểm không có bằng chứng phù hợp không được trở thành kết luận được chấp
nhận.

### REQ-VER-006 — Mức hỗ trợ phải dùng thang định tính đã định nghĩa

Tối thiểu phải có:

- `DIRECT` — hỗ trợ trực tiếp;
- `STRONG` — hỗ trợ mạnh;
- `WEAK` — hỗ trợ yếu/có giới hạn;
- `UNSUPPORTED` — chưa đủ bằng chứng;
- `CONTRADICTED` — bị bằng chứng phản bác đáng kể.

Không thay thang này bằng một tỷ lệ phần trăm giả như thể đó là xác suất chân lý
đã được hiệu chuẩn.

### REQ-VER-007 — Luận điểm `UNSUPPORTED` không được vào kết luận cuối

Không được chỉ làm mềm câu chữ bằng “có lẽ”, “dường như” để đưa một luận điểm
chưa đủ bằng chứng vào tập luận điểm được chấp nhận.

### REQ-VER-008 — Luận điểm `CONTRADICTED` không được trình bày như sự thật đã xác lập

Nếu còn cần nhắc tới, phải trình bày đúng là luận điểm đang bị phản bác hoặc
xung đột trong phạm vi bằng chứng đã kiểm.

### REQ-VER-009 — Điểm truy xuất và mức hỗ trợ luận điểm phải tách riêng

Điểm/xếp hạng của hệ truy xuất chỉ dùng để ưu tiên mở ứng viên. Không được dùng
trực tiếp làm mức `DIRECT`, `STRONG` hoặc `WEAK`.

### REQ-VER-010 — Phần tổng hợp chỉ được dùng tập luận điểm đã được chấp nhận

Phần tổng hợp cuối không được tự sinh thêm một kết luận quan trọng chưa đi qua
cửa kiểm luận điểm.

### REQ-VER-011 — Mỗi luận điểm quan trọng phải khai báo loại luận điểm

Tối thiểu hỗ trợ các loại:

- `textual` — văn bản nói gì;
- `historical` — mệnh đề lịch sử;
- `relationship` — quan hệ/song hành/căn chỉnh;
- `comparative` — so sánh nhiều nhân chứng/truyền thống;
- `interpretive` — diễn giải;
- `empirical` — mệnh đề thực nghiệm;
- `metaphysical` — mệnh đề siêu hình.

Loại luận điểm phải được dùng để chặn việc lấy sai loại bằng chứng làm căn cứ.
Một văn bản nói X không tự chứng minh X là sự thật lịch sử, thực nghiệm hoặc
siêu hình.

### REQ-VER-012 — Trạng thái công bố của luận điểm phải do cửa kiểm quyết định

Luận điểm mới chỉ được tạo ở trạng thái đang kiểm (`candidate`).

AI hoặc chương trình gọi không được tự gán `accepted` để bỏ qua kiểm chứng.
Trạng thái `accepted` phải là kết quả của Cửa kiểm luận điểm cuối sau khi các
điều kiện bắt buộc đã đạt.

### REQ-VER-013 — Sửa luận điểm phải giữ lịch sử thay thế

Khi một luận điểm bị phản chứng, thu hẹp hoặc viết lại, không được sửa đè làm
mất bản cũ.

Bản mới phải truy được tối thiểu:

- luận điểm cũ mà nó thay thế;
- lý do sửa;
- bằng chứng hoặc phản chứng dẫn tới thay đổi.

Dữ liệu có thể dùng trường như `supersedes_claim_id` và
`revision_reason`; tên trường cuối cùng do thiết kế triển khai quyết định.

### REQ-VER-014 — Không đủ căn cứ phải giữ trạng thái “chưa xác định”

Khi chưa có bằng chứng đủ để xác định một thông tin, hệ thống phải giữ trạng thái
chưa xác định/chưa kiểm/không chắc thay vì tự suy đoán cho đủ dữ liệu.

Yêu cầu này áp dụng đặc biệt cho:

- mức độc lập giữa nguồn;
- quan hệ nhân chứng;
- tác giả, niên đại, người dịch khi nguồn không xác nhận;
- tương đương đa ngôn ngữ;
- các trường phân loại mà dữ liệu chưa đủ.

---

## 4. Kiểm chứng câu trích

### REQ-QTE-001 — Câu trích phải có trạng thái kiểm chứng

Hệ thống phải phân biệt tối thiểu:

- `VERIFIED_EXACT` — khớp nguyên văn;
- `VERIFIED_NORMALIZED` — khớp sau chuẩn hóa không làm đổi nội dung;
- `PARAPHRASE` — diễn đạt lại có căn cứ;
- `UNVERIFIED` — chưa đủ điều kiện kiểm;
- `QUOTE_MISMATCH` — không khớp nguồn.

### REQ-QTE-002 — `QUOTE_MISMATCH` không được xuất như câu trích trực tiếp

Nếu câu trích không khớp nguồn, phải sửa cho đúng, chuyển thành diễn đạt lại có
căn cứ hoặc loại bỏ.

### REQ-QTE-003 — Diễn đạt lại phải được nhận diện là diễn đạt lại

`PARAPHRASE` không được đặt trong ngoặc kép hoặc trình bày như nguyên văn.

---

## 5. Phản chứng và độc lập nguồn

### REQ-CTR-001 — Chế độ Nghiên cứu phải chủ động tìm phản chứng

Với luận điểm quan trọng, hệ thống phải tìm các nhóm phù hợp như:

- ngoại lệ;
- nhân chứng khác;
- dị bản;
- song hành không khớp;
- nguồn cùng tầng nhưng xung đột;
- quan hệ phụ thuộc làm yếu tuyên bố “nhiều nguồn”;
- điều kiện giới hạn phạm vi.

### REQ-CTR-002 — “Không tìm thấy phản chứng” phải gắn với phạm vi đã kiểm

Chỉ được kết luận rằng chưa tìm thấy phản chứng trong corpus, truy vấn và phạm
vi đã kiểm. Không được suy thành “không tồn tại phản chứng”.

### REQ-CTR-003 — Nhiều trích dẫn không tự động là nhiều nguồn độc lập

Hệ thống phải biểu diễn được tối thiểu:

- `independent` — độc lập;
- `partially_dependent` — phụ thuộc một phần;
- `same_source_family` — cùng họ nguồn;
- `derived_from` — dẫn xuất từ nguồn khác;
- `uncertain` — chưa xác định.

Khi chưa biết, phải dùng `uncertain`, không tự nâng thành `independent`.

### REQ-CTR-004 — Phản chứng phải có khả năng thay đổi kết quả của luận điểm

Phản chứng không được chỉ là phần trang trí trong câu trả lời. Nó phải có thể
làm luận điểm:

- giữ nguyên có giải thích;
- viết lại;
- thu hẹp;
- hạ mức hỗ trợ;
- chuyển `UNSUPPORTED`;
- chuyển `CONTRADICTED`;
- bị loại;
- hoặc được thay bằng luận điểm mới có lịch sử sửa đổi.

---

## 6. Hồ sơ lần nghiên cứu

### REQ-RUN-001 — Chế độ Nghiên cứu phải tạo Hồ sơ lần nghiên cứu

Hồ sơ phải đủ để biết tối thiểu:

- câu hỏi và thời điểm;
- chế độ và phạm vi;
- commit của repository chính;
- repository/commit/root của locator khi dùng Connector;
- phiên bản các nguồn;
- truy vấn và giả thuyết tìm kiếm;
- mã bằng chứng;
- mã luận điểm;
- trạng thái tìm phản chứng;
- giới hạn.

Thiếu các thông tin nguồn gốc bắt buộc trong chế độ Nghiên cứu phải làm hồ sơ
không đạt nghiệm thu.

### REQ-RUN-002 — Phải phân biệt tái lập truy xuất và tái lập nghiên cứu

Tái lập truy xuất là khả năng lấy lại nền ứng viên/bằng chứng chính từ cùng
phiên bản nguồn và truy vấn.

Tái lập nghiên cứu là khả năng biết nguồn nào đã mở, luận điểm nào đã tạo, bằng
chứng nào ủng hộ/phản bác và luận điểm nào bị loại hoặc thay thế.

Không đặt mục tiêu tái tạo chuỗi suy nghĩ nội bộ của mô hình.

### REQ-RUN-003 — Hồ sơ phải ghi phạm vi đã kiểm và chưa kiểm

Không được để người đọc hiểu phạm vi đã khảo sát rộng hơn thực tế.

### REQ-RUN-004 — Hồ sơ phải trả lời được “luận điểm này dựa vào bằng chứng nào?”

Quan hệ luận điểm → bằng chứng phải truy ngược được bằng dữ liệu máy đọc.

### REQ-RUN-005 — Hồ sơ phải trả lời được “đã tìm phản chứng chưa?”

Trạng thái tìm phản chứng phải được lưu và có thể kiểm.

### REQ-RUN-006 — Hồ sơ đã chốt không được sửa đè âm thầm

Hồ sơ ở trạng thái đã chốt (`finalized`) không được thay đổi như thể lịch sử
cũ chưa từng tồn tại.

Nếu bằng chứng mới làm thay đổi kết quả, phải tạo hồ sơ mới hoặc bản sửa mới có
quan hệ truy ngược về hồ sơ trước và lý do thay đổi, ví dụ
`supersedes_run_id` + `revision_reason`.

---

## 7. Kiểm thử chất lượng nghiên cứu

### REQ-TST-001 — Bộ kiểm thử nghiên cứu chuẩn phải chạy được trên mọi môi trường

Các mẫu kiểm thử chuẩn phải nằm trong repository hoặc trong một nguồn kiểm thử
được ghim, không phụ thuộc đường dẫn cá nhân của một máy.

Bộ tối thiểu phải bao phủ 11 lỗi:

1. câu trích đổi một từ;
2. source SHA sai;
3. đoạn nguồn sai;
4. chú thích bản dịch giả làm văn bản gốc;
5. siêu dữ liệu song hành giả làm bằng chứng câu chữ;
6. hai nguồn phụ thuộc giả làm hai nhân chứng độc lập;
7. luận điểm mạnh hơn bằng chứng;
8. luận điểm lịch sử/thực nghiệm/siêu hình dùng sai loại bằng chứng;
9. chế độ Nghiên cứu bỏ tìm phản chứng;
10. tự tạo tương đương Pāli ↔ Hán không có bằng chứng repository;
11. phần tổng hợp sinh luận điểm mới chưa qua cửa kiểm.

### REQ-TST-002 — Lỗi nghiên cứu nghiêm trọng đã sửa phải trở thành kiểm thử hồi quy

Khi một lỗi nghiên cứu thật từng lọt qua hệ thống và đã được sửa, phải bổ sung
một bài kiểm thử để bảo đảm lỗi đó không quay trở lại.

**Kiểm thử hồi quy** là bài kiểm tra được giữ lại lâu dài nhằm phát hiện việc một
lỗi cũ xuất hiện trở lại sau thay đổi mã nguồn.

---

## 8. Hướng TƯƠNG LAI — chưa phải yêu cầu 2.0 phiên bản đầu

Đường truy xuất Connector sâu, tác vụ truy xuất từ xa hoặc cơ chế riêng cho tìm
Hán văn tùy ý chỉ là **TƯƠNG LAI**.

Nếu được xem xét sau này, tác vụ từ xa chỉ được làm truy xuất, kiểm thử hoặc sinh
tệp kết quả có nguồn gốc. Nó không được trở thành “AI suy luận” bỏ qua các cửa
kiểm.

Không cấp mã yêu cầu cho hạng mục TƯƠNG LAI cho tới khi nó được chủ động nâng
thành MỤC TIÊU.

## 9. Ngoài phạm vi 2.0 phiên bản đầu

Không đưa vào chỉ vì kiến trúc trông hiện đại hơn:

- cơ sở dữ liệu véc-tơ mới;
- embedding toàn corpus;
- đồ thị tri thức toàn diện;
- Kubernetes;
- microservices;
- cơ sở dữ liệu phân tán;
- hệ nhiều tác nhân tự hành;
- tìm kiếm ngữ nghĩa phổ quát;
- một điểm tin cậy phần trăm giả như xác suất chân lý;
- kho dữ liệu đám mây mới chỉ để phục vụ lớp kiểm chứng.

## 10. Quy tắc thay đổi yêu cầu 2.0

Một yêu cầu chỉ được sửa khi:

1. lý do thay đổi được ghi rõ;
2. PRD và Design 2.0 liên quan được đối chiếu;
3. tiêu chí nghiệm thu tương ứng được cập nhật;
4. mã nguồn/cấu hình/schema/kiểm thử liên quan được xem xét;
5. nếu là quyết định kiến trúc bền vững, ADR được tạo hoặc cập nhật.

Không được âm thầm sửa yêu cầu để hợp thức hóa cách triển khai đang có.
