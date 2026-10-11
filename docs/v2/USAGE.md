# Sử dụng phần tích hợp E

Quick đã tra cứu/kiểm nguồn được; Research tạo hồ sơ dự thảo và gói phản biện.
Research chưa có quyền công bố kết luận đã được chấp thuận. Các lệnh 1.0 trong
[CLI.md](../CLI.md) giữ nguyên. Kết quả và giới hạn nghiệm thu xem [E_REPORT.md](E_REPORT.md).

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

## Quick và câu trích

```sh
python -m corpus_research.v2_cli quick 'sutaṃ' --corpus suttacentral-bilara --limit 1
python -m corpus_research.v2_cli quick '如是我聞' --corpus cbeta-tei --limit 1
python -m corpus_research.v2_cli quick 'Thus' --corpus 84000-tei --limit 1
python -m corpus_research.v2_cli quote --record-id RECORD_ID --text 'EXACT_SOURCE_TEXT'
```

Thay `RECORD_ID` bằng ID từ kết quả search của chính index; ID index không phải
ID kinh hay bằng chứng. `retrieval` giữ nguyên dữ liệu/rank 1.0; chỉ
`verified_evidence` chứa bản ghi A đã kiểm từ blob Git. Không tạo Research Run,
không gọi B/C/D hoặc semantic reviewer. Để xem work/context/parallels/variants/
resolve/provenance, tiếp tục dùng lệnh 1.0 hoặc `LocalHost.retrieve()`; kết quả
metadata giữ là metadata, không tự thành bằng chứng câu chữ.

Resolver hiện hỗ trợ Bilara JSON, CBETA TEI và 84000 TEI. Nó tự giải work,
segment, sequence, vai trò, witness/ngôn ngữ theo định dạng nguồn. Bilara phân
biệt root/translation/comment; CBETA loại note/rdg khỏi dòng gốc; 84000 tách
heading/main/note. Phạm vi trích là một đoạn text liên tục không escape trong
byte nguồn, có thể ngắn hơn đoạn hiển thị 1.0. Không ghép câu qua markup/entity
hoặc tái tuần tự hóa XML để làm câu trích. Context có thể chứa markup nguồn.
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
host = ConnectorHost(trusted_source_contract, trusted_remote_config,
    locator_commit=PINNED_LOCATOR_SHA,
    locator_fetch=authenticated_github_reader,
    source_fetch=authenticated_github_reader)
found = host.lookup('ids', 'mn1')  # or terms/latin, with existing normalization
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
