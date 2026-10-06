# Thiết kế lớp kiểm chứng nghiên cứu

> Trạng thái tài liệu: **MỤC TIÊU**
>
> Phạm vi: thiết kế chuẩn cho lớp kiểm chứng nghiên cứu sẽ được xây trên hệ
> retrieval/Connector hiện hành.
>
> Tài liệu này **không mô tả tính năng đã triển khai đầy đủ**. Kiến trúc hiện
> hành nằm trong `docs/ARCHITECTURE.md`; yêu cầu có mã nằm trong
> `docs/REQUIREMENTS.md`; tiêu chí nghiệm thu nằm trong
> `docs/ACCEPTANCE.md`.

## 1. Ba trạng thái phải được giữ riêng

### HIỆN HÀNH

Đã có và đang được code/config/schema/tests/runtime artefact hỗ trợ:

```text
pinned upstream sources
→ deterministic parsers
→ SQLite / FTS / relations / variants / lemmas
→ local retrieval hoặc production locator
→ pinned upstream source
→ context / provenance
→ câu trả lời theo quy tắc AGENTS/SKILL
```

### MỤC TIÊU

Vòng nâng cấp v1 sẽ bổ sung:

```text
Evidence Record
→ kiểm chứng trích dẫn
→ Atomic Claim
→ kiểm chứng claim–evidence
→ kiểm tra độc lập nguồn
→ phản chứng bắt buộc trong research mode
→ Final Claim Gate
→ Research Run
```

### TƯƠNG LAI

Chỉ xem xét sau v1 nếu có nhu cầu đo được:

- đường truy xuất Connector sâu hơn khi locator hữu hạn không đủ;
- hỗ trợ remote CJK tùy ý bằng một cơ chế khác production `terms/cjk`;
- job từ xa/GitHub Action xác định để chạy retrieval nặng rồi trả artefact.

Những ý này **không phải requirement v1** và không được mô tả như runtime hiện
tại.

## 2. Khoảng trống mà lớp mới phải giải quyết

Hệ thống hiện hành đã làm tốt:

- định vị nguồn;
- truy nguyên SHA/path;
- tách `evidence_class`, `text_role`, `witness`;
- mở source upstream;
- đọc context;
- relation/variant workflows;
- fail-closed khi không đủ corpus evidence.

Nhưng vẫn còn một khoảng trống sau khi source đã được đọc:

> AI có thể diễn đạt một claim mạnh hơn điều bằng chứng thực sự hỗ trợ.

Các lỗi cần chặn gồm:

- trích dẫn lệch một từ nhưng vẫn đặt trong ngoặc kép;
- paraphrase bị trình bày như direct quote;
- claim lịch sử được suy từ một câu trong văn bản quy phạm;
- metadata song hành bị biến thành textual proof;
- hai citation cùng phụ thuộc một nguồn bị đếm như hai nguồn độc lập;
- claim bị phản chứng nhưng vẫn lọt vào kết luận;
- phần tổng hợp tự sinh thêm một kết luận chưa qua kiểm.

## 3. Nguyên tắc thiết kế

### 3.1. Bổ sung, không thay thế

Lớp kiểm chứng phải nằm **sau** retrieval/source opening hiện hành.

Không:

- viết lại SQLite/FTS;
- thay production locator;
- đưa vector DB vào chỉ vì có lớp verification;
- biến GitHub Action thành “AI suy luận”;
- tạo một scholarly score duy nhất thay cho evidence review.

### 3.2. Pointer không được nâng cấp thành Evidence Record

Pointer chỉ là chỉ dẫn mở source.

Evidence Record chỉ được tạo sau khi source thật đã được mở và nội dung liên
quan đã được đọc.

### 3.3. Claim là đơn vị được kiểm

Không kiểm một đoạn văn tổng hợp dài như một khối.

Mỗi kết luận quan trọng phải được tách thành Atomic Claim đủ nhỏ để:

- nối tới evidence;
- tìm phản chứng;
- đánh giá support;
- chấp nhận/hạ mức/từ chối.

### 3.4. Retrieval score và support level là hai lớp khác nhau

Retrieval score trả lời:

> ứng viên nào nên mở trước?

Claim verification trả lời:

> evidence đã mở hỗ trợ claim này đến mức nào?

Không ánh xạ trực tiếp score sang DIRECT/STRONG/WEAK.

## 4. Pipeline MỤC TIÊU

```text
question
→ scope
→ search hypotheses
→ retrieval hiện hành
→ locator/local FTS
→ pinned source
→ context
→ Evidence Record
→ quote verification
→ Atomic Claim
→ claim–evidence verification
→ independent-source analysis
→ counterevidence pass
→ revise / downgrade / reject
→ Final Claim Gate
→ accepted claim set
→ synthesis
→ final validation
→ Research Run Manifest
→ answer
```

Các bước retrieval phía trước giữ nguyên fast path hiện tại.

## 5. Hai chế độ nghiên cứu MỤC TIÊU

### 5.1. Quick mode

Dùng cho lookup hẹp:

- một thuật ngữ;
- một segment;
- một work ID;
- một relation/parallel cụ thể;
- kiểm một quotation nhỏ.

Pipeline tối thiểu:

```text
retrieval
→ source
→ context
→ Evidence Record
→ quote/provenance check
→ answer
```

Quick mode không bắt buộc chạy toàn bộ phản chứng đa nguồn nếu câu hỏi không có
tính khái quát/so sánh, nhưng vẫn phải fail-closed.

### 5.2. Research mode

Dùng cho:

- câu hỏi chủ đề;
- so sánh nhiều truyền thống;
- lịch sử;
- tranh luận;
- nghiên cứu phục vụ viết sách;
- claim tổng quát;
- câu hỏi cần nhiều witness.

Research mode bắt buộc:

- Evidence Record;
- Atomic Claim;
- claim verification;
- phân tích độc lập nguồn;
- counterevidence pass;
- Final Claim Gate;
- Research Run.

## 6. Evidence Record

### 6.1. Ý nghĩa

Evidence Record là biểu diễn có cấu trúc của **nguồn đã thực sự được mở và đọc**.

Nó không phải:

- pointer;
- search hit chưa mở;
- title;
- TOC;
- relation row;
- bridge row;
- metadata discovery candidate.

### 6.2. Trường MỤC TIÊU

Một Evidence Record v1 cần tối thiểu:

```text
evidence_id
run_id
corpus
repository
source_sha
source_blob_sha
source_path
indexed_source_path
work_id
segment_id
sequence_no
language
evidence_class
text_role
witness
quotation
context
quote_verification_status
retrieval_query
match_reasons
relation_ids
limitations
```

Không phải mọi trường locator đều bắt buộc có giá trị, nhưng:

- repository/source SHA/path phải đủ để truy ngược;
- work/segment/sequence phải được giữ khi nguồn có;
- `evidence_class`, `text_role`, `witness` phải giữ riêng;
- quotation/context phải phản ánh source đã mở, không lấy từ pointer.

### 6.3. Evidence Gate

Trước khi Evidence Record được dùng:

1. source repository phải đúng;
2. source SHA/blob phải phù hợp;
3. source path phải tồn tại;
4. vị trí work/segment phải có thể giải thích được;
5. text role/witness không được bị đánh tráo;
6. nếu có direct quote, trạng thái quote phải được kiểm.

Nếu gate thất bại, Evidence Record không được dùng như bằng chứng đã xác minh.

## 7. Kiểm chứng trích dẫn

### 7.1. Trạng thái

`quote_verification_status` dùng taxonomy:

- `VERIFIED_EXACT`;
- `VERIFIED_NORMALIZED`;
- `PARAPHRASE`;
- `UNVERIFIED`;
- `QUOTE_MISMATCH`.

### 7.2. Ý nghĩa

#### VERIFIED_EXACT

Chuỗi trích dẫn khớp nguyên văn theo cách so sánh exact được định nghĩa cho
source.

#### VERIFIED_NORMALIZED

Khớp sau các phép chuẩn hóa không thay đổi nội dung từ vựng, ví dụ normalization
Unicode/whitespace đã được khai báo.

Không được dùng trạng thái này để che:

- đổi từ;
- bỏ từ có nghĩa;
- đảo thứ tự;
- thêm nội dung;
- dịch lại.

#### PARAPHRASE

Nội dung là diễn giải có căn cứ nhưng không phải nguyên văn.

Không đặt trong ngoặc kép như direct quote.

#### UNVERIFIED

Chưa có đủ điều kiện để kiểm quotation.

Không trình bày như quotation đã xác minh.

#### QUOTE_MISMATCH

Quotation không khớp source theo contract.

Phải:

- sửa quote;
- hạ thành paraphrase nếu evidence vẫn hỗ trợ;
- hoặc loại bỏ.

## 8. Atomic Claim

### 8.1. Trường MỤC TIÊU

```text
claim_id
run_id
text
claim_type
status
supporting_evidence_ids
counter_evidence_ids
verification_status
independence_status
limitations
```

### 8.2. Loại claim

`claim_type` tối thiểu:

- `textual` — câu chữ/nội dung có trong văn bản;
- `historical` — mệnh đề về lịch sử;
- `relationship` — quan hệ/parallel/alignment;
- `comparative` — so sánh nhiều witness/truyền thống;
- `interpretive` — diễn giải;
- `empirical` — mệnh đề thực nghiệm;
- `metaphysical` — mệnh đề siêu hình.

Loại claim ảnh hưởng loại evidence nào có thể hỗ trợ nó.

Ví dụ:

- textual witness có thể DIRECT cho một claim textual;
- một passage quy phạm không tự DIRECT cho claim “mọi người lịch sử đều làm X”;
- một nghiên cứu thực nghiệm không tự chứng minh claim metaphysical.

## 9. Claim–Evidence Verification

### 9.1. Taxonomy support

`verification_status`:

- `DIRECT`;
- `STRONG`;
- `WEAK`;
- `UNSUPPORTED`;
- `CONTRADICTED`.

### 9.2. Quy tắc xuất bản

#### DIRECT

Evidence trực tiếp hỗ trợ đúng claim và đúng loại claim.

#### STRONG

Nhiều evidence hoặc inference hẹp hỗ trợ mạnh, nhưng không phải direct identity.

#### WEAK

Có tín hiệu hỗ trợ nhưng còn giới hạn đáng kể.

Chỉ được dùng khi câu trả lời nêu rõ giới hạn; không được viết như fact chắc chắn.

#### UNSUPPORTED

Evidence hiện có không đủ.

Không được vào accepted claim set.

#### CONTRADICTED

Có evidence trực tiếp/xung đột đủ mạnh làm claim không thể được trình bày như
kết luận đã xác lập.

Không được vào accepted claim set ở dạng ban đầu.

## 10. Phân tích độc lập nguồn

Nhiều citation không tự động là nhiều nguồn độc lập.

`independence_status` tối thiểu:

- `independent`;
- `partially_dependent`;
- `same_source_family`;
- `derived_from`;
- `uncertain`.

Ví dụ:

- BuddhaNexus Chinese derived từ CBETA không được tính như một witness độc lập
  với chính CBETA chỉ vì nằm ở repository khác;
- alignment và bản gốc mà alignment dẫn xuất từ đó có quan hệ phụ thuộc cần ghi
  nhận.

Nếu chưa xác định được dependency, dùng `uncertain`, không tự nâng thành
`independent`.

## 11. Counterevidence Pass

### 11.1. Bắt buộc trong Research mode

Với mỗi claim quan trọng, hệ thống phải chủ động tìm ít nhất các nhóm phù hợp:

- witness khác;
- variant;
- exception;
- parallel không khớp;
- nguồn cùng cấp nhưng xung đột;
- dependency làm yếu “nhiều nguồn”;
- điều kiện giới hạn phạm vi claim.

### 11.2. Counterevidence phải có tác dụng

Kết quả phản chứng có thể làm claim:

- giữ nguyên;
- sửa wording;
- thu hẹp scope;
- hạ DIRECT → STRONG/WEAK;
- chuyển UNSUPPORTED;
- chuyển CONTRADICTED;
- reject.

Counterevidence không được chỉ là một đoạn “ý kiến trái chiều” trang trí ở cuối.

### 11.3. “Không tìm thấy phản chứng”

Chỉ được nói:

> không tìm thấy phản chứng trong phạm vi corpus/truy vấn đã kiểm.

Không được suy:

> không tồn tại phản chứng.

## 12. Final Claim Gate

Trước synthesis, hệ thống tạo accepted claim set.

Một claim chỉ qua gate khi:

- có supporting evidence;
- Evidence Record hợp lệ;
- quotation phù hợp với trạng thái được trình bày;
- verification không phải UNSUPPORTED/CONTRADICTED;
- research mode đã xử lý counterevidence cần thiết;
- limitations quan trọng đã được gắn.

Synthesis chỉ được dùng accepted claim set.

Phần tổng hợp **không được tự sinh thêm claim quan trọng mới** chưa qua gate.

## 13. Research Run Manifest

### 13.1. Mục đích

Research Run ghi lại đường đi nghiên cứu đủ để rà soát và tái tạo ở mức thực tế.

Nó không nhằm lưu chain-of-thought nội bộ của mô hình.

### 13.2. Trường MỤC TIÊU

```text
run_id
question
created_at
mode
scope
main_repository
main_repository_commit
remote_repository
remote_repository_commit
remote_root
source_revisions
search_hypotheses
queries
evidence_ids
candidate_claim_ids
accepted_claim_ids
rejected_claim_ids
counterevidence_performed
counterevidence_summary
limitations
answer_artifact
model_identifier
verification_config
```

`model_identifier` và `verification_config` có thể optional trong v1 nếu hệ
thực thi chưa cung cấp ổn định, nhưng provenance corpus/repo/commit không được
optional trong Research mode.

### 13.3. Tái tạo truy xuất và tái tạo nghiên cứu

Phải phân biệt:

- **tái tạo truy xuất**: cùng source/index/query cho candidate tương tự;
- **tái tạo nghiên cứu**: biết source nào đã mở, claim nào được tạo, evidence nào
  hỗ trợ/chống, claim nào bị loại.

Không tuyên bố tái tạo toàn bộ reasoning nội bộ của mô hình.

## 14. Hợp đồng câu trả lời MỤC TIÊU

Research mode nên xuất theo cấu trúc:

1. **Kết luận chính**;
2. **Bằng chứng theo corpus/nhân chứng**;
3. **Song hành và dị bản**;
4. **Phản chứng / dữ liệu làm yếu claim**;
5. **Diễn giải**;
6. **Mức chắc chắn và giới hạn**;
7. **Provenance**;
8. **Research Run ID** nếu có.

Câu trả lời cuối chỉ tổng hợp accepted claims.

## 15. Tích hợp với Local mode

Không đổi retrieval engine.

```text
CLI search/context/evidence
→ source/provenance
→ Evidence Record builder
→ verifier
→ claim layer
```

Có thể tái sử dụng:

- record ID;
- context;
- provenance;
- variants;
- relations;
- source path/SHA;
- text role/witness.

## 16. Tích hợp với Connector mode

Không đổi production locator v1.

```text
production pointer
→ open pinned upstream source
→ Evidence Record
→ verifier
→ claim layer
```

Pointer row tuyệt đối không được biến trực tiếp thành Evidence Record.

Nếu Connector không mở được source thật, claim cần wording đó phải fail-closed.

## 17. Lưu trữ artefact verification

V1 cần một format máy đọc cho:

- Evidence Records;
- Atomic Claims;
- Research Runs.

**Chưa quyết định ở tài liệu này** chúng phải nằm trong SQLite, JSON/JSONL hay
một thư mục artefact riêng.

Quyết định implementation phải:

- không sửa upstream source;
- tái tạo được;
- dễ test;
- giữ stable IDs;
- không làm chậm fast path Quick mode không cần thiết.

Nếu quyết định storage có ảnh hưởng kiến trúc đáng kể, tạo ADR riêng.

## 18. Golden Research Tests

Test hiện tại chứng minh engine/software behavior nhưng chưa đủ cho chất lượng
nghiên cứu claim-level.

V1 phải có Golden Research Tests gồm tối thiểu các case cố ý sai:

1. quote đổi một từ;
2. source SHA sai;
3. segment sai;
4. translation note giả làm root text;
5. relation/parallel metadata giả làm textual proof;
6. hai nguồn phụ thuộc giả làm hai witness độc lập;
7. claim mạnh hơn evidence;
8. Research mode bỏ counterevidence pass;
9. AI tự tạo Pāli ↔ Chinese equivalence không có repository evidence;
10. synthesis sinh claim mới chưa qua Final Claim Gate.

Golden case phải định nghĩa:

- question;
- scope;
- expected evidence;
- evidence không được dùng làm primary;
- counterevidence đã biết;
- forbidden claims;
- expected accepted/rejected claim pattern;
- expected limitations.

## 19. Tiêu chí hoàn thành v1

Lớp verification v1 chỉ được coi là hoàn thành khi:

- không regression retrieval hiện hành;
- production locator vẫn deterministic;
- pointer vẫn không phải evidence;
- Evidence Record có provenance đầy đủ;
- quote sai bị phát hiện;
- claim không evidence bị reject;
- UNSUPPORTED/CONTRADICTED không lọt accepted set;
- Research mode thực hiện counterevidence pass;
- dependency giữa nguồn được biểu diễn;
- claim → evidence traceable;
- Research Run có thể rà soát;
- checked/unexamined scope rõ ràng;
- Golden Research Tests ổn định;
- fail-closed vẫn được giữ.

## 20. TƯƠNG LAI — Deep Connector fallback

> Trạng thái: **TƯƠNG LAI — không thuộc v1**

Nếu sau khi có lớp verification, production locator hữu hạn vẫn là bottleneck
thực tế, có thể xem xét một worker/job xác định từ xa.

Ví dụ khái niệm:

```text
Connector request
→ deterministic remote retrieval job
→ pinned corpus/index snapshot
→ result artefact có provenance
→ Connector đọc result
→ source opening
→ Evidence Record
```

GitHub Action hoặc worker tương tự chỉ được dùng như:

- retrieval worker;
- test runner;
- artefact generator.

Nó **không** là “AI brain”, không tự tổng hợp kết luận và không được bỏ qua
Evidence/Claim gates.

Chỉ triển khai khi có dữ liệu chứng minh locator hiện tại không đủ cho use case
quan trọng, đặc biệt CJK arbitrary retrieval.

## 21. Ngoài phạm vi v1

Không đưa vào v1 nếu không có requirement mới:

- vector database;
- embeddings toàn corpus;
- knowledge graph toàn diện;
- Kubernetes;
- microservices;
- distributed DB;
- autonomous multi-agent research;
- universal semantic search;
- universal numeric confidence score.

## 22. Quan hệ với tài liệu khác

- `docs/PROJECT_SPEC.md`: tóm tắt cấp dự án và ranh giới trạng thái;
- `docs/REQUIREMENTS.md`: yêu cầu có mã;
- `docs/ACCEPTANCE.md`: bằng chứng/test để chuyển MỤC TIÊU → HIỆN HÀNH;
- `docs/ARCHITECTURE.md`: kiến trúc đã triển khai;
- `AGENTS.md`: luật nghiên cứu luôn áp dụng;
- `.codex/skills/buddhist-corpus-research/SKILL.md`: hành vi agent hiện hành;
- `docs/REMOTE_AGENT.md`: runtime Connector hiện hành.

Nếu tài liệu này và code hiện hành khác nhau, khác biệt đó **không tự động là
bug của code**: tài liệu này đang mô tả MỤC TIÊU. Chỉ khi requirement tương ứng
được chuyển sang HIỆN HÀNH thì implementation mới phải đáp ứng đầy đủ.
