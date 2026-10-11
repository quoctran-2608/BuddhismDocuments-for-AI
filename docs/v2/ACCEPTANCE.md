# Buddhist Corpus Research 2.0 — Tiêu chí nghiệm thu

> Trạng thái tài liệu: **MỤC TIÊU**
>
> Vai trò: quy định cách chứng minh từng yêu cầu trong
> `docs/v2/REQUIREMENTS.md` đã thật sự được triển khai.
>
> Toàn bộ 2.0 hiện đang **CHƯA TRIỂN KHAI ĐẦY ĐỦ**. Có tài liệu thiết kế không
> đồng nghĩa yêu cầu đã đạt.
>
> Nghiệm thu hệ hiện hành nằm riêng trong `docs/ACCEPTANCE.md`.

## 1. Nguyên tắc nghiệm thu

Mỗi yêu cầu 2.0 chỉ được chuyển từ **MỤC TIÊU** sang **HIỆN HÀNH** khi có đủ bằng
chứng phù hợp.

Các mức bằng chứng có thể dùng:

- **TỰ ĐỘNG**: có bài kiểm thử chạy bằng máy;
- **CẤU TRÚC**: có thể kiểm bằng lược đồ dữ liệu, định dạng, cấu hình hoặc mã;
- **TÍCH HỢP**: có kiểm thử qua nhiều lớp của hệ thống;
- **NGHIÊN CỨU CHUẨN**: có tình huống nghiên cứu cố định kiểm hành vi học thuật;
- **RÀ SOÁT**: cần kiểm thủ công có chủ đích cho phần chưa thể tự động hoàn toàn.

Không được chuyển trạng thái chỉ vì đã có lớp, hàm hoặc trường dữ liệu mang đúng
tên.

### Bằng chứng triển khai Giai đoạn A — 11/10/2026

`tools/corpus_research/verification.py` đã có lõi Bản ghi bằng chứng, Cửa kiểm
bằng chứng và năm trạng thái kiểm câu trích. `tests/test_verification.py` có
44 bài kiểm thử độc lập với 13 submodule: giữ 32 phương thức ban đầu và bổ sung
12 phương thức về ranh giới tin cậy. Có tích hợp `retrieval.evidence()` trên
SQLite nhỏ, đọc blob Git thật ghim trong repo tạm và kiểm dữ liệu JSON kiểu
GitHub với cùng lõi. Mẫu thử nhỏ là dữ liệu phần mềm, không phải chứng cứ corpus.

Sau rà soát, `opened_source` và `paraphrase_review` đều là dữ liệu chưa tin cậy.
`source_contract` phải lấy từ config/manifest do ứng dụng kiểm soát, không từ
ứng viên. `source_reader(request)` là khả năng thực thi do ứng dụng cấu hình
riêng: nhận định danh kho/commit/path và bộ chọn work/segment/sequence, tự đọc
đúng phiên bản đã ghim, giải vị trí/vai trò/nhân chứng và phạm vi từ chính nguồn.
Cửa kiểm đối chiếu nội dung đầy đủ, định danh, vị trí và phạm vi với lần đọc độc
lập này. SHA blob tự tính chỉ kiểm tính nhất quán của byte; mã băm hay các trường
tự khai khớp nhau không chứng minh quan hệ commit/path → blob. Chính cấu hình
nguồn và lần đọc độc lập thiết lập quan hệ đó. Git cục bộ vẫn dùng `rev-parse`
và `cat-file`, không đọc nội dung working tree thay cho blob ghim.

Ứng dụng nối `read_local_source()` và bộ giải vị trí theo định dạng nguồn bên
trong `source_reader`; callback không được chỉ trả lại `opened_source`. Phần
giải vị trí 13 nguồn và tích hợp CLI chưa được bổ sung trong lát cắt này. Tệp
đã đọc đưa vào dưới dạng JSON, kể cả JSON do adapter Git từng trả ra, không tự
mang quyền xác minh. Con trỏ chưa mở vẫn là `CANDIDATE`; có nội dung mà thiếu
khả năng đọc độc lập giữ `UNVERIFIED`; đủ nguồn độc lập và các phép kiểm khác
mới đạt `VERIFIED`. Mâu thuẫn với căn cứ độc lập bị `REJECTED`.

`paraphrase_review` là đề xuất, nay cần thêm `review_id`. Khả năng thực thi
`review_reader(review_id)` do ứng dụng nối vào kênh người kiểm/phê duyệt đã xác
thực, trả bản đánh giá đã được chấp thuận gồm `review_id`, `quotation`,
`source_text`, `supported`, `reviewer`, `rationale`. Callback chỉ nhận mã tra
cứu, không nhận nội dung đề xuất để tự xác nhận. Tất cả trường trên phải khớp
chính xác, gồm kiểu boolean và người kiểm. Thay câu diễn đạt lại, văn bản nguồn
cần kiểm hoặc danh tính người kiểm làm đánh giá cũ mất hiệu lực. Thiếu đánh giá
đã xác thực giữ `UNVERIFIED`; đánh giá hợp lệ đồng ý trả `PARAPHRASE`, phản đối
trả `QUOTE_MISMATCH`. Diễn đạt lại luôn không có quyền trích nguyên văn. Máy
không tự xét đúng sai ngữ nghĩa; chưa có kênh phê duyệt thật tích hợp sẵn.

Hai callback nằm ngoài dữ liệu JSON, không được chọn bởi JSON hoặc mã do AI
sinh từ đề xuất. Các cờ `trusted`, `verified`, `attested`, `approved` không cấp
quyền; tệp JSON đánh giá tự tạo không phải kênh phê duyệt đã xác thực. Lõi không
thực hiện I/O trực tiếp và không bắt buộc SQLite/shell; callback tùy môi trường
có thể thực hiện I/O. Dữ liệu đầu vào/đầu ra vẫn chuyển được sang JSON. Thay đổi
tương thích có chủ ý: lời gọi cũ chỉ truyền dữ liệu sẽ giữ `UNVERIFIED`, dù
trước đây các trường tự khai khớp nhau đã cho qua. Các kỳ vọng thiếu an toàn ở
kiểm thử nguồn JSON, diễn đạt lại và tiến trình cô lập đã được siết lại; các
trường hợp hợp lệ dùng căn cứ độc lập do host kiểm thử cấu hình.

`VERIFIED` chỉ xác nhận nguồn/vị trí và phép kiểm câu trích áp dụng. Nó không
cấp mức hỗ trợ luận điểm, không xác nhận kết luận học thuật và không nâng
`computational_segmented` hoặc `parallel_alignment` thành nhân chứng chính.
`evidence_class`, `text_role`, `witness` được giữ riêng. Chưa có lớp luận điểm.

Kết quả Windows/Python 3.14: 44/44 bài A đạt (mốc trước 32/32). Baseline 1.0
chạy 36 bài với 29 lỗi, chặn 9 bài acceptance ở `setUpClass`; mốc A trước chạy
68 bài với 29 lỗi; sau rà soát chạy 80 bài với cùng 29 lỗi. Đối chiếu danh sách
`ERROR:` không có chênh lệch. Nhóm lỗi vẫn là thiếu submodule/tệp/Git object và
khóa SQLite khi dọn thư mục tạm. Không sửa hoặc bỏ qua lỗi 1.0; toàn suite chưa
xanh. Chưa xác nhận trên checkout đủ nguồn, phiên Work thật hoặc GitHub plugin
thật. Chưa có adapter remote xác minh phiên bản tích hợp: chỉ dữ liệu plugin
tự khai phải giữ `UNVERIFIED`; chỉ host đã nối công cụ đọc đúng phiên bản mới
có thể cung cấp khả năng tương đương đường Git cho cùng lõi.

Các mục A dưới đây ghi **đã có lõi, chờ nghiệm thu**, không chuyển toàn bộ yêu
cầu sang HIỆN HÀNH. Giai đoạn B–E vẫn chưa triển khai.

---

## 2. Ma trận nghiệm thu 31 yêu cầu

| Yêu cầu | Trạng thái hiện tại | Bằng chứng tối thiểu cần có |
|---|---|---|
| REQ-VER-001 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động: con trỏ/kết quả chưa mở không tạo được Bản ghi bằng chứng; siêu dữ liệu quan hệ chỉ được dùng đúng loại luận điểm |
| REQ-VER-002 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động + cấu trúc: thiếu nguồn gốc bắt buộc bị từ chối; trường không áp dụng được phép để trống, không tạo dữ liệu giả |
| REQ-VER-003 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động: sai kho nguồn/SHA/đường dẫn/đoạn làm Cửa kiểm bằng chứng thất bại |
| REQ-VER-004 | CHƯA TRIỂN KHAI | Nghiên cứu chuẩn: kết luận phức hợp phải được tách thành các luận điểm có thể kiểm độc lập |
| REQ-VER-005 | CHƯA TRIỂN KHAI | Tự động: luận điểm thiếu bằng chứng hỗ trợ không thể được chấp nhận |
| REQ-VER-006 | CHƯA TRIỂN KHAI | Cấu trúc + tự động: chỉ chấp nhận các mức DIRECT/STRONG/WEAK/UNSUPPORTED/CONTRADICTED đã định nghĩa |
| REQ-VER-007 | CHƯA TRIỂN KHAI | Tự động + nghiên cứu chuẩn: UNSUPPORTED không qua Cửa kiểm luận điểm cuối |
| REQ-VER-008 | CHƯA TRIỂN KHAI | Tự động + nghiên cứu chuẩn: CONTRADICTED không được xuất như kết luận đã xác lập |
| REQ-VER-009 | CHƯA TRIỂN KHAI | Tự động: thay đổi điểm truy xuất không tự thay đổi mức hỗ trợ của luận điểm |
| REQ-VER-010 | CHƯA TRIỂN KHAI | Nghiên cứu chuẩn: phần tổng hợp sinh luận điểm mới ngoài tập đã chấp nhận phải thất bại kiểm tra cuối |
| REQ-VER-011 | CHƯA TRIỂN KHAI | Tự động + nghiên cứu chuẩn: thiếu loại luận điểm bị từ chối; dùng sai loại bằng chứng không được nâng mức hỗ trợ |
| REQ-VER-012 | CHƯA TRIỂN KHAI | Tự động: AI hoặc chương trình gọi không thể tự ghi trạng thái `accepted`; chỉ Cửa kiểm luận điểm cuối được cấp trạng thái này |
| REQ-VER-013 | CHƯA TRIỂN KHAI | Tự động: sửa luận điểm tạo lịch sử thay thế, giữ bản cũ, lý do sửa và phản chứng liên quan |
| REQ-VER-014 | MỘT PHẦN: DỮ LIỆU A | Tự động + nghiên cứu chuẩn: thông tin chưa đủ căn cứ phải giữ trạng thái chưa xác định/chưa kiểm/không chắc; không tự suy đoán thành giá trị xác định |
| REQ-QTE-001 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Tự động: phân loại đúng các trạng thái khớp nguyên văn, khớp sau chuẩn hóa, diễn đạt lại, chưa kiểm và không khớp |
| REQ-QTE-002 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: câu trích sai một từ không được xuất như nguyên văn |
| REQ-QTE-003 | ĐÃ CÓ LÕI A; CHỜ NGHIỆM THU | Nghiên cứu chuẩn: diễn đạt lại không được trình bày như câu trích trực tiếp |
| REQ-CTR-001 | CHƯA TRIỂN KHAI | Tích hợp: chế độ Nghiên cứu thiếu bước tìm phản chứng phải không đạt |
| REQ-CTR-002 | CHƯA TRIỂN KHAI | Nghiên cứu chuẩn: “không tìm thấy phản chứng” phải kèm corpus/truy vấn/phạm vi đã kiểm |
| REQ-CTR-003 | CHƯA TRIỂN KHAI | Nghiên cứu chuẩn: nguồn phụ thuộc không được tính như xác nhận độc lập; chưa rõ phải giữ uncertain |
| REQ-CTR-004 | CHƯA TRIỂN KHAI | Tích hợp: phản chứng có thể làm luận điểm bị thu hẹp/hạ mức/loại/thay thế |
| REQ-RUN-001 | CHƯA TRIỂN KHAI | Tự động: chế độ Nghiên cứu thiếu commit kho chính, kho/commit/thư mục gốc của locator, phiên bản nguồn hoặc trường bắt buộc phải không đạt |
| REQ-RUN-002 | CHƯA TRIỂN KHAI | Cấu trúc: dữ liệu tách được tái lập truy xuất và tái lập nghiên cứu; không yêu cầu lưu chuỗi suy nghĩ nội bộ |
| REQ-RUN-003 | CHƯA TRIỂN KHAI | Tự động + nghiên cứu chuẩn: hồ sơ phải có phạm vi đã kiểm/chưa kiểm và câu trả lời không được mở rộng quá phạm vi |
| REQ-RUN-004 | CHƯA TRIỂN KHAI | Tự động: từ mã luận điểm truy ra được toàn bộ mã bằng chứng liên quan |
| REQ-RUN-005 | CHƯA TRIỂN KHAI | Tự động: trạng thái tìm phản chứng và tóm tắt kết quả có thể truy vấn |
| REQ-RUN-006 | CHƯA TRIỂN KHAI | Tự động: hồ sơ đã chốt (`finalized`) không được sửa đè; thay đổi phải tạo bản mới có quan hệ thay thế và lý do |
| REQ-TST-001 | CHƯA TRIỂN KHAI | Tự động: 11 mẫu nghiên cứu chuẩn nằm trong repo/nguồn ghim và chạy được trên môi trường sạch, không phụ thuộc đường dẫn cá nhân |
| REQ-TST-002 | CHƯA TRIỂN KHAI | Quy trình + tự động: mỗi sự cố nghiên cứu nghiêm trọng đã sửa có bài kiểm thử hồi quy tương ứng |
| REQ-ENV-001 | MỘT PHẦN: LÕI A; CHƯA THỬ WORK | Tự động + tích hợp: lõi kiểm chứng nhận/trả dữ liệu JSON tương đương trên Codex và ChatGPT Work; không yêu cầu SQLite, shell hay đường dẫn tuyệt đối để hiểu đúng trạng thái |
| REQ-ENV-002 | MỘT PHẦN: GIẢ LẬP; CHƯA THỬ PLUGIN | Tích hợp + rà soát: cùng một mẫu bằng chứng từ GitHub có thể đi qua đường plugin khi đủ dữ liệu; thiếu phép kiểm bắt buộc phải trả chưa xác minh và đóng khi thiếu dữ liệu |

---

## 3. Bộ kiểm thử nghiên cứu chuẩn

Mỗi tình huống chuẩn phải có tối thiểu:

- câu hỏi;
- phạm vi được phép;
- bằng chứng mong đợi;
- nguồn không được dùng như bằng chứng chính;
- phản chứng đã biết;
- luận điểm bị cấm;
- mẫu luận điểm được chấp nhận/bị loại;
- giới hạn bắt buộc phải xuất.

Bộ tối thiểu gồm 11 trường hợp:

1. **Câu trích đổi một từ** — phải phát hiện không khớp.
2. **Sai SHA nguồn** — Bản ghi bằng chứng phải bị từ chối.
3. **Sai đoạn nguồn** — vị trí không hợp lệ phải làm cửa kiểm thất bại.
4. **Chú thích giả làm văn bản gốc** — phải chặn sai vai trò văn bản.
5. **Siêu dữ liệu song hành giả làm bằng chứng câu chữ** — phải chặn.
6. **Hai nguồn phụ thuộc giả làm hai nhân chứng độc lập** — phải nhận ra quan hệ phụ thuộc.
7. **Luận điểm mạnh hơn bằng chứng** — phải thu hẹp, hạ mức hoặc loại.
8. **Sai loại bằng chứng** — luận điểm lịch sử/thực nghiệm/siêu hình không được xác nhận chỉ vì văn bản nói như vậy.
9. **Bỏ tìm phản chứng** — chế độ Nghiên cứu phải không đạt.
10. **Tự tạo tương đương Pāli ↔ Hán** — không có bằng chứng trong kho nguồn thì không được xác lập.
11. **Phần tổng hợp sinh luận điểm mới** — luận điểm chưa qua cửa kiểm phải bị phát hiện.

Các mẫu phải nhỏ, ổn định và có thể chạy trên mọi máy. Không dùng một đường dẫn
cá nhân làm điều kiện để bài kiểm thử quan trọng được chạy.

---

## 4. Kiểm thử hồi quy từ sự cố thật

Một **sự cố toàn vẹn nghiên cứu** là trường hợp hệ thống từng cho một kết luận,
câu trích, quan hệ nguồn hoặc trạng thái nghiên cứu sai lọt qua các cửa kiểm.

Khi sửa một sự cố như vậy:

```text
sự cố thật
→ xác định nguyên nhân
→ sửa mã/quy tắc
→ thêm kiểm thử hồi quy
→ giữ kiểm thử lâu dài
```

Không cần tạo thủ tục hành chính nặng. Mục tiêu duy nhất là biến lỗi đã biết
thành thứ hệ thống không được phép lặp lại.

---

## 5. Điều kiện chuyển một yêu cầu 2.0 sang HIỆN HÀNH

Một yêu cầu chỉ được chuyển trạng thái khi:

1. có triển khai thực;
2. hợp đồng dữ liệu/định dạng liên quan đã được chốt nếu cần;
3. có bài kiểm thử phù hợp;
4. có tình huống nghiên cứu chuẩn nếu yêu cầu liên quan hành vi nghiên cứu;
5. không làm hồi quy truy xuất/Connector hiện hành;
6. `docs/v2/REQUIREMENTS.md` và file này được cập nhật;
7. tài liệu cấp toàn dự án được cập nhật nếu trạng thái thực tế thay đổi.

Không chuyển trạng thái vì có mã khung, bản mô phỏng hoặc tài liệu.

## 6. Điều kiện nghiệm thu toàn bộ 2.0 phiên bản đầu

Chỉ coi 2.0 phiên bản đầu hoàn thành khi tối thiểu:

- 31 yêu cầu trong tài liệu này đã có bằng chứng nghiệm thu phù hợp;
- truy xuất và CLI hiện hành không hồi quy;
- locator chính thức vẫn tất định;
- Connector vẫn mở nguồn gốc bên ngoài đã ghim;
- con trỏ vẫn không phải bằng chứng;
- Bản ghi bằng chứng truy nguyên được;
- câu trích sai bị phát hiện;
- luận điểm không bằng chứng bị chặn;
- trạng thái `accepted` chỉ do cửa kiểm cấp;
- lịch sử sửa luận điểm được giữ;
- `UNSUPPORTED`/`CONTRADICTED` không lọt vào kết luận như sự thật;
- chế độ Nghiên cứu thực hiện tìm phản chứng;
- độc lập/phụ thuộc nguồn được biểu diễn;
- Hồ sơ lần nghiên cứu truy nguyên được;
- hồ sơ đã chốt không bị sửa đè;
- biết phạm vi đã kiểm/chưa kiểm;
- 11 tình huống nghiên cứu chuẩn chạy ổn định;
- sự cố nghiên cứu đã sửa có kiểm thử hồi quy;
- lõi kiểm chứng dùng cùng hợp đồng dữ liệu trên Codex và ChatGPT Work;
- đường GitHub plugin không bị thiết kế chặn và đóng khi thiếu khả năng xác minh;
- khi thiếu dữ liệu, hệ thống vẫn đóng và nêu giới hạn.

Đây là tiêu chí **MỤC TIÊU**, không phải tuyên bố trạng thái hiện tại.
