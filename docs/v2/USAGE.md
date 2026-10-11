# Sử dụng phần tích hợp E

Quick đã tra cứu/kiểm nguồn được; Research tạo hồ sơ dự thảo và gói phản biện.
Research chưa có quyền công bố kết luận đã được chấp thuận. Các lệnh 1.0 trong
[CLI.md](../CLI.md) giữ nguyên. Kết quả và giới hạn nghiệm thu xem [E_REPORT.md](E_REPORT.md).

Mã A–E đã gộp trên main tại `57db982274e267218594ae5ca463bd2a42d2be02`
(11/10/2026). Bản đồ môi trường × quy trình: [AI_ONBOARDING](../AI_ONBOARDING.md).

## Chuẩn bị local

Python chuẩn, Git và SQLite có FTS5; không cần package hay dịch vụ AI mới.
Chỉ dùng 13 checkout đã có đúng manifest. Không tự tải nguồn để chạy ví dụ.
Index phải đúng pins/parser/profile; nếu còn WAL chưa checkpoint thì adapter
từ chối vì reader immutable của 1.0 không đọc WAL.

Từ thư mục repo, PowerShell:

```powershell
$env:PYTHONPATH = 'tools'
python -m corpus_research.v2_cli --help
```

WSL/Linux:

```sh
export PYTHONPATH=tools
bin/buddhist-research --help
```

Ví dụ dưới dùng index hiện có `derived/corpus.sqlite3`. Nếu cần index mẫu và
đã có đủ nguồn, dựng riêng bằng CLI 1.0 (`bin/buddhist-corpus build --help`),
không ghi đè index đang sử dụng. Các phép đo E dùng profile `acceptance`, chưa
chứng minh hiệu năng/quy mô index đầy đủ. Có thể truyền `--db` khác.

`--root` chọn checkout mã/config; `--source-root` chọn checkout dữ liệu đã có
khi nguồn ở thư mục khác. Đây là cấu hình host ở CLI, không phải trường trong
proposal/approval JSON. Store, gói phản biện và artifact phải ở ngoài nguồn
ghim và khác corpus index.

Global options `--root`, `--source-root`, `--db`, `--store` phải đặt **trước**
subcommand. Đổi `--root` không đổi mặc định `--db/--store` (chúng lấy root của
mã entry point); dùng đường dẫn tường minh khi chọn checkout khác. `run-show`
cũng khởi tạo LocalHost/ResearchStore, cần index hợp lệ; không là reader JSON
thuần cho một package gửi tới Work.

Kết quả lệnh E ra JSON UTF-8 stdout, exit 0 khi dispatch thành công, kể cả
gate trả `REJECTED`/`UNVERIFIED` hoặc publication false. Phải kiểm status và
`checks`, không chỉ exit code. ValueError/OSError/SQLite error được bắt: JSON
`status=UNVERIFIED`, `publication_authorized=false`, `error` ra stderr, exit 2;
lỗi cú pháp argparse in usage/error thông thường ra stderr, exit 2.

## Quick và câu trích

```sh
python -m corpus_research.v2_cli quick 'sutaṃ' --corpus suttacentral-bilara --limit 1
python -m corpus_research.v2_cli quick '如是我聞' --corpus cbeta-tei --limit 1
python -m corpus_research.v2_cli quick 'Thus' --corpus 84000-tei --limit 1
python -m corpus_research.v2_cli quote --record-id RECORD_ID --text 'EXACT_SOURCE_TEXT'
```

Thay `RECORD_ID` bằng ID từ kết quả search của chính index; ID index không phải
ID kinh hay bằng chứng. Trong kết quả Quick, `retrieval` giữ nguyên dữ liệu/rank
1.0; chỉ `verified_evidence` chứa bản ghi A đã kiểm từ blob Git. `quote` trả
gate envelope `status/checks/evidence` trực tiếp; chỉ dùng `evidence` khi
`status == 'VERIFIED'`. Không tạo Research Run,
không gọi B/C/D hoặc semantic reviewer. Để xem work/context/parallels/variants/
resolve/provenance, tiếp tục dùng lệnh 1.0 hoặc `LocalHost.retrieve()`; kết quả
metadata giữ là metadata, không tự thành bằng chứng câu chữ.

Resolver hiện hỗ trợ Bilara JSON, CBETA TEI và 84000 TEI. Nó tự giải work,
segment, sequence, vai trò, witness/ngôn ngữ theo định dạng nguồn. Bilara phân
biệt root/translation/comment; CBETA loại note/rdg khỏi dòng gốc; 84000 tách
heading/main/note. Phạm vi trích là một đoạn text liên tục không escape trong
nội dung UTF-8 nguồn, có thể ngắn hơn đoạn hiển thị 1.0. Range được resolver
tính theo chỉ số ký tự Python trên chuỗi nguồn, không phải byte offset do đầu
vào khai. Không ghép câu qua markup/entity hoặc tái tuần tự hóa XML để làm
câu trích. Context có thể chứa markup nguồn.
Khi một unit/chunk có nhiều span, `quote --text` chọn span chứa câu trích
theo đúng phép kiểm exact/normalized của A; Quick chọn span chứa truy vấn
(exact, chuẩn hóa, bỏ dấu hoặc compact), rồi trích byte nguồn thực. Không có
hint thì vẫn chọn span dài nhất. Hai lượt đọc ghim phải giải ra cùng phạm vi.
Offset/range tự khai trong pointer hoặc transport không chọn được span.
Quick giữ hit/rank 1.0 nhưng không trả quote VERIFIED nếu truy vấn chỉ khớp
qua nhiều span/markup, metadata/identifier, lemma hoặc FTS mà không có dạng
truy vấn tương ứng trong một span nguồn. Khi đó dùng locator để xem ngữ cảnh
và `quote --text` cho câu thực trong đúng unit; không tự nối hoặc bịa câu.
Định dạng khác, XML có DTD/entity, đoạn không giải chắc chắn hoặc tệp quá 20 MB
giữ chưa xác minh. Đừng suy rộng ba resolver thành hỗ trợ đủ 13 corpus.

## Research dự thảo và thẩm định

```sh
python -m corpus_research.v2_cli run-create --run-id example-1 --question 'Nguồn ghim ghi câu nào tại các đoạn tìm được?' --query 'sutaṃ' --corpus suttacentral-bilara --counter-query 'anicca' --limit 1
python -m corpus_research.v2_cli run-show --run-id example-1
python -m corpus_research.v2_cli run-capture --run-id example-1 --version CURRENT_VERSION
python -m corpus_research.v2_cli review-export --run-id example-1 --version CURRENT_VERSION --question 'Kiểm câu trích, vai trò và phạm vi.' --output derived/reviews/example-1
python -m corpus_research.v2_cli review-import --input REPORT.json
python -m corpus_research.v2_cli publication-check --run-id example-1 --version CURRENT_VERSION
```

Lấy version mới sau mỗi mutation; dùng version cũ bị chặn. Gói xuất phải dùng
path mới; không ghi đè. JSON + Markdown gồm snapshot/căn cứ và câu hỏi thẩm
định, không có chuỗi suy nghĩ riêng. Báo cáo nhập chỉ là `PROPOSED`. Mẫu report
và các trường bắt buộc xem hợp đồng `research_store.import_review()` và test
roundtrip trong `tests/test_local_integration.py`; bằng chứng/report phải nối
đúng claim, package và snapshot. Cờ `trusted/approved/accepted` không cấp quyền.

`claim-add --input PROPOSAL.json` và `claim-revise --claim-id OLD_ID --input
PROPOSAL.json --reason REASON --revision-evidence-id EVIDENCE_ID` cần `--run-id`
và `--version`. D giữ bản cũ, tạo ID mới và làm hết hiệu lực kết quả dẫn xuất.
Mở lại run gọi `prepare()` rồi đọc A lại từ locator/quotation; snapshot không
được dùng như một capability hay approval.

`run-finalize` và `review-decision` có sẵn nhưng CLI mặc định không cấu hình
semantic approval. Chúng giữ lỗi/chưa xác minh; hồ sơ không bị giả chốt. Kể
cả hồ sơ đã finalized cũng không tự có giấy phép công bố.

`LocalHost` cho host ứng dụng nối các reader đã được xác thực; JSON không chọn
reader. D cung cấp `history_reader` qua transaction/version; `context_reader`
đọc Git HEAD/pins/config. Chưa có chính sách xác thực người duyệt được cung cấp
trong nhiệm vụ này nên không có lệnh nhận tệp tự phê duyệt. B giữ rào chắn
Research; cần cơ chế phê duyệt, currentness và phối hợp công bố được kiểm chứng
trước khi mở. Fixture callback trong test không phải kênh đó.

C thực thi `search`, `evidence`, `context`, `work`, `resolve` qua retrieval 1.0
và xác minh các hit văn bản hỗ trợ bằng A. `parallels/variants` có raw receipts
thật nhưng chưa có resolver A cho metadata/dị bản: báo incomplete. Mỗi bước
ghi riêng corpus/pin và profile; bound mặc định 20, tối đa 100. Mọi thao tác
bị cắt báo incomplete. `host.receipts` lưu raw operations để kiểm toán, không
phải quyền thẩm định. Hướng lexical chưa có reviewer xác nhận tính phù hợp;
không gọi chúng là phản chứng ngữ nghĩa đã được phát hiện. No-hit không chứng
minh phản chứng không tồn tại, đặc biệt trên profile mẫu.

## Work và GitHub Connector

`ConnectorHost` là adapter chuẩn Python không nhập SQLite/subprocess và không
tự gọi mạng. Ứng dụng nối `source_fetch`/`locator_fetch` vào công cụ GitHub đã
được cấp quyền. Host chọn pins/config từ cấu hình tin cậy, khóa SHA locator;
đừng cho proposal chọn nguồn hay callback. Callback nhận chính xác
`repository/source_sha/source_path`, đọc đầy đủ ở ref đó, trả identity đã
kiểm qua metadata công cụ + `content/source_blob_sha`. Không cắt dòng, chuẩn
hóa newline hay chỉ trả nội dung một đoạn. Thiếu binding hoặc byte/blob không
khớp thì chưa xác minh. A gọi lại reader độc lập trước khi cho qua.

```python
from corpus_research.connector_host import ConnectorHost

# Các biến cấu hình/reader/SHA dưới đây do host xác lập ngoài proposal.
host = ConnectorHost(trusted_source_contract, trusted_remote_config,
    locator_commit=PINNED_LOCATOR_SHA,
    locator_fetch=authenticated_github_reader,
    source_fetch=authenticated_github_reader)
found = host.lookup('ids', 'mn1')  # hoặc terms/latin với normalization hiện có
if found['status'] == 'CANDIDATE' and found['pointers']:
    checked = host.verify_pointer(found['pointers'][0], evidence_id='host-id')
```

Production v1 không lưu language: adapter chỉ điền khi thiếu, từ resolver
nguồn; language khai sai vẫn bị chặn. Remote locator chỉ là tuyến pointer,
không thành corpus thứ 14. Không dùng Code Search hay tự thêm CJK namespace.
Quan hệ song hành → identifier bridge → CBETA textual witness vẫn ba bước
riêng. Một ca Connector thật đã đi đến A VERIFIED, xem evidence; chưa nghiệm
thu toàn Connector hoặc phiên ChatGPT Work. JSON roundtrip và portable import
đã kiểm bằng fixture. Không có thẩm định độc lập thực tế hay dịch vụ hai AI.

## Tái lập kiểm thử và benchmark

```sh
PYTHONPATH=tools python -m unittest discover -s tests -v
BCR_SOURCE_ROOT=/existing/source/checkout PYTHONPATH=tools python -m unittest discover -s tests -p test_corpus_integration.py -v
PYTHONPATH=tools python -m corpus_research.v2_benchmark --root /existing/current/code --legacy-root /existing/pre-A/checkout --source-root /existing/sources --db /existing/acceptance.sqlite3 --output /outside/source/measurement.json.gz --repeats 7
```

Nguồn thật chỉ chạy khi đủ 13 checkout đúng pins; fixture/golden chạy độc lập.
Không dùng path cá nhân làm điều kiện bắt buộc của golden cases. Benchmark
chỉ đo Linux/WSL để ghi đúng đơn vị tài nguyên. Dùng cùng index và cache warm,
không tính build index/startup/host construction vào thời gian tác vụ. Raw
JSON gzip giữ các lượt chạy, kết quả thật/rank/provenance và hash mã; giải nén
bằng `gzip` chuẩn Python nếu cần kiểm. CHỜ CHỐT NGƯỠNG, không tự nghiệm thu.

## Python API và hợp đồng host

Đây là giao diện đã triển khai cho ứng dụng host/lập trình viên, chưa cam kết
ổn định API. Imports dùng `corpus_research.<module>` với `PYTHONPATH=tools`.
`root/db/path` là cấu hình ứng dụng; reader là callable do host chọn và xác
thực ngoài proposal/report JSON. Giá trị trả về là dữ liệu, không capability.
Ví dụ local: [onboarding](../AI_ONBOARDING.md#4-giao-diện-thật).

| Module / chữ ký gọi (bỏ `self`) | Input/output và giới hạn |
|---|---|
| `local_host.LocalHost(root, db, *, source_root=None, assessment_reader=None, review_reader=None, dependency_reader=None, max_candidates=20)` | Index read-only, pins config từ root; nguồn đã có; host bound 1..100 |
| `LocalHost.quick(query, *, corpus=None, language=None, limit=3)` | Retrieval + A envelopes/evidence/limitations/metrics; không tạo run |
| `LocalHost.verify_record(record_id, *, quotation=None, run_id=None, retrieval_query=None)` | Record ID → gate A; recipe chỉ đăng ký khi VERIFIED |
| `LocalHost.verify_pointer(pointer, *, quotation=None, run_id=None, retrieval_query=None)` | Pointer → nguồn ghim/range đã giải → A; offset/flags không mang quyền |
| `LocalHost.retrieve(operation, *args, **kwargs)` | Retrieval 1.0 được hỗ trợ; không tự gate metadata |
| `LocalHost.evidence_reader(evidence_id)` | Recipe host → A mới, không phát lại snapshot |
| `local_research.LocalResearch(host, path)` | D store riêng ngoài nguồn và corpus index |
| `LocalResearch.create(*, run_id, question, queries, corpora, limit=3, counter_queries=None)` | Scope host/index → run draft, artifact/receipts; literal textual candidate |
| `LocalResearch.prepare(run_id)` | Khôi phục locator/quotation proposals; lần dùng evidence tiếp theo chạy A lại |
| `LocalResearch.capture(run_id, *, expected_version, review_ids=None, counter_requests=None)` | Fresh A/B/C observations → snapshot version mới |
| `LocalResearch.finalize(run_id, *, expected_version, review_ids=None)` | Chốt audit khi checks PASS; thiếu approval mặc định bị chặn |
| `LocalResearch.publication_check(run_id, *, expected_version, review_ids=None)` | Fresh B/history checks; publication false |
| `connector_host.ConnectorHost(source_contract, remote_config, *, locator_commit, source_fetch=None, locator_fetch=None, review_reader=None)` | Host pin config/locator + readers; không tự mạng/SQLite/shell |
| `ConnectorHost.lookup(namespace, key)` | terms/latin hoặc exact ids → CANDIDATE/UNVERIFIED; không tự gọi A |
| `ConnectorHost.verify_pointer(pointer, *, evidence_id, quotation=None, run_id=None)` | Fetch đầy đủ → resolver/A; evidence_id do host cấp không chứng minh nguồn |
| `research_store.ResearchStore(path, *, context_reader=None, evidence_reader=None, assessment_reader=None, search_reader=None, dependency_reader=None, clock=None)` | DB persistent riêng; quyền file/auth do host |
| `ResearchStore.get_run(run_id, *, version=None)` | Snapshot/version và supersession projection; dữ liệu audit |
| `ResearchStore.run_history(run_id)` | Danh sách snapshot append-only theo version |
| `ResearchStore.trace_claim(run_id, claim_id)` | Evidence/assessment/counter/successors; historical observation |
| `ResearchStore.export_review(run_id, *, expected_version, review_questions)` | {json, markdown}; capture trước export; không cấp quyền |
| `ResearchStore.import_review(report)` | Kiểm package/hash/comment/citation → PROPOSED |
| `ResearchStore.record_review_decision(report_id, *, review_id)` | Cùng B assessment_reader, ASSESSED/binding → RECORDED hoặc UNVERIFIED; không publication |

Lõi nhận/trả dict/list JSON; chữ ký/validators xem trực tiếp
[A](../../tools/corpus_research/verification.py), [B](../../tools/corpus_research/claims.py),
[C](../../tools/corpus_research/counterevidence.py), [D](../../tools/corpus_research/research_run.py).
Hai điểm gọi lõi mẫu dưới đây cần biến/reader được **ứng dụng host** xác lập:

```python
from corpus_research.verification import evidence_gate
from corpus_research.claims import assess_claim

a_result = evidence_gate(candidate, source_contract, opened_source,
    mode='quick', source_reader=authenticated_source_reader)
b_result = assess_claim(claim, review_id=host_review_id,
    evidence_reader=fresh_a_reader, assessment_reader=authenticated_assessment_reader)
```

Không dùng mẫu này để tự nối callback phê duyệt. Candidate/opened_source là
DATA; A cần reader độc lập/source binding; B cần approval đúng subject/evidence.
Chỉ kiểm assessment khác null là sai: B REJECTED vẫn có thể chứa assessment.
UNSUPPORTED/CONTRADICTED trong assessment ASSESSED là đánh giá âm hợp lệ, được
lưu trong audit ở tập luận điểm bị bác bỏ.

## Review package và trạng thái

Ngữ nghĩa: [DESIGN mục 14.5](DESIGN.md#145-xuấtnhập-hồ-sơ-thẩm-định-độc-lập).
Shape thực thi: [ResearchStore](../../tools/corpus_research/research_store.py)
export_review/import_review/record_review_decision; mẫu report đầy đủ và negative
cases tại [test_local_integration](../../tests/test_local_integration.py) và
[test_research_run](../../tests/test_research_run.py). Không tạo schema thứ hai.

Package có package_id, run/version, snapshot_sha256, snapshot, run_history,
predecessor_snapshot, review_questions, exported_at và publication false.
Report phải trỏ đúng package/hash hiện hành, nhận xét từng claim với citation
đã có/đã kiểm trong snapshot và ghi reviewer/role/session/quan hệ với proposer
cùng phần unverified. Reviewer tự khai chưa là identity đã được xác thực.
Cờ approved/trusted/status không tạo approval; import chỉ PROPOSED. Đổi draft/
version sau export làm package/report cũ stale.

review_id chỉ tra assessment_reader host đã cấu hình; quyết định report lưu
riêng phải kiểm B ASSESSED và evidence khớp snapshot. RECORDED không sửa claim,
không tự finalization hoặc publication. Sửa claim tạo ID mới/history, capture
lại và thẩm định lại. Run finalized có thể giữ assessment âm hợp lệ để kiểm toán;
không xóa UNSUPPORTED/CONTRADICTED khỏi lịch sử. publication-check luôn false.

## Xử lý lỗi và mở rộng

Tra [onboarding troubleshooting](../AI_ONBOARDING.md#9-troubleshooting).
Thiếu source/Git object hoặc sai pin thì dừng nhánh, không tải corpus.
Thiếu locator/callback/format giữ chưa xác minh; quote mismatch kiểm đúng unit/
câu thực. No-hit và C incomplete chỉ nói về phạm vi đã kiểm. Thiếu semantic
approval dùng draft/review package, không nối fake callback. Windows full và
Work còn giới hạn trong E_REPORT.

Khi được giao mở rộng resolver/adapter: đọc A/C contract, test source binding/
span/currentness và missing capability, giữ scope/receipts/limitations, chạy
kiểm thử lớp liên quan và nguồn thật nếu đã có. Không sửa pins/index/ranking/
CLI 1.0 hay nới gate để hợp ví dụ. Có fixture không đủ để tự nghiệm thu học thuật.
