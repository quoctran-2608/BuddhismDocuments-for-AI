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
3. `REQUIREMENTS.md` — sẽ được tạo trong Giai đoạn 3 để chứa các yêu cầu có mã
   dành riêng cho 2.0.
4. `ACCEPTANCE.md` — sẽ được tạo trong Giai đoạn 3 để chứa tiêu chí nghiệm thu
   dành riêng cho 2.0.
5. Tài liệu triển khai — chỉ tạo sau khi đọc mã nguồn hiện hành và thật sự cần.

## Ranh giới với tài liệu hiện hành

```text
docs/
→ tài liệu chung và hệ thống hiện hành

docs/v2/
→ chương trình nâng cấp 2.0 chưa triển khai đầy đủ
```

Không tạo một bộ `docs/v1/` mới. Hệ hiện hành đã có các nguồn chuẩn của chính
nó như `PROJECT_SPEC.md`, `ARCHITECTURE.md`, `CLI.md`,
`REMOTE_AGENT.md`, cấu hình, schema, mã nguồn và kiểm thử.

Khi 2.0 được triển khai từng phần, trạng thái chỉ được chuyển từ **MỤC TIÊU**
sang **HIỆN HÀNH** sau khi có mã nguồn và kiểm thử/đối chiếu nghiệm thu tương
ứng. Không coi việc đã viết tài liệu là bằng chứng đã triển khai.
