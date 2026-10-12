# Bằng chứng E — 11/10/2026

## Bằng chứng cuối và mốc Git

Mã A–E đã gộp vào main tại
[57db982274e267218594ae5ca463bd2a42d2be02](https://github.com/quoctran-2608/BuddhismDocuments-for-AI/commit/57db982274e267218594ae5ca463bd2a42d2be02).
Commit này chỉ bổ sung ba tệp evidence sau; code/tests/pins giữ nguyên commit
được duyệt `49862169878a796951d069830459b526f4ee2d47`:

- [phase-e-final-tests-20261011.json](phase-e-final-tests-20261011.json): tested
  commit, môi trường/command, digest mã, counts và 13 pins trước/sau.
- [WSL raw log](phase-e-final-wsl-approved-20261011.log.gz): 410/410,
  failure/error/skip 0, trong đó E portable 78 và E corpus thật 14.
- [Windows portable raw log](phase-e-final-windows-portable-20261011.log.gz): 78/78;
  không chạy lại Windows full trong vòng cuối này.

**Phân biệt provenance:** JSON/log committed trên main `57db982…` ghi lần chạy
code `4986216…`, không tự nhận đã ghi log chạy HEAD `57db982…`. Full WSL được
chạy lại tại evidence-only HEAD `57db982…` và báo 410/410 trước merge; log lần
đó giữ ngoài Git. Có thể kiểm digest/code tree giữa hai commit và tái chạy
theo command/layout trong JSON; không có raw log committed của lần HEAD đó.
Giới hạn lưu dấu vết này không được đổi thành khẳng định toàn suite Windows,
Work hoặc nghiệm thu học thuật đã đạt.

## Checkpoint và benchmark lịch sử

Các tệp dưới ghi checkpoint `1b2d0f0` trước gia cố span (394 tests), khác
bằng chứng cuối trên. E1/E2 mẫu và E3 draft cost không được đo lại sau sửa span.

- `test-results.json`: môi trường, số test và hash tệp đã chạy; log raw gzip
  baseline/cuối WSL, Windows, nguồn thật và golden ở cùng thư mục.
- `benchmark-14.json.gz`: lượt đo cuối với 14 observations/tác vụ sau một
  warm-up, dùng mã checkpoint `1b2d0f010ec2dab8664378516005ed2ad05e4fe6`.
  Có full results/rank/provenance, digest, từng thời gian/CPU/RSS/IO/phases,
  source state/index hash và code hash.
- `benchmark-7.json.gz`: lượt xác nhận trước đó cùng checkpoint, 7 observations;
  giữ để thấy dao động giữa các lượt, không chọn lượt nhanh nhất. Lượt cuối
  tăng số observations lên 14 theo quyết định trước khi chạy; không lấy min
  làm số báo cáo. `benchmark-summary.json` là bản trích nguyên dữ liệu tổng hợp
  của lượt 14, không thay raw.
- `research-example.json`: hồ sơ MN1 draft thật, quote/source/claim/biên nhận C
  và gói export/hash snapshot; thiếu semantic approval nên không công bố.
- `connector-before-fix.json` / `connector-actual.json`: thử nghiệm production
  `ids/mn1` qua công cụ GitHub MCP được cấp quyền; đầu tiên pointer thiếu
  language bị REJECTED, sau sửa được A VERIFIED. Metadata/sha của file fetch
  gắn đúng canonical URL repository/ref/path; hai lượt source fetch độc lập
  được nối vào reader host, resolver giải vị trí từ full bytes. Không dùng
  một JSON fixture làm kênh source fetch thực. Locator SHA và tool requests
  được ghi trong kết quả. Logger runner Windows có lỗi encoding khi in câu
  Pāli sau khi đã lưu kết quả VERIFIED; dữ liệu JSON lưu UTF-8 đầy đủ, adapter
  đã hoàn tất các checks. CLI sản phẩm có regression riêng cho stdout UTF-8.

Tất cả source corpus giữ nguyên ở pins. WSL dùng các worktree tạm có symlink
đến 13 checkout đã có để không chép/tải corpus. Vì Git xem symlink thay gitlink
là type change, raw benchmark ghi 13 dòng `T` của **worktree đo tạm**, không
phải diff nhánh E; mã tracked trong worktree đo đúng checkpoint, không đổi.
Reader source được cấu hình root checkout thật, không đọc symlink vượt root
để bỏ qua luật A. Nhánh E gốc không thay gitlink/pins hoặc upstream.

Baseline 1.0 là `f7415f574ed1510d5854ee00db6baafe2484e355`, main gần nhất trước
A được ghi trong nghiệm thu A; chưa có verification.py. Blob manifest/config/
index/retrieval/CLI/model khớp hai bản. Index acceptance được dựng riêng bằng
code 1.0 không đổi, cùng file/hash cho hai phiên bản; build không nằm trong
latency tác vụ. Chưa đo cold cache/index full, startup hay toàn corpus.

Tài nguyên Linux: CPU self và child subprocess; ru_maxrss là high-water KiB
toàn worker, có cả warm-up/case trước, không phải cấp phát riêng một operation.
IO getrusage là blocks của self+children; `/proc/self/io` là bytes/chars của
self, không bao gồm child bytes. Zero cached disk IO là số quan sát, không
phải thay cho phần chưa đo. Thời gian source/verification trong phases không
chồng nhau; median các phases không nhất thiết cộng đúng median tổng.

Đọc JSON gzip bằng Python chuẩn:

```sh
python -c "import gzip,json; r=json.load(gzip.open('docs/v2/evidence/benchmark-14.json.gz','rt',encoding='utf-8')); print(r['summary'])"
```

Logs/results chứng minh thực thi phần mềm, không phải review độc lập hay đáp
án nghiên cứu chuẩn học thuật. Work chưa có phiên thử; Connector mới một ca.
AI token/cost và tỷ lệ lỗi Research học thuật CHƯA ĐO; CHỜ CHỐT NGƯỠNG.
Không commit corpus index, ResearchStore DB, cache, full downloaded source hay
gói phản biện lớn. Raw gzip chỉ là báo cáo đo/log nhỏ, không có credentials.


## Academic pilots — nghiệm thu ứng dụng thực tế

[Academic Pilot 01: nghiệp và khổ đau, 12/10/2026](academic-pilots/2026-10-12-karma-suffering/README.md) kiểm toán bài Phật giáo do AI tạo, khác software tests A–E. Có bằng chứng source/provenance verification trong mẫu; academic acceptance chưa hoàn thành. Hồ sơ có báo cáo Work lịch sử (public redacted projection), bản hiệu đính, kiểm toán ChatGPT độc lập, correction log và evidence manifest. Chưa chứng minh BCR 2.0 tốt hơn 1.0 trong đánh giá toàn bài; không đổi benchmark E, pins hoặc quyền publication.
