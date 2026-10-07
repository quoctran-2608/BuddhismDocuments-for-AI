# Đặc tả tổng thể dự án Buddhist Corpus Research

> Trạng thái tài liệu: **HIỆN HÀNH**
>
> Vai trò: tài liệu chuẩn cấp dự án để hiểu mục tiêu, phạm vi, nguyên tắc,
> kiến trúc cấp cao, năng lực hiện tại, giới hạn hiện tại và hướng nâng cấp đã
> được chấp thuận.
>
> Lưu ý: tài liệu này không thay thế các nguồn chuẩn chuyên biệt như
> `AGENTS.md`, `manifest.json`, `config/`, `schema/`, mã nguồn và kiểm thử.

## 1. Tóm tắt dự án

Dự án xây dựng một hạ tầng nghiên cứu Phật học cho AI dựa trên các nguồn dữ liệu
được ghim phiên bản và có thể truy nguyên.

Mục tiêu không chỉ là “tìm được một đoạn văn”, mà là giúp AI:

1. đi từ câu hỏi tự nhiên tới đúng corpus và đúng nguồn;
2. đọc đúng văn bản ở đúng phiên bản nguồn;
3. giữ riêng các nhân chứng, bản dịch, chú thích, dị bản và dữ liệu quan hệ;
4. truy nguyên mọi kết luận nghiên cứu về repository, đường dẫn, định danh và
   commit SHA;
5. không tự lấp khoảng trống bằng trí nhớ mô hình khi corpus không đủ dữ liệu.

Định hướng cốt lõi của hệ thống là:

> **Kiến thức mô hình có thể tạo giả thuyết tìm kiếm; chỉ bằng chứng trong
> repository mới được dùng để xác lập kết luận nghiên cứu.**

## 2. Bài toán gốc

Dự án bắt đầu từ 13 repository dữ liệu Phật học có cấu trúc, ngôn ngữ, mức độ
thẩm quyền và mục đích rất khác nhau.

Nếu chỉ clone các repository rồi cho AI đọc trực tiếp, sẽ xuất hiện nhiều vấn
đề:

- không có chỉ mục thống nhất xuyên corpus;
- cùng một tác phẩm có nhiều định danh và nhiều nhân chứng;
- metadata về song hành dễ bị nhầm thành bằng chứng câu chữ;
- bản dịch, ghi chú và root text có thể bị trộn;
- corpus phục vụ khám phá bằng máy dễ bị dùng thay cho bản văn mạnh hơn;
- đối chiếu đa ngôn ngữ dễ bị AI suy từ trí nhớ thay vì từ bằng chứng;
- truy xuất từ xa qua GitHub Connector không có SQLite local;
- dữ liệu dẫn xuất dễ bị nhầm thành nguồn gốc;
- một kết quả đứng đầu bảng xếp hạng dễ bị hiểu nhầm là “nguồn đúng nhất”.

Dự án giải quyết các vấn đề này bằng cách tách rõ:

```text
nguồn gốc
→ chỉ mục dẫn xuất
→ truy xuất
→ định tuyến từ xa
→ mở nguồn đã ghim
→ đọc ngữ cảnh và provenance
→ tổng hợp nghiên cứu
```

## 3. Người dùng và trường hợp sử dụng

Hệ thống hướng tới hai nhóm sử dụng chính:

### 3.1. Người nghiên cứu dùng CLI cục bộ

Các trường hợp điển hình:

- tra một thuật ngữ Pāli/Sanskrit/romanized;
- tìm một cụm Hán văn;
- xem ngữ cảnh trước/sau;
- xem metadata tác phẩm;
- tìm quan hệ song hành;
- giải định danh SuttaCentral sang CBETA;
- xem dị bản;
- so sánh nhiều nhân chứng;
- kiểm provenance của một record;
- tạo gói evidence từ record + context + provenance + variants.

### 3.2. AI nghiên cứu qua GitHub Connector

Các trường hợp điển hình:

- nghiên cứu một thuật ngữ hoặc chủ đề;
- tìm bản văn theo work ID;
- mở nhiều corpus để đối chiếu;
- theo pointer tới đúng file upstream đã ghim;
- đọc nguồn thật trước khi kết luận;
- trả lời kèm provenance;
- dừng và báo giới hạn khi production locator không đủ độ bao phủ.

## 4. Nguyên tắc bất biến

Các nguyên tắc sau là nền móng của dự án và không được thay đổi âm thầm.

### 4.1. Pointer không phải bằng chứng

Pointer chỉ là con trỏ định tuyến tới nguồn.

Một pointer có rank, score, corpus, repository, source SHA, path và định danh
không đồng nghĩa với việc nội dung chưa mở có thể được trích dẫn như bằng chứng.

Quy trình đúng:

```text
pointer
→ mở pinned upstream source
→ tìm đúng vị trí
→ đọc đủ ngữ cảnh
→ kiểm provenance / text role / witness
→ mới dùng làm evidence
```

### 4.2. Cơ sở dữ liệu SQLite không phải nguồn gốc

SQLite, FTS, locator, benchmark và các artefact sinh ra đều là dữ liệu dẫn xuất.

Nguồn gốc vẫn là 13 repository upstream ở các commit SHA đã ghim.

### 4.3. Không có dữ liệu thì đóng thất bại

Local mode:

**không đủ dữ liệu trong corpus hiện tại**

Connector mode:

**không đủ dữ liệu trong remote corpus export hiện tại**

Không dùng web hoặc trí nhớ mô hình để biến một khoảng trống corpus thành một
kết luận có vẻ chắc chắn.

### 4.4. Giữ riêng nhân chứng và vai trò văn bản

Ba khái niệm khác nhau:

- `evidence_class`: thẩm quyền/nguồn gốc của corpus;
- `text_role`: đoạn này là root text, translation, note, heading, alignment,
  computational text hay vai trò khác;
- `witness`: bản/edition/nhân chứng cụ thể.

Không được hòa ba khái niệm này thành một nhãn “độ tin cậy”.

### 4.5. Quan hệ không phải câu chữ

Parallel relation, identifier bridge, RDF relation hoặc alignment metadata có
thể chứng minh một quan hệ, nhưng không tự động chứng minh hai đoạn văn giống
nhau hoặc một câu chữ cụ thể tồn tại trong bản nguồn.

### 4.6. Xếp hạng truy xuất không phải chân lý học thuật

Rank/score giúp quyết định ứng viên nào nên mở trước.

Nó không quyết định:

- truyền thống nào đúng;
- nhân chứng nào cổ hơn;
- nguồn nào có thẩm quyền giáo lý cao hơn;
- hai thuật ngữ đa ngôn ngữ có thực sự tương đương;
- một kết luận nghiên cứu có đủ bằng chứng hay chưa.

## 5. Cấu trúc repository

Dự án có ba loại repository với ba vai trò khác nhau.

### 5.1. Repository chính

`quoctran-2608/BuddhismDocuments-for-AI`

Vai trò:

- kiến trúc;
- luật nghiên cứu;
- skill cho AI;
- cấu hình;
- schema;
- parser;
- chỉ mục/retrieval code;
- CLI;
- test;
- tài liệu;
- mã sinh artefact remote.

Đây là nơi chuẩn của kiến trúc và phương pháp nghiên cứu.

### 5.2. Repository locator từ xa

Repository được khai báo trong `config/remote-corpus.json`.

Hiện tại:

`quoctran-2608/BuddhismDocuments-for-AI-remote`

Vai trò:

- chứa artefact dẫn xuất cho GitHub Connector;
- cung cấp production pointer locator;
- định tuyến từ key sang pointer nguồn.

Hiện production root là:

`remote/pointer-production-v1`

Repository này:

- không phải corpus Phật học thứ 14;
- không phải nguồn chuẩn của câu chữ;
- không thay thế upstream source;
- có thể tái tạo từ local index và source contract.

### 5.3. Mười ba repository upstream

Đây mới là tầng bằng chứng gốc.

Danh sách và SHA chuẩn nằm ở:

- `manifest.json`;
- `config/corpus-sources.json`.

Các nguồn bao gồm SuttaCentral, CBETA, 84000, OpenPecha, BuddhaNexus,
PTS archive và dữ liệu Pāli dẫn xuất.

Quan hệ tổng thể:

```text
quoctran-2608/BuddhismDocuments-for-AI
        │
        │ config/remote-corpus.json
        ▼
quoctran-2608/BuddhismDocuments-for-AI-remote
        │
        │ production pointers
        ▼
13 repository upstream ở pinned SHA
        │
        ▼
văn bản / metadata / variants / relations thực sự
```

## 6. Hai chế độ thực thi hiện hành

### 6.1. Local mode

Local mode là offline nghiêm ngặt.

Luồng:

```text
13 pinned source repositories
→ deterministic parsers
→ SQLite
→ FTS / relations / variants / lemmas
→ CLI
→ source verification
→ answer
```

Không được tải thêm nguồn nghiên cứu từ internet để lấp dữ liệu thiếu.

### 6.2. GitHub Connector mode

Connector mode là ngoại lệ đọc từ xa có kiểm soát.

AI chỉ được dùng:

1. repository chính;
2. remote locator repo được config khai báo;
3. upstream repository được pointer chỉ tới, ở pinned source SHA/blob SHA.

Luồng:

```text
question
→ search hypotheses
→ production locator
→ ranked pointers
→ pinned upstream source
→ context / provenance
→ relations / variants khi cần
→ witness-separated synthesis
```

GitHub Code Search không phải cơ chế định tuyến production.

## 7. Tầng dữ liệu cục bộ hiện hành

SQLite schema hiện có các thành phần chính:

- `source_state`;
- `search_index_state`;
- `works`;
- `records`;
- `relations`;
- `variants`;
- `lemmas`;
- `records_fts`;
- `records_cjk_fts`.

Nguồn chuẩn của schema là:

`schema/corpus-index.sql`

Cơ sở dữ liệu sinh ra nằm dưới `derived/` và không phải source of truth.

## 8. Truy xuất hiện hành

Hệ thống hiện tại không phải vector/embedding semantic RAG.

Nó dùng:

- SQLite FTS5;
- exact match;
- Unicode normalization;
- diacritic folding;
- compact Unicode matching;
- corpus-provided lemma;
- sinh ứng viên bằng CJK trigram;
- evidence-class weighting;
- deterministic tie-break.

Điểm và trọng số cụ thể là chi tiết thực thi; nguồn chuẩn nằm trong
`tools/corpus_research/retrieval.py` và `tools/corpus_research/index.py`.

### 8.1. CJK local search

Local index có `records_cjk_fts` dùng trigram cho `lzh`/`zh`.

Mục đích là sinh ứng viên cho chuỗi con Hán văn dài.

Đây là hạ tầng truy xuất, không phải một từ điển thuật ngữ Phật học CJK.

## 9. Production locator hiện hành

Production v1 materialize hai namespace:

```text
terms/latin
ids
```

Theo artefact production hiện tại:

- `terms/latin`: 26.547 key;
- `ids`: 32.498 key;
- tổng: 59.045 key;
- 58.643 query có kết quả;
- 402 query không có kết quả;
- 706.011 pointer;
- 517 file;
- 0 trường `raw_text` trong artefact production.

Production v1 không materialize `terms/cjk`.

Lý do: vocabulary trigram cục bộ rất lớn và là token hạ tầng tìm kiếm, không
phải một vocabulary thuật ngữ Phật học có nghĩa để xuất trực tiếp thành
production namespace.

### 9.1. Định tuyến

Term key:

```text
NFC
→ casefold
→ collapse whitespace
```

Identifier:

- giữ nguyên spelling gốc;
- không casefold.

Bucket:

```text
SHA-256(exact UTF-8 key)
→ 2 ký tự hex đầu
→ locator/<namespace>/<bucket>/part-000001.jsonl
```

Chi tiết runtime phải đọc từ `config/remote-corpus.json` và production manifest
thay vì hard-code giá trị từ tài liệu này.

## 10. Hệ phân cấp bằng chứng hiện hành

Dự án phân biệt các lớp bằng chứng:

1. `canonical_root` — bản gốc/canonical/root witness;
2. `authoritative_structured` — edition có cấu trúc thẩm quyền cao;
3. `metadata_relationship` — metadata và quan hệ;
4. `parallel_alignment` — corpus căn chỉnh/song hành;
5. `computational_segmented` — corpus phân đoạn bằng máy;
6. `derived_critical_lemma` — dữ liệu khảo dị/lemma dẫn xuất;
7. `auxiliary_reference` — nguồn tham khảo phụ trợ.

Thứ bậc này hướng dẫn cách dùng nguồn, nhưng không thay thế việc đọc đúng
`text_role`, `witness` và ngữ cảnh.

## 11. Khả năng hiện hành

### 11.1. CLI nghiên cứu

Các năng lực chính:

- `status`;
- `build`;
- `search`;
- `context`;
- `work`;
- `parallels`;
- `resolve`;
- `variants`;
- `compare`;
- `provenance`;
- `evidence`.

Ngoài ra có các lệnh export/benchmark/analysis phục vụ artefact Connector.

Nguồn chuẩn của giao diện dòng lệnh là `docs/CLI.md` và
`tools/corpus_research/cli.py`.

### 11.2. SuttaCentral ↔ CBETA

Hệ thống hỗ trợ luồng:

```text
SuttaCentral parallel relation
→ SuttaCentral-to-CBETA identifier bridge
→ resolved CBETA textual witness
```

Ba bước phải được giữ riêng.

Bridge metadata không phải textual proof.

### 11.3. Variant và witness comparison

Hệ thống có bảng variants và lệnh compare.

Compare giữ nhân chứng riêng và không tự harmonize.

## 12. Những gì hệ thống hiện tại chưa làm

Các điểm sau không được mô tả như tính năng hiện hành:

- semantic vector search toàn corpus;
- embedding-based universal RAG;
- arbitrary exhaustive CJK lookup qua remote production locator;
- tự động kiểm chứng claim-by-claim;
- bắt buộc tìm phản chứng cho mọi research claim;
- quote verification có trạng thái máy đọc;
- Research Run Manifest;
- universal confidence score;
- knowledge graph toàn bộ corpus;
- autonomous research agents;
- web research làm nguồn bổ sung mặc định.

## 13. Giới hạn hiện hành

### 13.1. Connector không bao phủ mọi truy vấn CJK tùy ý

Production v1 không có `terms/cjk`.

Connector vẫn có thể tới nguồn Hán văn qua:

- exact work ID;
- Latin/Indic hypothesis được corpus hỗ trợ;
- pointer của các corpus liên quan;
- quan hệ/identifier đã biết.

Nếu route hiện có không xác lập được claim, phải báo giới hạn.

### 13.2. Một kết quả truy xuất chưa đủ để trở thành kết luận nghiên cứu

Một kết quả truy xuất chỉ là ứng viên.

AI vẫn phải đọc context và phân biệt:

- root text;
- translation;
- note;
- metadata;
- alignment;
- ứng viên do xử lý tính toán tạo ra.

### 13.3. Claim verification chưa được máy hóa đầy đủ

Hệ thống hiện đã mạnh ở:

- provenance;
- witness separation;
- evidence hierarchy;
- source opening;
- fail-closed.

Nhưng sau khi evidence đã được đọc, việc AI hình thành claim và đánh giá claim
có vượt quá nguồn hay không vẫn còn phụ thuộc nhiều vào quy trình tác nhân.

Đây là khoảng trống chính của hướng nâng cấp tiếp theo.

## 14. Hướng nâng cấp đã được chấp thuận — MỤC TIÊU

> Trạng thái phần này: **MỤC TIÊU — CHƯA TRIỂN KHAI ĐẦY ĐỦ**
>
> Thiết kế chi tiết và data contract mục tiêu nằm trong
> `docs/v2/DESIGN.md`.

Không thay thế hệ retrieval hiện tại.

Không viết lại Connector.

Không bỏ SQLite/FTS.

Mục tiêu là bổ sung một tầng kiểm chứng nghiên cứu:

```text
question
→ scope
→ search hypotheses
→ truy xuất hiện hành
→ pinned source
→ context
→ Evidence Record
→ quote verification
→ Atomic Claim
→ claim/evidence verification
→ independent witnesses
→ counterevidence
→ revise / downgrade / reject
→ Final Claim Gate
→ accepted claims
→ synthesis
→ final validation
→ Research Run Manifest
→ answer
```

### 14.1. Evidence Record

Mục tiêu là biến “nguồn đã thực sự mở và đọc” thành record có cấu trúc.

Pointer không bao giờ tự động trở thành Evidence Record.

### 14.2. Quote verification

Các trạng thái mục tiêu:

- VERIFIED_EXACT;
- VERIFIED_NORMALIZED;
- PARAPHRASE;
- UNVERIFIED;
- QUOTE_MISMATCH.

Quote mismatch không được xuất như trích dẫn trực tiếp.

### 14.3. Atomic Claim

Mỗi kết luận nghiên cứu quan trọng được tách thành mệnh đề có thể kiểm.

Một claim phải nối được tới supporting evidence và, khi phù hợp, counterevidence.

### 14.4. Claim–Evidence Verification

Các mức mục tiêu:

- DIRECT;
- STRONG;
- WEAK;
- UNSUPPORTED;
- CONTRADICTED.

UNSUPPORTED không được đi vào kết luận cuối.

CONTRADICTED không được trình bày như kết luận đã xác lập.

### 14.5. Counterevidence

Research mode mục tiêu phải chủ động tìm:

- ngoại lệ;
- nhân chứng khác;
- dị bản;
- nguồn cùng cấp nhưng xung đột;
- quan hệ phụ thuộc giữa các nguồn;
- điều kiện giới hạn claim.

“Không tìm thấy phản chứng” chỉ có nghĩa là chưa thấy trong phạm vi corpus và
truy vấn đã kiểm.

### 14.6. Final Claim Gate

Chỉ claim được chấp nhận mới được đi vào synthesis.

Phần tổng hợp không được tự sinh thêm kết luận quan trọng chưa qua kiểm.

### 14.7. Research Run Manifest

Mục tiêu là có thể trả lời:

- câu hỏi là gì;
- phạm vi nào đã kiểm;
- repo/commit nào được dùng;
- locator version nào;
- query nào đã chạy;
- evidence nào đã mở;
- claim nào được nhận/reject;
- counterevidence pass có chạy hay không;
- giới hạn gì còn lại.

## 15. Hai mức nghiên cứu mục tiêu

### 15.1. Quick mode

Dùng cho lookup hẹp như:

- thuật ngữ;
- segment;
- work ID;
- parallel.

Giữ pipeline nhanh:

```text
retrieval
→ pinned source
→ context
→ evidence
→ answer
```

Vẫn phải có provenance, quote discipline và fail-closed.

### 15.2. Research mode

Dùng cho:

- nghiên cứu chủ đề;
- so sánh đa nguồn;
- tranh luận học thuật;
- lịch sử;
- nghiên cứu phục vụ viết sách;
- câu hỏi cần nhiều nhân chứng.

Bắt buộc hơn về:

- Evidence Record;
- Atomic Claim;
- verification;
- counterevidence;
- final gate;
- run manifest.

## 16. Các nguyên tắc chống suy diễn quá mức

Dự án hiện hành và hướng nâng cấp cùng giữ các nguyên tắc:

- không tìm thấy ≠ không tồn tại;
- nhiều citation ≠ nhiều nguồn độc lập;
- văn bản nói X ≠ X là sự kiện lịch sử đã được chứng minh;
- luật nói X ≠ mọi người trong lịch sử đều làm X;
- wording bản dịch ≠ cấu trúc khái niệm nguyên ngữ;
- parallel relation ≠ textual identity;
- rank cao ≠ chân lý giáo lý;
- AI đề xuất phương trình Pāli–Chinese ≠ phương trình đã được corpus chứng minh;
- một nghiên cứu khoa học hỗ trợ một hiệu ứng ≠ chứng minh một mệnh đề siêu hình.

## 17. TƯƠNG LAI — sau v1

> Trạng thái: **TƯƠNG LAI — chưa phải requirement triển khai**

Nếu production locator hữu hạn sau này trở thành nút thắt đã được đo lường, có
thể xem xét một đường truy xuất sâu từ xa bằng job/worker xác định (ví dụ GitHub
Action) để tạo artefact truy xuất có provenance. Worker này chỉ làm retrieval,
kiểm thử hoặc sinh artefact; nó không phải “AI brain” và không được bỏ qua
Evidence/Claim gates.

Đặc biệt, đây mới là nơi xem xét giải pháp cho arbitrary remote CJK retrieval;
không được âm thầm materialize toàn bộ trigram vocabulary thành `terms/cjk`.

Chi tiết: `docs/v2/DESIGN.md`.

## 18. Ngoài phạm vi v1 của hướng nâng cấp

Không ưu tiên trong v1:

- vector DB;
- embeddings toàn corpus;
- knowledge graph toàn diện;
- Kubernetes;
- microservices;
- distributed DB;
- autonomous multi-agent research;
- semantic search phổ quát;
- xác suất/confidence score giả tạo.

V1 ưu tiên lớp kiểm chứng nhỏ, có thể kiểm thử và không phá fast path hiện tại.

## 19. Tiêu chí chất lượng cấp dự án

Hệ thống phải hướng tới các thuộc tính sau:

- nguồn upstream được ghim và truy nguyên được;
- derived artifact tái tạo được;
- pointer không bị dùng như textual evidence;
- metadata không bị dùng như câu chữ;
- witness không bị tự hòa hợp;
- local và Connector giữ cùng nguyên tắc evidence;
- không có corpus evidence thì fail closed;
- production Connector không phụ thuộc GitHub Code Search;
- thay đổi retrieval không âm thầm phá ranking semantics;
- thay đổi kiến trúc phải cập nhật tài liệu chuẩn tương ứng;
- HIỆN HÀNH, MỤC TIÊU, TƯƠNG LAI và LỊCH SỬ phải được phân biệt rõ.

Các requirement có mã nằm trong `docs/REQUIREMENTS.md`; tiêu chí nghiệm thu,
ánh xạ code/config/test và các khoảng trống kiểm thử nằm trong
`docs/ACCEPTANCE.md`.

## 20. Tài liệu nên đọc theo nhu cầu

### Muốn hiểu dự án

1. `docs/PROJECT_SPEC.md`;
2. `README.md`;
3. `docs/ARCHITECTURE.md`.

### Muốn AI nghiên cứu đúng

1. `AGENTS.md`;
2. `.codex/skills/buddhist-corpus-research/SKILL.md`;
3. `docs/REMOTE_AGENT.md` nếu dùng Connector.

### Muốn biết nguồn nào đang được ghim

- `manifest.json`;
- `config/corpus-sources.json`.

### Muốn biết Connector đang chạy ở đâu

- `config/remote-corpus.json`;
- production manifest trong remote repo.

### Muốn biết schema

- `schema/corpus-index.sql`.

### Muốn biết CLI

- `docs/CLI.md`;
- `tools/corpus_research/cli.py`.

### Muốn hiểu SC ↔ CBETA

- `docs/SC_CBETA_BRIDGE.md`.

### Muốn hiểu thiết kế lớp kiểm chứng MỤC TIÊU

- `docs/v2/DESIGN.md`;
- `docs/REQUIREMENTS.md`;
- `docs/ACCEPTANCE.md`.

### Muốn hiểu vì sao kiến trúc chọn như hiện tại

- `docs/adr/README.md`;
- các ADR tương ứng trong `docs/adr/`.

### Muốn xem lịch sử phát triển và benchmark

- `progress.md`;
- lịch sử Git.

## 21. Quy tắc về trạng thái tài liệu

Mọi đặc tả quan trọng phải được hiểu theo bốn trạng thái:

### HIỆN HÀNH

Đã triển khai và có bằng chứng trong code/config/schema/test/runtime artefact.

### MỤC TIÊU

Đã chấp thuận về hướng hoặc đang được đặc tả, nhưng chưa được triển khai đầy đủ.

### TƯƠNG LAI

Ý tưởng hoặc hướng có điều kiện, chưa thuộc phạm vi triển khai cam kết.

### LỊCH SỬ

Mô tả khảo sát, benchmark, POC, quyết định hoặc trạng thái ở một thời điểm trước.

Không được lấy nội dung LỊCH SỬ để phủ định runtime HIỆN HÀNH.

Không được mô tả MỤC TIÊU hoặc TƯƠNG LAI như thể đã có implementation.

## 22. Kết luận định hướng

Có thể tóm tắt sự tiến hóa của dự án bằng hai câu:

**Hiện tại:**

> Đưa AI tới đúng nguồn, đúng phiên bản và đúng ngữ cảnh.

**Hướng nâng cấp:**

> Không cho AI đi xa hơn những gì nguồn thực sự cho phép kết luận.

Hai mục tiêu này bổ sung nhau. Lớp kiểm chứng mới phải được xây trên retrieval
và Connector hiện tại, không thay thế những phần đã hoạt động tốt.
