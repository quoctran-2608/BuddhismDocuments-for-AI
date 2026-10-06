---
name: buddhist-corpus-research
description: Nghiên cứu corpus Phật học ưu tiên provenance, dùng local SQLite hoặc GitHub Connector production.
---

# Kỹ năng nghiên cứu corpus Phật học

Đọc và tuân thủ `AGENTS.md` trước khi dùng kỹ năng này.

Tài liệu này mô tả **AI phải hành động như thế nào** khi nhận yêu cầu nghiên cứu.
Nó không thay thế:

- kiến trúc: `docs/ARCHITECTURE.md`;
- giao thức Connector chi tiết: `docs/REMOTE_AGENT.md`;
- runtime config: `config/remote-corpus.json`;
- yêu cầu/tiêu chí nghiệm thu: `docs/REQUIREMENTS.md`,
  `docs/ACCEPTANCE.md`.

## 1. Hợp đồng cốt lõi

```text
kiến thức mô hình → chỉ được tạo giả thuyết tìm kiếm
bằng chứng repository → mới được xác lập kết luận nghiên cứu
```

Pointer locator không phải bằng chứng.

Không dùng web chung hoặc trí nhớ mô hình như một “nguồn thứ 14” để lấp khoảng
trống corpus.

## 2. Tự chọn chế độ thực thi

### Local mode

Dùng khi có shell và SQLite index cục bộ.

Bắt đầu bằng:

```bash
bin/buddhist-corpus status
```

Nếu source thiếu hoặc SHA sai, coi là lỗi provenance và dừng nhánh nghiên cứu đó.

### GitHub Connector mode

Dùng khi có GitHub Connector nhưng không có shell/SQLite local.

Không hỏi người dùng repo nào là repo chính hay repo remote. Tự đọc:

1. `config/remote-corpus.json` trong repo chính;
2. manifest của production root được config khai báo;
3. locator production;
4. pinned upstream source mà pointer chỉ tới.

Giao thức định tuyến chi tiết nằm trong `docs/REMOTE_AGENT.md`.

## 3. Quy trình chung

```text
câu hỏi người dùng
→ xác định phạm vi
→ tạo giả thuyết tìm kiếm có căn cứ
→ truy xuất ứng viên
→ chọn nguồn/nhân chứng phù hợp
→ mở bằng chứng thật
→ đọc ngữ cảnh
→ kiểm provenance + text role + witness
→ xem relations/variants khi cần
→ tổng hợp nhưng giữ nhân chứng riêng
→ nêu giới hạn
```

Không dừng ở một kết quả tìm kiếm nếu câu hỏi mang tính chủ đề, so sánh hoặc
đa nguồn.

## 4. Giả thuyết tìm kiếm

Kiến thức mô hình được phép đề xuất:

- dạng Pāli/Sanskrit/romanized có khả năng liên quan;
- work ID có khả năng liên quan;
- thuật ngữ nội bộ cần thử;
- nhánh corpus có khả năng chứa dữ liệu.

Nhưng giả thuyết không được trình bày như kết luận.

Đặc biệt, phương trình Pāli ↔ Sanskrit ↔ Hán ↔ Tạng chỉ trở thành bằng chứng khi
repository có alignment, relation, dictionary, shared identifier hoặc dữ liệu
khác hỗ trợ.

## 5. Nghiên cứu thuật ngữ

Ưu tiên theo thứ tự:

1. dạng chính xác;
2. chuẩn hóa Unicode/case;
3. lemma/morphology do corpus cung cấp;
4. biến thể chính tả đã được corpus chứng thực;
5. ngữ cảnh các lần xuất hiện;
6. parallel/alignment khi có.

Không tự bịa dạng từ.

### Local

Ví dụ:

```bash
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus search "anicca" --language pli --context 2 --with-provenance
bin/buddhist-corpus variants mn1
```

### Connector

Dùng exact ID hoặc `terms/latin` theo giao thức trong
`docs/REMOTE_AGENT.md`.

## 6. Nghiên cứu đoạn văn

### Local

```bash
bin/buddhist-corpus search "如是我聞" --language lzh
bin/buddhist-corpus context --record-id RECORD_ID --window 3
bin/buddhist-corpus provenance --record-id RECORD_ID
```

### Connector

Production v1 không có arbitrary `terms/cjk`.

Nếu có exact work ID hoặc giả thuyết Latin/Indic được hỗ trợ, dùng chúng để đi
tới nguồn Hán văn. Nếu route hiện có không đủ để xác lập đoạn cần tìm, báo rõ
giới hạn thay vì giả vờ đã tìm hết Hán tạng.

## 7. Nghiên cứu chủ đề/khái niệm

Không tổng hợp từ một keyword hit.

Dùng vòng lặp:

```text
bằng chứng mồi
→ thuật ngữ thực sự xuất hiện trong nguồn
→ các lần xuất hiện
→ ngữ cảnh/cấu trúc tác phẩm
→ song hành
→ dị bản
→ nhân chứng độc lập
→ tổng hợp
```

Với Connector, thử nhiều giả thuyết có căn cứ thay vì tiêu hết ngân sách vào
một corpus đầu tiên.

## 8. Nghiên cứu song hành

### Local

```bash
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus compare ID1 ID2
```

Với SuttaCentral ↔ CBETA phải giữ ba bước riêng:

```text
SuttaCentral parallel relation
→ SuttaCentral-to-CBETA identifier bridge
→ resolved CBETA textual witness
```

Relation/bridge là metadata, không phải bằng chứng câu chữ.

## 9. Nghiên cứu dị bản

### Local

```bash
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus variants mn1
```

Giữ riêng:

- lemma;
- reading;
- witness sigla;
- confidence nếu nguồn có;
- source path/SHA.

Không tự tạo bản hòa hợp.

## 10. Dùng nguồn discovery

BuddhaNexus, OpenPecha và Translation Memory thường dùng để:

- phát hiện ứng viên;
- phát hiện quan hệ/căn chỉnh;
- tìm identifier hoặc vị trí đáng mở.

Khi có witness mạnh hơn, quay lại:

- SuttaCentral Bilara;
- CBETA;
- 84000 TEI;
- hoặc nguồn phù hợp khác.

Nếu không resolve được về witness mạnh hơn, nêu giới hạn của nguồn discovery.

## 11. Tách đúng loại bằng chứng

Luôn đọc:

- `evidence_class`;
- `text_role`;
- `witness`.

Ví dụ:

- `translation_note` không phải `root_text`;
- `metadata_relationship` không phải textual witness;
- `computational_segmented` không tự động là bản văn cuối cùng.

## 12. Local CLI — lối tắt

Nếu chưa có index:

```bash
bin/buddhist-corpus build --profile core
```

Các lệnh thường dùng:

```bash
bin/buddhist-corpus search "QUERY"
bin/buddhist-corpus context --record-id ID --window 3
bin/buddhist-corpus evidence --record-id ID --context 2
bin/buddhist-corpus work WORK_ID
bin/buddhist-corpus parallels WORK_OR_SEGMENT_ID
bin/buddhist-corpus resolve CBETA_OR_SC_ID
bin/buddhist-corpus variants WORK_OR_SEGMENT_ID
bin/buddhist-corpus compare ID1 ID2
bin/buddhist-corpus provenance --record-id ID
```

Chi tiết đầy đủ xem `docs/CLI.md`.

## 13. Connector — các nguyên tắc không được vi phạm

Trong Connector mode:

- đọc `config/remote-corpus.json`, không hard-code runtime;
- dùng production locator, không dùng GitHub Code Search làm router;
- không quét toàn bộ 256 bucket;
- pointer chỉ là ứng viên;
- mở pinned upstream source trước khi trích dẫn;
- giữ source SHA/path/work/segment/text role/witness;
- không giả định tồn tại `terms/cjk`;
- không dùng benchmark/POC lịch sử như production;
- source không mở được thì không tuyên bố đã đọc wording đó.

Chi tiết hash, normalization, namespace và pointer format nằm trong
`docs/REMOTE_AGENT.md`.

## 14. Phạm vi người dùng

Nếu người dùng giới hạn:

- một Nikāya;
- một bộ A-hàm;
- một work ID;
- CBETA;
- một Vinaya;
- một ngôn ngữ;
- một witness;

thì giữ đúng phạm vi đó.

Không tự mở rộng sang truyền thống/corpus khác nếu không cần thiết.

## 15. Fail-closed

### Local mode

Nếu corpus local không đủ:

**không đủ dữ liệu trong corpus hiện tại**

### Connector mode

Nếu production route/nguồn được phép không đủ:

**không đủ dữ liệu trong remote corpus export hiện tại**

Sau câu này có thể giải thích ngắn coverage nào thiếu.

Không chuyển sang web chung để lấp chỗ trống nếu nhiệm vụ đang ở chế độ corpus
research.

## 16. Hợp đồng câu trả lời

Câu trả lời nghiên cứu phải tách rõ:

1. **Kết luận** — điều nguồn thực sự hỗ trợ;
2. **Bằng chứng theo corpus/nhân chứng** — không hòa nhiều witness thành một;
3. **Song hành/dị bản** — nêu loại quan hệ và khác biệt quan trọng;
4. **Diễn giải** — phần tổng hợp của AI, tách khỏi trích dẫn;
5. **Mức chắc chắn và giới hạn**;
6. **Provenance** cho item được dùng:
   `corpus | repository | source_path | work_id | segment_id | source_sha |
   evidence_class | text_role | witness`.

Chỉ trích câu chữ đã thực sự mở trong source.

## 17. Quan hệ với lớp kiểm chứng MỤC TIÊU

Evidence Record, quote verification, Atomic Claim, counterevidence, Final Claim
Gate và Research Run đang là **MỤC TIÊU — chưa triển khai đầy đủ**.

Không giả vờ skill hiện tại đã có các gate đó.

Khi lớp này được triển khai, thiết kế/yêu cầu chuẩn nằm trong:

- `docs/RESEARCH_VERIFICATION_DESIGN.md`;
- `docs/REQUIREMENTS.md`;
- `docs/ACCEPTANCE.md`.
