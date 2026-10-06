# Luật nghiên cứu corpus Phật học cho AI

> Trạng thái: **HIỆN HÀNH**
>
> Vai trò: bộ luật nghiên cứu cấp cao nhất áp dụng cho mọi tác nhân AI và mọi
> nhiệm vụ nghiên cứu trong repository này.
>
> Cách vận hành cụ thể xem `.codex/skills/buddhist-corpus-research/SKILL.md`;
> kiến trúc xem `docs/ARCHITECTURE.md`; giao thức Connector xem
> `docs/REMOTE_AGENT.md`.

## 1. Luật trung tâm

> **Kiến thức sẵn có của mô hình có thể đề xuất giả thuyết tìm kiếm; chỉ bằng
> chứng trong repository mới được phép xác lập kết luận nghiên cứu.**

Kiến thức mô hình không được âm thầm trở thành “nguồn thứ 14”.

## 2. Hai chế độ thực thi

### 2.1. Local mode — offline nghiêm ngặt

Build, lập chỉ mục, nghiên cứu bằng CLI và công việc Codex bên trong checkout
phải hoạt động offline nghiêm ngặt.

Không được:

- dùng Web Search, trình duyệt, `curl`, `wget`, API mạng hoặc nguồn học thuật từ
  xa để lấp khoảng trống corpus;
- chạy `git fetch`, `git pull`, `git clone`, `git submodule update` hoặc lệnh nào
  tải thêm dữ liệu nghiên cứu từ xa;
- dùng GitHub API thay cho source data cục bộ;
- tải model, package, dictionary hoặc corpus để bổ sung bằng chứng.

Chỉ dùng file đã có trong checkout và công cụ chuẩn đã cài đặt.

Nếu submodule, Git object, LFS object hoặc source file cần thiết bị thiếu, dừng
nhánh nghiên cứu đó và báo:

**không đủ dữ liệu trong corpus hiện tại**

### 2.2. GitHub Connector mode — đường đọc từ xa đã khai báo

Một phiên ChatGPT/GitHub Connector không có SQLite local được phép dùng đường
Connector đã được tài liệu hóa. Đây là ngoại lệ đọc dữ liệu nghiên cứu có kiểm
soát, không phải giấy phép duyệt web công khai.

AI chỉ được đọc:

1. repository chính `quoctran-2608/BuddhismDocuments-for-AI`;
2. repository locator được `config/remote-corpus.json` khai báo;
3. repository nguồn gốc mà pointer chỉ tới, đúng `source_sha` hoặc
   `source_blob_sha` đã ghim.

Trong Connector mode:

- đọc `.codex/skills/buddhist-corpus-research/SKILL.md` và
  `config/remote-corpus.json` trước;
- dùng production locator thay vì GitHub Code Search để định tuyến;
- coi locator row là pointer ứng viên, không phải bằng chứng câu chữ;
- mở pinned upstream source và đọc ngữ cảnh liên quan trước khi kết luận;
- không dùng Web Search chung hoặc internet không liên quan làm corpus evidence;
- nếu production locator không đủ để xác lập claim, báo:
  **không đủ dữ liệu trong remote corpus export hiện tại**.

Ngoại lệ Connector không cho phép sửa pinned source repository hoặc thay dữ liệu
corpus bị thiếu bằng nội dung internet.

## 3. Tầng nguồn bất biến

Mười ba source repository/submodule là nguồn gốc bất biến trong phạm vi nghiên
cứu.

- Không sửa, chuẩn hóa, format, tái sinh hoặc commit vào source repository như
  một phần của nghiên cứu.
- Parser, index, cache, report và artefact dẫn xuất phải nằm ngoài source.
- Artefact dẫn xuất phải có thể tái tạo từ các commit nguồn đã ghim.
- Database lớn sinh ra phải nằm dưới `derived/` và không phải nguồn chuẩn của
  câu chữ.

Trong local mode, trước khi nghiên cứu chạy:

```bash
bin/buddhist-corpus status
```

Nguồn bị thiếu hoặc SHA không khớp phải được coi là lỗi provenance.

## 4. Phân cấp bằng chứng

Ưu tiên nhân chứng mạnh nhất hiện có. Nguồn phục vụ khám phá không được âm thầm
thay thế nhân chứng chính.

1. **Bản văn gốc/canonical/root có nhân chứng xác định** — ví dụ SuttaCentral
   Bilara roots và các nhân chứng Pāli riêng biệt.
2. **Ấn bản có cấu trúc, thẩm quyền cao** — ví dụ CBETA TEI P5 và 84000 TEI.
3. **Metadata/quan hệ** — ví dụ SuttaCentral parallels, 84000 RDF/Toh. metadata.
   Chúng chứng minh quan hệ, không tự chứng minh câu chữ.
4. **Corpus song hành/căn chỉnh** — 84000 Translation Memory và OpenPecha. Dùng
   cho bằng chứng căn chỉnh và khám phá; khi có thể phải kiểm wording ở source
   edition phù hợp.
5. **Corpus phân đoạn bằng tính toán** — BuddhaNexus. Dùng để tìm ứng viên; khi
   có nhân chứng mạnh hơn phải quay lại CBETA, SuttaCentral hoặc nguồn phù hợp.
6. **Dữ liệu khảo dị/lemma dẫn xuất** — `third-party/pali-canon`. Dùng lemma,
   morphology, collation và variant data như phân tích dẫn xuất; phải nêu base
   witnesses và không trình bày reconstructed/selected reading như primary
   witness không điều kiện.
7. **Nguồn tham khảo phụ trợ** — PTS archive và các export nhiễu tương tự; phải
   nêu giới hạn chất lượng đã biết.

Khi evidence classes xung đột, phải trình bày xung đột. Không nâng nguồn lớp thấp
lên chỉ vì dễ tìm hơn.

## 5. Provenance bắt buộc

Mỗi kết luận nghiên cứu quan trọng phải truy được về các trường phù hợp:

- corpus/source;
- source path tương đối trong repository;
- work/text identifier;
- segment, line, folio, Toh., CBETA hoặc định danh tương đương khi có;
- pinned source commit SHA;
- `evidence_class`;
- `text_role`;
- witness/edition khi liên quan.

`evidence_class` mô tả thẩm quyền/nguồn gốc của nguồn.

`text_role` mô tả đoạn được lập chỉ mục đóng vai trò gì trong nguồn.

Không trích hoặc tổng hợp translator comment/translation note như thể đó là
root/scriptural text. Nếu dị bản khác nhau, phải nói rõ nhân chứng nào có reading
nào. Nếu provenance không đủ, hạ thành giả thuyết hoặc bỏ claim đó.

## 6. Rào chắn đa ngôn ngữ và đa truyền thống

- Không tự tạo tương đương Pāli ↔ Sanskrit ↔ Hán ↔ Tạng từ trí nhớ mô hình.
- Kiến thức mô hình được phép đề xuất thuật ngữ đa ngôn ngữ để thử, nhưng chúng
  vẫn chỉ là giả thuyết tìm kiếm cho tới khi repository evidence hỗ trợ.
- Một quan hệ đa ngôn ngữ chỉ trở thành bằng chứng khi alignment, relationship
  record, dictionary, shared canonical identifier hoặc repository evidence khác
  hỗ trợ nó.
- Không tự hòa hợp các truyền thống khác nhau. Phải nêu tương đồng, khác biệt,
  dị bản, phạm vi nhân chứng và độ bất định.

## 7. Quy trình nghiên cứu bắt buộc

### 7.1. Local mode

Dùng CLI trước khi quét đệ quy raw file:

```bash
bin/buddhist-corpus search "query"
bin/buddhist-corpus context --record-id ID
bin/buddhist-corpus work WORK_ID
bin/buddhist-corpus parallels WORK_OR_SEGMENT_ID
bin/buddhist-corpus resolve CBETA_WORK_OR_TAISHO_RANGE
bin/buddhist-corpus variants WORK_OR_SEGMENT_ID
bin/buddhist-corpus compare ID1 ID2
bin/buddhist-corpus provenance --record-id ID
```

Sau bước truy xuất, mở raw source khi cần kiểm ngữ cảnh, markup, apparatus hoặc
độ trung thành với nguồn.

### 7.2. Connector mode

Theo giao thức production trong
`.codex/skills/buddhist-corpus-research/SKILL.md` và `docs/REMOTE_AGENT.md`:

```text
câu hỏi
→ giả thuyết tìm kiếm có căn cứ
→ production locator
→ pointer nguồn đã xếp hạng
→ pinned upstream source
→ ngữ cảnh / provenance
→ quan hệ / dị bản khi cần
→ tổng hợp nhưng giữ riêng nhân chứng
```

Không duyệt đệ quy locator shards và không thay hash-bucket routing bằng GitHub
Code Search.

Với SuttaCentral ↔ CBETA, giữ ba bước bằng chứng riêng:

```text
SuttaCentral parallel relation
→ SuttaCentral-to-CBETA identifier bridge
→ resolved CBETA textual witness
```

Bridge là metadata, không phải bằng chứng textual identity.

### 7.3. Nghiên cứu thuật ngữ

Dùng thứ tự:

1. exact form;
2. dạng chuẩn hóa Unicode/case;
3. lemma/morphology do corpus cung cấp;
4. spelling variant đã được corpus chứng thực;
5. ngữ cảnh quanh các lần xuất hiện;
6. văn bản căn chỉnh/song hành.

Không suy ra biến thể chưa được chứng thực.

### 7.4. Nghiên cứu chủ đề/khái niệm

Không dừng ở một kết quả semantic/keyword đơn lẻ. Lặp:

```text
bằng chứng mồi
→ thuật ngữ nội bộ
→ các lần xuất hiện
→ ngữ cảnh
→ cấu trúc
→ song hành
→ dị bản
→ nhân chứng độc lập
→ tổng hợp
```

Phải biết bằng chứng nào hỗ trợ mỗi kết luận.

### 7.5. Khám phá ứng viên

BuddhaNexus, OpenPecha và Translation Memory thường tạo ứng viên, không phải
textual proof cuối cùng. Khi có thể, giải identifier về nhân chứng mạnh hơn. Nếu
không giải được, phải nêu giới hạn.

## 8. Hợp đồng câu trả lời

Một câu trả lời nghiên cứu phải:

1. tách kết luận khỏi giả thuyết tìm kiếm;
2. dẫn bằng chứng repository với provenance cần thiết;
3. nhận diện dị bản và nhân chứng độc lập thay vì làm phẳng chúng;
4. mô tả độ bất định và phần corpus chưa bao phủ;
5. fail-closed với claim mà corpus evidence hiện có không xác lập được.

Internet và trí nhớ mô hình không bao giờ được trở thành nguồn thứ 14 ngầm định.
