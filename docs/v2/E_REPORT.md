# Báo cáo Giai đoạn E — 11/10/2026

> **Cập nhật trạng thái sau merge — 11/10/2026:** mã A–E đã nằm trên main tại
> [57db982274e267218594ae5ca463bd2a42d2be02](https://github.com/quoctran-2608/BuddhismDocuments-for-AI/commit/57db982274e267218594ae5ca463bd2a42d2be02).
> Bảng 394 tests/số đo E1–E3 và nhận xét “main vẫn nền D/không merge” bên dưới
> giữ bối cảnh checkpoint `1b2d0f0` và báo cáo trước merge. Phần gia cố span
> ghi 410/410 riêng; [evidence cuối](evidence/README.md) chỉ rõ log chạy mã
> `4986216…`, commit evidence-only `57db982…` và giới hạn bằng chứng lần chạy lại.
> Không đổi benchmark cũ thành benchmark sau sửa span. Mã đã gộp không mở
> Research publication hoặc nghiệm thu học thuật toàn 2.0.


E đã hoàn thành phần lớn phần khả dụng trong môi trường này, còn các điều
kiện rõ ràng chưa đạt. Quick tra cứu và kiểm nguồn thật; Research tạo hồ sơ
có bằng chứng/biên nhận, sửa luận điểm và xuất/nhập thẩm định, giữ dự thảo.
Không có kênh semantic approval xác thực nên chưa được phép công bố Research.
Không tuyên bố toàn bộ BCR 2.0 hoàn thành hoặc tự quyết định merge/ngưỡng.

## Phạm vi triển khai

- Adapter `LocalHost` sau retrieval 1.0; đọc Git blob/pin + resolver riêng
  Bilara JSON, CBETA TEI, 84000 TEI, tự giải vị trí/vai trò/nhân chứng. Chỉ quote
  span liên tục trong byte gốc, không ghép XML/JSON escape thành nguồn giả.
- Entry point `buddhist-research`: Quick/search-verify/quote tách khỏi B/C/D;
  Research create/show/capture/claim-add/revise/export/import/finalize/check.
- `LocalResearch` dùng D store hiện có; audit retrieval, A evidence thật,
  candidate B, C plans/actual receipts, version/history và package phản biện.
  Reader semantic mặc định thiếu; report nhập là PROPOSED, không tự phê duyệt.
- C nối search/evidence/context/work/resolve văn bản; pointer hit được đối
  chiếu A, scope từng bước đúng corpus/pin/profile, bound bị cắt báo incomplete.
  Parallels/variants có raw data, chưa xác minh metadata/dị bản bằng A.
- `ConnectorHost` giữ production locator → pointer → upstream ghim; JSON và
  pure contract chạy không SQLite/shell. Một ca GitHub Connector thật đạt A.
- Benchmark tái sử dụng được, 11 golden rule descriptors + positive controls,
  integration nguồn thật, regression các lỗi E và hướng dẫn [USAGE.md](USAGE.md).

Không đổi mã A/B/C/D, toàn bộ test cũ, 13 gitlinks/manifest/pins, schema/SQLite
corpus/ranking/FTS/lệnh 1.0 hay production locator. PRD/DESIGN và kế hoạch năm
chặng A–E giữ nguyên tiêu chí; chỉ cập nhật nhận định trạng thái đã lỗi thời.

## Kiểm thử và cách hiểu

Bảng và evidence lịch sử dưới đây ghi kết quả checkpoint `1b2d0f0`, trước
vòng gia cố span. Kết quả chạy lại được ghi riêng ở phần ngay sau bảng.

| Bộ | WSL chạy/đạt | Windows chạy/đạt | Failure/error/skip |
|---|---:|---:|---|
| Baseline D trước E | 318/318 | 309 chạy, 282 đạt, 29 error entries | Windows chưa đủ nguồn và lỗi cleanup cũ |
| A | 44/44 | 44/44 | 0/0/0 |
| B | 82/82 | 82/82 | 0/0/0 |
| C | 70/70 | 70/70 | 0/0/0 |
| D | 77/77 | 77/77 | 0/0/0 |
| E local fixture | 40/40 | 40/40 | 0/0/0 |
| E Connector/Work contract | 11/11 | 11/11 | 0/0/0 |
| Golden software, thuộc E | 11/11 | 11/11 | 0/0/0 |
| E corpus thật | 14/14 | 0 chạy | Windows 1 class skip thiếu nguồn |
| Toàn suite sau E | 394/394 | 371 chạy, 344 đạt, 29 error, 1 class skip | Windows còn lỗi cũ; WSL 0/0/0 |

76 bài E gồm 62 portable và 14 corpus thật; golden là tập con, không cộng
hai lần. WSL Python 3.12.3/SQLite 3.45.1, đủ 13 source pins. Windows Python
3.14/SQLite version trong evidence. Baseline Windows thiếu nguồn và old tests
có connection chưa đóng trước TemporaryDirectory cleanup. Lượt CLI full trước có 30
error entries, một cleanup bổ sung đã tái hiện trên commit nền. Lượt counted
cuối có 29 error entries cùng baseline; 344 successes = 282 baseline + 62 E.
Cleanup SQLite cũ có dao động theo thời điểm thu gom connection.
Không sửa implementation/test 1.0 để che lỗi, không gọi Windows full là đạt.
Đếm success/error/class skip trực tiếp bởi unittest trong báo cáo counted;
setUpClass error/skip không tăng testsRun, teardown có thể thêm error thứ hai.

11 golden descriptors có đủ câu hỏi, scope/source, evidence/counter, claim
đúng/sai, expected, limitations, pass criterion và tên method trong repo.
Reviewer/approval trong test là software oracle. Có control accepted hợp lệ
cho textual/relationship và synthesis, cùng ca thiếu căn cứ giữ candidate;
không dùng hệ thống chặn mọi claim để tự nhận thành công. 14 ca thật kiểm byte,
SHA, segment, note/main, rank, C và D; chưa có expected interpretation độc lập
cho toàn bộ 11 mẫu. Logs và JSON: [evidence](evidence/README.md).

### Gia cố chọn span trước merge

Đã tái hiện lỗi tại bản E được duyệt `e4c02d95`: một TEI unit hoặc Bilara
chunk có span dài không chứa từ khóa và span ngắn chứa từ khóa. Quick trả
VERIFIED cho span dài; `quote --text` từ chối câu đúng trong span ngắn. Bốn
regression ban đầu thất bại ở cả Bilara chunk, CBETA TEI và 84000 TEI
(12 subtest failures). Đây là lỗi chọn đoạn trong E, không phải lỗi cửa A.

Resolver nay chọn trong các span của đúng unit đã giải từ nguồn ghim: theo
câu trích bằng phép exact/normalized hiện có của A, hoặc theo truy vấn Quick
bằng exact/normalize/fold/compact. A vẫn kiểm câu thực, pin/blob/location và
đọc nguồn độc lập lần hai; hai lượt phải giải cùng range. Không lấy offset
từ pointer/transport, không ghép span qua markup/JSON, không đổi A/B/C/D.
Nếu truy vấn chỉ khớp xuyên span, trong metadata, qua lemma/FTS mà không có
dạng truy vấn trong một span, giữ retrieval hit/rank nhưng không cấp quote
VERIFIED. Không có hint vẫn chọn span dài nhất. Giới hạn ghi trong [USAGE.md](USAGE.md).

Thêm 16 bài ở `test_source_span_selection.py`: Quick và quote CLI cho span
ngắn ở cả ba định dạng, reread/Connector, sai hoặc thiếu vị trí, sai pin/blob,
offset giả, câu ghép qua markup/chunk, query thuộc note/unit khác hoặc xuyên
span, normalized/folded query với quote nguyên byte, ranh giới từ, hành vi
không hint, và second read khác range bị A chặn. Giữ nguyên toàn bộ bài cũ.
WSL chạy lại: E portable **78/78**, E corpus thật **14/14**, toàn suite
**410/410**, không failure/error/skip. Đủ 13 nguồn ghim; HEAD và tracked bytes
nguồn được kiểm trước/sau và giữ nguyên. Windows E portable **78/78**;
không chạy lại Windows full trong vòng này. Harness/logs vòng này giữ ngoài
Git tại `phase-e-evidence-20261011/span-fix-*`; không ghi đè evidence lịch sử.

Để tái chạy offline trên môi trường có đủ nguồn: `PYTHONPATH=tools python3
-m unittest discover -s tests -v`; có thể chạy từng `test_local_integration.py`,
`test_connector_contract.py`, `test_golden_research.py`,
`test_source_span_selection.py`, `test_corpus_integration.py` bằng `-p`.
`BCR_SOURCE_ROOT` chọn checkout nguồn đã có cho E corpus thật; các bài 1.0
cần nguồn tại layout checkout như lần WSL đã chạy. Không tải nguồn bị thiếu.

Các số E1/E2/E3 phía dưới vẫn là phép đo lịch sử ở checkpoint `1b2d0f0`,
không phải số đo sau sửa span. Vòng gia cố chỉ chạy regression/integration;
không đo lại hiệu năng, chất lượng học thuật, thẩm định độc lập hay AI cost.

## E1 — Bảo toàn 1.0

Baseline lịch sử: `f7415f574ed1510d5854ee00db6baafe2484e355`, main gần nhất
trước A đã ghi trong nghiệm thu A. `verification.py` chưa tồn tại. Truy vết
lịch sử cho thấy code retrieval đã ổn định trước đó; blob manifest/config/
index/retrieval/CLI/model khớp checkpoint E. Không lấy main có A–D làm 1.0.

Cùng index acceptance hash và 13 pins: 25.394 records, 12 works, 3.931
relations, 3.646 variants, 1.270 lemmas. Build riêng 2.726 giây, không cộng
vào latency. Lượt cuối 14 observations sau 1 warm-up mỗi tác vụ; giữ cả lượt
7 observations trước đó. Không chọn lượt nhanh nhất. Cache warm, không flush,
không đo startup/host construction; chạy nhóm legacy trước nhóm E, không
interleave, nên dao động lịch thực thi/cache nền có thể ảnh hưởng chênh lệch.
Các symlink worktree đo và hash mã được khai rõ trong raw, không thay pins.

| Tác vụ | 1.0 median ms | E retrieval median ms | Chênh | Output/rank/provenance giống |
|---|---:|---:|---:|---|
| pali | 1.657 | 0.915 | -44.8% | Có |
| latin | 1.156 | 0.650 | -43.8% | Có |
| cjk | 2.228 | 1.471 | -34.0% | Có |
| identifier | 0.817 | 0.518 | -36.6% | Có |
| context | 0.580 | 0.527 | -9.2% | Có |
| evidence | 2.122 | 2.032 | -4.3% | Có |
| provenance | 0.296 | 0.299 | +1.0% | Có |
| work | 2.902 | 2.910 | +0.3% | Có |
| parallels | 1.141 | 1.138 | -0.3% | Có |
| variants | 3.904 | 3.787 | -3.0% | Có |
| resolve | 6.354 | 6.083 | -4.3% | Có |
| compare | 13.988 | 13.742 | -1.8% | Có |

12/12 tác vụ có kết quả đầy đủ/hash giống qua mọi observation. Có đo thật
thời gian và tài nguyên, nhưng không suy ra 2.0 cải thiện tốc độ từ dao động
microbenchmark khi code retrieval giống hệt; cũng không tuyên bố không suy
giảm ở index đầy đủ/cold cache. **CHỜ CHỐT NGƯỠNG**.

## E2 — Chi phí Quick

Cùng truy vấn/corpus và limit=1: retrieval 1.0 so với Quick có A thực.

| Nguồn | 1.0 ms | Quick ms | Tăng ms | Retrieval / đọc nguồn / kiểm A ms | Source reads |
|---|---:|---:|---:|---|---:|
| suttacentral-bilara | 0.916 | 18.948 | 18.032 | 1.117 / 17.402 / 0.242 | 2 |
| cbeta-tei | 1.434 | 73.613 | 72.179 | 1.709 / 57.513 / 13.698 | 2 |
| 84000-tei | 2.183 | 37.487 | 35.303 | 2.526 / 29.609 / 5.259 | 2 |

Mỗi tác vụ có một A VERIFIED, rank/content retrieval giữ nguyên; không B/C/D
hay approval/AI. Phần tăng chủ yếu là Git pinned reads, decode/giải nguồn và
kiểm ngữ cảnh/byte XML, chứ không phải xếp hạng. Đã tránh lookup evidence DB
lặp cho hit search, dùng LRU parser theo full immutable content, giới hạn tập
ứng viên; giữ hai lượt source read bắt buộc. Median từng phase có thể không
cộng chính xác thành median tổng. CHỜ CHỐT NGƯỠNG latency và bộ nhớ.

## E3 — Research và giới hạn phép đo chất lượng

Research mẫu thực chạy 14 lần: median 128.850 ms,
min/max 122.667/133.145 ms, CPU self+
child median 89.475 ms. Mỗi run có 1 evidence,
1 candidate claim, 2 retrieval calls,
8 source reads, 1 bước C thực thi; query
counter này có 0 ứng viên, không diễn giải thành không tồn tại phản chứng.
Accepted claims=0 là trạng thái quan sát do thiếu approval, không phải tỷ lệ
chặn nhầm. Không có kết luận Research được công bố. Golden software chạy
11 cases/lượt: median 16.767 ms, 14 lượt;
đủ positive controls và nhánh chặn/pending đã nêu.

| Worker | Self peak MiB | Child peak MiB | Median CPU mỗi observation ms | Tổng IO input/output blocks |
|---|---:|---:|---:|---:|
| legacy | 30.12 | 0.00 | 1.848 | 0 / 0 |
| current | 30.29 | 0.00 | 1.483 | 0 / 0 |
| quick_baseline | 30.00 | 0.00 | 1.502 | 0 / 0 |
| quick | 115.76 | 115.76 | 33.328 | 0 / 0 |
| research | 30.00 | 27.35 | 89.475 | 0 / 8848 |
| golden | 30.00 | 0.00 | 16.853 | 0 / 0 |

RSS là high-water toàn process, gồm warm-up/case trước; không phải memory
allocation riêng cho mỗi query. Quick peak cao hơn do parse/giữ cấu trúc và
byte XML; chưa đo steady-state/live app/large corpus. IO bytes/chars self và
block IO self+children nằm trong raw; cached zero IO là số đọc được.

**CHƯA ĐO** lỗi học thuật bỏ lọt, luận điểm hợp lệ bị chặn nhầm, hiệu quả tìm
phản chứng ngữ nghĩa và giá trị tăng thêm của reviewer, vì không có expected
answers/reviewer độc lập thực tế. Không lấy đồng ý hai AI làm chuẩn. Token/
chi phí AI **CHƯA ĐO**, không gọi dịch vụ AI; không gán 0 thay cho số chưa đo.
Fixture 11/11 là kết quả kiểm quy tắc phần mềm, không phải tỷ lệ đúng Research
trên corpus. Mẫu số khoa học chưa có, không dựng phần trăm giả.

## Ví dụ Research thực

Câu hỏi: trong các đoạn tìm bằng `sutaṃ`, bản ghim ghi câu nào? Corpus chỉ
Bilara trong acceptance profile. Search thực chọn MN1 `mn1:1.1`; A mở
`root/pli/ms/sutta/mn/mn1_root-pli-ms.json` ở SHA
`0914c609e49215bb1473199929ee8a2996b423c4`, blob
`096c49f188d43174850a5bfebdc3432789cae836`. Đọc được **“Evaṁ me sutaṁ—”**, đúng
byte gốc, role root_text, language pli, witness root:root-pli-ms, seq=2.

B tạo đề xuất hẹp “Đoạn mn1/mn1:1.1 có câu trích: Evaṁ me sutaṁ—”; chưa có
assessment xác thực nên giữ candidate. C thực chạy `anicca` trong corpus/pin/
profile đã giao, không thấy hit trên mẫu, ghi checked/unchecked scope và
cảnh báo không kết luận phản chứng không tồn tại. Đây là hướng lexical chưa
được reviewer chứng nhận tính phù hợp. D lưu run, source context, phiên bản,
A/B/C và xuất gói phản biện; final/publication vẫn chặn. Không suy ra nghĩa
triết học, tương đương Pāli–Hán hay kết luận phổ quát từ ví dụ này.
[Hồ sơ JSON](evidence/research-example.json) có claim/evidence/receipt/package
hash; DB/gói lớn giữ ngoài Git. Mã chạy đúng checkpoint E, không giả mốc main.

## Work/Connector và phản biện

11 fixture kiểm roundtrip, source binding, blob/SHA/location, fake flags,
missing reader, namespace/hash bucket và pure import không SQLite/shell.
Work: **CHƯA KIỂM PHIÊN THỰC**. Thẩm định độc lập: **CHƯA THẨM ĐỊNH ĐỘC LẬP
THỰC TẾ**. Export/import/revision/snapshot/currentness/host-decision đã kiểm
software + local sources; approval oracle không phải một người có quyền.

Connector thật dùng tài khoản repo đã cấp quyền, production locator SHA
`b31a154863c347f150a3bbb2df8bf269b50aeade`, `ids/mn1`, bucket `07`, rồi Bilara
ghim đọc hai lần; A VERIFIED cho `mn1:0.1` (“Majjhima Nikāya 1 ”). Không dùng
Code Search. Lần đầu thiếu language trong production pointer làm A reject;
E điền khi thiếu từ resolver, không ghi đè trường khai sai, có regression.
Một ca đó không chứng minh full Work/Connector, remote C/D workflow, hoặc
chuỗi parallel → identifier bridge → CBETA source đã được nghiệm thu.

## Nghiệm thu và việc còn chờ

Ma trận [ACCEPTANCE.md](ACCEPTANCE.md) giữ 31 yêu cầu + 2 bổ sung, cập nhật
trạng thái/evidence không làm yếu tiêu chí. Phần khả dụng đã có mã/fixture/
nguồn thật/số đo; Research publication và full BCR 2.0 **chưa nghiệm thu**.

Còn thiếu resolver các định dạng khác/metadata/variants; câu trích qua markup;
đáp án nghiên cứu và reviewer độc lập; policy/authenticated semantic approval
cùng publication coordination/currentness; Work và rộng hơn một ca Connector;
benchmark index đầy đủ/cold cache và ngưỡng chính thức. Windows full chưa đạt.
Không tự thêm dịch vụ hai AI, ứng dụng web, corpus, model hay thay kiến trúc.

Người bảo trì cần chốt ngưỡng từ số đo, cung cấp/phê chuẩn kênh thẩm định thực,
thử Work/Connector ở runtime đích, rồi rà soát độc lập trước quyết định merge.
Không tạo thêm phase. Nhánh E được commit/push, main vẫn nền D; không PR/merge.
Danh sách tệp, kiểm pins/code và trạng thái Git cuối nằm trong evidence audit.
