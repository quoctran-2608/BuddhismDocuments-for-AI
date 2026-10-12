# Tóm lược kiểm toán độc lập — Academic Pilot 01

**Ngày:** 12/10/2026. **Trạng thái:** CHẤP NHẬN CÓ ĐIỀU KIỆN như một pilot thăm dò provenance/tầng A. **KHÔNG CHẤP NHẬN** là nghiệm thu học thuật, kiểm toán tự động bài viết hoàn chỉnh, hoặc bằng chứng BCR 2.0 tốt hơn 1.0.

Bản tóm lược này là lưu trữ sơ bộ cho GitHub; bản kiểm toán đầy đủ (`BCR_Pilot01_Independent_Audit_2026-10-12.md`) có SHA-256 `b3d161b6829de90497a9a8987bc5e8702e6879a73a695ca28905b6dfdfa38d13`. Chưa lưu bản đầy đủ vào nhánh bootstrap để tránh tạo hai bản có thể lệch trong khi Work đang hiệu đính/hợp nhất hồ sơ.

## Điểm đã xác minh

1. 275/275 checksum trong `SHA256SUMS.txt` của Work khớp tệp đã lưu. File Word bản gốc trong gói có SHA-256 trùng bản chủ dự án gửi: `570c4cee4092df7a1343020b5a3d37e98ffca89e1473c362fde732f9625f55d4`.
2. Source ledger ghi 16 nguồn (11 Pāli root, 3 bản dịch Anh, 2 CBETA), đã kiểm SHA-256 và Git blob theo các commit ghim. Năm blob mã/config chủ chốt của BCR khớp mốc `main` nêu trong bootstrap.
3. Tính nhất quán của 59 bộ tool RPC receipts được kiểm (15 locator, 44 source); đây là kiểm chứng cấu trúc receipt, không phải chứng thực lịch sử thực thi bằng chữ ký máy chủ.
4. Offline replay từ mã snapshot và dữ liệu nguồn đã lưu tái lập 13 `VERIFIED`, 2 `REJECTED` ở 15/15 kiểm A.
5. Work ghi rõ local retrieval/Quick/Research bị chặn, không ngụy tạo ResearchStore hoặc approval.

## Phát hiện phải giữ trong báo cáo corrected

**IA-01 — Sai đơn vị kinh.** Work dùng gate `T02n0100:0453a01` và vùng `0453a01–09` để bàn về **kinh 211**, nhưng trong CBETA T100 tại SHA `dbdea41071e1e260ad84b72faefd4587333cf76d`, kinh 211 ở `0452b04–0452c16`; `0452c17` bắt đầu kinh 212. Gate A có thể kiểm đúng byte tại đoạn được giao nhưng **không** xác nhận quan hệ đoạn đó với kinh 211. Trước mắt phân loại là lỗi chọn/diễn giải vị trí của Work/harness; chưa đủ để quy lỗi code A.

**IA-02 — Hai nguyên nhân từ chối quote Hán.** Bài viết ghi `一切人所知覺者，皆是本所造因。`, khác dấu câu so với CBETA T99 `0253a06–07`. Nguồn cũng chia span qua thẻ `lb`. Bỏ dấu câu trong phép thử offline bổ sung vẫn không cho A ghép câu qua span; một span ngắn liên tục có thể `VERIFIED`. Không gộp sai dấu câu của bài với giới hạn đọc XML thành một lỗi.

**IA-03 — Không dùng 13 VERIFIED như 13 câu trích của bài đã kiểm.** Chỉ `article-pali-quote` và `article-han-quote` là câu trích đưa vào từ bài và cả hai bị A từ chối. 13 lượt `VERIFIED` còn lại có `quotation_input=null`, do adapter chọn câu nguồn làm đối chứng. Claim registry 104 mục là phân tích sơ bộ của Work, **không phải** 104 B assessments đã chạy.

**IA-04 — SN 35.145/146.** Trong Bilara được ghim, `sn35.145` là `Bāhirānattahetusutta`, còn `sn35.146` là `Kammanirodhasutta` với đoạn về nghiệp cũ/mới. Phát hiện sai dẫn chiếu theo hệ định danh này là phân tích của Work, không phải bằng chứng BCR tự phát hiện claim-to-source mismatch. Không suy rộng sang mọi hệ đánh số.

**IA-05 — Giá trị học thuật chưa đo.** Thiếu full local index/corpus, run C/D và ground truth ngữ nghĩa độc lập. Không tính semantic false acceptance/rejection hay lợi ích tăng thêm so với 1.0. Research publication vẫn đóng.

## Cửa nghiệm thu

| Nội dung | Phán quyết |
|---|---|
| Toàn vẹn bản gốc/gói, kiểm source SHA | PASS trong mẫu |
| Replay của thuật toán A | PASS 15/15 offline |
| Đối chiếu Hán tạng kinh 211 trong báo cáo cũ | PHẢI HIỆU ĐÍNH |
| Local 1.0, Local Quick và Research A/B/C/D | BLOCKED |
| Lợi ích gia tăng 2.0 vs 1.0 | CHƯA ĐO |
| Semantic approval / nghiên cứu được công bố | CHƯA NGHIỆM THU |

**Bước kế tiếp:** Work chuẩn bị bản hiệu đính và raw evidence delta (không xóa receipt cũ); sau đó một môi trường WSL với checkout/index ghim mới có thể chạy lại retrieval/Quick/Research trên cùng ca. Không làm giả currentness hoặc cấp phép publication.
