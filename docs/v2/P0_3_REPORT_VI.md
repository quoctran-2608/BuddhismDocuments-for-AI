# P0/3 — Kiểm đầu ra agent và cập nhật skill

Ngày 05/11/2026 theo Asia/Bangkok. Baseline main đã xác minh:
`74cfcc03f6a5b9fbb80462c35cd9e440a1fdaf4a`. Nhánh mới:
`feature/agent-output-verification`. Đây là phát triển phần mềm, không phải
một lượt đánh giá học thuật mới.

## Quan sát dẫn tới thay đổi

Đã đọc final report, bản first-assessment khóa, ledger, 38 subprocess records,
negative gate receipts/logs và các hiệu đính sau khóa của thử nghiệm 04/11.
Ledger có **336 evidence records**; 38 commands không bao gồm toàn bộ batch
API. Báo cáo/ledger không là semantic ground truth hoặc reader capability.

Bản khóa viết `Bāhirāniccahetuanattasutta`, trong khi native unit
`sn35.145:0.3` ghi `Bāhirānattahetusutta`. Gate A đã đọc đúng nguồn nhưng
không so tên do Codex gõ trong văn xuôi. Năm negative controls exit 0 vẫn trả
REJECTED/UNVERIFIED. Đây là hai lỗi sử dụng/diễn đạt cần code và skill bảo vệ.

Khảo sát AGENTS/skill/PROJECT_SPEC, P0/1–P0/2 và A/B/C/D/E cho thấy đã có
pin/path/work/witness verification, quote checks, source-reader freshness,
support/challenge proposals và scope limits. Không xây lại những phần đó.
Còn thiếu contract cho các fields đầu ra, links condition/attribution và
kiểm title/namespace trước khi export, cùng hướng dẫn agent dùng năng lực mới.

## Code sau nâng cấp

- `output_verification.py`: OutputContext giữ claim/source IDs và notes ngoài
  document AI; schema `bcr-output-1` cho TITLE/QUOTE/IDENTIFIER/CONCLUSION.
  Dùng lại `_evidence_record`, `verify_quote`, `_read_capability`; đọc A đầu/cuối,
  so provenance/run binding, source role và các links đã ghi nhận.
- `output_workflow.py`: fact reader mở lại blob ghim để kiểm title SN native
  `:0.3`, title TEI header và metadata acronym SC có namespace. Giữ UID và
  mapping riêng. Writer/renderer public luôn kiểm document với capability thật;
  receipt CHECKED đã serialize không là vé export.
- CLI E thêm `output-check`. CHECKED có JSON/Markdown; REJECTED/UNVERIFIED chỉ
  có JSON chẩn đoán, report null. Exit 0 không được hiểu là gate đạt. Outputs
  mới UTF-8 LF, không ghi đè file cũ hoặc Research Store.
- Skill được rút gọn, dẫn tới hướng dẫn sâu, thêm preflight baseline/source/
  index/mode, P0/1/P0/2, JSON status, output check và tự soát văn xuôi.
  Không cần đổi AGENTS hoặc policy. Không có adapter Codex/Claude/API mới.

Hướng dẫn contract/API/CLI và prompt dùng từ chat mới:
[P0_3_USAGE](P0_3_USAGE.md). Defaults Quick/Research/P0/1/P0/2 giữ nguyên;
đường xuất cũ không tự được gắn chứng nhận P0/3. Agent phải dùng đường mới cho
fields cần kiểm, không giả đã kiểm mọi câu chat/Word.

## Trước/sau: điều code thực sự phát hiện

| Loại | Kết quả đã chạy | Phạm vi còn giới hạn |
|---|---|---|
| AC04 title Pāli | Đọc mới đúng pin, title đúng CHECKED, **tên sai lịch sử REJECTED/TITLE_MATCH FAIL**. Không dùng script trả sẵn đánh giá ngữ nghĩa. | Chỉ field TITLE có binding; không tự trích mọi tên trong văn xuôi. Reader title chưa phủ mọi collection/corpus. |
| Quote/identity | Chặn quote sai, source path/work/pin/witness/role khác, ID thuộc run khác, source mất/không VERIFIED. | Quote đúng không chứng minh claim đúng; context/unit được đọc có thể chưa đủ. |
| Namespace AC04 | Alt acronym `SN 35.145` của UID `sn35.146` chỉ CHECKED trong namespace SC_ALT_ACRONYM với metadata ghim; đổi UID sang 145 bị chặn. | Không suy textual equivalence hoặc đổi số ở mọi hệ. Metadata không là câu kinh. |
| AC01 scope/speaker | Chặn scope UNIVERSAL, mất scope links hoặc đổi recorded stance REPORTED_REJECTED thành ENDORSED; quote bị thuật lại không được gắn SCRIPTURAL_TEACHING theo annotation ấy. | Speaker/stance ban đầu do AI/người đọc ghi, code không tự xác định lập trường từ ngôn ngữ tự nhiên. |
| AC05/AC11 conditions | MN135 EN native units 5.2/5.3 và 7.2/7.3 đọc mới; giữ đầy đủ postmortem/rebirth links và quote trong cấu trúc/render; bỏ một link bị chặn. | Code không tự biết annotation đã nhận diện đủ/mang đúng nghĩa temporal/causal chưa. |
| Metadata/note | Không nhận text role metadata/note/comment như SCRIPTURAL_TEACHING; không cho JSON tự sửa provenance. | Những trường hợp gán nghĩa sai nhưng giữ đúng fields vẫn cần AI nhận diện. |
| Exit 0 | Năm negative controls thực trong commands/logs được đọc đúng thành gate không đạt; observer không biến JSON thành authority. | Receipt chỉ cho biết điều tool đã báo; source phải kiểm qua reader thật. |

Kết luận luôn được gắn AI_INTERPRETATION hoặc UNRESOLVED, kèm scope và notes.
CHECKED không được đổi thành B accepted. Test riêng xác nhận prose có thể còn
sai dù fields/links hợp lệ: `semantic_truth_verified=false`, không confidence
score hoặc tỷ lệ accuracy. Code kiểm bảo toàn annotations, không tuyên bố
chứng minh đúng toàn bộ lập luận bằng cú pháp.

## Kiểm thử cuối và loại bằng chứng

| Lượt thực | Kết quả |
|---|---|
| Full unittest WSL Ubuntu/Python 3.12.3 | **484 phương thức PASS**, 0 FAIL/ERROR; `OK (skipped=3)`. Ba class cần env Pilot được chạy riêng dưới đây. |
| Existing Pilot index read-only | **21/21 PASS**, 0 FAIL/ERROR/SKIP: P0/1 9, P0/2 7, P0/3 5; có subcases AC05/AC11 và năm exit-zero controls. |
| P0/3 software tests trong full suite | **22 phương thức PASS** trên Git/SQLite fixture thật; title/quote/link/render/currentness/CLI/schema/role và chống replay receipt. |
| Skill quick_validate | PASS bằng validator skill-creator trên WSL. Python Windows thiếu PyYAML; không tải package để khắc phục. |
| Hồ sơ bảo toàn | 132/132 file evaluation không đổi byte so trước test; 130/130 entries FINAL-SHA256SUMS đúng; 62/62 + 239/239 checksum Pilot cũ đúng; 37 claim/259 ô còn PENDING. |

Full suite dùng bản sao byte-identical của code/config/tests hiện tại trong
Git workspace Linux tạm, links tới 13 checkout nguồn đã có và acceptance index
tạm. Không sửa test cũ hoặc đổi ROOT/assertions để làm PASS. Lượt Pilot chạy
trực tiếp worktree hiện tại trên index lịch sử mount `loop,ro,noload`, SQLite
immutable, unmount sau chạy. 13 source HEAD/pins đúng và tracked trees sạch
trước/sau; không download hoặc ghi lại corpus/index.

Phân loại bằng chứng: P0/3 dùng so sánh code trên source facts và links. Synthetic
software fixtures không là diễn giải Phật học. Các test P0/2 cũ vẫn có scripted
model fixture và giữ MODEL_INFERENCE_NOT_EXECUTED; không lấy chúng chứng minh
AI hiểu nghĩa. Năm bài P0/3 source thật không dùng model trả sẵn kết luận.
Không revalidate đủ 336 ledger records hoặc gọi 38 commands là log mọi API.

Raw logs/receipts, timings và tested-file hashes nằm tại
[evidence P0/3](evidence/p0-3-2026-11-05/README.md). Không chạy model thật,
không có nghiên cứu/phát hiện học thuật mới hoặc semantic accuracy mới.
Chưa chạy Windows native full suite, agent forward-test trong chat mới hoặc
Connector runtime của lớp output. Những phần đó không được tính PASS.

## Skill và thao tác agent mới

Trước: skill nhấn truy xuất/đọc source nhưng chưa hướng dẫn cụ thể P0/1/P0/2,
status JSON và đối chiếu fields văn xuôi. Sau: agent phải kiểm đúng checkout/
baseline và code/source roots, dùng source constraints trước lexical ranking,
chỉ gọi P0/2 khi có adapter hợp lệ, giữ candidate phản chứng chưa xét riêng,
ghi annotations trước viết và chạy output-check trước export. Title/ID/scope
được lấy qua helper thay vì gõ lại từ trí nhớ. Skill ngắn hơn, không chép lại
contract dài và không đặt quy trình thuê chuyên gia ở mỗi lần proposal.

Giảm kiểm tay đối với title chính tả, provenance/citation, ID namespace và
links bị mất. Chưa đo mức giảm lỗi của một agent mới thực sự; validator YAML
và kiểm phần mềm không thay forward-test hành vi. AI vẫn chịu trách nhiệm
nhận diện đủ conditions, lượng từ, speaker/stance, causal inference, dịch nghĩa,
alignment, gloss và nguồn phản bác; lỗi trong notes ban đầu có thể còn lọt.

Title reader hiện chỉ có SN `snN.N:0.3` và TEI header được mô tả; ngoài đó
giữ UNVERIFIED thay vì đoán. Metadata mapping kiểm đúng pin/UID, không chứng
minh cùng văn bản. Lớp mới opt-in không thể ngăn host cố ý bỏ qua hoặc sửa cả
context lẫn report; context hash không phải quyền/semantic authority. Kiểm
facts không làm các diễn giải đối nghịch tự được giải quyết.

AGENTS, A/B/C/D approval core, P0/1/P0/2, schema gốc, 13 gitlinks/pins, corpus,
index, hồ sơ Research Agent khóa và publication/rights policy không thay đổi.
Không giao chuyên gia, không tự merge. Giữ:

HUMAN_ADJUDICATION_PENDING · DISTRIBUTION_CLEARED = 0 · PUBLICATION_NOT_PERMITTED.
