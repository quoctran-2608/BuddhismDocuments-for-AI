# P0/3 — Software/output-check evidence, 05/11/2026

`results.json` lưu counts, title regression, source state, hash code/test/skill
và thông tin bảo toàn. `full-suite.stderr`/`full-suite.stdout` là raw log 484
phương thức PASS; ba class Pilot SKIP ở discover được chạy riêng trong
`pilot.stderr` (21/21 PASS). `skill-validation.stdout` là kết quả validator,
không phải chứng nhận agent làm đúng mọi tình huống.

Không dùng model để tự trả kết luận title: regression đọc source ghim thật
và đối chiếu field. Điều kiện/speaker/stance vẫn là recorded interpretations;
đạt CHECKED không là semantic approval/accepted/publication.

Receipts mới đầy đủ tại `D:\WORKING\BuddhismDocuments-for-AI\.m\p03-tools\release-results`.
`SHA256SUMS.txt` kiểm byte UTF-8 LF, trừ chính list; scoped .gitattributes giữ LF.
Hồ sơ evaluation/Pilot cũ được giữ nguyên, không phải ground truth. Không có
ZIP hoặc API model adapter mới. Hướng dẫn/tái chạy:
[P0_3_USAGE](../../P0_3_USAGE.md); giới hạn: [P0_3_REPORT](../../P0_3_REPORT_VI.md).

HUMAN_ADJUDICATION_PENDING · DISTRIBUTION_CLEARED = 0 · PUBLICATION_NOT_PERMITTED.
