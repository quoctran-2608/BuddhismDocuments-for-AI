# Buddhist Corpus Research 2.0 — Bộ tài liệu nâng cấp

> Trạng thái: **MỤC TIÊU**
>
> Thư mục này chỉ chứa tài liệu dành riêng cho chương trình nâng cấp
> **Buddhist Corpus Research 2.0**. Các tài liệu mô tả hệ thống đang vận hành
> vẫn nằm ở cấp `docs/` và không được hiểu lẫn với nội dung trong thư mục này.

## Đọc theo thứ tự

1. [PRD.md](PRD.md) — **Đề bài 2.0**: vì sao nâng cấp, phải đạt gì, giữ gì, không
   làm gì.
2. [DESIGN.md](DESIGN.md) — **Thiết kế 2.0**: bằng chứng, luận điểm, phản chứng,
   cửa kiểm, lịch sử sửa đổi và hồ sơ lần nghiên cứu.
3. [REQUIREMENTS.md](REQUIREMENTS.md) — **Yêu cầu 2.0**: 29 yêu cầu có mã,
   tách khỏi yêu cầu của hệ hiện hành.
4. [ACCEPTANCE.md](ACCEPTANCE.md) — **Nghiệm thu 2.0**: cách chứng minh từng
   yêu cầu đã thật sự được triển khai.
5. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) — **Kế hoạch triển khai ngắn**: điểm chèn vào mã hiện hành, phần giữ nguyên, lát cắt đầu tiên và thứ tự làm.

## Ranh giới với tài liệu hiện hành

```text
docs/
→ tài liệu chung và hệ thống hiện hành

docs/v2/
→ chương trình nâng cấp 2.0 chưa triển khai đầy đủ
```

Không tạo một bộ `docs/v1/` mới. Hệ hiện hành đã có các nguồn chuẩn của chính
nó như `PROJECT_SPEC.md`, `ARCHITECTURE.md`, `CLI.md`,
`REMOTE_AGENT.md`, cấu hình, lược đồ dữ liệu, mã nguồn và kiểm thử.

Khi 2.0 được triển khai từng phần, trạng thái chỉ được chuyển từ **MỤC TIÊU**
sang **HIỆN HÀNH** sau khi có mã nguồn và kiểm thử/đối chiếu nghiệm thu tương
ứng. Không coi việc đã viết tài liệu là bằng chứng đã triển khai.
