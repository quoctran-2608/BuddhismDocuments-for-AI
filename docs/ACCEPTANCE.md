# Tiêu chí nghiệm thu và ánh xạ kiểm chứng

> Trạng thái tài liệu: **HIỆN HÀNH**
>
> Vai trò: nối requirement có mã tới cách kiểm chứng, mã nguồn, cấu hình và test.
>
> Lưu ý quan trọng: tài liệu này phân biệt **có bằng chứng tự động** với
> **mới có bằng chứng cấu trúc/quy trình**. Không được hiểu “có dòng trong bảng”
> là mọi yêu cầu đều đã có test tự động.

## 1. Mức bằng chứng nghiệm thu

- **TỰ ĐỘNG**: có test hiện hữu kiểm hành vi chính;
- **CẤU TRÚC**: có thể kiểm bằng config/schema/manifest/code tĩnh;
- **QUY TRÌNH**: là luật vận hành/AI behavior, hiện chưa có test máy đầy đủ;
- **RÀ SOÁT**: cần kiểm bằng đối chiếu tài liệu hoặc kiểm tra thủ công có chủ đích;
- **CHƯA TRIỂN KHAI**: requirement MỤC TIÊU, chưa được nghiệm thu.

Repo hiện có 45 test method trong 6 file test chính:

- `tests/test_acceptance.py`: 9;
- `tests/test_cbeta_resolver.py`: 10;
- `tests/test_cjk_substring_search.py`: 1;
- `tests/test_normalization.py`: 7;
- `tests/test_remote_access.py`: 15;
- `tests/test_text_roles.py`: 3.

Con số này mô tả test hiện có trong repo; tài liệu này không tuyên bố chúng đã
được chạy lại trong phiên chuẩn hóa docs hiện tại.

---

# 2. Nguồn và tính bất biến

| Requirement | Mức | Bằng chứng / cách nghiệm thu |
|---|---|---|
| REQ-SRC-001 | CẤU TRÚC + TỰ ĐỘNG một phần | `manifest.json`; `cli.py::source_status`; acceptance/local source checks trong quy trình |
| REQ-SRC-002 | QUY TRÌNH | `AGENTS.md` quy định tầng nguồn bất biến; rà soát để xác nhận submodule nguồn không bị chỉnh sửa |
| REQ-SRC-003 | CẤU TRÚC | `bin/buddhist-corpus status` so manifest SHA với local SHA và trả lỗi nếu mismatch |
| REQ-SRC-004 | CẤU TRÚC | `config/corpus-sources.json` phải có mapping cho toàn bộ corpus được hỗ trợ |

### Tiêu chí tối thiểu

REQ-SRC-001 đạt khi:

1. `manifest.json` có đúng 13 source entries;
2. mỗi entry có `commit_sha`;
3. local `status` có thể so SHA;
4. không có source web/model memory được coi như corpus thứ 14.

REQ-SRC-003 không đạt nếu source contract mismatch nhưng command vẫn báo success.

---

# 3. Dữ liệu dẫn xuất

| Requirement | Mức | Bằng chứng / cách nghiệm thu |
|---|---|---|
| REQ-DER-001 | CẤU TRÚC | `.gitignore`, docs, schema/build path; DB nằm dưới `derived/` và không được dùng như source-of-origin |
| REQ-DER-002 | TỰ ĐỘNG + CẤU TRÚC | schema có `source_path/source_sha`; `test_evidence_bundles_record_context_provenance_and_variants`; text-role/provenance tests |
| REQ-DER-003 | TỰ ĐỘNG | `test_profile_sensitive_parser_state`; parser/search index version state |
| REQ-DER-004 | TỰ ĐỘNG + CẤU TRÚC | `test_cjk_fts_vocabulary_analysis_is_deterministic_and_read_only`; CJK vocabulary docs/manifest |

REQ-DER-002 đạt khi một record có thể truy về file và SHA nguồn, không chỉ về DB
row ID.

---

# 4. Truy xuất và xếp hạng

| Requirement | Mức | Bằng chứng / test |
|---|---|---|
| REQ-RET-001 | TỰ ĐỘNG | `test_term_pointer_candidates_reuse_search_per_corpus`; production exporter dùng `score_record_match` |
| REQ-RET-002 | TỰ ĐỘNG | `test_remote_export_is_deterministic_and_preserves_evidence`; `test_pointer_poc_is_deterministic_and_never_exports_raw_text`; benchmark/production deterministic tests |
| REQ-RET-003 | TỰ ĐỘNG | `test_preserves_diacritics_in_primary_normalization`; `test_explicit_diacritic_fold_is_separate` |
| REQ-RET-004 | TỰ ĐỘNG | `test_pali_inflection_uses_corpus_lemma` |
| REQ-RET-005 | TỰ ĐỘNG | `test_middle_substring_uses_trigram_candidates_for_long_cbeta_text` |
| REQ-RET-006 | QUY TRÌNH | AGENTS/PROJECT_SPEC; chưa có Golden Research Test kiểm việc AI không biến rank thành scholarly truth |

### Tiêu chí xếp hạng

REQ-RET-001 không đạt nếu remote production tự tạo một hệ score học thuật khác
với local retrieval.

REQ-RET-006 hiện là khoảng trống test nghiên cứu: code có rank đúng nhưng chưa có
test máy bảo đảm AI không diễn giải rank quá mức.

---

# 5. Bằng chứng và provenance

| Requirement | Mức | Bằng chứng / test |
|---|---|---|
| REQ-EVD-001 | TỰ ĐỘNG một phần + QUY TRÌNH | pointer tests chứng minh no raw text; AGENTS/REMOTE_AGENT bắt buộc mở source; chưa có test end-to-end bắt AI quote source thay vì pointer |
| REQ-EVD-002 | TỰ ĐỘNG | `test_evidence_bundles_record_context_provenance_and_variants`; provenance outputs; pointer provenance tests |
| REQ-EVD-003 | TỰ ĐỘNG một phần | `test_search_defaults_stay_plain_and_options_add_evidence`; evidence/context APIs; AI có đọc đủ context hay không vẫn là QUY TRÌNH |
| REQ-EVD-004 | TỰ ĐỘNG một phần + QUY TRÌNH | `test_buddhanexus_candidate_resolves_to_cbeta_primary`; rules trong AGENTS |
| REQ-EVD-005 | QUY TRÌNH | evidence hierarchy trong AGENTS/config; chưa có Golden Research Test cho source-class conflict |

### Khoảng trống cần giữ rõ

Các test hiện tại chứng minh hệ thống **cung cấp được provenance/context**, nhưng
chưa chứng minh đầy đủ AI **luôn dùng chúng đúng cách**. Đây là một trong các lý
do lớp verification mục tiêu tồn tại.

---

# 6. Nhân chứng và vai trò văn bản

| Requirement | Mức | Bằng chứng / test |
|---|---|---|
| REQ-WIT-001 | TỰ ĐỘNG + CẤU TRÚC | schema tách fields; `test_legacy_migration_and_bilara_roles`; provenance test |
| REQ-WIT-002 | TỰ ĐỘNG | `test_84000_note_isolation_parent_relation_and_provenance`; `test_note_exclusion_preserves_inline_text_and_note_tail` |
| REQ-WIT-003 | CẤU TRÚC + TỰ ĐỘNG gián tiếp | `compare()` trả `harmonized: false`; acceptance/variant workflows |
| REQ-WIT-004 | QUY TRÌNH | text_role được cung cấp và test; chưa có Golden Research Test chống việc AI quote translation như root |

REQ-WIT-002 đạt khi prose của note không còn nằm trong
`translation_main`, note có role riêng và vẫn giữ provenance cùng nguồn.

---

# 7. Quan hệ, song hành và cầu nối

| Requirement | Mức | Bằng chứng / test |
|---|---|---|
| REQ-REL-001 | QUY TRÌNH + TỰ ĐỘNG gián tiếp | data model tách relations khỏi records; các test quy trình SC↔CBETA |
| REQ-REL-002 | TỰ ĐỘNG | `test_nikaya_agama_parallel_relation`; `test_nikaya_agama_resolves_through_local_cbeta_bridge` |
| REQ-REL-003 | TỰ ĐỘNG | 10 resolver tests, đặc biệt non-overlap/reversed/malformed cases |
| REQ-REL-004 | QUY TRÌNH | AGENTS cross-language guardrails; chưa có Golden Research Test |

Các test resolver bắt buộc giữ fail-closed cho:

- reversed input range;
- malformed input identifier;
- malformed record locator;
- non-overlapping segment range.

---

# 8. GitHub Connector và production locator

| Requirement | Mức | Bằng chứng / test |
|---|---|---|
| REQ-CON-001 | CẤU TRÚC | `config/remote-corpus.json`; REMOTE_AGENT/SKILL yêu cầu đọc config |
| REQ-CON-002 | CẤU TRÚC + QUY TRÌNH | project spec/architecture/remote docs; remote manifest là derived artefact |
| REQ-CON-003 | CẤU TRÚC + QUY TRÌNH | hash locator code/docs; không có dependency Code Search trong production routing |
| REQ-CON-004 | TỰ ĐỘNG | `test_pointer_poc_is_deterministic_and_never_exports_raw_text`; `test_pointer_benchmark_is_deterministic_and_reports_pointer_invariants`; production test |
| REQ-CON-005 | TỰ ĐỘNG | `test_source_blob_sha_matches_pinned_local_source_file`; evidence/pointer tests |
| REQ-CON-006 | TỰ ĐỘNG | normalization tests + production exporter tests |
| REQ-CON-007 | TỰ ĐỘNG | `test_pointer_production_v1_is_resumable_and_preserves_original_ids` kiểm `Dhp` và `dhp` riêng |
| REQ-CON-008 | TỰ ĐỘNG một phần + CẤU TRÚC | locator generation code; deterministic pointer tests |
| REQ-CON-009 | TỰ ĐỘNG | production test kiểm `terms/latin`, `ids`, và `terms_cjk.materialized=false` |
| REQ-CON-010 | TỰ ĐỘNG | `test_pointer_selection_keeps_best_distinct_work_file_per_corpus`; `test_term_pointer_candidates_reuse_search_per_corpus` |
| REQ-CON-011 | TỰ ĐỘNG | `test_pointer_production_v1_is_resumable_and_preserves_original_ids` |

### Nghiệm thu production locator v1

Một artefact production hợp lệ tối thiểu phải:

1. tự nhận `artifact_kind = pointer_production_v1`;
2. không phải proof of concept;
3. không export raw text;
4. materialize đúng namespace đã thiết kế;
5. giữ original identifier spelling;
6. không có duplicate query/corpus/work/source theo invariant đã định;
7. bảo toàn source locator;
8. có thể tái sinh deterministic;
9. không bị artefact staging chưa hoàn tất ghi đè.

Production artefact hiện tại công bố:

- 26.547 key Latin;
- 32.498 ID;
- 59.045 key tổng;
- 706.011 pointer;
- 0 raw-text field.

Các con số production phải lấy từ remote production summary, không lấy benchmark
lịch sử làm nguồn chuẩn.

---

# 9. Đóng thất bại và giới hạn

| Requirement | Mức | Bằng chứng / test |
|---|---|---|
| REQ-FAIL-001 | QUY TRÌNH | AGENTS local offline rule; chưa có sandbox/network-denial test |
| REQ-FAIL-002 | QUY TRÌNH | AGENTS Connector allowlist; chưa có automated agent-policy test |
| REQ-FAIL-003 | TỰ ĐỘNG | `test_fail_closed_when_query_has_no_evidence`; resolver fail-closed tests |
| REQ-FAIL-004 | CẤU TRÚC + QUY TRÌNH | production manifest không có `terms/cjk`; docs tuyên bố coverage limit |

REQ-FAIL-003 đạt khi query không có evidence trả trạng thái fail-closed và thông
điệp thiếu dữ liệu, thay vì fabricated result.

---

# 10. Quản trị tài liệu

| Requirement | Mức | Cách nghiệm thu |
|---|---|---|
| REQ-DOC-001 | CẤU TRÚC | `docs/DOCUMENTATION_GOVERNANCE.md` tồn tại và có authority matrix |
| REQ-DOC-002 | CẤU TRÚC + RÀ SOÁT | Project Spec và Requirements tách HIỆN HÀNH/MỤC TIÊU/LỊCH SỬ |
| REQ-DOC-003 | RÀ SOÁT | README sau giai đoạn đồng bộ phải là cửa vào, không tuyên bố chi tiết trái config/schema |
| REQ-DOC-004 | RÀ SOÁT | progress/survey phải được gắn đúng vai trò lịch sử, không giả làm trạng thái hiện tại |

REQ-DOC-003 và REQ-DOC-004 đã được xử lý trong Giai đoạn 6: README đã được
viết lại thành cửa vào hiện hành; `progress.md` và `CORPUS_SURVEY.md` đã được
gắn nhãn LỊCH SỬ rõ ràng. Giai đoạn 8 sẽ kiểm toán chéo lần cuối.

---

# 11. Ma trận test hiện hữu

## 11.1. Acceptance tests

`tests/test_acceptance.py`

- `test_pali_inflection_uses_corpus_lemma`
  - REQ-RET-004;
- `test_chinese_phrase_prefers_primary_cbeta`
  - REQ-EVD-004 / evidence hierarchy behavior;
- `test_nikaya_agama_parallel_relation`
  - REQ-REL-001/002;
- `test_nikaya_agama_resolves_through_local_cbeta_bridge`
  - REQ-REL-002;
- `test_cbeta_resolver_matches_suffix_case_insensitively`
  - REQ-REL-003;
- `test_84000_work_has_toh_metadata_and_rdf_relation`
  - REQ-REL-001;
- `test_buddhanexus_candidate_resolves_to_cbeta_primary`
  - REQ-EVD-004;
- `test_fail_closed_when_query_has_no_evidence`
  - REQ-FAIL-003;
- `test_variant_workflow_returns_local_witnesses`
  - REQ-WIT-003.

## 11.2. CBETA resolver tests

`tests/test_cbeta_resolver.py`

Nhóm này là bằng chứng chính cho REQ-REL-003:

- range từ relation IDs;
- granular segment ID;
- CBETA TEI;
- work dài không bị truncate;
- invalid relation IDs fallback;
- relation IDs hợp lệ ưu tiên;
- non-overlap fail-closed;
- reversed range fail-closed;
- malformed record locator fail-closed;
- malformed input fail-closed.

## 11.3. CJK substring

`tests/test_cjk_substring_search.py`

- `test_middle_substring_uses_trigram_candidates_for_long_cbeta_text`
  - REQ-RET-005.

## 11.4. Normalization

`tests/test_normalization.py`

Bảo vệ:

- REQ-RET-003;
- REQ-CON-006;
- CBETA/Taishō normalization;
- profile-sensitive parser state;
- lexical relative source path.

## 11.5. Remote access

`tests/test_remote_access.py`

Đây là nhóm chính cho Connector/artefact:

- evidence bundle;
- search options;
- deterministic remote export;
- safe replacement behavior;
- WAL visibility;
- raw-text-free pointer POC;
- distinct work/source selection;
- shared ranking;
- source blob SHA;
- benchmark invariants;
- compact POC reconstruction;
- repetition analysis read-only;
- key-universe analysis read-only;
- CJK vocabulary analysis read-only;
- production v1 resumable/original IDs.

## 11.6. Text roles

`tests/test_text_roles.py`

Bảo vệ REQ-WIT-001/002:

- migration và Bilara roles;
- 84000 note isolation + parent relation + provenance;
- loại note mà vẫn giữ inline text và note tail đúng.

---

# 12. Yêu cầu MỤC TIÊU: trạng thái nghiệm thu hiện tại

Toàn bộ nhóm dưới đây đang là **CHƯA TRIỂN KHAI** và chưa được coi là pass.
Semantics mục tiêu chi tiết nằm trong `docs/RESEARCH_VERIFICATION_DESIGN.md`:

| Requirement | Trạng thái nghiệm thu hiện tại | Test mục tiêu cần có |
|---|---|---|
| REQ-VER-001 | CHƯA TRIỂN KHAI | pointer/title/relation không được nâng thành Evidence Record |
| REQ-VER-002 | CHƯA TRIỂN KHAI | Evidence Record thiếu provenance phải bị reject |
| REQ-VER-003 | CHƯA TRIỂN KHAI | sai SHA/path/segment phải fail gate |
| REQ-VER-004 | CHƯA TRIỂN KHAI | kết luận phức hợp phải được tách thành claim có thể kiểm |
| REQ-VER-005 | CHƯA TRIỂN KHAI | claim không evidence bị reject |
| REQ-VER-006 | CHƯA TRIỂN KHAI | support status chỉ dùng taxonomy định tính |
| REQ-VER-007 | CHƯA TRIỂN KHAI | UNSUPPORTED không qua final gate |
| REQ-VER-008 | CHƯA TRIỂN KHAI | CONTRADICTED không được xuất như kết luận đã được xác lập |
| REQ-VER-009 | CHƯA TRIỂN KHAI | retrieval score không tự biến thành support level |
| REQ-VER-010 | CHƯA TRIỂN KHAI | synthesis không sinh claim mới ngoài accepted set |
| REQ-VER-011 | CHƯA TRIỂN KHAI | claim thiếu `claim_type` bị reject; loại evidence không phù hợp không được nâng support |
| REQ-QTE-001 | CHƯA TRIỂN KHAI | exact/normalized/paraphrase/unverified/mismatch classification |
| REQ-QTE-002 | CHƯA TRIỂN KHAI | quote sai một từ không được xuất direct quote |
| REQ-QTE-003 | CHƯA TRIỂN KHAI | paraphrase không được gắn ngoặc kép |
| REQ-CTR-001 | CHƯA TRIỂN KHAI | research mode thiếu counter-pass phải fail |
| REQ-CTR-002 | CHƯA TRIỂN KHAI | “no counterevidence” phải kèm scope |
| REQ-CTR-003 | CHƯA TRIỂN KHAI | nguồn phụ thuộc không được tính như độc lập |
| REQ-CTR-004 | CHƯA TRIỂN KHAI | counterevidence có thể downgrade/reject claim |
| REQ-RUN-001 | CHƯA TRIỂN KHAI | manifest completeness |
| REQ-RUN-002 | CHƯA TRIỂN KHAI | retrieval/research reproducibility tách riêng |
| REQ-RUN-003 | CHƯA TRIỂN KHAI | checked/unexamined scope |
| REQ-RUN-004 | CHƯA TRIỂN KHAI | claim → evidence traceability |
| REQ-RUN-005 | CHƯA TRIỂN KHAI | counterevidence status queryable |

---

# 13. Golden Research Tests cần bổ sung ở giai đoạn nâng cấp

Các test hiện tại chủ yếu kiểm engine/software. Lớp nâng cấp phải có một bộ
Golden Research Tests kiểm chất lượng nghiên cứu.

Mỗi golden case nên có:

- câu hỏi;
- scope được phép;
- evidence mong đợi/được chấp nhận;
- nguồn không được dùng như primary evidence;
- counterevidence đã biết;
- forbidden claims;
- claim pattern mong đợi;
- giới hạn cần xuất.

Tối thiểu phải có fixtures cố ý sai cho:

1. quote đổi một từ;
2. source SHA sai;
3. segment sai;
4. translation note giả làm root text;
5. parallel metadata giả làm textual proof;
6. hai nguồn phụ thuộc giả làm hai witness độc lập;
7. claim mạnh hơn evidence;
8. claim historical/empirical/metaphysical bị kiểm bằng sai loại evidence;
9. research mode bỏ counterevidence pass;
10. AI tự tạo phương trình Pāli ↔ Chinese không có repository evidence;
11. phần tổng hợp sinh kết luận mới chưa qua claim gate.

---

# 14. Điều kiện để chuyển requirement MỤC TIÊU sang HIỆN HÀNH

Một requirement verification/counterevidence/run chỉ được đổi trạng thái khi:

1. có implementation thực;
2. data model/format đã xác định nếu cần;
3. có unit/integration test phù hợp;
4. có ít nhất một Golden Research Test nếu requirement liên quan hành vi nghiên cứu;
5. `PROJECT_SPEC.md` được cập nhật trạng thái;
6. `REQUIREMENTS.md` và file này được cập nhật;
7. không làm regression retrieval/Connector hiện tại.

Không được đổi trạng thái chỉ vì code skeleton hoặc tài liệu đã được viết.

---

# 15. Điều kiện nghiệm thu toàn bộ vòng nâng cấp v1

Vòng nâng cấp verification v1 chỉ được coi là hoàn thành khi tối thiểu:

- retrieval hiện tại không regression;
- production locator vẫn deterministic;
- Connector vẫn mở pinned source;
- pointer vẫn không phải evidence;
- Evidence Record có provenance đầy đủ;
- quote sai bị phát hiện;
- claim không evidence bị reject;
- `claim_type` được bắt buộc và kiểm đúng loại evidence;
- UNSUPPORTED/CONTRADICTED không lọt vào kết luận cuối;
- research mode có counterevidence pass;
- dependency/độc lập giữa nguồn được biểu diễn;
- claim → evidence traceable;
- Research Run có thể được rà soát;
- biết corpus/source revisions của run;
- biết checked/unexamined scope;
- Golden Research Tests ổn định;
- fail-closed vẫn được bảo toàn.

Đây là tiêu chí **MỤC TIÊU**, không phải tuyên bố trạng thái hiện tại.
