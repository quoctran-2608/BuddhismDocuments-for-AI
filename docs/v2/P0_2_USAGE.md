# P0/2 — Đánh giá, phản biện và tổng hợp AI proposal

Đường tùy chọn local; không thay Quick, Research cũ hoặc P0/1. Đây là khả năng
**AI đề xuất**, tách khỏi source verification A và academic approval B. Không
cần thuê/mời chuyên gia mỗi lần chạy pipeline. Thiếu model vẫn ghi kết quả
UNRESOLVED và `MODEL_INFERENCE_NOT_EXECUTED`, không tạo nhận định Codex viết sẵn.

## Luồng và entry point

```text
Research claim hiện hành + scope/limitations
→ evidence_reader đọc lại các ID qua A
→ support (1 call, đầu vào nguồn/context và phần thiếu)
→ challenge (1 call khác mục tiêu, thấy support và toàn bộ evidence)
→ kiểm ID/câu trích/action, đọc lại A và kiểm current run
→ synthesis có rào chắn
→ JSON + Markdown mới, tách khỏi D/approval
```

Trước tiên tạo draft bằng [P0/1](P0_1_USAGE.md) với nguyên văn claim và locator
đã đối chiếu. Xem `run-show` lấy version; chạy trên cùng host/code commit.
Giữ quy tắc offline và pins/parser/profile hiện có. Sau đó:

```sh
export PYTHONPATH=tools
python -m corpus_research.v2_cli --root /path/to/code \
  --db /path/to/existing.sqlite3 --source-root /path/to/pinned-checkouts \
  --store /path/to/new-research.sqlite3 \
  semantic-assess --run-id MY_RUN --claim-id MY_CLAIM --version VERSION \
  --output /path/to/new-output/proposal
```

Thay `VERSION` bằng số version thật; global options đứng trước subcommand.
Không có model config, lệnh này vẫn kiểm nguồn và xuất báo cáo trung thực:
support/challenge null, synthesis UNRESOLVED, `NO_MODEL_CONFIGURED`. Exit 0 chỉ
nghĩa dispatch thành công; đọc status/errors, không suy approval từ exit code.
Lỗi cấu hình, version, output hoặc I/O theo quy ước CLI E ra stderr và exit 2.

`--counter-query QUERY` tùy chọn, tối đa hai query. Host chạy lại kế hoạch C
của claim nếu đã có, cộng query tường minh qua executor C hiện có. Receipt ghi
phạm vi/candidate/giới hạn; `EXPANDED_COUNTER_CANDIDATE` chỉ là ứng viên cần
AI phân tích. Không đổi nguồn P0/1 và không tự gắn supporting IDs vào claim.
Không query/plan thì report ghi `COUNTER_SEARCH_NOT_EXECUTED`; challenge chỉ
phản biện evidence đã cung cấp, không được hiểu là đã tìm hết phản chứng.

## Model adapter do host cấu hình

`--model-config /trusted/host.json` chọn command **do host quản lý**. Không
đọc config này từ nguồn, câu trả lời model hoặc proposal JSON. Adapter không
phụ thuộc provider: một chương trình nhận một JSON request UTF-8 trên stdin,
gọi model được host cho phép, trả đúng một JSON object trên stdout. Mỗi lần
support/challenge là process/stateless call riêng; process không có tool API
do BCR cấp. Stderr dùng chẩn đoán; receipt chỉ lưu hash stderr, không copy nội
dung có thể chứa bí mật vào báo cáo.

Ví dụ chạy fixture phần mềm có sẵn, từ thư mục repo:

```json
{
  "command": ["python3", "tests/fixtures/semantic_model.py", "lower"],
  "model_id": "software-fixture",
  "model_version": "1",
  "mode": "FIXTURE",
  "data_policy": "LOCAL_ONLY",
  "timeout": 30,
  "max_context_bytes": 65536,
  "max_output_bytes": 32768
}
```

Thêm `--model-config host.json` vào lệnh trên. Fixture đọc input thực để trỏ
citation, nhưng **không suy luận Phật học**; kịch bản `lower` chủ động trả mức
WEAK ở challenge để kiểm đường hạ mức. Mọi kết quả FIXTURE luôn mang
`MODEL_INFERENCE_NOT_EXECUTED`, kể cả khi hai subprocess đã chạy thành công.

Model thật: host thay command bằng adapter model đã cấu hình, khai đúng
`model_id`, `model_version`, `mode=MODEL` và chính sách dữ liệu. `MODEL` là khai
báo của host, không là chứng thực provider hoặc chất lượng model. Không tự
tìm API key, tải model/package hoặc gửi Word/claim riêng tư/copyrighted text ra
API ngoài. `LOCAL_ONLY`/`AUTHORIZED_REMOTE` là policy do host chịu trách nhiệm
thực thi; command adapter không phải network/OS sandbox. Remote chỉ dùng khi
quyền sử dụng dữ liệu và cách xử lý riêng tư đã được xác lập. Phiên triển khai
này không cấu hình hoặc gọi model thật; xem [báo cáo](P0_2_REPORT_VI.md).

Command chạy không qua shell; source/model text không chọn command, file hoặc
tools. Có tối đa 2 call/claim, timeout 0..60 giây/call; context/output bound
1 KiB..1 MiB. Quá context không cắt im lặng: giữ UNRESOLVED. Timeout, process
failure, output quá lớn, JSON lỗi/trùng key, schema/ID/citation sai đều đóng an
toàn. Mỗi claim dùng một adapter instance mới; không có retry/agent loop.
Trên POSIX timeout giết process group; Windows giết process trực tiếp. Host
cần quản lý command/tiến trình con, credentials và isolation riêng.

## Request/response contract

Request có `schema_version`, `stage`, `instructions`, `response_contract` và
`data`: nguyên văn claim, loại, evidence A hiện hành, quote/context/provenance,
giới hạn nguồn/tìm kiếm, missing sources và initial support ở lượt challenge.
Evidence/source/claim/model text luôn là dữ liệu không đáng tin về chỉ dẫn.
Prompt yêu cầu giải thích ngắn có citation; không yêu cầu/lưu chain-of-thought.

Support response phải có **đúng** các trường sau:

```json
{
  "claim_id": "MY_CLAIM",
  "assessment_status": "PROPOSED",
  "support_level": "WEAK",
  "supporting_evidence_ids": ["ACTUAL_EVIDENCE_ID"],
  "considered_evidence_ids": ["ALL_SUPPLIED_EVIDENCE_IDS"],
  "reasoning": [{"evidence_id": "ACTUAL_EVIDENCE_ID", "quote": "EXACT_CONTEXT_SUBSTRING", "explanation": "Giải thích căn cứ ngắn."}],
  "scope_limits": ["Điều kiện và phạm vi cần giữ."],
  "missing_evidence": [],
  "unresolved_questions": []
}
```

Các giá trị in hoa là chỗ thay, không phải evidence IDs mẫu hợp lệ. Mức hỗ trợ
dùng enum B hiện có: DIRECT/STRONG/WEAK/UNSUPPORTED/CONTRADICTED. UNRESOLVED là
assessment status, đi cùng `support_level=null`, không tạo enum support mới.
Host tự thêm provenance đã đối chiếu và cờ approval/publication false; model
không được tự cung cấp hoặc sửa các trường ấy.

Challenge có cùng trường, thêm:

```json
{
  "action": "UNRESOLVED",
  "counter_evidence_ids": ["ACTUAL_COUNTER_ID"],
  "issues": [{"issue": "Vấn đề cụ thể", "impact": "UNRESOLVED", "evidence_ids": ["ACTUAL_ID"], "explanation": "Vì sao vấn đề còn mở."}]
}
```

`action`: KEEP giữ mức, LOWER phải hạ DIRECT→STRONG/WEAK hoặc STRONG→WEAK;
LIMIT không tăng mức và phải có giới hạn; UNRESOLVED dùng mức null;
CONTRADICTION cần mức CONTRADICTED và counter IDs có citation. Mọi evidence ID
đều thuộc tập hiện hành; challenge phải giải thích có citation từng nguồn đã
đưa vào, kể cả nguồn nó đề xuất không liên quan. `quote` phải thực sự có trong
quotation/context A, không chỉ trùng ID. `issues.impact` RESOLVED/UNRESOLVED là
proposal của AI, không xác nhận học thuật. Không có confidence score chung.

## Tổng hợp và báo cáo

Synthesis là bước chương trình riêng, không phải phiếu bầu đồng thuận. Nguồn
thiếu/chưa VERIFIED, claim/run blocked, lỗi model, vấn đề quan trọng hoặc câu
hỏi còn mở buộc UNRESOLVED. Không chấp nhận challenge nâng mức bằng action
KEEP/LOWER. Các điều kiện từ nguồn, host, support và challenge được hợp lại;
báo cáo không xuất câu viết lại tự do đã tách khỏi điều kiện. Mức hỗ trợ luôn
là đề xuất về **claim được hiển thị nguyên văn và phạm vi đi kèm**, không phải
một câu kết luận đã chấp thuận.

Report phân biệt facts đã kiểm bằng code, support proposal, challenge proposal,
kết luận giới hạn và việc còn thiếu. Source independence luôn chưa xác lập,
count null: nhiều bản dịch không thành nhiều chứng thực độc lập. Kiểm cú pháp
và citation không thể chứng minh AI hiểu đúng causal/temporal conditions hay
đã tìm đủ phản chứng; không có tỷ lệ accuracy học thuật từ fixture.

Hai artifact mới `proposal.json`/`proposal.md` giữ tách support/challenge,
request/response hợp lệ, hash input/output, model/version/config và timing.
Response lỗi không lưu như assessment hợp lệ; transport receipt giữ hash nếu
đã nhận byte. Nội dung nhạy cảm nằm local theo policy host; không tự publish.
Output UTF-8 **LF**, mở độc quyền, không ghi đè nguồn/corpus/index hoặc file cũ.
Proposal không được nối vào `assessment_reader`/`review_reader` của A/B/C.
Không sửa Research Store hoặc tạo accepted claims; bản báo cáo là audit data,
không được replay thành authority. Run đổi version/superseded khi gọi model
thì kết quả chuyển UNRESOLVED; nguồn được kiểm lại trước từng call và cuối.

## API và tests

```python
from corpus_research.model_adapter import CommandModel
from corpus_research.semantic_workflow import assess_research_claim, write_assessment

model = CommandModel(host_argv, model_id=host_model_id, model_version=host_version)
proposal = assess_research_claim(research, run_id=run_id, claim_id=claim_id,
    expected_version=version, model=model, counter_queries=explicit_queries)
paths = write_assessment(research, proposal, fresh_output_prefix)
```

Lõi `semantic_assessment.assess_evidence` nhận Claim B + `evidence_reader`
capability A, model adapter và scope/missing/counter IDs do host cung cấp;
không nhận JSON VERIFIED làm reader. Không thay schema Claim/Evidence/D hoặc
callback approval. Dùng `--model-config`/API chỉ ở boundary host được tin cậy.

```sh
PYTHONPATH=tools:tests python3 -m unittest test_semantic_assessment -v
BCR_P01_DB=/path/to/existing-pilot.sqlite3 BCR_SOURCE_ROOT=/path/to/pins \
BCR_P01_CLAIMS=/path/to/frozen/atomic-claims-register.json \
PYTHONPATH=tools:tests python3 -m unittest test_declared_sources_corpus test_semantic_pilot -v
```

Pilot test không tải hoặc viết lại corpus/index, không lấy đánh giá Codex cũ
làm đáp án. Phân biệt test source/plumbing và semantic inference chưa chạy.

`HUMAN_ADJUDICATION_PENDING` · `DISTRIBUTION_CLEARED = 0` · `PUBLICATION_NOT_PERMITTED`.
