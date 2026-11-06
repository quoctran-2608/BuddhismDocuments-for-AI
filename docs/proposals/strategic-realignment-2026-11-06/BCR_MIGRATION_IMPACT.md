# Tác động nếu triển khai điều chỉnh chiến lược

Ngày 06/11/2026. **ĐỀ XUẤT CHỜ THẨM ĐỊNH.** Tài liệu này liệt kê tác động
tương lai; không phải migration đã chạy. Nhánh hiện tại chỉ thêm thư mục đề
xuất và bằng chứng audit rút gọn, không thay tài liệu chuẩn/code/tests/skill.

Đọc cùng [định hướng](BCR_STRATEGIC_REALIGNMENT_VI.md),
[audit](BCR_CAPABILITY_AUDIT.md), [workflow](BCR_TARGET_WORKFLOW.md) và
[roadmap](BCR_PRIORITIZED_ROADMAP.md).

## 1. Tài liệu và skill

Áp dụng [DOCUMENTATION_GOVERNANCE](../../DOCUMENTATION_GOVERNANCE.md): một miền
hợp đồng có một nơi chuẩn; không sao chép đủ schema/pins vào mọi hướng dẫn.
Nội dung mới chỉ được chuyển sang hiện hành khi có code/runtime evidence đúng
phạm vi. Các mốc lịch sử được giữ nguyên và dẫn link, không viết lại thành
thành công mới.

| Nơi có thể bị ảnh hưởng | Cập nhật sau thẩm định | Điều cần giữ / điều kiện |
|---|---|---|
| `docs/PROJECT_SPEC.md` | Nêu rõ BCR cung cấp hạ tầng chứng cứ, agent lập luận; draft hữu ích khác accepted synthesis | Giữ source hierarchy, Quick/Research và giới hạn approval; đây đã là phần lớn mục tiêu hiện có, tránh viết lại toàn spec |
| `docs/AI_ONBOARDING.md` | Refresh bản đồ P0/1–P0/3, preview trước binding, actual runtime/coverage matrix | Không dùng số test ở mốc 11/10 làm số hiện tại hoặc hứa Work/full Connector |
| `docs/ARCHITECTURE.md` | Mô tả composer/view dùng A/D/E khi đã triển khai; chỉ rõ dữ liệu vs capability | Không tạo layer học thuật/DB mới chỉ vì một pack; không đổi source authority |
| `docs/v2/PRD.md`, `DESIGN.md`, `REQUIREMENTS.md` | Điều chỉnh ưu tiên và cách mô tả verification; nêu proposal/draft thay universal semantic claims | Giữ 33 requirement IDs, Final Claim Gate, scope/independence/history và các mục tiêu chưa đạt. Không xóa điều kiện để nghiệm thu dễ hơn |
| `docs/v2/ACCEPTANCE.md`, `IMPLEMENTATION_PLAN.md` | Mapping P1–P4 với requirement cũ và bộ test/coverage mới | Giữ mục nghiệm thu còn thiếu, evidence lịch sử và phân biệt nguồn/semantic/runtime |
| `docs/v2/USAGE.md`, `P0_1_USAGE.md` | Đường candidate preview → explicit declared; giải thích all-or-nothing, roots/profile và failures | Chỉ chỉ dẫn command/API thực có. Không khuyên bỏ source reference bắt buộc hoặc đổi witness khi fail |
| `P0_2_USAGE.md` | Giữ optional support/challenge; model capability thật, no-model result rõ | Chưa có lý do sửa model contract; không nối proposal thành assessment_reader |
| `P0_3_USAGE.md` | Hướng dẫn render facts, coverage title theo collection khi có, giới hạn free prose | Chưa có code reader thì chưa nâng coverage. Không biến CHECKED thành semantic certificate |
| `.codex/skills/buddhist-corpus-research/SKILL.md` | Thêm quyết định ngắn: đang khám phá hay kiểm nguồn khai báo; preview source/coverage; lấy facts qua helper; draft/limitations | Giữ skill ngắn, link tới USAGE; không thêm schema dài hoặc yêu cầu chuyên gia mọi run; không đổi AGENTS policy |
| `AGENTS.md` | **Không cần sửa để ưu tiên hạ tầng chứng cứ** | Luật evidence/offline/provenance/witness/fail-closed đã tương thích. Chỉ xét sửa nếu có yêu cầu policy rõ, ngoài scope đề xuất hiện tại |
| `README.md`, `docs/CLI.md`, `REMOTE_AGENT.md` | Link đường bắt đầu khi tính năng có thật; native/module fallback đúng môi trường | Không lặp config/production counts hoặc nói Connector có shell/local reader |
| P0/1–P0/3 REPORT và hồ sơ thí nghiệm cũ | Không sửa kết quả lịch sử; báo cáo mới dẫn tới chúng | README workload chậm cập nhật hoặc baseline object thiếu ở phiên cũ là dữ kiện lịch sử, không âm thầm hiệu đính |

## 2. API và code: tương thích ngược phải được giữ

| Thành phần | Hướng tác động nhỏ nhất | Cam kết tương thích / điểm cần thẩm định |
|---|---|---|
| `source_resolvers.py` | Tái sử dụng parsing/selectors; preview có thể cần catalog khả năng đọc trước resolve | Không sửa logic quote/offset/span để che ô rỗng; phân biệt native text và text được phép quote. Giữ `resolve_source` behavior cũ nếu caller không bật preview |
| `local_host.py` | View preflight/candidate và sửa profile recognition/policy có kiểm | Giữ source contract/fresh readers, max bound và WAL/pin/parser checks. Current scopes lưu trong C/D không được âm thầm đổi khi replay |
| `index.py`/`source_state` | Dùng parser/mode mapping hiện có trước schema mới | Base parser version khác không tự là profile khác. Legacy state không chứa đủ thông tin phải giữ unknown hoặc policy rõ; không sửa metadata index khóa |
| `declared_sources.py` | Candidate review ngoài binding, diagnostics bổ sung opt-in | `verify_declared_source` vẫn corpus/work bắt buộc; no guessed edition, no lexical fallback. `create_declared_run` giữ all-or-nothing/original IDs/text/ref sidecar |
| `retrieval.py`/CLI 1.0 | Tái sử dụng discovery/context/variants; pagination/coverage chỉ nếu cần | Không đổi ranking/default, score thành support hoặc tự chạy Research trong Quick. Additive fields/options phải kiểm consumer/golden outputs |
| `local_research.py`/CLI E | Composer/preflight theo lựa chọn tường minh, output paths rõ | Không biến query-create thành check nguyên văn claim; không chạy step phụ thuộc sau failure; old commands vẫn hoạt động theo contract |
| `research_run.py`/`research_store.py` | Dùng trace/export/history; thêm summary/render trước thêm trường persisted | expected_version/currentness/revision guards giữ nguyên. Pack lưu không thay host reader; export local không cấp publication |
| `output_workflow.py`/`output_verification.py` | Render facts + reader coverage theo collection đã xác minh | Không đổi bcr-output-1 âm thầm; kiểm title/namespace/quote theo pin; saved receipt không là export ticket; free prose chưa được chứng minh |
| P0/2 semantic modules/model adapter | Giữ nguyên pipeline proposal tùy chọn | Không nâng proposal thành approved, không adapter/provider/credential mới trong roadmap tối thiểu |
| `connector_host.py`/production export | Giữ adapter/router hiện có | Local pack không tự làm Connector Research hoạt động. Cần PR/runtime evidence riêng cho khả năng mới; không production terms/cjk giả |
| A/B/C/D core và authorization | Không có thay đổi cần thiết cho priority shift | Reader authority, Final Claim Gate, dependency uncertainty/history và publication guard tiếp tục áp dụng |

Không thêm tên trường `edition`, `source_sha256` hoặc cơ chế approval vào
P0/1 vì tên có vẻ tiện. Phải dùng fields đang tồn tại; `source_sha` là Git
commit SHA, `source_blob_sha` là Git blob SHA; SHA-256 artifact là checksum
khác. Pack labels trong workflow là bố cục đề xuất, chưa là schema public.

Sửa scope có thể làm constraint mới khác snapshot cũ. Cần bảng tương thích
legacy và tests replay: run cũ không được tự nhận scope mới đã thực thi; nếu
scope/plan thay phải dùng version/run mới theo D. Không rewrite receipts hoặc
index để làm check exact-scope đạt.

## 3. Dữ liệu, lưu trữ và quyền

Không cần migration corpus/index/ResearchStore cho việc đổi ưu tiên bằng tài
liệu. Composer pack ban đầu dùng JSON/sidecar/snapshot đã có. Nếu về sau cần
field persisted, phải có ví dụ thiếu dữ liệu thật, kế hoạch tương thích,
versioning và rollback riêng trước khi thay schema.

Không thay 13 gitlinks/pins, upstream files, index khóa, 12 cases/37 original
claims/259 PENDING decisions, frozen notes hay các ZIP lịch sử. Mọi fixture
phần mềm/probe mới phải ở vùng tạm hoặc test mới có nhãn; không sửa fixtures
cũ để che lỗi. Không tải model/dictionary/corpus hoặc thêm vector DB.

Pack local có thể chứa nguồn chịu quyền khác nhau. Duy trì rights register
và chính sách truy cập hiện hành; việc gom/render không phải clearance mới.
Không giao chuyên gia, upload raw source/private article hoặc mở publication.
Artifact công khai của audit chỉ gồm metadata/observations và software logs.

## 4. Tests, validation và acceptance bị ảnh hưởng

| Nhóm | Giữ nguyên | Bổ sung khi triển khai |
|---|---|---|
| Retrieval/normalization/CJK/remote/bridge | Default outputs/rank, bounded search, pointer identity, witness provenance | Coverage/truncation, Pāli forms, Hán 1–2/>=3, pagination nếu thêm; không suy no-hit là absence |
| A/source reader/span/roles | Pin/path/blob/work/segment/witness checks, note separation, contiguous span | Native absent/empty/escaped và preview không có authority; nguồn thay đổi/mất |
| P0/1/Pilot | AC01 nguồn đúng dù lexical top hit khác; AC04 namespaces; failure/multi-source/no fallback | MN135 valid+empty trước binding; candidate vs required, original ref không biến mất |
| B/C/D/E | Final gate, scope/receipt binding, dependency uncertain, history/version, publication closed | Same-core khác parser; incompatible/unknown/stale profile; run cũ không tự đổi scope; pack failures/sidecar đầy đủ |
| P0/2 | No-model/FIXTURE/real-model trace phân biệt; proposal không quyền | Chỉ thêm live test khi có host/data authorization và scope tương ứng; không bắt buộc cho lookup |
| P0/3 | Title/quote/namespace/conditions/stance/currentness, receipt replay blocked | Native MN/AN selectors; container vs subwork; renderer facts không gõ lại; N08–N10 vẫn cảnh báo giới hạn semantic |
| Docs/skill/UX | Links, exact API/defaults, chính sách không đổi | Một chat mới làm đúng luồng mà không đọc report đáp án; ghi actual errors/steps/coverage. Validator skill không thay behavioral forward test |

Docs-only PR này chạy 71 methods được ghi trong audit và probes chẩn đoán;
không ghi nhận full suite hoặc semantic acceptance mới. PR code sau này chạy
toàn checks phù hợp và giữ raw logs/hash/commit/tested environment; không dùng
counts của PR này để tránh kiểm hồi quy.

## 5. Trình tự chuyển đổi và dừng/rollback

1. Thẩm định năm tài liệu đề xuất: chốt capability boundary, ba cải tiến đầu,
   scope compatibility và tiêu chí. Chưa merge code hoặc đổi policy.
2. Triển khai từng thay đổi opt-in nhỏ trên nhánh riêng. Ghi baseline và lỗi
   hiện có trước sửa; tests mới nhắm lỗi thực, không mirror implementation.
3. Cập nhật nguồn tài liệu chuẩn đúng miền khi capability thực có bằng chứng;
   giữ mốc lịch sử và link từ skill/onboarding, không copy nhiều hợp đồng.
4. Chạy nhiệm vụ end-to-end mới có protocol trước, dữ liệu được phép, held-out
   thích hợp. Đo lỗi source/workflow riêng với semantic quality; không lấy
   CHECKED để tự cấp approval.
5. Nếu wrapper/preview/render chưa đạt: tắt tùy chọn hoặc revert code PR mới;
   đường 1.0/Quick/P0/1 cũ vẫn còn. Không khôi phục bằng sửa corpus/pin/receipt
   cũ. Nếu đã tạo run mới, giữ lịch sử hoặc supersede có lý do theo D.

Điều kiện dừng một triển khai: xuất hiện silent source substitution, source
pin/currentness bị bỏ qua, metadata thành wording, snapshot tự cấp quyền,
mất required failure/history, hoặc dữ liệu chưa clear bị đưa ra ngoài. Ghi
lỗi thật, khắc phục trước tiếp tục; không giảm tiêu chí để làm output đạt.

## 6. Kết quả không thay đổi sau migration đề xuất

BCR giúp AI lấy, tổ chức và kiểm chứng nguồn tốt hơn. AI analysis vẫn là
interpretation/proposal; semantic approval có thẩm quyền và quyền công bố
không tự phát sinh. Chưa có lý do thay AGENTS hoặc loại Gate A–E để đạt mục
tiêu này. Không có migration nào thực thi trong nhánh tài liệu hiện tại.

`HUMAN_ADJUDICATION_PENDING` · `DISTRIBUTION_CLEARED = 0` · `PUBLICATION_NOT_PERMITTED`.
