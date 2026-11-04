# P0/1 — Truy xuất theo nguồn mệnh đề đã khai báo

Đây là đường **tùy chọn, local/offline**. Không thay xếp hạng retrieval 1.0,
`quick`, `run-create` hoặc CLI cũ. Kết quả `VERIFIED` chỉ xác minh nguồn/câu trích
qua A, không chứng nhận nguồn hỗ trợ ngữ nghĩa của mệnh đề.

## Kiểm một nguồn trước khi tạo draft

Chuẩn bị `source.json` từ định danh đã đối chiếu; ví dụ dưới dùng đúng Bilara
pin trong manifest và một segment thực thuộc SN 36.21:

```json
{
  "corpus": "suttacentral-bilara",
  "repository": "suttacentral/bilara-data",
  "work_id": "sn36.21",
  "source_path": "root/pli/ms/sutta/sn/sn36/sn36.21_root-pli-ms.json",
  "source_sha": "0914c609e49215bb1473199929ee8a2996b423c4",
  "witness": "root:root-pli-ms",
  "segment_id": "sn36.21:2.1"
}
```

```sh
export PYTHONPATH=tools
python -m corpus_research.v2_cli --db /path/to/existing.sqlite3 \
  --source-root /path/to/existing-source-checkouts \
  verify-source --claim-id my-claim --input source.json
```

PowerShell: `$env:PYTHONPATH='tools'`; dùng cùng các đối số trên một dòng.
Global options đứng trước subcommand. Không tải nguồn hoặc sửa index để chạy ví dụ.

`corpus` và `work_id` là bắt buộc. Các trường tùy chọn được hỗ trợ:

| Trường | Hợp đồng |
|---|---|
| `repository` | Phải khớp cấu hình host của corpus. |
| `source_sha` | Phải khớp pin manifest; bỏ trống trường này thì lấy pin do host quản lý và ghi đầy đủ trong evidence, không suy đoán phiên bản. |
| `source_path` | Đường dẫn **tương đối trong repo nguồn**, không thêm prefix checkout. Không traversal/absolute path. |
| `witness` | So khớp chính xác witness do resolver đọc từ nguồn; không tự chuẩn hóa hay gộp bản dịch/bản gốc. |
| `segment_id` | Định danh native chính xác, kể cả unit nằm trong chunk core. Không tự chuyển hệ đánh số hoặc nối range/span. |
| `quotation` | Câu trích cần kiểm trong đúng unit; A áp dụng phép kiểm hiện có. Không cung cấp thì resolver chọn span theo chính sách hiện có. |

Không gửi giá trị null/rỗng. `edition` và các trường lạ bị từ chối: schema/ba
resolver hiện tại chưa có hợp đồng edition thống nhất. Không đổi edition thành
witness theo suy đoán. `claim_id` là liên kết do caller cung cấp, không phải
quyền semantic approval hay điều kiện tìm kiếm FTS.

Đường mới lọc **đồng thời** corpus/work/path/pin, đọc blob Git ghim qua source
reader hiện có, so witness, rồi kiểm lại qua A. Chỉ một file phù hợp mới được
chọn; file có nhiều unit/chunk cần `segment_id`. Nếu chỉ có một unit/chunk,
evidence ghi rõ unit thực đã đọc, không có nghĩa đã đọc toàn tác phẩm.

Đọc `status`, `reason` và `gate`, không chỉ exit code. Exit 0 nghĩa dispatch
thành công, kể cả `REJECTED`/`UNVERIFIED`; lỗi input/I/O/SQLite theo quy ước E
ra stderr JSON và exit 2. Một số reason:

| Reason | Hành động |
|---|---|
| `PIN_MISMATCH`, `REPOSITORY_MISMATCH`, `INDEX_PIN_MISMATCH` | Kiểm pin/config/index; không đổi sang nguồn khác. |
| `DECLARED_SOURCE_NOT_INDEXED` | Work/path không có trong index hiện tại; báo thiếu coverage hoặc sai locator. Không khẳng định nguồn không tồn tại ở mọi nơi. |
| `SOURCE_OR_SEGMENT_UNAVAILABLE` | Đọc `failures`: thiếu repository/blob, segment không giải được hoặc span không hỗ trợ. |
| `WITNESS_MISMATCH` | Nguồn mở được không có witness khai báo. |
| `AMBIGUOUS_DECLARED_SOURCE` | Cần locator/witness cụ thể hơn; `candidates` chỉ là dữ liệu đề xuất. |
| `CANDIDATE_BOUND_EXCEEDED` | Cần thêm path/witness hoặc chính sách host rõ ràng; không cắt top-N rồi tự chọn. |
| `SEGMENT_REQUIRED_FOR_MULTI_UNIT_SOURCE` | Bổ sung segment đã được đối chiếu. |

Không có nhánh tự fallback sang từ khóa. SN 35.145 và SN 35.146 là hai work
riêng trong Bilara pin này; không tự sửa reference ở một hệ số khác sang một
trong hai số này. Quan hệ tương đương cần chứng cứ và quyết định riêng.

## Tạo draft giữ nguyên mệnh đề

Tạo `claims.json` có đúng hai khóa `claims` và `source_references`:

```json
{
  "claims": [
    {"claim_id": "my-claim", "text": "Mệnh đề gốc cần kiểm chứng.", "claim_type": "textual"}
  ],
  "source_references": {
    "my-claim": [{
      "corpus": "suttacentral-bilara", "work_id": "sn36.21",
      "source_path": "root/pli/ms/sutta/sn/sn36/sn36.21_root-pli-ms.json",
      "source_sha": "0914c609e49215bb1473199929ee8a2996b423c4",
      "witness": "root:root-pli-ms", "segment_id": "sn36.21:2.1"
    }]
  }
}
```

Thay text ví dụ bằng **nguyên văn claim cần kiểm**, chọn `claim_type` theo hợp
đồng B hiện có. Mỗi claim ID duy nhất phải có ít nhất một reference. Đây là
input cho run mới: không nhận supporting/counter evidence IDs hoặc revision
có sẵn; không sửa run/claim pilot lịch sử. Các alias như `E01#range` của Pilot
không được tự giải thành segment: phải truyền locator native đã đối chiếu.

```sh
python -m corpus_research.v2_cli --db /path/to/existing.sqlite3 \
  --source-root /path/to/existing-source-checkouts --store derived/p01-research.sqlite3 \
  claim-run-create --run-id p01-new-draft --question 'Kiểm nguồn mệnh đề đã khai báo' \
  --corpus suttacentral-bilara --input claims.json
```

Kết quả giữ claim ID/text; chỉ gắn supporting IDs khi **mọi** reference của
claim đã VERIFIED qua A. Nếu một reference lỗi, claim không nhận evidence thay
thế và mang limitation `DECLARED_SOURCE_UNRESOLVED`. Từng binding vẫn có kết
quả riêng để chẩn đoán. Chưa có semantic approval thì accepted set rỗng.

`retrieval_artifact` trỏ đến sidecar JSON mới cạnh store, chứa
`declared_bindings`, nhãn `source_origin=DECLARED`, reference nguyên bản và gate
envelope/provenance; `answer_artifact` trong D là đường tương đối. Artifact chỉ
là audit data, không là reader/approval. Capture/publication qua API E vẫn đọc
lại nguồn thật, không phát lại status VERIFIED của snapshot.

API tương ứng:

```python
from corpus_research.declared_sources import verify_declared_source, create_declared_run

binding = verify_declared_source(host, reference, claim_id=claim_id)
result = create_declared_run(research, run_id=run_id, question=question,
    claims=claims, source_references=references_by_claim, corpora=corpora)
```

Không đổi schema Claim/Evidence/SQLite hoặc hợp đồng cũ. `source_references`
là envelope input mới ánh xạ claim ID → các locator đã tồn tại trong schema
Evidence/source request. Gate A/B/C/D/E vẫn giữ thẩm quyền hiện có.

## Tìm thêm nguồn và phản chứng

Sau khi kiểm nguồn khai báo, chạy discovery bổ sung tường minh:

```sh
python -m corpus_research.v2_cli --db /path/to/existing.sqlite3 \
  --source-root /path/to/existing-source-checkouts \
  source-search pubbekatahetu --claim-id my-claim --corpus suttacentral-bilara --limit 3
```

Kết quả có `source_origin=EXPANDED`, `replaces_declared_source=false`,
`discovery` chứa kết quả Quick/xếp hạng cũ và kiểm nguồn A. Lệnh này không sửa
claim/run hoặc ghi đè nguồn DECLARED. API: `search_expanded_sources(host, query,
claim_id=..., corpus=..., limit=...)`. Nguồn mở rộng có thể lệch tác phẩm vì
đây là discovery, không phải kết quả ràng buộc.

Để ghi kế hoạch/phép tìm phản chứng vào run, tiếp tục dùng
`make_counterevidence_plan` và `LocalResearch.capture(..., counter_requests=...)`
của C/E; kết quả nằm riêng trong `counterevidence`, không tự đổi
`supporting_evidence_ids`. Sidecar lúc tạo draft có `expanded_sources=[]` vì
chưa chạy discovery; lệnh discovery trả kết quả riêng để caller lưu. Không tự
gán hit mở rộng là phản chứng ngữ nghĩa. Bằng chứng kiểm nguồn không giải quyết
Final Claim Gate.

## Chạy kiểm thử

```sh
PYTHONPATH=tools:tests python -m unittest test_declared_sources -v
BCR_P01_DB=/path/to/existing-core.sqlite3 BCR_SOURCE_ROOT=/path/to/pinned-sources \
  BCR_P01_CLAIMS=/path/to/frozen/atomic-claims-register.json \
  PYTHONPATH=tools:tests python -m unittest test_declared_sources_corpus -v
```

Corpus tests SKIP nếu thiếu biến môi trường cần thiết, không tải hoặc dựng lại
index. Bài giữ nguyên claim gốc cần thêm `BCR_P01_CLAIMS`; các bài còn lại kiểm
định danh SN ở pin đã nêu. Chạy index bất biến đã checkpoint, không dùng WAL
chưa checkpoint. Báo cáo thực chạy và hạn chế: [P0_1_REPORT_VI.md](P0_1_REPORT_VI.md).

`HUMAN_ADJUDICATION_PENDING` · `DISTRIBUTION_CLEARED = 0` · `PUBLICATION_NOT_PERMITTED`.
