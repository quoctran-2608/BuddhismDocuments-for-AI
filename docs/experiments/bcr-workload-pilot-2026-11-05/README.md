# BCR — Thử nghiệm giảm tải cho Codex Research Agent (pilot 4 claims)

## Quyết định thực nghiệm

Mục tiêu duy nhất ở lượt này: quan sát liệu **số claim xử lý trong mỗi phiên Codex** (4 vs 2 vs 1) làm thay đổi chất lượng thực thi BCR và số lỗi có thể kiểm hay không. **Cả ba phương án đều phải tuân cùng 5 chặng** để không nhầm lợi ích chia công việc với lợi ích có thêm checklist.

- **A:** 1 chat Codex mới, xử lý cả **AC04-C01, AC05-C01, AC06-C01, AC09-C01**.
- **B:** 2 chat Codex mới độc lập, lần lượt **AC04+AC05** và **AC06+AC09**.
- **C:** 4 chat Codex mới độc lập, mỗi chat chỉ **1 claim**.
- Tổng cộng 7 chat Codex mới (không tính chat tổng hợp). Đừng dùng chat phát triển hoặc chat đã biết kết luận. Không được xem kết quả của nhánh khác trước khi khóa kết quả của chính mình.
- Chỉ khác khối lượng claim mỗi chat. **Không được đổi model/mức suy luận một cách cố ý giữa các nhóm.** Giữ cùng môi trường, cùng nguồn, cùng quyền truy cập và cùng tiêu chí; nếu khác phải ghi lại.

Baseline Git P0/3 đã xác minh: `dfdd3cbb79e3dbfb49a855702fa00e4bad3b3410`. Commit P0/3 feature `06c497842127e656abfd6a387ac1c254a465a727` có cùng Git tree với merge commit, nhưng phải báo rõ HEAD thực chạy. Sử dụng `AGENTS.md`, skill và P0/1, P0/3. P0/2 chỉ sử dụng nếu có adapter hợp lệ; không giả mạo model inference. Không tải nguồn, không sửa code/index/pins.

## Thực hiện

1. Mở **7 phiên chat mới**, mỗi phiên chọn cùng repo/worktree khả dụng. Chạy đúng nội dung trong `prompts/A.md`, `B1.md`, `B2.md`, `C1.md`…`C4.md` tương ứng. Có thể làm lần lượt để tránh ghi đè; mỗi phiên phải dùng thư mục output/run/store riêng.
2. Các phiên ghi đầu ra vào `bcr-workload-experiment-20261105/runs/<RUN_ID>/` ngoài source và corpus, không sửa hồ sơ đã khóa. Lưu ít nhất `run-summary.json`, `findings-vi.md`, `commands.jsonl`, các evidence/structured-output receipts thực tế nếu có, và SHA-256.
3. **Khóa tất cả 7 kết quả** trước khi để bất kỳ phiên nào đọc báo cáo của nhau hoặc hồ sơ forward-test cũ. Không chia sẻ các `findings` giữa các phiên.
4. Điền `scorecard.csv` hoặc dùng một chat đánh giá riêng để chấm dựa trên **nguồn ghim**, không chấm theo mức độ tự tin/văn phong của Codex. Chấm theo claim × phương án, không cộng 299 units thành các source độc lập.
5. Dùng `rubric.md` để rút kết luận; thiếu log tokens/chi phí thì ghi `NOT_AVAILABLE` thay vì ước lượng.

## 5 chặng bắt buộc giống nhau trong mọi nhánh

1. **Preflight + Gate A:** đúng checkout, index, nguyên văn frozen claim, nguồn DECLARED/pin/witness. Không lấy lexical hit thay nguồn.
2. **Hiểu nguồn:** xác định ai nói gì, segment/context, thuật ngữ, điều kiện, metadata vs root, nguồn khác nhau.
3. **Đối chiếu claim:** điểm chứng minh được, không được, suy rộng, vấn đề chưa giải quyết.
4. **Phản biện:** tìm phản chứng/ngoại lệ có phạm vi, tách ứng viên chưa đọc khỏi chứng cứ đã xét.
5. **Kiểm đầu ra:** ghi notes trước kết luận, dùng `output-check` cho TITLE/QUOTE/IDENTIFIER/CONCLUSION khi phù hợp; giữ semantic prose UNRESOLVED, xuất báo cáo và receipt.

**Nguyên tắc quan trọng:** BCR Gate A/ CHECKED không chứng minh correctness ngữ nghĩa; một kết luận sai vẫn có thể CHECKED. Đánh giá semantic cần đối chiếu độc lập từng mệnh đề, không suy từ số lần PASS.

## Những giới hạn phương pháp cần nêu

- Đây là pilot với 4 claims **đã xuất hiện trong các thử nghiệm lịch sử**, không phải bộ mù học thuật. Các chat phải mới và không đọc báo cáo cũ, nhưng việc chọn 4 claims có thể gây bias của người thiết kế.
- Các phiên độc lập không chắc có cùng số token, số phút, hoặc cùng số evidence units thực tế. Nếu C có kết quả tốt hơn nhưng dùng nhiều công suy luận/tìm kiếm hơn, không được quy hết cho kích thước phiên.
- BCR không có semantic ground truth độc lập cho toàn bộ 37 claims. Đánh giá ngoại hiện chỉ có thể xác minh lỗi cụ thể/giới hạn, không tuyên bố phần trăm độ chính xác.
- Cả 3 nhánh đều có 5 chặng: phép thử này so sánh **quy mô batch**, **chưa chứng minh tác dụng riêng của việc chia chặng so với làm một lần**. Sau pilot, có thể bổ sung nhánh đối chứng cùng batch-size nhưng không chia chặng.

### Điểm dừng

Không chạy thêm hay đổi tiêu chí giữa chừng nếu gặp lỗi; ghi lỗi và giới hạn. Chỉ mở rộng lên 6–8 claims sau khi thấy pilot 4 claims có đủ nhật ký và so sánh được.

**Tuyệt đối không merge, không sửa code, không mở publication gate.**
