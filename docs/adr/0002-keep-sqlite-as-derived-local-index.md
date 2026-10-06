# ADR-0002 — Giữ SQLite là chỉ mục cục bộ dẫn xuất

- **Trạng thái:** Chấp nhận
- **Ngày ghi ADR:** 2026-10-06
- **Phạm vi:** tầng chỉ mục
- **Liên quan:** REQ-DER-001, REQ-DER-002, REQ-DER-003

## Bối cảnh

Mười ba nguồn upstream có định dạng khác nhau: JSON, TEI XML, RDF, TMX, văn bản
dòng, dữ liệu phân đoạn và dữ liệu lemma/khảo dị.

AI hoặc CLI không thể nghiên cứu hiệu quả nếu mỗi truy vấn phải quét trực tiếp
toàn bộ cây nguồn. Tuy nhiên, nếu database chuẩn hóa được coi là nguồn gốc thì
sẽ mất ranh giới giữa văn bản upstream và dữ liệu do parser tạo ra.

## Quyết định

Dùng SQLite làm tầng chỉ mục cục bộ dẫn xuất, tái tạo được từ các source SHA đã
ghim.

Database chứa record, work, relation, variant, lemma và các chỉ mục FTS cần cho
truy xuất. Database không phải nguồn chuẩn của câu chữ và không được coi như
corpus upstream độc lập.

Build phải có trạng thái theo source SHA, phiên bản parser và phiên bản chỉ mục
để hỗ trợ build gia tăng.

## Lý do

- SQLite đủ đơn giản để chạy cục bộ, dễ kiểm tra và không cần hạ tầng máy chủ;
- hỗ trợ FTS5, transaction, truy vấn quan hệ và trạng thái build trong một artefact;
- cho phép chuẩn hóa 13 nguồn về một giao diện nghiên cứu thống nhất;
- vẫn giữ upstream source làm nơi kiểm chứng cuối cùng;
- phù hợp yêu cầu local mode hoạt động offline.

## Phương án đã không chọn

### Dùng database như nguồn chuẩn mới

Không chọn vì parser có thể sai, dữ liệu dẫn xuất có thể thay đổi và provenance
sẽ yếu đi nếu tách khỏi source path/SHA.

### Dùng dịch vụ tìm kiếm phân tán ngay từ đầu

Không tương xứng với nhu cầu hiện tại, tăng vận hành và làm khó tái tạo local.

### Chỉ quét file nguồn khi có truy vấn

Không khả thi về hiệu năng và làm cho logic tìm kiếm/phân hạng khó kiểm thử.

## Hệ quả

- database có thể lớn nhưng được phép đặt ngoài Git;
- thay parser/index version có thể buộc rebuild phần liên quan;
- mọi record dẫn xuất quan trọng phải giữ source path và source SHA;
- khi cần kiểm chứng câu chữ, quay lại source upstream.

## Khi nào xem xét lại

Xem xét khi SQLite trở thành nút thắt thực tế không giải quyết được bằng chia
profile, build gia tăng hoặc tối ưu chỉ mục, và chỉ khi giải pháp thay thế vẫn
giữ được offline reproducibility và provenance.
