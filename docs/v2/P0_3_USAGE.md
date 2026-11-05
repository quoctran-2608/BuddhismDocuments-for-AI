# P0/3 — Kiểm các trường đầu ra trước khi xuất báo cáo

Đường opt-in, giữ nguyên P0/1, P0/2 và gate A/B/C/D/E. `CHECKED` chỉ nói các
fields/links đã được kiểm; **không phải** A VERIFIED, B accepted, semantic
approval hoặc quyền công bố. Không chứng minh đúng sai toàn văn xuôi.

## Bắt đầu từ một chat Codex mới

Chọn worktree/commit thực có `output-check` trong CLI `--help`; đừng suy từ tên
main. P0/3 trên feature branch trước khi được kiểm toán/merge. Có thể đưa yêu
cầu ngắn sau cho chat mới, kèm đường repo và phạm vi nghiên cứu:

> Đọc AGENTS.md và skill buddhist-corpus-research trong checkout này. Xác nhận
> HEAD/baseline, nguồn và scope index thực; chọn Local/Connector đúng capability.
> Dùng P0/1 bind nguồn claim, mở context và giữ witness riêng. Chỉ dùng P0/2
> nếu có model adapter được phép; nếu không ghi MODEL_INFERENCE_NOT_EXECUTED.
> Ghi condition/scope/speaker/stance có citation trước khi viết kết luận. Đưa
> title/quote/identifier/conclusion vào contract P0/3 và chạy output-check.
> Tự kiểm phần diễn giải còn lại, giữ UNRESOLVED, không cấp approval/publication.

Skill đã được rút gọn tại
[SKILL.md](../../.codex/skills/buddhist-corpus-research/SKILL.md).
CLI Windows/WSL và source-root tách code xem [USAGE](USAGE.md);
Connector tiếp tục theo [REMOTE_AGENT](../REMOTE_AGENT.md). Không giả định
reader local/P0/3 CLI chạy được trong Connector không có shell/index.
API có thể dùng reader capability host thật; JSON locator/ledger không thay
reader. Không tải corpus để lấp thiếu dữ liệu.

## Hai đầu vào tách biệt

1. **OutputContext do host giữ:** claim IDs/source IDs hiện hành cùng các notes
   đã ghi trước khi viết báo cáo. Fresh A kiểm quote anchors của notes. Những
   tên gọi condition/speaker/stance trong notes vẫn là AI interpretation, không
   được code chứng nhận đúng nghĩa. Hash context chỉ phục vụ trace, không phải
   dấu phê duyệt hoặc chứng thực thời điểm ghi nhận.
2. **Document AI viết:** chỉ có `schema_version="bcr-output-1"` và `items`.
   Không được tự cung cấp readers, thay notes, thêm approved/accepted hoặc
   publication flags. Mỗi item bind một claim có thật trong context.

Notes theo claim ID, mỗi claim có đúng ba lists:

```json
{
  "MY_CLAIM": {
    "conditions": [{"id": "time", "evidence_id": "ACTUAL_ID", "quote": "EXACT_SOURCE_CONTEXT", "description": "Điều kiện thời gian được người đọc ghi nhận."}],
    "scope_limits": [{"id": "narrow", "text": "Chỉ phạm vi đoạn và nhân chứng đã đọc."}],
    "attributions": [{"id": "voice", "evidence_id": "ACTUAL_ID", "quote": "EXACT_SOURCE_CONTEXT", "speaker": "Người nói được ghi nhận", "stance": "REPORTED_REJECTED"}]
  }
}
```

Các chữ in hoa là chỗ thay, không phải ID hợp lệ. Note IDs duy nhất trong claim,
không dùng prefix `host:`. Stance: ENDORSED/REPORTED/REPORTED_REJECTED/UNRESOLVED.
Không đoán stance từ câu trích chỉ vì nó qua A. Code kiểm quote anchor và việc
giữ annotation, không suy ra ai nói hay tác phẩm tán thành/bác bỏ câu ấy.

Host tự thêm scope `host:0`, `host:1`… từ limitations của claim và giới hạn
semantic mặc định. Dùng `context.notes[claim_id]` lấy IDs, không gõ/suy số lượng.
Không có notes không có nghĩa không có điều kiện trong nguồn: agent vẫn phải
đọc và nhận diện. Đầu vào bỏ sót condition ngay từ đầu là giới hạn còn lại.

## Item contract

Mọi item có `item_id`, `claim_id`, `kind`, `text`. Không thêm văn xuôi ngoài
contract rồi tuyên bố toàn báo cáo đã CHECKED. Fields riêng:

| kind | Fields thêm | Phép kiểm |
|---|---|---|
| TITLE | `evidence_id`, `source` | Tên đầy đủ khớp heading/metadata từ pinned blob, NFC và strip whitespace; không casefold/bỏ dấu/fuzzy match. |
| QUOTE | `evidence_id`, `source`, `use` | `verify_quote` hiện có trên đúng context.text của unit hiện hành; không mượn before/after hoặc witness khác. |
| IDENTIFIER | `evidence_id`, `source`, `namespace` | UID giữ nguyên; acronym/alt phải có metadata ghim đúng UID và namespace. |
| CONCLUSION | `evidence_ids`, `condition_ids`, `scope_limit_ids`, `attributions`, `scope`, `label` | Giữ đủ links/annotations, nguồn thuộc claim, không tăng quyền hoặc xóa giới hạn. |

`source` có đúng các giá trị hiện hành từ `source_identity(evidence)`:
corpus, repository, source_path, source_sha, source_blob_sha, work_id,
segment_id, witness, text_role, evidence_class. Cả path/pin/work/witness/role
phải khớp, không chỉ ID. Evidence được đọc lại qua A đầu/cuối lượt kiểm.
Evidence gắn run khác không được chuyển sang claim/run hiện tại.

QUOTE `use`: TEXTUAL_QUOTE, METADATA_REPORT hoặc SCRIPTURAL_TEACHING.
SCRIPTURAL_TEACHING không nhận metadata/note/comment như root; cần annotation
stance ENDORSED đã ghi. Đổi REPORTED_REJECTED thành ENDORSED bị chặn. ENDORSED
được ghi sai ngay từ đầu vẫn là lỗi diễn giải mà code không tự biết.

CONCLUSION `scope`: BOUNDED/UNRESOLVED; `label`: AI_INTERPRETATION/UNRESOLVED.
`condition_ids` và `scope_limit_ids` phải giữ đủ tập đã ghi, không chỉ một phần.
`attributions` là list `{id,speaker,stance}` theo notes. Renderer lấy condition
quotes/descriptions, scope text và provenance từ context đã kiểm, không nhận
bản viết lại tự do làm thay thế. Claim/run blocked chỉ được ghi UNRESOLVED.
Model/caller có thể vẫn viết câu sai trong `text` dù links đúng: CHECKED không
là chứng nhận ngữ nghĩa; agent cần soát lượng từ, điều kiện và suy luận ấy.

## Reader built-in và phạm vi title/identifier

LocalOutputFacts mở lại pinned Git qua host/source reader, không coi index.title
hoặc tên tệp là proof. Hiện hỗ trợ title Bilara SN UID dạng `snN.N` ở native
heading `:0.3` (root và bản dịch) và TEI
`teiHeader/fileDesc/titleStmt/title` của CBETA/84000. Không đoán vị trí title
của mọi collection/format khác; không hỗ trợ/không rõ thì UNVERIFIED.
Title metadata được ghi role riêng, không biến header thành lời kinh.

Namespace hỗ trợ với Bilara: SC_BILARA_UID; SC_ACRONYM/SC_ALT_ACRONYM/SC_VOLPAGE
chỉ khi mở được `structure/text_extra_info.json` tại pin SC trong manifest.
Provenance mapping ghi rõ metadata_relationship. Ví dụ UID `sn35.146` có alt
acronym `SN 35.145`: giữ UID 146 và namespace alt, không thay bằng UID 145.
Mapping đó không chứng minh hai văn bản tương đương hoặc cho phép đổi số ở
mọi hệ. Không có mapping thì không tự suy bằng số/tên giống nhau.

## API và CLI

API giúp agent tránh gõ lại source/condition/scope IDs:

```python
from corpus_research.output_verification import OutputContext, source_identity, verify_output
from corpus_research.output_workflow import LocalOutputFacts, write_output_check

run = research.prepare(run_id)  # giữ snapshot/version và claim IDs thật
context = OutputContext(claims=run['claims'], notes=recorded_notes,
    evidence_reader=research.host.evidence_reader,
    fact_reader=LocalOutputFacts(research.host))
# item.evidence_id lấy từ claim hiện hành; source = source_identity(fresh_record)
# conclusion.scope_limit_ids lấy từ context.notes[cid]['scope_limits']
receipt = verify_output(document, context)  # diagnostic data, never an export ticket
result = write_output_check(research, run_id=run_id, expected_version=run['version'],
    document=document, notes=recorded_notes, output=fresh_output_prefix)
```

CLI đọc cùng contract, không chạy model hoặc sửa Research Store:

```sh
export PYTHONPATH=tools
python -m corpus_research.v2_cli --root /path/to/code --db /path/to/index.sqlite3 \
  --source-root /path/to/pins --store /path/to/new-research.sqlite3 \
  output-check --run-id MY_RUN --version VERSION --input draft-output.json \
  --notes recorded-notes.json --output /path/to/new-output/checked
```

VERSION lấy thật từ run-show. Output mới UTF-8 LF, không ghi đè source/index
hoặc file cũ. Public writer/renderer luôn kiểm lại document với capability
hiện hành; không nhận một receipt CHECKED đã lưu làm vé xuất báo cáo.
CHECKED có receipt JSON và Markdown; REJECTED/UNVERIFIED chỉ có
JSON, `report=null`. Exit 0 nghĩa dispatch thành công kể cả REJECTED; phải đọc
status/checks. Cả tên JSON/Markdown phải mới để tránh dùng report thành công cũ
cạnh receipt từ chối mới. Run đổi version/superseded giữa lượt kiểm thì không
export report đã kiểm.

`observe_tool_result(exit_code, payload)` đọc status/gate nội bộ của receipt,
không coi exit 0 là VERIFIED. Đây là quan sát JSON, **không xác thực nguồn**;
không được nối nó hoặc ledger 336 records làm evidence_reader mới.

P0/2 report cũ vẫn giữ hành vi mặc định. Với thông tin/conclusion cần kiểm,
agent chuyển sang contract P0/3 trước khi xuất. Không quét hoặc chứng nhận
Word/văn xuôi chat tùy ý. Mẫu và giới hạn thực chạy xem
[P0_3_REPORT_VI](P0_3_REPORT_VI.md).

HUMAN_ADJUDICATION_PENDING · DISTRIBUTION_CLEARED = 0 · PUBLICATION_NOT_PERMITTED.
