# ADR-0003 — Dùng truy xuất từ vựng nhạy theo ngôn ngữ

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** truy xuất cục bộ
- **Liên quan:** REQ-RET-003, REQ-RET-004, REQ-RET-005

## Bối cảnh

Corpus chứa Pāli, Sanskrit/romanized, Hán văn, tiếng Anh, Tây Tạng và các dạng
dữ liệu khác. Một tokenizer duy nhất không phục vụ tốt mọi hệ chữ.

FTS theo từ phù hợp nhiều truy vấn Latin/romanized nhưng kém với truy vấn chuỗi
con nằm giữa đoạn Hán văn dài. Ngược lại, trigram CJK là hạ tầng sinh ứng viên,
không phải mô hình ngữ nghĩa hay từ điển thuật ngữ.

## Quyết định

Giữ pipeline truy xuất hiện hành theo hướng từ vựng, xác định được và nhạy theo
ngôn ngữ:

- FTS5 `unicode61` cho tìm kiếm Unicode thông thường;
- exact match và chuẩn hóa Unicode/case;
- bỏ dấu là bước riêng, không phá primary normalization;
- lemma/morphology do corpus cung cấp được dùng khi có;
- `records_cjk_fts` dùng FTS5 trigram cho `lzh`/`zh` để sinh ứng viên cho
  chuỗi có ít nhất ba ký tự CJK hữu dụng;
- sau bước sinh ứng viên vẫn dùng logic kiểm/xếp hạng chung.

## Lý do

- giữ truy xuất minh bạch và dễ giải thích;
- khai thác lemma thật từ corpus thay vì bịa biến thể;
- giải quyết đúng vấn đề chuỗi con Hán văn mà không cần vector database;
- có thể kiểm thử deterministic;
- phù hợp fast path hiện tại và dữ liệu 50 triệu record.

## Phương án đã không chọn

### Một tokenizer chung cho mọi ngôn ngữ

Không đáp ứng tốt CJK và làm mất đặc thù hình thái/nguyên dạng.

### Vector/embedding search làm mặc định

Chưa có nhu cầu đủ mạnh để đánh đổi khả năng kiểm soát, tái tạo và chi phí build;
hơn nữa semantic similarity không tự giải quyết provenance hay claim verification.

### Quét toàn bảng cho truy vấn CJK ngắn

Không phù hợp hiệu năng và tạo hành vi khó dự đoán.

## Hệ quả

- local CJK search có coverage tốt hơn cho chuỗi dài nhưng không phải semantic search;
- truy vấn CJK 1–2 ký tự không được hứa hẹn hỗ trợ bằng full-table fallback;
- production remote không được suy ra trực tiếp từ vocabulary trigram local.

## Khi nào xem xét lại

Xem xét khi Golden Research Tests chứng minh truy xuất hiện tại bỏ sót có hệ
thống những trường hợp quan trọng mà không thể khắc phục bằng normalization,
lemma, chỉ mục hoặc query expansion có kiểm soát.
