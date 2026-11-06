# Kiểm toán năng lực BCR tại baseline điều chỉnh chiến lược

Ngày 06/11/2026, Asia/Bangkok. **KHẢO SÁT CÓ MỐC; ĐỀ XUẤT CHỜ THẨM ĐỊNH.**
Không thay tiêu chí nghiệm thu chuẩn tắc hoặc chứng nhận chất lượng học thuật.

## 1. Phương pháp và phạm vi xác nhận

- Baseline/HEAD khi khảo sát và chạy probes:
  `dfdd3cbb79e3dbfb49a855702fa00e4bad3b3410`; tree
  `f56fd057785c8a5ee35c66b4040027fb0150a208`. Remote `main` được đọc qua
  Connector chỉ để quản lý dự án. Merge object được phục hồi từ metadata
  commit, kiểm Git object SHA chính xác; toàn bộ tree đã có local. Không
  fetch/pull/clone hoặc lấy corpus qua API.
- Đọc trực tiếp AGENTS, skill, PROJECT_SPEC, AI_ONBOARDING, ARCHITECTURE,
  v2 DESIGN/REQUIREMENTS/ACCEPTANCE/USAGE, P0/1–P0/3 usage/report và các module
  index/retrieval, A–E, declared sources, semantic/output workflow.
- Đọc A/B1, forward test, native-unit audit, nguồn ghim và receipts liên quan.
  Báo cáo lịch sử là quan sát để kiểm lại, không là đáp án học thuật.
- Runtime mới: Ubuntu WSL/Python 3.12; đọc Git bằng user sở hữu checkout.
  Index Pilot hiện có được mount `loop,ro,noload`, SQLite immutable, không
  WAL/checkpoint/build lại. Sau chạy đã unmount; size/mtime image không đổi.
  Không hash lại toàn bộ image lớn; không tuyên bố có hash toàn index mới.
- Chạy 71 phương thức phần mềm chọn lọc và probes thực trên nguồn/index.
  Không chạy lại toàn suite, không chạy model inference hoặc nghiên cứu
  ngữ nghĩa mới. Test fixture không phải kinh văn/semantic ground truth.

Bằng chứng mới được rút gọn tại [audit-observations.json](evidence/audit-observations.json)
và [selected-tests.log](evidence/selected-tests.log), có
[SHA256SUMS](evidence/SHA256SUMS.txt). Raw receipts/scripts kiểm toán nằm local
ngoài checkout tại `.m/strategic-tools/`; hashes được giữ trong bản rút gọn.
Không đính kèm raw corpus hoặc bài riêng tư vào PR.

## 2. Sổ bằng chứng quan sát

Các đường local dưới đây tính từ workspace chứa các checkout; **không được
coi các tệp JSON đã lưu là source-reader capability**.

| Mã | Bằng chứng | Điều được dùng để kết luận |
|---|---|---|
| E1 | `tools/corpus_research/` tại baseline; tests tương ứng | Hành vi có trong code và hợp đồng thực thi, không suy từ tên module |
| E2 | `.m/strategic-tools/runtime-audit.json`, `mount-receipt.json` | 13 pins/trees, index state, sáu key rỗng/hai positive controls, binding probe, 71 tests mới |
| E3 | `.m/strategic-tools/core-scope-probe.json` | Index Git/SQLite **tạm** do fixture builder có sẵn tạo; cả ba corpus build bằng `core`; combined scope vẫn lỗi |
| E4 | `bcr-workload-experiment-20261105/runs/A/`: findings, stage/source receipts, p03, run-summary, LOCK | A có 4 claim, confounder đã khai; AC05 sáu reference EN rỗng, liên kết claim bị chặn |
| E5 | `bcr-workload-experiment-20261105/runs/B1/`: stage1-declared-run receipt, p03-AC05 receipt, native-range mapping, findings, LOCK | B1 có 2 claim; AC05 bốn EN rỗng; 34 unit VERIFIED vẫn không được link vì reference bắt buộc chưa đủ |
| E6 | `bcr-p03-forward-test-20261105/`: source-unit-audit, empty-native-unit-observations, claims/native-references, final report, negative controls N01–N10 | Hành vi agent và coverage checker; phân biệt lần thử rỗng với reference đã đưa vào binding |
| E7 | `.m/strategic-tools/history-verification.json` | 1.023 file lịch sử trong bốn cây đã kiểm không đổi từ inventory bảo toàn của lượt audit; manifests cũ còn đúng |
| E8 | Evidence triển khai [P0/1](../../v2/evidence/p0-1-2026-11-04/README.md), [P0/2](../../v2/evidence/p0-2-2026-11-04/README.md), [P0/3](../../v2/evidence/p0-3-2026-11-05/README.md), [E](../../v2/evidence/README.md) | Kết quả chạy **lịch sử** với tested code/môi trường riêng, không nhận là lượt chạy mới |

README gốc workload còn nói “B1 chưa chạy”; thư mục B1 thực có LOCK và receipts.
Khảo sát này dùng payload/LOCK đã tồn tại, ghi nhận README cũ bị chậm cập nhật,
không sửa nó. B2/C1–C4 chưa có kết quả trong môi trường được khảo sát. Không
kết luận batching nào tốt hơn. User hiện yêu cầu đọc A/B1; đây là audit sau
thí nghiệm, không phải một research arm mới hoặc ca mù.

## 3. Bốn mức hiện trạng

**M1 — Có và đã kiểm nghiệm trong phạm vi nêu:** có code, test và/hoặc nguồn
thật đúng phạm vi. **M2 — Có code, nghiệm thu chưa đầy đủ:** không suy toàn
runtime/corpus từ test hợp đồng. **M3 — Chỉ thiết kế:** hợp đồng mục tiêu chưa
có đường thực thi đầy đủ. **M4 — Chưa có:** không tìm thấy capability tương ứng.
Một module có thể có M1 ở lõi và M2 ở độ bao phủ.

| Năng lực/module | Mức | Chứng cứ và giới hạn thực |
|---|---|---|
| Pins/config, Git reader `verification.read_local_source` | M1 local | 13/13 HEAD đúng pin và tracked clean trước/sau lượt này; không xác minh đủ nội dung mọi source |
| `index.py`, schema corpus, FTS/normalization | M1 hạ tầng; M2 coverage | Parser cho 13 sources có code; index khảo sát chỉ ba corpus. Profile không đồng nghĩa mọi đoạn/role/ngôn ngữ được lập chỉ mục |
| `retrieval.search/context/work/evidence/provenance` | M1 local | Retrieval có test lịch sử và code; `evidence()` chỉ gom dữ liệu index, chưa qua A. Tập FTS và top-N hữu hạn |
| Pāli exact/normalize/fold/lemma | M1 cơ chế; M2 coverage | Lemma chỉ từ corpus có sẵn. Index Pilot ba corpus hiện có `lemma_count=0`; không tự có từ điển hình thái toàn corpus |
| Hán văn local CJK trigram/CBETA resolve | M1 cơ chế; M2 phạm vi | >=3 ký tự cho đường trigram; 1–2 ký tự không bảo đảm substring. Resolve metadata bridge vẫn cần mở witness |
| `source_resolvers` + A | M1 ba định dạng; M2 đủ 13 nguồn | Bilara/CBETA/84000; span liên tục, không flatten escape/markup. Vị trí rỗng bị từ chối đúng. Context lân cận không tự đủ nghĩa |
| P0/1 `declared_sources` | M1 local | Kiểm identity/pin/witness, no fallback, tất cả reference phải VERIFIED. Vẫn cần work/path trong index; `edition` không được hỗ trợ |
| `LocalHost.quick` và `LocalResearch.create` | M1 local draft; M2 tiện dụng | Quick không B/C/D; create theo query tạo literal quotation candidates, không nhận claim gốc như P0/1. Scope chung có vấn đề E3 |
| B `claims`/Final Claim Gate | M1 contracts; M2 authority thực | Assessment/history do host; không tự suy nghĩa. Research guard vẫn đóng, không có accepted synthesis thực được cấp quyền |
| C `counterevidence`/executor | M1 plans/receipts; M2 semantic completeness | Per-step scope và candidate binding có code. Parallels/variants chưa có A resolver tích hợp đầy đủ; lexical hit chưa là phản bác |
| D `research_run`/`ResearchStore` | M1 draft/version/trace/export | DB riêng, currentness/history. `trace_claim` là historical observation; export JSON/Markdown không cấp publication |
| `ConnectorHost` + production locator | M1 hợp đồng; M2 toàn runtime | Lookup ids/terms-latin, callbacks pin/blob. Lịch sử E có một ca Bilara thực; chưa nghiệm thu toàn Connector/Research/Output runtime |
| P0/2 semantic modules/model adapter | M1 software guard; M2 inference thực | Pipeline support/challenge có code và fixture; hồ sơ đang xét không có inference model được xác thực. Thiếu model vẫn UNRESOLVED |
| P0/3 output modules | M1 fields/links; M2 coverage/render | 22 tests mới chạy lại; title SN/TEI, namespace SC hữu hạn. Title MN probe trả không có facts; free prose/notes semantics ngoài khả năng |
| Work runtime, Research Connector tích hợp đầy đủ | M3 | Portable contracts không là bằng chứng một phiên runtime thực hoặc adapter Research từ xa đã có |
| Research Evidence Pack liền mạch, native candidate preview tổng hợp | M3 ở đề xuất này | Các phần dữ liệu đã có nhưng chưa có một command/view hoàn chỉnh trả mọi trường mong muốn |
| Semantic truth certification toàn lập luận, arbitrary remote CJK/vector RAG, agent framework | M4 | Không có năng lực đã nghiệm thu như vậy; không cần tạo để giải quyết các blocker quan sát |

### Coverage thực của index được mở lần này

Đây là `source_state` của **index Pilot cụ thể**, không phải tuyên bố bao phủ
toàn bộ repository hoặc production remote:

| Corpus | records | relations | variants | lemmas | parser_version |
|---|---:|---:|---:|---:|---|
| cbeta-tei | 12.615.232 | 0 | 1.056.173 | 0 | `2026-09-22.6` |
| suttacentral-bilara | 22.985 | 0 | 4.542 | 0 | `2026-09-23.1-text-role` |
| suttacentral-relations | 0 | 430.436 | 0 | 0 | `2026-09-22.8-sc-cbeta-bridge` |

Đây là counters đã lưu khi build trong `source_state`, không phải phép đếm lại
mọi row hoặc audit semantic coverage. `search_index_state` có version
`2026-09-23.cjk-trigram-v1`; counter 12.616.163 của thành phần ấy đếm records
`lzh/zh` theo `rebuild_search_indexes`, không là tổng mọi ngôn ngữ. Không lấy
counter khác nhau để kết luận index hỏng. Không đo recall toàn corpus lần này.

`core` Bilara gom tối đa 50 entries không rỗng/chunk, root + EN translation +
variants; không tự gồm mọi ngôn ngữ/comment. Source reader có thể mở native
segment trong chunk, nhưng row index không phải danh mục đủ tất cả native
keys. Production chỉ materialize `terms/latin` và `ids`; không đọc lại remote
manifest/coverage mới ở nhiệm vụ này, không công bố số pointer hiện tại.

## 4. Điều tra tám vướng mắc thực tế

| Vướng mắc | Phân loại và độ chắc | Quan sát trực tiếp | Thay đổi tối thiểu cần xem xét |
|---|---|---|---|
| 1. EN MN 135 rỗng lặp lại | **Lỗi chọn locator của AI + thiếu preview**; dữ liệu rỗng có thật; chưa thấy lỗi A | E4 sáu keys, E5 bốn keys; E6 ghi sáu keys MN và lặp hai keys ở claim khác. E2 mở đúng blob: 5.5/6.5/7.4/7.5/8.4/8.5 đều có giá trị `""`; 5.2/5.3 không rỗng và VERIFIED | Preview native keys/role/witness/span trước binding; không tự thay rỗng bằng câu root hoặc unit kế |
| 2. Candidate discovery lẫn nguồn bắt buộc | **Thiếu orchestration rõ**, nguy cơ dùng sai; P0/1 phân biệt đúng | `LocalResearch.create` theo query tạo claim mới; `create_declared_run` bảo toàn claim/ref. A/B1 đưa cả EN trống vào danh sách bắt buộc nên all-or-nothing chặn | Hiển thị candidate trước; chỉ xác nhận DECLARED từ nguồn đã được đối chiếu; expansion luôn nhãn riêng. Không hồi tố xóa refs để “PASS” |
| 3. Kiểm segment/role/witness/alternative trước bind | **Có primitives, thiếu view tổng hợp** | Resolver giải từ blob; verify-source dùng được trước run; title MN không thuộc facts reader. Không có catalog trả trạng thái rỗng/escape và lựa chọn thay thế toàn diện | Dùng source reader + A, trả chẩn đoán theo unit, facts không suy đoán; alternative cần caller chọn và giữ identity riêng |
| 4. Index/host coverage và scope | **Giới hạn dữ liệu + lỗi code tái hiện về nhận diện profile** | E2 có ba corpus, combined scope lỗi. E3 tất cả build `core`, singleton thành công; combined vẫn lỗi vì `.rsplit(':',1)[-1]` so các base parser versions khác nhau | Tách parser revision khỏi profile compatibility bằng policy host rõ. Không chỉ bỏ check hoặc hứa hỗ trợ mọi mixed profile |
| 5. Pāli/Hán/đối chiếu nhân chứng | **Giới hạn index/resolver, thiếu coverage có đo** | CJK >=3; lemma Pilot=0; `compare` giới hạn 50 rows/ID, không harmonize; parallels/variants không có đầy đủ A path | Coverage card, paginated/bounded đọc có nhãn; bổ sung resolver/thuật ngữ chỉ khi task thật chứng minh nhu cầu |
| 6. Nhiều thao tác/receipts | **Ma sát môi trường + workflow**; chưa đo nguyên nhân chất lượng | A/B1/forward gặp root/db/source-root, ownership, CRLF/encoding, mount, scope. B1 có 90 subprocess records lúc report, không phải mọi API/internal Git call | Một preflight có output ngắn + raw log tự ghi; tái dùng host config/scope. Chưa kết luận nhiều log gây lỗi ngữ nghĩa |
| 7. Gõ lại title/ID/provenance | **Lỗi sử dụng AI + coverage/render còn thiếu** | Sai title lịch sử bị chặn ở TITLE; N10 cùng loại sai ở prose vẫn CHECKED. MN native title ở :0.2, không thể dùng mặc định SN :0.3 | Render citation/title từ facts đã kiểm, báo unsupported ở nơi chưa có reader. Không fuzzy match hay sửa tên từ trí nhớ |
| 8. Dễ đọc/truy vết output | **Đã có trace, thiếu trình bày tích hợp** | D trace/export có evidence/context; review Markdown đính snapshot JSON lớn, P0/3 Markdown chủ yếu các block JSON. A/B1 có narrative riêng ngoài certification | Evidence Pack và view claim/evidence/giới hạn, link tới raw records; không tuyên bố CHECKED cho toàn narrative |

Không có đủ dữ liệu để quy kết việc AI chọn key rỗng là do batching, model
yếu, dữ liệu bị hỏng hoặc skill là nguyên nhân duy nhất. Skill đã yêu cầu
đọc nguồn và có `verify-source`; thiếu preview có thể làm việc ấy khó hơn,
nhưng tác động nhân quả cần P4 đo riêng. Không giải thích sự rỗng bằng giả
thuyết biên tập chưa có bằng chứng.

### Chuỗi nguyên nhân đã kiểm lại của MN 135

`native key rỗng → resolver không có location/span → P0/1 UNVERIFIED → mọi
reference chưa VERIFIED → supporting IDs=[] → P0/3 EVIDENCE_BINDING hoặc
CONCLUSION_EVIDENCE FAIL`.

E2 dùng một run/store **mới, tạm**, claim probe phần mềm không phải claim Pilot:
một ref rỗng + một ref EN hợp lệ cho kết quả `[UNVERIFIED, VERIFIED]`,
supporting IDs và accepted IDs đều rỗng. Đây là hành vi all-or-nothing được
thiết kế, không là lỗi chọn sai nguồn của checker. Không sửa AC05 lịch sử.

Forward test đã ghi nhận rỗng ở bước audit rồi chọn refs khác cho draft; A và
B1 giữ các refs rỗng trong binding. Vì vậy không lấy số lần thử rỗng của ba
phiên như ba số claim thất bại tương đương. Không gộp units, bindings, items,
documents, subprocess hoặc witnesses thành một mẫu số chất lượng.

### Vấn đề `scope` đã tái hiện và giới hạn kết luận

`state_parser_version(corpus, 'core')` trả base version theo từng parser.
`LocalHost.scope` lấy phần cuối sau `:` làm profile; khi không có suffix, nó
lấy **toàn bộ base version**. Bilara và CBETA khác base version nên bị coi như
mixed profiles. Probe E3 dùng builder/fixture có sẵn, index tạm, không sửa
assertion/test hoặc index khóa. Từng singleton còn được xuất thành constraint
`indexed_profile:<base-version>`.

Do đó không đủ căn cứ nói lỗi ở A/B1 chỉ vì người dùng thực sự trộn build
profiles. Đã xác minh lỗi chẩn đoán/nhận diện profile trên cùng-core fixture;
chưa nghiệm thu policy gộp mọi corpus hoặc suy rằng bỏ guard là an toàn. Sửa
sau này cần nhận diện đúng mode từng component và vẫn chặn stale parser,
pin sai, acceptance/full không tương thích theo policy tường minh.

## 5. Ma trận KEEP / SIMPLIFY / IMPROVE / DEFER

Mỗi hàng là một đề xuất thiết kế, **chưa triển khai**. Các kiểm thử dưới đây là
yêu cầu cho PR triển khai sau, không được tính đã PASS ở audit này.

| Nhóm; module/tài liệu | Vấn đề thực và bằng chứng | Thay đổi tối thiểu | Rủi ro hồi quy | Kiểm thử phải giữ/bổ sung |
|---|---|---|---|---|
| KEEP — manifest/config/Git reader/A | Nguồn và quote cần binding, E1/E2 | Giữ contract pin/blob/path/unit, fresh readers, fail-closed | Cache/preview bị nhận là authority | test_verification, source span; wrong pin/path/blob/witness/segment, source mất |
| KEEP — retrieval/schema/CLI 1.0 | Đã có FTS, normalization/CJK, ranking; không có bằng chứng cần thay engine | Giữ defaults, cải thiện view bằng wrapper opt-in | Đổi rank hoặc tăng chi phí lookup cũ | acceptance/retrieval/CJK/normalization, E1 output/rank |
| KEEP — B/Final Claim Gate | Đúng nguồn không chứng minh claim, E1/E6 | Giữ assessment/history capability và Research guard | Proposal tự thành accepted | claims + golden; fake approval, unsupported/contradicted, stale revision |
| KEEP — C/D | Cần scope và trace; E1/E4/E5 | Giữ per-step receipts, uncertainty, append-only/version | Mất phản chứng/lịch sử hoặc replay snapshot | counterevidence/research_run; truncated search, dependency uncertain, stale snapshot |
| KEEP — ConnectorHost/router | Pointer không text; E1/E8 | Giữ pin locator/source, allowlist, namespace | Mở nguồn ngoài contract hoặc mở broad CJK giả | connector_contract/remote_access, no source binding, wrong blob/key |
| SIMPLIFY — USAGE/skill/preflight E | Nhiều root/mount/encoding/profile, E4–E6 | Một checklist thực thi và summary; log raw tự động, giữ option cũ | Chọn sai db/source-root; giảm log quá mức | distinct roots, WAL/index thiếu, output ngoài sources, nonzero và JSON reject |
| SIMPLIFY — D export/P0/3 renderer | JSON lớn và facts gõ lặp, E1/E6 | Summary + citations từ fields, raw JSON vẫn giữ | Renderer nâng CHECKED thành academic approval | quote/title/namespace/freshness; snapshot vẫn truy được |
| IMPROVE — source_resolvers/LocalHost/P0/1 preview | Rỗng lặp, all-or-nothing chặn, E2/E4/E5 | Catalog native key/role/witness/span + validate-source trước bind | Silent substitution, alias/range đoán | MN empty/valid, missing/escaped key, wrong witness, ambiguity, no fallback |
| IMPROVE — scope/index coverage | Same-core bị coi mixed, E2/E3 | Policy phân biệt parser revision/profile; coverage theo corpus/language/role | Chấp nhận stale/mixed không tương thích | same-core khác parser, acceptance/full/core, stale, unindexed, query/top-N giới hạn |
| IMPROVE — claim discovery workflow | Query-create và declared-create khác nghĩa, E1/E4/E5 | Candidate→review→explicit declared refs; giữ original ref và expanded origin | Xóa yêu cầu lỗi để tạo PASS giả | claim text/ID nguyên vẹn; required failure; expanded không thay declared |
| IMPROVE — evidence pack dùng D/A | Các phần đã có, view chưa liền mạch | Compose envelopes/trace/context, không DB mới | Saved evidence được reuse không fresh; rights leak | Pack replay/source mất, metadata vs wording, unresolved/missing/context, rights local |
| IMPROVE — title/identifier facts P0/3 | SN có, MN/AN/CBETA subwork chưa đủ, E2/E6 | Reader từng collection có selector/provenance rõ; render facts | Heading container bị coi title tiểu kinh | Native MN/AN positives + sai title; TEI container vs subwork, aliases/namespace |
| DEFER — semantic modules/P0/2 tham vọng toàn diện | Chưa model/ground truth, E6/E8 | Giữ optional proposal; chưa mở rộng thành truth scoring/approval | Tăng code mà không cải thiện evidence | Giữ fixture/model status, no academic approval; live tests chỉ khi quyền dữ liệu có thật |
| DEFER — full Work/remote arbitrary CJK/vector/agent framework | M3/M4; chưa chứng minh cần trước blocker local | Chỉ khảo sát khi bounded workflow thất bại có đo | Tăng kiến trúc/quyền và phá offline | Runtime riêng, source allowlist/coverage; không lấy portability làm runtime PASS |

## 6. Kiểm thực chạy, kết quả và phần chưa chạy

Lệnh điều phối local mới: `wsl -d Ubuntu -u root -- python3
<workspace>/.m/strategic-tools/readonly_runner.py`; mount chỉ đọc, chuyển sang
`tranquoc` chạy `audit_runtime.py`, finally unmount. Fixture scope chạy riêng
bằng `core_scope_probe.py` trên `/tmp`, không đụng source/index lịch sử.

| Lượt | Kết quả thực | Ý nghĩa |
|---|---|---|
| unittest test_declared_sources | 22/22 PASS | P0/1 software contract |
| unittest test_source_span_selection | 16/16 PASS | Span/quote/location contract |
| unittest test_output_verification | 22/22 PASS | P0/3 fields/links/authority |
| unittest test_connector_contract | 11/11 PASS | Portable Connector contract, không phiên live |
| Tổng bốn module | **71/71 PASS**, 0 FAIL/ERROR/SKIP; log unittest 7,003 giây, khoảng runner 7,007 giây | Phạm vi phần mềm đã chọn; không là full-suite mới |
| Nguồn/index probes | Sáu empty UNVERIFIED, hai positive VERIFIED; all-or-nothing tái hiện | Kết quả mong đợi của probes chẩn đoán, không tính thành unittest methods |
| Same-core scope probe | Tái hiện lỗi combined; singleton thành công | Defect observation, không báo combined đã PASS hoặc đã sửa |
| Title MN từ LocalOutputFacts | Không trả facts dù evidence EN hợp lệ | Coverage chưa có, không kết luận title nguồn sai |
| Historical checksums | 239 preparation + 130 evaluation + 270 forward + 174 A + 180 B1 entries khớp | Kiểm integrity, không semantic adjudication |

71 tests chạy trên source code baseline từ worktree mới; fixtures dựng Git và
SQLite tạm bằng helper có sẵn, không đổi test/fixture repository. Raw log là
log mới của audit này. Số 484 full + 21 Pilot ở E8 là **lịch sử P0/3**, không
phải lần chạy mới trên baseline được khảo sát.

**Chưa chạy trong nhiệm vụ:** full suite A/B/C/D/E, toàn Pilot classes,
Windows-native full, Work/Connector live, query-recall benchmark, model
inference, audit ngữ nghĩa độc lập, batching comparison. Không có test FAIL
trong 71 methods đã chọn; scope probe có lỗi đã biết được tái hiện và chưa sửa.
Không dùng SKIP hoặc giới hạn chưa đo làm PASS. Không có token/provider cost
hoặc số đo tốc độ nghiên cứu/chi phí thao tác có đối chứng mới.

## 7. Bảo toàn và giới hạn audit

1.023 file trong preparation/evaluation/forward/workload không đổi so inventory
bảo toàn; 37 claims và 259 quyết định ở 12 case vẫn PENDING. 13 nguồn đúng pin,
tracked clean trước/sau. Diff nhánh chỉ trong thư mục đề xuất mới; AGENTS,
skill, code, tests, fixtures, config, pins, corpus/index và tài liệu chuẩn
không thay. Các ZIP lịch sử không được ghi hoặc đóng gói lại.

Không có phán quyết semantic mới, không chứng minh toàn bộ report A/B1 đúng,
không revalidate mọi evidence lịch sử. Hashes/receipts chỉ xác nhận bytes và
lượt quan sát được nêu. Không thực hiện chuyên gia, cấp quyền chia sẻ hoặc
phê duyệt pháp lý/học thuật.

`HUMAN_ADJUDICATION_PENDING` · `DISTRIBUTION_CLEARED = 0` · `PUBLICATION_NOT_PERMITTED`.
