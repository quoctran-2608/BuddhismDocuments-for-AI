# Rubric — kiểm toán mù sau khi cả 7 run đã khóa

Không dùng nhận định của bất kỳ run nào làm đáp án. Người kiểm toán đọc pinned source và ngữ cảnh thực (P0/1 A) độc lập, sau đó kiểm từng nhận định.

## Những cột dữ liệu nên đối chiếu **theo từng claim**

1. **Evidence correctness**: citation/repository/source SHA/work/segment chính xác? Có trích sai ký tự, nhầm witness, lấy metadata làm kinh văn? Ghi incident ID và nguồn so sánh.
2. **Faithfulness**: có bỏ điều kiện sau khi chết/tái sinh, ngữ cảnh người nói, hoặc suy rộng 'tất cả'/'không bao giờ'? Mỗi lỗi phải có đoạn nguồn chứng minh, không chỉ câu nhận xét của người chấm.
3. **Counterevidence coverage**: phân biệt loại phản chứng đã mở so với candidate; so sánh tác phẩm/nguồn được tìm và thực sự đọc, không coi số lượng lớn là chất lượng cao hơn.
4. **P0/3**: số item CHECKED/UNVERIFIED/REJECTED; phân biệt trường cấu trúc với văn xuôi tự do. CHECKED không cộng vào điểm semantic correctness.
5. **Lỗi vận hành**: sai root/ownership/index, exit-0 hiểu nhầm Gate A, replay receipt, gõ sai TITLE, lỗi tool, sự cố bỏ chặng.
6. **Tài nguyên**: thời gian thực đo/claim, tokens/claim (nếu có), tổng subproc, số source units VERIFIED thực, số nguồn unique/work independent. Không ước lượng token từ wordcount.

## Cách kết luận

- Ghi số lỗi có **chứng cứ kiểm độc lập**, số lỗi **đang tranh luận**, số trường hợp **không thể xác minh**. Không dựng nhãn điểm tổng hợp hoặc tỷ lệ semantic accuracy.
- Nhánh A (4 claim / một chat) so với B (2 claim / chat) so với C (1 claim / chat) đánh giá riêng cho từng case; kiểm xem cải thiện có nhất quán qua bốn case không, hay phụ thuộc khó/dễ.
- Nếu C dùng nhiều thời gian/token hơn, kết luận rằng chất lượng có thể tăng do **đầu tư tài nguyên** chứ chưa chứng minh nguyên nhân duy nhất là chia nhỏ.
- Nếu A/B/C đều có cùng lỗi, chia nhỏ đơn thuần khó giải quyết loại lỗi đó; cần rào chắn khác.
- Bất kỳ tình trạng thiếu corpus, model khác, baseline khác, contamination phải là confounder, không xóa/hợp thức hóa.
- Thí nghiệm này giữ năm chặng ở cả ba nhánh; **không** chứng minh riêng tác dụng chia chặng. Nếu muốn kiểm riêng, thực hiện vòng 2 với số claim/chặng giống nhau nhưng hai cách workflow khác nhau.
- Chỉ sau khi chấm mù mới cho phép đọc báo cáo cũ và phân tích tiến bộ theo thời gian.

## Dấu hiệu có giá trị để quyết định bước phát triển

Cần đủ kết quả để chấp nhận một rule batch mới: 1) có giảm các lỗi source/logic được audit; 2) không tăng bỏ sót phản chứng; 3) thời gian/tokens tăng trong mức chấp nhận được; 4) tác dụng lặp lại trong bộ case thứ hai chưa dùng khi thiết kế. Pilot bốn case chỉ là bước định hướng, không tự xác lập kích cỡ tối ưu.
