# Hướng dẫn CLI

> Trạng thái: **HIỆN HÀNH**
>
> Tất cả lệnh CLI là local-only. Tiến độ/lỗi build đi ra stderr; kết quả chính
> được xuất JSON ra stdout.

Kiến trúc tổng thể: `docs/ARCHITECTURE.md`.

Luật nghiên cứu: `AGENTS.md`.

## 1. Nghiên cứu cục bộ thông thường

```bash
# Kiểm 13 nguồn local và trạng thái index
bin/buddhist-corpus status

# Build
bin/buddhist-corpus build --profile core
bin/buddhist-corpus build --profile discovery
bin/buddhist-corpus build --profile all

# Build riêng một nguồn nặng và hoãn rebuild FTS
bin/buddhist-corpus build --profile core --source cbeta-bm --defer-fts

# Tìm kiếm và kiểm nguồn
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus search "如是我聞" --language lzh
bin/buddhist-corpus search "anicca" --language pli --context 2 --with-provenance
bin/buddhist-corpus context --record-id 123 --window 3
bin/buddhist-corpus evidence --record-id 123 --context 2
bin/buddhist-corpus work UT22084-001-001
bin/buddhist-corpus parallels an1.1-5
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus resolve T02n0125:0563a14..0563a27
bin/buddhist-corpus variants T01n0001
bin/buddhist-corpus compare mn1 T01n0001
bin/buddhist-corpus provenance --record-id 123
```

Nếu không dùng `--context` hoặc `--with-provenance`, `search` giữ output
mặc định và thứ tự xếp hạng hiện hành.

Context được giới hạn trong cùng corpus, work ID và source path, sắp theo
`sequence_no`.

## 2. Build profile

### `core`

Nguồn cốt lõi/thẩm quyền chính cùng dữ liệu lemma cần thiết.

### `discovery`

Nguồn alignment/segmentation phục vụ phát hiện ứng viên.

### `all`

Toàn bộ 13 nguồn được hỗ trợ.

### `acceptance`

Mẫu thật, nhỏ và xác định dùng cho kiểm thử.

Có thể chọn database dẫn xuất khác bằng option toàn cục:

```bash
bin/buddhist-corpus --db /tmp/corpus.sqlite3 build --profile acceptance
```

Không đặt database bên trong source submodule.

## 3. Ghi chú về index

Build thông thường tạo/cập nhật:

- FTS Unicode thông thường;
- CJK trigram index có phiên bản.

Local Chinese substring search cần ít nhất ba ký tự CJK hữu dụng để dùng đường
trigram.

Coverage local này không được hiểu là coverage của Connector production.

## 4. Production GitHub Connector artefact

Sinh hoặc tiếp tục production v1 cục bộ:

```bash
bin/buddhist-corpus export-pointer-production-v1 \
  --output remote/pointer-production-v1 \
  --limit 20 \
  --workers 4
```

Exporter hiện hành kiểm production key universe dự kiến:

```text
terms/latin: 26,547 normalized non-CJK lemma keys
ids:         32,498 exact original work_id keys
total:       59,045
```

Đây là invariant của production v1 hiện tại và được kiểm trong exporter/tests.

Exporter:

- giữ nguyên spelling của identifier;
- dùng logic truy xuất/xếp hạng chung;
- cân bằng theo corpus;
- gộp nguồn trùng theo identity đã định;
- không ghi `raw_text`;
- chỉ publish sau khi staged artefact hợp lệ;
- hỗ trợ tiếp tục/tái tạo sau khi generation bị gián đoạn.

Runtime Connector không đọc phần này để hard-code đường dẫn. Nó phải đọc
`config/remote-corpus.json`.

Hướng dẫn runtime: `docs/REMOTE_AGENT.md`.

## 5. Quy tắc bucket production

Term key:

```text
NFC
→ casefold
→ collapse whitespace
```

Identifier:

```text
giữ nguyên spelling gốc
```

Bucket:

```text
SHA-256(exact UTF-8 production key)
→ hai ký tự hex thường đầu tiên
```

Path:

```text
locator/terms/latin/<bucket>/part-000001.jsonl
locator/ids/<bucket>/part-000001.jsonl
```

Production v1 không có `terms/cjk`.

## 6. Lệnh pointer POC lịch sử

Lệnh này được giữ để tái tạo/kiểm lịch sử, không phải runtime production hiện
hành:

```bash
bin/buddhist-corpus export-remote-pointers \
  --query anicca \
  --query dukkha \
  --query jhāna \
  --query nibbāna \
  --query Mahākassapa \
  --query 無常 \
  --query 如是我聞 \
  --query 苦 \
  --query 空 \
  --identifier T02n0099 \
  --identifier T01n0001 \
  --output remote/pointer-poc
```

Không dùng `pointer-poc` cho nghiên cứu thông thường khi
`config/remote-corpus.json` khai báo `pointer_production_v1`.

## 7. Benchmark và phép đo

### Benchmark pointer xác định

```bash
bin/buddhist-corpus export-pointer-benchmark \
  --latin-keys 200 \
  --cjk-keys 200 \
  --identifier-keys 100 \
  --output remote/pointer-benchmark
```

### POC compact serialization lịch sử

```bash
bin/buddhist-corpus export-pointer-compact-poc \
  --benchmark remote/pointer-benchmark \
  --output remote/pointer-compact-poc
```

### Phân tích mức lặp — chỉ đọc

```bash
bin/buddhist-corpus analyze-pointer-repetition \
  --benchmark remote/pointer-benchmark
```

### Đo production key universe — chỉ đọc

```bash
bin/buddhist-corpus analyze-pointer-key-universe \
  --benchmark remote/pointer-benchmark
```

### Đo CJK FTS vocabulary — chỉ đọc

```bash
bin/buddhist-corpus analyze-cjk-fts-vocabulary \
  --benchmark remote/pointer-benchmark
```

Analyzer CJK chỉ tạo TEMP FTS5 vocabulary view:

```sql
CREATE VIRTUAL TABLE temp.cjk_vocab_measurement
USING fts5vocab(main, records_cjk_fts, 'row');
```

Kết quả là vocabulary token trigram cấp thấp của chỉ mục, không phải từ điển
thuật ngữ Phật học.

Nó không được materialize thành production `terms/cjk`.

Lý do kiến trúc xem ADR-0008 trong `docs/adr/`.

## 8. Legacy full-record export

```bash
bin/buddhist-corpus export-remote --output remote/corpus
```

Lệnh này được giữ cho tương thích/lịch sử.

Nó **không phải** đường production Connector hiện hành.

Không dùng output của lệnh này thay cho pointer production v1.

## 9. Hợp đồng các lệnh nghiên cứu chính

### `status`

Kiểm source contract và trạng thái index.

### `search`

Tìm record có xếp hạng; có thể kèm context/provenance bằng option tương ứng.

### `context`

Lấy cửa sổ record trước/sau trong cùng work/source.

### `work`

Lấy metadata và record theo work ID.

### `parallels`

Lấy relation/song hành/căn chỉnh theo work hoặc segment.

### `resolve`

Giải định danh SuttaCentral/CBETA hoặc range phù hợp về witness cục bộ.

### `variants`

Lấy dữ liệu dị bản.

### `compare`

So sánh record/witness nhưng không tự tạo bản hòa hợp.

### `provenance`

Trả hợp đồng nguồn của record.

### `evidence`

Gói record, context, provenance và variants liên quan.

## 10. Kiểm thử

Chạy toàn bộ test suite:

```bash
PYTHONPATH=tools python3 -m unittest discover -s tests -v
```

Số test hiện hữu và ánh xạ requirement → test được theo dõi trong
`docs/ACCEPTANCE.md`.

Tài liệu này không dùng một con số test cố định làm nguồn chuẩn lâu dài.
