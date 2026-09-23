# KHO NGUỒN GỐC DỮ LIỆU PHẬT GIÁO CHO AI (TẦNG 1 — RAW)

Kho dữ liệu này được clone tự động theo danh mục trong [`manifest.json`](manifest.json).

> **Nguyên tắc:** Dữ liệu trong thư mục `raw/` là bản gốc đối sánh, giữ nguyên tính toàn vẹn và bất biến để AI luôn có thể truy ngược nguồn gốc và trích dẫn chuẩn xác.

---

## CÁCH TẢI TOÀN BỘ DỮ LIỆU

Kho này dùng Git submodules để giữ nguyên nguồn gốc và commit SHA của 13 repository thành phần.

```bash
git clone --recurse-submodules https://github.com/quoctran-2608/BuddhismDocuments-for-AI.git
```

Nếu đã clone mà chưa lấy dữ liệu submodule:

```bash
git submodule update --init --recursive
```

---

## NGHIÊN CỨU OFFLINE VÀ LOCAL INDEX

Quy tắc nghiên cứu bắt buộc nằm trong [`AGENTS.md`](AGENTS.md). Hệ thống chỉ
dùng dữ liệu local, không Web Search và không tự tải dữ liệu còn thiếu.

```bash
# Kiểm tra 13 nguồn local và trạng thái index
bin/buddhist-corpus status

# Xây index cốt lõi, incremental theo commit SHA
bin/buddhist-corpus build --profile core

# Tìm kiếm có provenance
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus search "如是我聞" --language lzh

# Bundled evidence và static export cho GitHub Connector
bin/buddhist-corpus evidence --record-id 123 --context 2
bin/buddhist-corpus export-remote --output remote/corpus
```

Tài liệu:

- [Khảo sát corpus](docs/CORPUS_SURVEY.md)
- [Kiến trúc hệ thống](docs/ARCHITECTURE.md)
- [Hướng dẫn CLI](docs/CLI.md)
- [GitHub Connector research access](docs/REMOTE_AGENT.md)
- [Buddhist corpus research skill](.codex/skills/buddhist-corpus-research/SKILL.md)

Database sinh ra nằm trong `derived/`, không phải source-of-truth và không được
commit.

---

## 1. BẢNG TỔNG KẾT CÁC REPOSITORY ĐÃ CLONE (13/13 REPO)

| STT | Phân loại | Repo & Thư mục cục bộ | Phiên bản (Commit SHA) | Kích thước | Mô tả nội dung & Mục đích sử dụng |
|:---:|:---|:---|:---:|:---:|:---|
| 1 | **GĐ 1** | [`suttacentral/bilara-data`](suttacentral/bilara-data) | `0914c609` | 210.1 MB | Pāli Sơ kỳ, bản dịch, ghi chú, dị bản, mã đoạn ID (`mn1:3.2`) dạng JSON. Rất chuẩn cho RAG. |
| 2 | **GĐ 1** | [`suttacentral/sc-data`](suttacentral/sc-data) | `cf4fcfb4` | 1.22 GB | Quan hệ song hành giữa Nikāya và A-hàm, cấu trúc kinh điển và metadata hệ thống. |
| 3 | **GĐ 1** | [`cbeta-org/xml-p5`](cbeta/xml-p5) | `dbdea410` | 2.59 GB | Đại Tạng Kinh Hán văn bản TEI P5 XML chuẩn gốc của CBETA (A-hàm, Đại thừa, Luận, Mật giáo). |
| 4 | **GĐ 1** | [`cbeta-org/BM_u8`](cbeta/BM_u8) | `83bc009a` | 1.47 GB | Hán tạng dạng plain UTF-8 đơn giản, tối ưu cho AI đọc nhanh và nạp vào vector store. |
| 5 | **GĐ 1** | [`84000/data-translation-memory`](84000/data-translation-memory) | `0c89d8ef` | 727.6 MB | Dữ liệu đối chiếu song ngữ Tây Tạng ↔ Anh căn chỉnh từng đoạn (định dạng TMX). |
| 6 | **GĐ 2** | [`84000/data-rdf`](84000/data-rdf) | `c40f0261` | 7.8 MB | Metadata, quan hệ tác phẩm, liên kết Toh. để xây dựng đồ thị tri thức (Knowledge Graph). |
| 7 | **GĐ 2** | [`84000/data-tei`](84000/data-tei) | `bdfc81c9` | 240.9 MB | Bản dịch Kangyur/Tengyur định dạng TEI XML giữ nguyên cấu trúc văn bản. |
| 8 | **GĐ 2** | [`OpenPecha-Data/C0A2DD042`](openpecha/C0A2DD042) | `1164df36` | 91.3 MB | Corpus song song đa ngôn ngữ (Tây Tạng - Anh, Hoa, Pháp, Đức,...) đã chia đoạn. |
| 9 | **GĐ 3** | [`BuddhaNexus/segmented-pali`](buddhanexus/segmented-pali) | `60d3af5b` | 511.4 MB | Pāli đã phân đoạn cho mạng nơ-ron, hỗ trợ tìm câu tương đồng và liên văn bản. |
| 10 | **GĐ 3** | [`BuddhaNexus/segmented-chinese`](buddhanexus/segmented-chinese) | `06808274` | 4.06 GB | Hán tạng đã phân đoạn cho AI, dùng để phát hiện văn bản song hành. |
| 11 | **GĐ 3** | [`BuddhaNexus/segmented-sanskrit`](buddhanexus/segmented-sanskrit) | `8ba2ab31` | 395.4 MB | Phạn văn (Sanskrit) đã phân đoạn từ nhiều nguồn để phát hiện liên văn bản. |
| 12 | **Bổ trợ** | [`bdhrs/pts-archive`](pts/pts-archive) | `50a8d453` | 35.2 MB | Dữ liệu số hóa một phần PTS (dùng tra cứu/đối chiếu tham khảo). |
| 13 | **Bổ trợ** | [`dangerzig/pali-canon`](third-party/pali-canon) | `7d44211b` | 1.47 GB | Dữ liệu ngữ pháp, từ gốc (lemmatization) và tìm kiếm Pāli toàn văn. |

---

## 2. THÔNG SỐ LƯU TRỮ TRÊN ĐĨA

* **Tổng dung lượng toàn bộ 13 repo:** **~12.85 GB**
* **Dung lượng đĩa còn trống hiện tại:** **~32.2 GB** / 91.99 GB (Thoải mái cho việc chuẩn hóa Tầng 2 và xây dựng vector index Tầng 3).
* **Chi tiết file manifest:** [`manifest.json`](manifest.json)
