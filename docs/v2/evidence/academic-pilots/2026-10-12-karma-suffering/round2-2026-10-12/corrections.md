# Round 2 — giải thích và hiệu đính chỉ số

Báo cáo nguyên gốc `report-vi.md` và `round2-summary-original.json` được lưu **nguyên byte**. Bảng sau là lớp **diễn giải hiệu đính**, không sửa lịch sử.

| Diễn đạt ban đầu | Diễn đạt kiểm toán được | Lý do |
|---|---|---|
| 102 C reader calls/receipts | **102 receipt entries, 57 unique (case,search_id), 45 entry trùng nội dung** | Không thể quảng bá 102 independent counterevidence searches |
| 57 candidate claims | **57 historical claim records; 56 candidate IDs còn active; 1 rejected (AC07)** | Không phải 57 claim được accepted/đang hoạt động |
| 12/12 Research | **12 draft runs; B = 11 UNVERIFIED + 1 REJECTED, 0 accepted** | Không có thẩm định ngữ nghĩa đã được chấp thuận |
| 25/25 retrieval equal | **25/25 non-regression** Quick so CLI 1.0 hiện hành tại cùng code `a6707b3...` | Không phải so baseline tiền A `f7415...` hay độ đúng semantic |
| Article P013/P029 mismatch | **2 original article quote gates REJECTED** | Không được cộng source-generated controls vào article quote successes |
| AC03 Quick VERIFY at Y32n0030 | **Đúng ở witness khác, chưa chứng minh T99.977** | Phải kiểm source/work/witness attribution |
| 12 cases PASS | **12 trường hợp thực thi thành công; học thuật INCONCLUSIVE/AC07 BLOCKED** | Lỗi/giới hạn nguồn khác với lỗi code |

**Không phát hiện đủ bằng chứng yêu cầu sửa code BCR từ vòng này.** Việc tiếp theo là semantic adjudication có ground truth độc lập, và hoàn tất lưu raw archive ngoài Git.
