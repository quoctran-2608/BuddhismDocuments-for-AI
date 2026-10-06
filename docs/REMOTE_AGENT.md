# Hướng dẫn vận hành GitHub Connector

> Trạng thái: **HIỆN HÀNH**
>
> Phạm vi: giao thức runtime dành cho AI nghiên cứu qua GitHub Connector.
>
> Tài liệu này là hướng dẫn Connector chuyên biệt. Luật nghiên cứu tổng quát nằm
> ở `AGENTS.md`; cách AI xử lý câu hỏi nằm ở
> `.codex/skills/buddhist-corpus-research/SKILL.md`.

## 1. Vai trò của các repository

### Repo chính

`quoctran-2608/BuddhismDocuments-for-AI`

Chứa:

- luật nghiên cứu;
- skill;
- kiến trúc;
- source mappings;
- runtime config;
- code build/retrieval/export;
- tests và docs.

### Repo locator từ xa

Không hard-code. Đọc `config/remote-corpus.json`.

Tại thời điểm tài liệu này được đồng bộ, config khai báo:

```text
repository: quoctran-2608/BuddhismDocuments-for-AI-remote
branch: main
root_path: remote/pointer-production-v1
mode: pointer_production_v1
```

Nếu config đổi, config là nguồn chuẩn.

Repo remote là artefact dẫn xuất phục vụ truy cập, không phải nguồn câu chữ.

### Upstream source repositories

Mỗi pointer production chỉ tới repository nguồn gốc cùng pinned
`source_sha`, `source_path` và thường có `source_blob_sha`.

Bằng chứng nghiên cứu đến từ file upstream sau khi đã mở và đọc.

## 2. Luồng runtime chuẩn

```text
câu hỏi người dùng
→ đọc skill + remote config
→ tạo giả thuyết tìm kiếm có căn cứ
→ chọn production key
→ tính bucket
→ mở đúng locator shard
→ tìm dòng key khớp chính xác
→ đọc ranked pointers
→ chọn corpus/witness phù hợp
→ mở pinned upstream source
→ đọc context/provenance
→ xem relations/variants khi cần
→ tổng hợp
```

Không hỏi người dùng phải dùng repo nào.

## 3. Production namespace

Production v1 materialize đúng hai namespace:

```text
terms/latin  → normalized non-CJK lemma keys
ids          → exact original work_id spelling
```

Không materialize `terms/cjk`.

CJK trigram local là hạ tầng tìm kiếm, không phải vocabulary thuật ngữ để dùng
làm production key.

Số lượng key và thống kê artefact hiện tại phải đọc từ production
`manifest.json` và `production-summary.json` của root được config khai báo,
không lấy số benchmark lịch sử làm nguồn chuẩn.

## 4. Chọn loại key

### Identifier

Dùng namespace `ids` khi có exact work/text identifier.

Giữ nguyên spelling gốc.

Ví dụ:

`Dhp` và `dhp` là hai key khác nhau.

Không casefold identifier.

### Thuật ngữ

Dùng `terms/latin` cho Pāli, Sanskrit, romanized hoặc giả thuyết non-CJK có thể
biểu diễn bằng production lemma key.

Với câu hỏi tiếng Việt/Anh/Hán, mô hình được phép đề xuất Pāli/Sanskrit/romanized
như **giả thuyết tìm kiếm**, nhưng không được trình bày phương trình đa ngôn ngữ
đó như kết luận trước khi repository hỗ trợ.

## 5. Chuẩn hóa term key

Với `terms/latin`:

```text
Unicode NFC
→ Unicode casefold
→ tách theo whitespace
→ ghép lại bằng một ASCII space
```

Không strip diacritics khi tính production key.

Với `ids`, không chuẩn hóa spelling.

## 6. Tính bucket

Với exact production key:

```text
SHA-256(exact UTF-8 key)
→ lấy 2 ký tự hexadecimal thường đầu tiên
```

Đường dẫn:

```text
<root_path>/locator/terms/latin/<bucket>/part-000001.jsonl
<root_path>/locator/ids/<bucket>/part-000001.jsonl
```

Trong shard, tìm dòng JSONL có `key` khớp **chính xác** production key.

Không quét toàn bộ 256 bucket.

Không dùng GitHub Code Search làm router.

Ví dụ đã được production xác nhận:

```text
key: anicca
bucket: 45
path:
remote/pointer-production-v1/
  locator/terms/latin/45/part-000001.jsonl
```

## 7. Nếu shard quá lớn

Nếu Connector không đọc được file JSONL theo cách thông thường nhưng có Git
blob SHA phù hợp, có thể đọc blob của shard.

Việc đổi từ file fetch sang blob fetch không thay đổi phương pháp nghiên cứu.

## 8. Cấu trúc locator row

Một dòng locator có dạng khái niệm:

```text
key
query_kind
pointer_count
pointers[]
```

Pointer production giữ các trường provenance/ranking như:

```text
rank
score
match_reasons
record_id
corpus
repository
source_sha
source_blob_sha
source_path
indexed_source_path
work_id
segment_id
sequence_no
evidence_class
text_role
witness
```

Không suy câu chữ từ các trường này.

## 9. Chọn pointer

Production exporter đã:

- dùng ranking cốt lõi chung với local retrieval;
- tìm ứng viên theo corpus;
- gộp `(corpus, work_id, source_path)`;
- giới hạn số ứng viên theo corpus;
- áp dụng thứ tự ổn định sau cùng.

Khi nghiên cứu:

- giữ thứ tự pointer như gợi ý mở nguồn;
- không hiểu rank là thẩm quyền học thuật;
- với nghiên cứu đa nguồn, không chỉ mở corpus đứng đầu nếu câu hỏi cần witness
  độc lập.

## 10. Mở bằng chứng thật

Với mỗi claim muốn sử dụng:

1. mở `repository` tại `source_sha`;
2. mở `source_path`, hoặc dùng `source_blob_sha` khi phù hợp;
3. định vị `work_id`, `segment_id`, `sequence_no` nếu có;
4. đọc đủ ngữ cảnh;
5. kiểm `evidence_class`, `text_role`, `witness`;
6. chỉ sau đó mới dùng wording làm evidence.

Nếu source discovery là compressed/binary và Connector không render được wording,
không tuyên bố đã đọc wording đó. Tìm witness đọc được mạnh hơn nếu có.

## 11. Topic/comparative research

Không dừng ở một production key.

Dùng vòng:

```text
chủ đề
→ 2–6 giả thuyết có căn cứ
→ locator rows
→ nhóm pointer theo corpus
→ mở witness mạnh
→ lấy thuật ngữ thực sự xuất hiện trong source
→ thử giả thuyết bổ sung
→ xem parallels / variants / witness độc lập
→ tổng hợp
```

Ưu tiên witness chính/thẩm quyền khi câu hỏi cần textual proof.

BuddhaNexus, Translation Memory và OpenPecha thường là nguồn discovery/alignment;
nếu có thể, quay lại SuttaCentral, CBETA, 84000 TEI hoặc witness phù hợp hơn.

## 12. Phạm vi người dùng

Nếu người dùng yêu cầu chỉ:

- một Nikāya;
- một A-hàm;
- CBETA;
- một work ID;
- một Vinaya;
- một ngôn ngữ;
- một truyền thống;

thì giữ đúng phạm vi đó.

Không mở rộng âm thầm.

## 13. CJK remote coverage

Production v1 không có arbitrary Chinese-term namespace.

Để tới nguồn Hán văn, có thể dùng:

- exact work ID;
- Pāli/Sanskrit/romanized hypothesis có căn cứ;
- pointer của corpus Hán xuất hiện dưới key được hỗ trợ;
- relation/identifier đã được repository chứng thực.

Không dùng trigram benchmark lịch sử như production key.

Nếu route hiện hành không xác lập được câu hỏi CJK, nói rõ coverage limit.

## 14. Song hành SuttaCentral ↔ CBETA

Giữ ba lớp:

```text
SuttaCentral parallel relation
→ SuttaCentral-to-CBETA identifier bridge
→ CBETA textual witness đã resolve
```

Không dùng bridge như quotation.

Chi tiết subsystem xem `docs/SC_CBETA_BRIDGE.md`.

## 15. Key không tồn tại hoặc route không đủ

Nếu production key không tồn tại:

- thử giả thuyết khác có căn cứ;
- dùng thuật ngữ đã thấy trong source đã mở để refine;
- không quét tất cả shard;
- không bịa `terms/cjk`;
- không chuyển sang web chung như một nguồn corpus.

Nếu vẫn không đủ:

**không đủ dữ liệu trong remote corpus export hiện tại**

Kèm giải thích coverage thiếu nếu hữu ích.

## 16. Diễn giải rank

Pointer rank trả lời:

> file nào nên mở trước?

Nó không trả lời:

- truyền thống nào đúng;
- witness nào cổ hơn;
- source nào có authority giáo lý cao hơn;
- hai thuật ngữ có tương đương hay không;
- một witness có đủ để kết luận hay không.

Những việc này phải dựa vào evidence hierarchy, source context, text role,
witness separation và relations thực sự.

## 17. Artefact lịch sử

Các path như:

- `remote/pointer-poc/`;
- `remote/pointer-benchmark/`;
- `remote/pointer-compact-poc/`;

là artefact lịch sử/đo lường.

Không dùng chúng cho nghiên cứu thông thường nếu
`config/remote-corpus.json` đang khai báo `pointer_production_v1`.

## 18. Quan hệ với CLI

Production artefact được sinh cục bộ bằng CLI.

Lệnh, option và các công cụ benchmark/analysis nằm trong `docs/CLI.md`.

Tài liệu này chỉ mô tả runtime đọc artefact qua Connector.

## 19. Hợp đồng câu trả lời

Câu trả lời Connector phải tách:

1. kết luận được nguồn hỗ trợ;
2. bằng chứng theo witness/corpus;
3. parallels/variants;
4. diễn giải;
5. mức chắc chắn và coverage limit;
6. provenance:
   `corpus | repository | source_path | work_id | segment_id | source_sha |
   evidence_class | text_role | witness`.

Không trích pointer metadata như lời văn nguồn.

## 20. Những gì chưa thuộc runtime hiện hành

Evidence Record, quote verification, Atomic Claim, counterevidence gate và
Research Run là **MỤC TIÊU — chưa triển khai đầy đủ**.

Không giả vờ Connector hiện tại đã có các lớp đó.
