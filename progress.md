# HỒ SƠ TIẾN ĐỘ VÀ BÀN GIAO DỰ ÁN

> Ngày chốt hồ sơ: **25/09/2026**<br>
> GitHub repository chính: `quoctran-2608/BuddhismDocuments-for-AI`<br>
> GitHub repository artefact Connector: `quoctran-2608/BuddhismDocuments-for-AI-remote`<br>
> Thư mục checkout đang làm việc: `Buddhism-forAI-Documents/raw`<br>
> Commit mã triển khai compact: `1c1e57bdadacb1c8e9794f52d460b5cf34a0b831`<br>
> Nhánh đang mở: `feat/github-connector-research-access`<br>
> Trạng thái với `main`: nhánh đang mở, `main` và `origin/main` cùng trỏ tới commit trên.

Tài liệu này giúp một AI hoặc người phát triển mới tiếp nhận repository mà không
phải tự dựng lại toàn bộ lịch sử. Nội dung được tổng hợp từ mã nguồn, tài liệu,
lịch sử Git, cơ sở dữ liệu cục bộ, các bản export (xuất dữ liệu) và kết quả kiểm
thử thực tế tại ngày 25/09/2026.

---

## 1. Tóm tắt ngắn

Dự án ban đầu chỉ là một kho tập hợp **13 nguồn dữ liệu Phật giáo** dưới dạng Git
submodule (kho Git con), tổng dung lượng nguồn gốc khoảng 12,85 GB theo
`README.md`. Vấn đề là 13 nguồn có cấu trúc, ngôn ngữ, định danh và mức độ thẩm
quyền khác nhau; không có một cách tìm kiếm, đối chiếu và trích dẫn thống nhất.

Dự án đã phát triển thành một hệ thống nghiên cứu gồm:

1. **Tầng nguồn bất biến**: 13 submodule được ghim bằng commit SHA.
2. **Tầng chỉ mục SQLite cục bộ**: chuẩn hóa dữ liệu thành bản ghi văn bản, tác
   phẩm, quan hệ, dị bản và lemma (dạng từ gốc).
3. **Tầng truy xuất CLI**: tìm kiếm, đọc ngữ cảnh, xem xuất xứ, tìm song hành,
   giải định danh CBETA, xem dị bản và so sánh nhân chứng.
4. **Tầng phương pháp nghiên cứu**: bắt buộc dùng bằng chứng trong repository,
   tách nguồn phát hiện khỏi nguồn làm chứng, tách bản văn chính khỏi ghi chú.
5. **Tầng GitHub Connector**: cho AI không có shell/SQLite truy cập bằng con trỏ
   đến file nguồn gốc trên GitHub.

Trạng thái hiện tại:

- 13/13 submodule tồn tại và khớp SHA trong `manifest.json`.
- Chỉ mục cục bộ hiện có dữ liệu của cả 13 corpus, khoảng **50.028.723 bản ghi
  văn bản**, **1.032.823 quan hệ**, **1.383.170 dị bản** và **50.560 lemma** theo
  `source_state`.
- File SQLite hiện tại khoảng **42,94 GiB** và được đặt ngoài repository; đường
  `derived/corpus.sqlite3` chỉ là symbolic link (liên kết tượng trưng).
- Bộ kiểm thử hiện tại qua **41/41 test**.
- Proof of concept (POC, bản chứng minh ý tưởng) pointer-only hiện có 11 key:
  `anicca`, `dukkha`, `jhāna`, `nibbāna`, `Mahākassapa`, `無常`, `如是我聞`,
  `苦`, `空`, `T02n0099`, `T01n0001`.
- POC giữ tối đa 20 pointer khác `(work_id, source_path)` cho mỗi corpus, thay
  vì lấy một danh sách global top 20.
- POC mới không chứa `raw_text` trong các file JSONL con trỏ; nó chỉ chứa thông
  tin định vị file nguồn.
- Trong quá trình xây GitHub Connector, dự án đã tạo và sử dụng thêm repository
  riêng `quoctran-2608/BuddhismDocuments-for-AI-remote` để chứa artefact dẫn
  xuất cho Connector. Repository chính vẫn là
  `quoctran-2608/BuddhismDocuments-for-AI`.
- Bản export cũ có sao chép văn bản vẫn còn trên đĩa và trong repository remote
  riêng. Việc chuyển đổi toàn bộ remote sang pointer-only **chưa hoàn tất**.

---

## 2. Bài toán gốc của dự án

### 2.1. Vấn đề dữ liệu

13 nguồn không đồng nhất:

- JSON chia đoạn của SuttaCentral;
- TEI XML của CBETA và 84000;
- văn bản UTF-8 dạng dòng của CBETA BM_u8;
- RDF mô tả quan hệ tác phẩm;
- TMX/JSON căn chỉnh Tây Tạng–Anh;
- corpus đã phân đoạn bằng máy của BuddhaNexus;
- dữ liệu lemma, hình thái học và khảo dị Pāli;
- các bản tham khảo PTS có chất lượng không đồng đều.

Nếu AI tìm trực tiếp bằng cách quét file hoặc dựa vào trí nhớ mô hình, các lỗi
sau rất dễ xảy ra:

1. Trộn bản dịch, ghi chú dịch giả và bản văn gốc thành một loại.
2. Xem dữ liệu quan hệ song hành như bằng chứng rằng hai văn bản có cùng nội
   dung.
3. Trích BuddhaNexus hoặc dữ liệu căn chỉnh như nguồn văn bản cuối cùng dù chúng
   chủ yếu dùng để phát hiện ứng viên.
4. Tự suy diễn tương đương Pāli–Sanskrit–Hán–Tạng mà không có bằng chứng local.
5. Mất đường dẫn nguồn, số đoạn, số dòng, nhân chứng và commit SHA.
6. Tìm kiếm Hán văn kém vì cách tách từ thông thường không phù hợp.
7. Không thể dùng cơ sở dữ liệu local khi AI chỉ có GitHub Connector.

### 2.2. Mục tiêu nghiên cứu

Hệ thống phải bảo đảm:

- chỉ bằng chứng có trong repository mới được dùng để kết luận;
- mọi kết quả có provenance (xuất xứ có thể truy ngược);
- ưu tiên nguồn mạnh hơn nhưng không che giấu xung đột giữa các nhân chứng;
- giữ nguyên khác biệt giữa truyền thống, ngôn ngữ và ấn bản;
- không tự tải dữ liệu, package (gói phần mềm) hoặc mô hình từ mạng;
- dữ liệu nguồn không bị sửa;
- dữ liệu sinh ra có thể tái tạo từ SHA đã ghim;
- khi không đủ bằng chứng phải “fail closed” (từ chối kết luận an toàn) bằng câu:
  **không đủ dữ liệu trong corpus hiện tại**.

### 2.3. Mục tiêu truy cập từ xa mới nhất

Yêu cầu gần nhất trong `prompt.txt` là bỏ mô hình:

```text
locator → shard chứa bản sao raw_text
```

và chuyển sang:

```text
locator → con trỏ đã xếp hạng
        → repository nguồn
        → source_sha đã ghim
        → source_path
        → work_id / segment_id
        → GitHub Connector mở file gốc
```

Lý do:

- không sao chép khoảng 50 triệu bản ghi lên repository remote;
- không duy trì corpus thứ hai;
- không tạo search engine (bộ máy tìm kiếm) thứ hai;
- giữ nguyên cách xếp hạng, provenance và phương pháp nghiên cứu;
- lúc người dùng nghiên cứu chỉ cần:
  `ChatGPT ↔ GitHub Connector ↔ GitHub`;
- SQLite chỉ tham gia lúc tạo chỉ mục/con trỏ, không tham gia runtime (thời gian
  chạy phục vụ người dùng).

---

## 3. Các nguyên tắc bắt buộc

### 3.1. Chế độ offline tuyệt đối

`AGENTS.md` là quy tắc cao nhất:

- không Web Search, trình duyệt, `curl`, `wget` hoặc API mạng;
- không `git fetch`, `git pull`, `git clone`, `git submodule update`;
- không tải package, từ điển, corpus hoặc mô hình còn thiếu;
- nếu thiếu submodule, Git object hoặc file nguồn thì dừng nhánh điều tra và báo
  **không đủ dữ liệu trong corpus hiện tại**.

Lưu ý: GitHub Connector mode là một đường truy cập dành cho môi trường khác.
Khi làm việc trực tiếp trong checkout local này, vẫn phải tuân thủ offline.

### 3.2. Tầng nguồn bất biến

Không được sửa file bên trong 13 thư mục submodule. Parser (bộ phân tích), index
(chỉ mục), cache (bộ nhớ đệm), báo cáo và dữ liệu sinh ra phải nằm ngoài
submodule.

### 3.3. Thứ bậc bằng chứng

Từ mạnh tới yếu:

1. `canonical_root`: bản văn gốc hoặc nhân chứng văn bản chính.
2. `authoritative_structured`: ấn bản có cấu trúc đáng tin cậy.
3. `metadata_relationship`: metadata và quan hệ, không phải câu chữ.
4. `parallel_alignment`: dữ liệu song song/căn chỉnh.
5. `computational_segmented`: dữ liệu phân đoạn bằng máy để tìm ứng viên.
6. `derived_critical_lemma`: dữ liệu khảo dị/lemma đã qua xử lý.
7. `auxiliary_reference`: dữ liệu tham khảo phụ trợ.

Điểm quan trọng: `evidence_class` trả lời “nguồn có thẩm quyền tới đâu”, còn
`text_role` trả lời “đoạn này là loại nội dung gì”.

Ví dụ `text_role`:

- `root_text`: bản văn chính;
- `translation_main`: phần dịch chính;
- `translation_heading`: tiêu đề bản dịch;
- `translator_comment`: bình luận của dịch giả;
- `translation_note`: chú thích bản dịch;
- `alignment_text`: văn bản dùng trong căn chỉnh;
- `computational_text`: văn bản đã xử lý bằng máy;
- `derived_text`: văn bản dẫn xuất;
- `auxiliary_text`: văn bản tham khảo.

Một ghi chú có thể thuộc nguồn có cấu trúc đáng tin, nhưng vẫn không được trình
bày như lời kinh chính.

---

## 4. Các repository GitHub và 13 nguồn dữ liệu đã ghim

### 4.1. Hai repository do dự án quản lý

#### Repository chính

```text
quoctran-2608/BuddhismDocuments-for-AI
```

Vai trò:

- chứa mã nguồn của hệ thống;
- chứa tài liệu, schema, CLI, parser và test;
- chứa cấu hình và con trỏ Git submodule tới 13 nguồn;
- là nơi chuẩn của kiến trúc và phương pháp nghiên cứu;
- không commit cơ sở dữ liệu SQLite lớn hoặc các export dẫn xuất.

Git remote `origin` của checkout hiện tại:

```text
https://github.com/quoctran-2608/BuddhismDocuments-for-AI.git
```

#### Repository mới dành cho GitHub Connector

```text
quoctran-2608/BuddhismDocuments-for-AI-remote
```

Đây là repository được tạo thêm trong quá trình phát triển chức năng GitHub
Connector. Nó không phải repository nguồn Phật học thứ 14 và không phải nơi chuẩn
của nội dung nghiên cứu. Nó là kho chứa artefact dẫn xuất để ChatGPT/GitHub
Connector có thể đọc qua GitHub khi không có quyền chạy shell hoặc SQLite.

Git URL được ghi trong cache local:

```text
https://github.com/quoctran-2608/BuddhismDocuments-for-AI-remote.git
```

Lý do cần tách repository này khỏi repository chính:

1. **Không làm phình kho mã chính**: full export thử nghiệm đã có khoảng 1,9 GiB
   và 4.545 file dù mới chứa 221.151 record, nhỏ hơn rất nhiều so với chỉ mục
   hiện tại có hơn 50 triệu record.
2. **Tách mã nguồn khỏi dữ liệu sinh ra**: mã, schema và phương pháp nghiên cứu
   nằm ở repo chính; shard/locator/pointer có thể tái tạo nằm ở repo remote.
3. **Phù hợp với GitHub Connector**: Connector cần đọc file trên GitHub nhưng
   không chạy được SQLite local. Repo remote cung cấp một cây file tĩnh để định
   tuyến tới bằng chứng.
4. **Không biến artefact thành source-of-truth**: repo remote chỉ dẫn tới nguồn
   đã ghim; kết luận nghiên cứu vẫn phải xác minh trong repository nguồn gốc.
5. **Cho phép thay thế chiến lược export**: ban đầu repo này chứa full-record
   shard có `raw_text`; sau đó thêm pointer-only POC mà không buộc repo mã chính
   mang theo dữ liệu lớn.
6. **Giữ runtime đơn giản**: mục tiêu cuối là
   `ChatGPT ↔ GitHub Connector ↔ GitHub`, còn SQLite chỉ dùng lúc tạo chỉ mục và
   artefact.

Mối quan hệ giữa hai repository:

```text
quoctran-2608/BuddhismDocuments-for-AI
  ├─ mã, cấu hình, tài liệu, test và phương pháp chuẩn
  └─ config/remote-corpus.json
        │
        ▼
quoctran-2608/BuddhismDocuments-for-AI-remote
  └─ remote/pointer-poc/
        │
        ▼
13 repository nguồn gốc tại các source_sha đã ghim
```

### 4.2. Tên đầy đủ của 13 repository nguồn

Ngoài hai repository do dự án quản lý ở trên, hệ thống dùng 13 repository nguồn
upstream (nguồn bên ngoài). Mỗi nguồn được gắn thành submodule trong repository
chính và được ghim tại một commit SHA cụ thể.

| Corpus trong hệ thống | GitHub repository nguồn | Thư mục submodule | SHA đã ghim | Vai trò chính |
|---|---|---|---|---|
| `suttacentral-bilara` | `suttacentral/bilara-data` | `suttacentral/bilara-data` | `0914c609...` | Pāli gốc, bản dịch, bình luận, dị bản |
| `suttacentral-relations` | `suttacentral/sc-data` | `suttacentral/sc-data` | `cf4fcfb4...` | Quan hệ song hành, cấu trúc, metadata |
| `cbeta-tei` | `cbeta-org/xml-p5` | `cbeta/xml-p5` | `dbdea410...` | Hán tạng TEI XML và apparatus (bộ máy khảo dị) |
| `cbeta-bm` | `cbeta-org/BM_u8` | `cbeta/BM_u8` | `83bc009a...` | Hán tạng UTF-8 theo dòng, tìm nhanh |
| `84000-tm` | `84000/data-translation-memory` | `84000/data-translation-memory` | `0c89d8ef...` | Căn chỉnh Tây Tạng–Anh |
| `84000-rdf` | `84000/data-rdf` | `84000/data-rdf` | `c40f0261...` | Metadata và quan hệ Toh. |
| `84000-tei` | `84000/data-tei` | `84000/data-tei` | `bdfc81c9...` | Bản dịch Kangyur/Tengyur dạng TEI |
| `openpecha` | `OpenPecha-Data/C0A2DD042` | `openpecha/C0A2DD042` | `1164df36...` | Corpus Tây Tạng đa ngôn ngữ căn chỉnh dòng |
| `buddhanexus-pali` | `BuddhaNexus/segmented-pali` | `buddhanexus/segmented-pali` | `60d3af5b...` | Pāli phân đoạn bằng máy |
| `buddhanexus-chinese` | `BuddhaNexus/segmented-chinese` | `buddhanexus/segmented-chinese` | `06808274...` | Hán văn phân đoạn bằng máy |
| `buddhanexus-sanskrit` | `BuddhaNexus/segmented-sanskrit` | `buddhanexus/segmented-sanskrit` | `8ba2ab31...` | Sanskrit phân đoạn bằng máy |
| `pts-archive` | `bdhrs/pts-archive` | `pts/pts-archive` | `50a8d453...` | Bản PTS/ROTA tham khảo, có nhiễu |
| `pali-canon-derived` | `dangerzig/pali-canon` | `third-party/pali-canon` | `7d44211b...` | Lemma, hình thái học, khảo dị nhiều nhân chứng |

Tổng cộng có **15 GitHub repository liên quan trực tiếp**:

- 2 repository do dự án quản lý;
- 13 repository nguồn upstream.

Ngày 25/09/2026 đã kiểm tra từng submodule bằng `git -C <path> rev-parse HEAD`:
**13/13 khớp chính xác với `manifest.json`**.

---

## 5. Kiến trúc hiện tại

### 5.1. Luồng dữ liệu

```text
13 submodule bất biến, có SHA
        │
        ▼
Parser local, xác định theo từng corpus
        │
        ▼
SQLite: records / works / relations / variants / lemmas
        │
        ├──────────────► CLI local
        │                 search, context, evidence, resolve...
        │
        └──────────────► Export cho GitHub Connector
                          ├─ legacy: shard có raw_text
                          └─ hiện hành: pointer POC không có raw_text
```

### 5.2. Schema SQLite

File: `schema/corpus-index.sql`.

Các bảng chính:

- `source_state`: trạng thái build của từng corpus, SHA, parser version và số
  lượng đối tượng.
- `search_index_state`: phiên bản chỉ mục tìm kiếm dẫn xuất.
- `works`: metadata tác phẩm.
- `records`: bản ghi văn bản và provenance.
- `relations`: quan hệ song hành, căn chỉnh, quan hệ tác phẩm hoặc ghi chú.
- `variants`: dị bản và nhân chứng.
- `lemmas`: surface form (dạng xuất hiện), lemma, từ loại và hình thái học.
- `records_fts`: FTS5 `unicode61` cho tìm kiếm Unicode thông thường.
- `records_cjk_fts`: FTS5 `trigram` cho chuỗi con CJK.

### 5.3. Các profile build

- `acceptance`: mẫu thật nhỏ, cố định, dùng cho test chấp nhận.
- `core`: SuttaCentral, CBETA BM_u8, 84000 TEI/RDF và dữ liệu Pāli dẫn xuất.
- `discovery`: 84000 TM, OpenPecha và ba corpus BuddhaNexus.
- `all`: toàn bộ 13 nguồn.

Build là incremental (gia tăng): khóa trạng thái gồm corpus, SHA nguồn, phiên bản
parser và phạm vi profile. Corpus không đổi sẽ được bỏ qua.

### 5.4. Tối ưu lưu trữ và WSL

- Bilara `core` gộp tối đa 50 đoạn vào một record.
- CBETA BM_u8 `core` gộp tối đa 300 dòng.
- `all` giữ dạng chi tiết hơn.
- Với đoạn Hán/Tạng dài từ 2.000 ký tự, hệ thống tránh lưu nhiều bản sao
  `normalized`, `folded`, `compact` gần giống nhau.
- Khi DB nằm dưới `/mnt/`, build dùng workspace tạm trên filesystem Linux để
  tránh chi phí ghi SQLite lên NTFS/WSL, rồi checkpoint về `derived/`.
- Có thể build nguồn nặng riêng bằng `--source` và hoãn FTS bằng `--defer-fts`.

### 5.5. Xếp hạng tìm kiếm

`score_record_match()` trong `tools/corpus_research/retrieval.py` là hàm xếp
hạng dùng chung.

Điểm match (khớp):

- chính xác: `120`;
- chuẩn hóa Unicode/case: `95`;
- bỏ dấu: `75`;
- compact Unicode: `70`;
- FTS: `30`;
- khớp lemma do corpus cung cấp: cộng `80`;
- có `segment_id`: cộng `5`;
- sau đó cộng trọng số theo `evidence_class`.

Tie-break (quy tắc phá hòa) ổn định:

```text
score giảm dần → corpus → source_path → sequence_no
```

Xếp hạng chỉ giúp chọn ứng viên trước. Nó không tự quyết định nguồn nào đúng.

### 5.6. Tìm kiếm CJK

FTS theo từ không tìm tốt chuỗi nằm giữa đoạn Hán văn dài. Vì vậy dự án thêm
`records_cjk_fts` dùng trigram:

- áp dụng cho `lzh` và `zh`;
- yêu cầu ít nhất ba ký tự CJK hữu dụng;
- tạo ứng viên bằng trigram, sau đó vẫn kiểm tra chính xác và xếp hạng bằng logic
  chung;
- không fallback (quét dự phòng) toàn bảng cho truy vấn một hoặc hai ký tự;
- chưa tuyên bố hỗ trợ tương tự cho chữ Tạng.

### 5.7. CLI hiện có

Launcher: `bin/buddhist-corpus`.

Các lệnh:

- `status`: kiểm tra nguồn và trạng thái index;
- `build`: build incremental;
- `search`: tìm kiếm có xếp hạng;
- `context`: lấy đoạn trước/sau;
- `work`: xem tác phẩm;
- `parallels`: xem quan hệ song hành/căn chỉnh;
- `resolve`: giải UID SuttaCentral hoặc định danh/range CBETA;
- `variants`: xem dị bản;
- `compare`: trả các nhân chứng riêng, không tự hòa hợp;
- `provenance`: xem hợp đồng nguồn của record;
- `evidence`: gói record, ngữ cảnh, provenance và dị bản;
- `export-remote`: export legacy có bản sao record;
- `export-remote-pointers`: export POC con trỏ không có `raw_text`.

Đầu ra chính là JSON trên stdout; tiến độ và lỗi đi ra stderr.

---

## 6. Tiến trình công việc theo commit

### Giai đoạn 1 — Tập hợp nguồn

#### `9c2d1c3` — Initialize Buddhist source corpus

Đã làm:

- thêm `.gitmodules`;
- ghim 13 repository thành submodule;
- tạo `manifest.json` ghi URL, thư mục, SHA, kích thước và trạng thái tải;
- viết README ban đầu.

Vì sao:

- cần giữ nguyên nguồn gốc và phiên bản cụ thể;
- tránh chép dữ liệu rồi mất lịch sử;
- cho phép kiểm tra tính toàn vẹn bằng SHA.

Kết quả:

- hình thành tầng raw bất biến;
- 13 nguồn có thể truy ngược.

### Giai đoạn 2 — Hệ nghiên cứu offline thống nhất

#### `bb41a4b` — Add offline Buddhist corpus research system

Đã làm:

- thêm `AGENTS.md` và research skill;
- khảo sát cấu trúc 13 corpus;
- thiết kế schema SQLite chung;
- viết parser cho từng nguồn;
- viết CLI, retrieval và ranking;
- thêm profile build;
- thêm test acceptance và normalization;
- viết tài liệu kiến trúc, CLI và khảo sát corpus.

Vì sao:

- trước đó không có index xuyên corpus;
- không có record schema và API truy xuất chung;
- cần dùng Python standard library và SQLite FTS5 để không tải dependency.

Kết quả:

- có pipeline local từ submodule tới SQLite;
- có tìm kiếm đa corpus với provenance;
- có các bảng riêng cho quan hệ, dị bản và lemma;
- dữ liệu sinh ra nằm ngoài nguồn gốc.

### Giai đoạn 3 — Cầu nối SuttaCentral–CBETA

#### `4ae460b` — Add SuttaCentral to CBETA identifier bridge

Đã làm:

- phân tích HTML Hán văn local của SuttaCentral;
- lấy `<article id>`, link CBETA rõ ràng và mốc dòng Taishō;
- thêm quan hệ:
  - `suttacentral_cbeta:work`;
  - `suttacentral_cbeta:line_range`;
- thêm lệnh `resolve`;
- thêm tài liệu và test.

Vì sao:

- quan hệ `an1.1-5 ↔ ea9.7` chỉ đưa tới UID Āgama;
- muốn trích văn bản Hán local phải có bước nối UID đó sang work/range CBETA;
- không được suy ID CBETA từ tên file nếu file không nói rõ.

Kết quả:

- luồng đúng trở thành:
  SuttaCentral parallel → bridge metadata → record CBETA riêng;
- bridge không bị trình bày như bằng chứng câu chữ.

Số liệu khảo sát local:

- 4.714 HTML mirror;
- 2.779 có UID, link CBETA rõ và mốc Taishō;
- 1.935 trường hợp không có định danh CBETA rõ bị để unresolved (chưa giải).

#### `20cc330` — Fix CBETA range resolution for granular records

Đã làm:

- resolver hỗ trợ cả record gộp `core` và record từng dòng `all`;
- ưu tiên `relation_ids` hợp lệ;
- fallback sang `segment_id` hợp lệ;
- bỏ giới hạn ngầm 5.000 record khi quét một work dài;
- thêm bộ test riêng cho resolver.

Vì sao:

- logic ban đầu hoạt động với chunk `core` nhưng có thể bỏ sót index `all`;
- CBETA có tác phẩm dài hơn 5.000 dòng.

Kết quả:

- cùng một range có thể giải đúng trên cả hai hình dạng index.

#### `9e056cf` — Reject reversed CBETA ranges

Đã làm:

- từ chối range có điểm đầu sau điểm cuối.

Vì sao:

- tránh biến input sai thành kết quả có vẻ hợp lệ;
- giữ nguyên nguyên tắc fail closed.

Kết quả:

- range đảo hoặc malformed (sai định dạng) trả không tìm thấy.

### Giai đoạn 4 — Cải thiện tìm Hán văn

#### `b084f0d` — Add CJK trigram substring retrieval

Đã làm:

- thêm bảng FTS5 trigram;
- thêm phiên bản chỉ mục tìm kiếm;
- thêm quá trình rebuild và báo trạng thái chỉ mục;
- hợp nhất ứng viên FTS Unicode và trigram;
- thêm test với đoạn CBETA dài.

Vì sao:

- `unicode61` không bảo đảm tìm chuỗi nằm giữa văn bản Hán dài;
- các cột chuẩn hóa của đoạn dài chủ ý để trống nhằm tiết kiệm dung lượng.

Kết quả:

- truy vấn như `我聞一時` tìm được trong record dài;
- không phải quét toàn bộ bảng.

### Giai đoạn 5 — Tách vai trò văn bản

#### `476e190` — Separate text roles and 84000 notes

Đã làm:

- thêm cột `text_role`;
- migration (chuyển đổi schema cũ) để gán vai trò hợp lý;
- tách note trong 84000 TEI khỏi phần dịch chính;
- thêm quan hệ `84000:note_of`;
- gán vai trò rõ cho Bilara, CBETA, 84000, OpenPecha, BuddhaNexus, PTS;
- thêm test riêng cho ghi chú và vai trò.

Vì sao:

- `evidence_class` không đủ để biết đoạn là kinh chính, bản dịch hay ghi chú;
- note của dịch giả từng có nguy cơ bị trộn vào `translation_main`.

Kết quả:

- phần dịch chính không còn chứa prose của note;
- note có record và provenance riêng;
- AI có thể ngăn việc trích chú thích như lời kinh.

### Giai đoạn 6 — GitHub Connector với full export

#### `de88e26` — Add GitHub connector research access

Đã làm:

- thêm `evidence` bundle;
- cho `search` tùy chọn trả context và provenance;
- viết `remote_export.py`;
- chia records, relations, variants thành JSONL shard;
- giữ context overlap giữa biên shard;
- thêm manifest và tài liệu cho agent remote;
- thêm test deterministic (xác định, lặp lại cho cùng kết quả).

Vì sao:

- AI dùng GitHub Connector không chạy được SQLite local;
- cần một dạng tĩnh mà Connector đọc được.

Kết quả:

- có export có thể duyệt bằng GitHub;
- nhưng mô hình này sao chép `raw_text`, tạo dữ liệu remote rất lớn.

#### `e701ddb` — Point connector access to remote corpus repository

Đã làm:

- thêm `config/remote-corpus.json`;
- tạo và đưa vào kiến trúc repository riêng:
  `quoctran-2608/BuddhismDocuments-for-AI-remote`;
- tách repository mã/kiến trúc chính
  `quoctran-2608/BuddhismDocuments-for-AI` khỏi repository chứa artefact remote.

Vì sao:

- không nên đưa hàng nghìn shard lớn vào repository mã chính;
- main repo phải là nơi chuẩn của kiến trúc, remote repo chỉ là artefact dẫn xuất.

Kết quả:

- Connector có file cấu hình để tìm chính xác:
  - repository: `quoctran-2608/BuddhismDocuments-for-AI-remote`;
  - branch: `main`;
  - root path hiện tại: `remote/pointer-poc`;
- repository mới trở thành tầng phân phối artefact cho Connector, không trở thành
  nguồn Phật học hoặc nguồn chuẩn thứ hai.

#### `a6af3dd` — Add deterministic remote corpus locator

Đã làm:

- tạo locator tĩnh, chia bucket theo hash;
- map term CJK, term Latin và identifier tới shard;
- thêm manifest locator.

Vì sao:

- nếu không có locator, Connector phải dựa vào GitHub Code Search;
- GitHub Code Search không bảo đảm index đầy đủ hoặc tức thời.

Kết quả:

- runtime có thể định tuyến truy vấn mà không phụ thuộc Code Search.

#### `eb747f9` — Prioritize remote shards with shared ranking

Đã làm:

- tách logic xếp hạng chung thành `score_record_match()`;
- dùng cùng logic cho search local và thứ tự shard remote;
- thêm score, match reason và tie-break ổn định.

Vì sao:

- không được tạo ranking thứ hai cho remote;
- candidate tốt phải được mở trước.

Kết quả:

- local và remote dùng cùng ngữ nghĩa xếp hạng cuối;
- locator routing vẫn không được tuyên bố là bản sao byte-for-byte của SQLite
  FTS/BM25.

#### `5b77413` — Clarify corpus-balanced connector research

Đã làm:

- cập nhật phương pháp chọn candidate theo loại câu hỏi;
- với nghiên cứu chủ đề/so sánh, nhóm pointer theo corpus và lấy mẫu từng corpus;
- giữ user scope (phạm vi người dùng yêu cầu).

Vì sao:

- một corpus lớn hoặc có điểm cao có thể chiếm hết 20–50 kết quả đầu;
- nghiên cứu đa truyền thống cần nhìn nhiều nguồn độc lập.

Kết quả:

- quick lookup vẫn ưu tiên top global;
- nghiên cứu so sánh dùng corpus-balanced selection (chọn cân bằng theo corpus).

### Giai đoạn 7 — Chuyển sang pointer-only POC

#### `3c1e94a` — Add GitHub source pointer export POC

Đã làm:

- thêm mapping `corpus → github_repository` trong
  `config/corpus-sources.json`;
- đổi `config/remote-corpus.json` sang `remote/pointer-poc`;
- thêm lệnh `export-remote-pointers`;
- viết `tools/corpus_research/pointer_export.py`;
- tạo con trỏ chứa repository, SHA, path, ID, vai trò, nhân chứng và điểm;
- thêm test không xuất `raw_text`;
- cập nhật tài liệu local/Connector;
- tạo POC ban đầu cho `anicca`, `無常`, `T02n0099`.

Vì sao:

- full export không phù hợp với khoảng 50 triệu record;
- không muốn duy trì bản sao corpus và bộ máy tìm kiếm thứ hai;
- Connector có thể mở trực tiếp file gốc ở commit đã ghim.

Kết quả:

- POC ban đầu chỉ khoảng **45 KiB**, gồm 7 file;
- ba file JSONL locator có tổng khoảng **27.252 byte**;
- mỗi query có 20 pointer, tổng 60 pointer;
- JSONL không chứa key hoặc nội dung `raw_text`;
- output được kiểm tra deterministic;
- remote repo local cache ghi nhận commit:
  `11bd1d8c670997440f7a27e16caca49c7e7f2c20`
  — `Add raw-text-free source pointer POC`.

#### `46b519a` — Balance pointer POC candidates by corpus

Đã làm:

- vẫn gọi `search()` hiện có cho term query và
  `score_record_match()` hiện có cho identifier query;
- lấy candidate riêng theo từng corpus;
- gộp các record cùng `(corpus, work_id, source_path)`, chỉ giữ record đứng đầu
  theo `record_rank_key()` hiện có;
- giữ tối đa `--limit` candidate khác work/file cho mỗi corpus;
- thêm `source_blob_sha` vào pointer;
- tạo lại POC cho 9 term/cụm từ và 2 identifier;
- thêm test cho reuse ranking, collapse duplicate, giữ corpus khác và blob SHA.

Vì sao:

- global top 20 có thể chỉ là nhiều đoạn của cùng một work/file hoặc cùng một
  corpus lớn;
- GitHub Connector cần mở đúng file đã ghim, nên Git blob SHA giúp kiểm chứng
  sâu hơn file nguồn mà không sao chép `raw_text`.

Kết quả:

- POC dùng lại ranking cũ, không có ranking/search engine mới;
- một corpus không thể lấn át toàn bộ danh sách chỉ vì có nhiều segment cùng
  work/file;
- mỗi pointer có `source_blob_sha` tính offline bằng:
  `git rev-parse <source_sha>:<source_path>`;
- POC hiện có 11 key, 523 pointer, 15 file, 302.273 byte;
- 523/523 `source_blob_sha` đã được đối chiếu với Git object local;
- output tái sinh deterministic, digest trước/sau giống nhau.

---

## 7. Trạng thái chỉ mục cục bộ

### 7.1. Vị trí và dung lượng

`derived/corpus.sqlite3` là symbolic link tới:

```text
/home/tran_quoc/.local/share/buddhist-corpus/corpus.sqlite3
```

Kích thước file đích ngày 25/09/2026:

```text
46.111.674.368 byte ≈ 42,94 GiB
```

Đây là artefact local, bị `.gitignore` bỏ qua và không phải source-of-truth.
Checkout mới sẽ không tự có file này hoặc đường dẫn home nói trên.

### 7.2. Dữ liệu theo `source_state`

| Corpus | Records | Relations | Variants | Lemmas | Parser state |
|---|---:|---:|---:|---:|---|
| `84000-rdf` | 0 | 12.393 | 0 | 0 | `2026-09-22.6` |
| `84000-tei` | 155.856 | 36.051 | 0 | 0 | `2026-09-23.1-note-roles` |
| `84000-tm` | 779.074 | 389.957 | 0 | 0 | `2026-09-22.6` |
| `buddhanexus-chinese` | 17.221.401 | 0 | 0 | 0 | `2026-09-22.6` |
| `buddhanexus-pali` | 2.067.130 | 0 | 0 | 0 | `2026-09-22.6` |
| `buddhanexus-sanskrit` | 3.588.841 | 0 | 0 | 0 | `2026-09-22.6` |
| `cbeta-bm` | 11.967.766 | 0 | 0 | 0 | `2026-09-22.6:full` |
| `cbeta-tei` | 12.615.232 | 0 | 1.056.173 | 0 | `2026-09-22.6` |
| `openpecha` | 442.330 | 163.986 | 0 | 0 | `2026-09-22.6` |
| `pali-canon-derived` | 0 | 0 | 307.076 | 50.560 | `2026-09-22.6` |
| `pts-archive` | 15.530 | 0 | 0 | 0 | `2026-09-22.6` |
| `suttacentral-bilara` | 1.175.563 | 0 | 19.921 | 0 | `2026-09-23.1-text-role:full` |
| `suttacentral-relations` | 0 | 430.436 | 0 | 0 | `2026-09-22.8-sc-cbeta-bridge` |
| **Tổng** | **50.028.723** | **1.032.823** | **1.383.170** | **50.560** | |

`MAX(records.id)` hiện là `50.236.808`, lớn hơn số record vì ID có khoảng trống
sau các lần xóa/rebuild nguồn.

Chỉ mục CJK:

- component: `text-search`;
- version: `2026-09-23.cjk-trigram-v1`;
- rebuild gần nhất: `2026-09-25T00:47:35.451559+00:00`;
- số record `lzh`/`zh` được ghi trong state: `41.855.049`.

### 7.3. Báo cáo build cũ

`derived/core-build-report.json` chỉ ghi một lần chạy `core` cũ, trong đó sáu
nguồn đều `unchanged`. Không dùng file này để kết luận DB hiện tại chỉ có profile
`core`: `source_state` của DB hiện hành cho thấy cả 13 corpus đã được build.

---

## 8. Trạng thái export remote

### 8.1. Legacy full-record export

Thư mục local:

```text
remote/corpus/
```

Trạng thái:

- khoảng **1,9 GiB**;
- **4.545 file**;
- manifest ghi:
  - 221.151 record;
  - 22.993 work;
  - 478.880 relation;
  - 311.618 variant;
- chỉ gồm sáu corpus thuộc lần export `core` cũ;
- có JSONL record chứa `raw_text`;
- có context overlap ở biên shard;
- có locator tĩnh.

Đây không phải full export của DB 50 triệu record hiện tại. Nó là artefact cũ từ
giai đoạn thử Connector bằng bản sao dữ liệu.

### 8.2. Pointer-only POC

Thư mục local:

```text
remote/pointer-poc/
```

Trạng thái POC hiện tại:

- **11 key**;
- **523 pointer**;
- khoảng **302.273 byte** (xấp xỉ 295 KiB);
- **15 file**;
- `raw_text_exported: false`;
- key:
  - `anicca`;
  - `dukkha`;
  - `jhāna`;
  - `nibbāna`;
  - `mahākassapa`;
  - `無常`;
  - `如是我聞`;
  - `苦`;
  - `空`;
  - `t02n0099`;
  - `t01n0001`;
- mỗi corpus giữ tối đa 20 pointer khác `(work_id, source_path)` cho mỗi key;
- locator chia bucket bằng hai ký tự hex đầu của SHA-256 trên normalized key.

Các trường pointer:

```text
rank
score
match_reasons
record_id
corpus
repository
source_sha
source_path
source_blob_sha
indexed_source_path
work_id
segment_id
sequence_no
evidence_class
text_role
witness
```

Lưu ý: README/manifest của POC có chữ `raw_text` để tuyên bố rằng không xuất
trường này. Điều cần kiểm tra là ba file JSONL locator: chúng không có key
`raw_text` và không có nội dung văn bản nguồn.

`source_blob_sha` là Git blob SHA của chính file `source_path` tại `source_sha`.
Exporter tính nó offline bằng `git rev-parse <source_sha>:<source_path>`; chỉ
ghi `null` khi Git object local không có. POC hiện tại có blob SHA cho toàn bộ
523 pointer.

### 8.3. Ví dụ đã xác minh

#### `anicca`

Pointer hạng 1:

```text
repository: suttacentral/bilara-data
source_sha: 0914c609e49215bb1473199929ee8a2996b423c4
source_path: root/pli/ms/abhidhamma/kv/kv11/kv11.4_root-pli-ms.json
work_id: kv11.4
segment_id: kv11.4:3.3
score: 275
match_reasons: exact, corpus-lemma
```

File local tương ứng tồn tại và có `anicca`.

#### `無常`

Pointer hạng 1:

```text
repository: cbeta-org/BM_u8
source_sha: 83bc009a6f3333fa2d61cb436ee6181b1335beb4
source_path: B/B09/new.txt
work_id: B09n0037
segment_id: B09n0037:0208a01
score: 195
match_reasons: exact
```

File local tương ứng tồn tại và có `無常`.

#### `T02n0099`

Pointer hạng 1:

```text
repository: cbeta-org/BM_u8
source_sha: 83bc009a6f3333fa2d61cb436ee6181b1335beb4
source_path: T/T02/new.txt
work_id: T02n0099
segment_id: T02n0099:0001a01
score: 195
match_reasons: exact
```

Đã xác minh file `cbeta/BM_u8/T/T02/new.txt` có các dòng của `T02n0099`, gồm
những đoạn có `無常`, ví dụ các mốc `0001a07`, `0001a10`, `0001a14`.

### 8.4. Trạng thái repository remote riêng

Hai repository do dự án quản lý cần được phân biệt rõ:

| Repository | Vai trò |
|---|---|
| `quoctran-2608/BuddhismDocuments-for-AI` | Repo chính: mã, tài liệu, cấu hình, test và 13 submodule |
| `quoctran-2608/BuddhismDocuments-for-AI-remote` | Repo mới: artefact tĩnh cho GitHub Connector |

`config/remote-corpus.json` trỏ tới:

```text
repository: quoctran-2608/BuddhismDocuments-for-AI-remote
branch: main
root_path: remote/pointer-poc
mode: pointer_poc
```

Cache Git local tại `.m/remote-corpus.git` ghi nhận:

- `main` và `origin/main` ở commit
  `0d5d2367e35b317151d1b31df48e4491b44acc0f`;
- commit này cập nhật POC thành 15 file, 11 key và 523 pointer.

Do quy tắc offline, hồ sơ này không gọi mạng để xác minh lại GitHub. Kết luận
trên dựa vào ref `origin/main` đã có trong cache local.

Quan trọng: cây HEAD của remote repo vẫn có:

- `remote/corpus/`: 4.545 file legacy;
- `remote/pointer-poc/`: 7 file mới.

Vì vậy “pointer-only” hiện mới là đường runtime được cấu hình và POC đã commit;
repository remote chưa được dọn bỏ full-record export cũ.

---

## 9. Kiểm thử và xác minh

Lệnh đã chạy ngày 25/09/2026:

```bash
PYTHONPATH=tools python3 -m unittest discover -s tests -v
```

Kết quả:

```text
Ran 41 tests in 12.646s
OK
```

Phạm vi test:

- tìm biến tố Pāli qua lemma corpus;
- tìm câu Hán và ưu tiên CBETA;
- quan hệ Nikāya–Āgama;
- bridge SuttaCentral–CBETA;
- range CBETA trên chunk `core` và record `all`;
- suffix chữ cái CBETA không phân biệt hoa/thường;
- từ chối range đảo, ID sai và locator sai;
- không cắt ở 5.000 dòng;
- tìm chuỗi con CJK bằng trigram;
- migration `text_role`;
- tách note 84000 và quan hệ với đoạn cha;
- evidence bundle gồm context, provenance và variants;
- full remote export deterministic;
- không ghi đè thư mục lạ;
- đọc được dữ liệu đã commit trong WAL;
- pointer POC deterministic;
- pointer POC không xuất `raw_text`;
- thứ tự pointer dùng ranking chung.
- exporter gọi `search()` cũ riêng theo corpus;
- duplicate cùng work/file bị collapse;
- corpus khác vẫn được giữ khi có candidate;
- `source_blob_sha` khớp file Git đã ghim.

Ngoài test tự động, đã xác minh:

- 13/13 SHA nguồn khớp manifest;
- ba pointer đầu đều mở được file local tương ứng;
- `T02n0099` dẫn đúng tới `cbeta-org/BM_u8`, SHA và path;
- ba JSONL locator không chứa token `raw_text`;
- nhánh hiện tại, `main` và `origin/main` cùng commit.

---

## 10. Các vấn đề đã gặp và cách xử lý

### 10.1. I/O chậm trên WSL/NTFS

Vấn đề:

- SQLite ghi nhiều lần trên `/mnt/e` rất chậm;
- Git/status hoặc `COUNT(*)` trên DB 43 GiB có thể vượt timeout.

Cách xử lý:

- build trên filesystem Linux tạm;
- checkpoint về thư mục đích;
- đặt DB chính ở
  `/home/tran_quoc/.local/share/buddhist-corpus/corpus.sqlite3`;
- dùng symbolic link từ `derived/corpus.sqlite3`;
- kiểm tra SHA từng submodule riêng thay vì phụ thuộc một lệnh `status` dài.

Ngày 25/09/2026, `bin/buddhist-corpus status` không hoàn thành trong 120 giây.
Đây là vấn đề hiệu năng vận hành, không phải bằng chứng source contract sai.

### 10.2. Export locator legacy từng lỗi filesystem chỉ đọc

Log `.m/locator-export.stderr` cho thấy một lần export cũ đã:

- copy snapshot SQLite;
- export xong records, relations, variants;
- index tới `1500/3004` shard;
- sau đó lỗi:

```text
[Errno 30] Read-only file system: 'buddhist-locator-probe.sqlite3'
```

Process ghi trong `.m/locator-export.pid` không còn chạy. POC pointer-only sau đó
đã được tạo thành công bằng đường khác và đã có test.

### 10.3. Full export không thể mở rộng tới 50 triệu record

Legacy export 221 nghìn record đã khoảng 1,9 GiB. Nếu sao chép toàn bộ hơn 50
triệu record, dung lượng và số file sẽ rất lớn. Vì vậy thiết kế mới chỉ xuất
pointer và buộc Connector mở file nguồn gốc.

### 10.4. Metadata không được biến thành văn bản

Bridge SuttaCentral–CBETA, RDF và parallel edges chỉ chứng minh quan hệ hoặc định
danh. Resolver luôn trả CBETA record riêng làm nhân chứng văn bản. Khi không
resolve được, hệ thống không tự sửa ID/range.

### 10.5. Ghi chú từng bị lẫn với nội dung chính

84000 TEI chứa note lồng trong đoạn. Parser hiện loại note khỏi
`translation_main`, tạo record `translation_note` riêng và liên kết bằng
`84000:note_of`.

---

## 11. Những việc chưa hoàn tất hoặc còn rủi ro

### 11.1. Chưa tạo pointer locator cho toàn bộ nhu cầu tìm kiếm

POC hiện có 11 key và 523 pointer. Nó vẫn không phải:

- export đủ mọi term;
- export đủ mọi identifier;
- chỉ mục tổng quát cho toàn bộ 50 triệu record;
- bằng chứng rằng mọi câu hỏi Connector đều có thể trả lời.

Nếu query không thuộc 11 key hoặc pointer không đủ để xác lập kết luận, phải báo:

**không đủ dữ liệu trong remote corpus export hiện tại**.

### 11.2. Legacy `remote/corpus` vẫn còn

Mặc dù config đã chuyển sang `remote/pointer-poc`, full-record export cũ vẫn tồn
tại trong remote repo. Nếu mục tiêu cuối là “không giữ bất kỳ bản sao raw_text
nào trên remote”, cần một thay đổi riêng để:

1. xác nhận không còn consumer (bên sử dụng) phụ thuộc legacy;
2. xóa `remote/corpus` khỏi remote repo;
3. cập nhật lịch sử hoặc chính sách lưu trữ nếu cần;
4. xác minh Connector chỉ đọc pointer path.

Không tự xóa khi chưa có yêu cầu rõ vì đây là thay đổi phá vỡ tương thích và có
thể tốn dung lượng/lịch sử Git.

### 11.3. Lệnh legacy vẫn còn trong CLI

`export-remote` vẫn có thể tạo shard chứa `raw_text`. Nó được giữ để tương thích
và để test kiến trúc cũ. Tài liệu đã ghi rõ không dùng nó cho pointer-only path.

Nếu muốn ngăn dùng nhầm, có thể cân nhắc:

- đánh dấu deprecated (không khuyến nghị, sẽ bỏ);
- yêu cầu cờ xác nhận rõ;
- chuyển test legacy sang module riêng;
- hoặc loại bỏ sau khi remote cũ được dọn.

### 11.4. DB local không portable

DB 43 GiB nằm trong home của máy hiện tại. AI mới trên máy khác phải:

- có sẵn DB tương ứng;
- hoặc build lại từ submodule;
- hoặc chỉ dùng acceptance DB cho test;
- tuyệt đối không commit DB vào Git.

### 11.5. `status` cần tối ưu

`status()` hiện thực hiện `COUNT(*)` trên các bảng lớn. Với DB 50 triệu record,
đây có thể là lý do timeout. Nên cân nhắc:

- dùng tổng trong `source_state` cho chế độ nhanh;
- thêm `status --deep` để đếm thật khi cần;
- thêm timeout hoặc hiển thị tiến độ;
- tách kiểm tra SHA nguồn khỏi kiểm kê DB.

### 11.6. README có số liệu lịch sử

Các số dung lượng/đĩa trống trong `README.md` là lúc clone nguồn ban đầu, không
phản ánh DB 43 GiB và export hiện tại. Không dùng “32,2 GB còn trống” như số liệu
live.

### 11.7. Nhánh scope chưa tích hợp

Có nhánh local:

```text
feat/connector-research-interface
```

Commit riêng:

```text
2d81345f40472686fd140a719f61b2b42881e486
Add configurable research scopes
```

Nó thêm:

- `config/scopes/all.json`;
- `config/scopes/nikaya-agama-vinaya.json`;
- `tools/corpus_research/scope.py`;
- `tests/test_scope.py`.

Commit này có parent là `476e190`, tức tách nhánh trước chuỗi thay đổi Connector
sau đó. Nó chưa nằm trong `main` và có thể xung đột nếu cherry-pick (lấy riêng
commit) trực tiếp. Cần review/rebase riêng; không được coi là chức năng hiện có
trên HEAD.

### 11.8. File chưa được Git theo dõi

Trước khi tạo tài liệu này, `git status` có:

```text
?? prompt.txt
```

`prompt.txt` chứa yêu cầu pointer-only gần nhất nhưng chưa thuộc commit. Không
được coi nó là tài liệu chuẩn đã phát hành nếu chưa quyết định commit.

Sau khi tạo hồ sơ này, `progress.md` cũng là file mới cho đến khi được commit.

### 11.9. Thư mục `.m`

`.m/` bị ignore và chứa:

- log phiên làm việc;
- lỗi/cảnh báo;
- cache repository remote;
- file kiểm tra GitHub Code Search;
- artefact chẩn đoán.

Nó không phải source-of-truth. Không commit `.m`; log có thể chứa metadata phiên
làm việc hoặc thông tin vận hành nhạy cảm.

---

## 12. Hướng dẫn cho AI tiếp nhận

### 12.1. Trình tự bắt buộc

1. Đọc `AGENTS.md`.
2. Đọc tài liệu này.
3. Đọc:
   - `docs/ARCHITECTURE.md`;
   - `docs/CLI.md`;
   - `docs/CORPUS_SURVEY.md`;
   - `docs/SC_CBETA_BRIDGE.md`;
   - `docs/REMOTE_AGENT.md`.
4. Không dùng mạng trong local mode.
5. Không sửa submodule.
6. Kiểm tra trạng thái Git và SHA nguồn.
7. Chạy test trước khi thay đổi.
8. Sau thay đổi, chạy lại toàn bộ test liên quan.

### 12.2. Lệnh kiểm tra cơ bản

```bash
# Test toàn bộ
PYTHONPATH=tools python3 -m unittest discover -s tests -v

# Kiểm tra trạng thái; có thể chậm trên DB lớn
bin/buddhist-corpus status

# Tìm kiếm local
bin/buddhist-corpus search "sutaṃ" --language pli
bin/buddhist-corpus search "如是我聞" --language lzh

# Gói bằng chứng
bin/buddhist-corpus evidence --record-id RECORD_ID --context 2

# Quan hệ và resolver
bin/buddhist-corpus parallels ea9.7
bin/buddhist-corpus resolve ea9.7
bin/buddhist-corpus resolve T02n0125:0563a14..0563a27

# POC pointer
bin/buddhist-corpus export-remote-pointers \
  --query anicca \
  --query dukkha \
  --query jhāna \
  --query nibbāna \
  --query Mahākassapa \
  --query 無常 \
  --query 如是我聞 \
  --query 苦 \
  --query 空 \
  --identifier T02n0099 \
  --identifier T01n0001 \
  --output remote/pointer-poc
```

### 12.3. Khi nghiên cứu bằng local CLI

Luồng đề nghị:

```text
search
→ xem match_reasons
→ context/evidence
→ provenance
→ parallels/resolve nếu cần
→ variants nếu cần
→ mở file raw để kiểm tra markup hoặc ngữ cảnh lớn
→ tổng hợp, giữ các nhân chứng riêng
```

### 12.4. Khi nghiên cứu bằng GitHub Connector

Luồng:

```text
đọc config/remote-corpus.json
→ mở manifest pointer POC
→ kiểm tra coverage thật
→ chuẩn hóa key và tính bucket
→ đọc JSONL pointer
→ chọn candidate theo loại câu hỏi và user scope
→ mở repository nguồn tại source_sha
→ mở source_path
→ dùng work_id/segment_id/sequence_no định vị đoạn
→ kiểm tra nội dung, ngữ cảnh, text_role, witness
→ mới được đưa ra kết luận
```

Pointer không phải bằng chứng. File nguồn đã ghim mới là nơi xác minh câu chữ.

### 12.5. Hợp đồng của một câu trả lời nghiên cứu

Mỗi phát hiện cần có:

```text
corpus
source_path
work_id
segment_id hoặc định danh tương đương
source_sha
evidence_class
text_role
witness
```

Phải tách:

- phát hiện và giả thuyết tìm kiếm;
- metadata và câu chữ;
- nguồn phát hiện và nguồn làm chứng;
- bản văn chính, bản dịch, bình luận và ghi chú;
- các nhân chứng khác nhau.

---

## 13. Đề xuất công việc tiếp theo

Theo thứ tự ưu tiên:

### Ưu tiên 1 — Quyết định chiến lược pointer toàn phần

Cần thiết kế rõ “pointer-only cho toàn bộ corpus” nghĩa là gì. Không thể đơn giản
precompute (tính trước) mọi cụm từ có thể có mà không làm locator phình lớn.

Các hướng cần đánh giá bằng số liệu:

1. Locator theo identifier đầy đủ + token/CJK n-gram có kiểm soát.
2. Chỉ locator tới file/work thay vì mọi record.
3. Chỉ mục phân tầng:
   corpus → file/work → vị trí.
4. Dùng manifest theo collection để thu hẹp trước.
5. Kết hợp pointer tĩnh với việc đọc file nguồn, nhưng không phụ thuộc GitHub
   Code Search.

Phải đo:

- số key;
- số pointer;
- kích thước Git;
- số file;
- độ chính xác candidate;
- thời gian Connector mở và xác minh;
- mức bao phủ theo corpus.

### Ưu tiên 2 — Tối ưu `status`

Tạo chế độ nhanh dựa trên `source_state` và tách deep count. Đây là vấn đề vận
hành đã quan sát thực tế.

### Ưu tiên 3 — Dọn legacy remote có kiểm soát

Sau khi pointer path đủ dùng:

- khóa hoặc deprecate `export-remote`;
- xóa full-record artefact khỏi HEAD remote;
- xác minh không còn `raw_text` trong pointer tree;
- cập nhật tài liệu và test migration.

### Ưu tiên 4 — Đánh giá nhánh research scopes

Review `2d81345`, viết lại trên HEAD hiện tại nếu ý tưởng còn cần, thay vì
cherry-pick mù từ parent cũ.

### Ưu tiên 5 — Cập nhật số liệu vận hành

Phân biệt rõ:

- kích thước nguồn gốc;
- kích thước DB dẫn xuất;
- kích thước export legacy;
- kích thước pointer POC;
- dung lượng đĩa live.

---

## 14. Bản đồ file quan trọng

| File/thư mục | Vai trò |
|---|---|
| `AGENTS.md` | Quy tắc nghiên cứu bắt buộc |
| `README.md` | Tổng quan nguồn và cách dùng |
| `manifest.json` | Hợp đồng 13 submodule và SHA |
| `.gitmodules` | URL/path của submodule |
| `config/corpus-sources.json` | Vai trò nguồn, profile và GitHub repository mapping |
| `config/remote-corpus.json` | Vị trí pointer POC remote |
| `schema/corpus-index.sql` | Schema SQLite |
| `bin/buddhist-corpus` | CLI launcher |
| `tools/corpus_research/index.py` | Parser, build, incremental state, FTS |
| `tools/corpus_research/model.py` | Chuẩn hóa và model Record/Work |
| `tools/corpus_research/retrieval.py` | Search, ranking, context, resolver, provenance |
| `tools/corpus_research/remote_export.py` | Full-record export legacy |
| `tools/corpus_research/pointer_export.py` | Pointer-only POC |
| `tests/` | 36 test hiện hành |
| `docs/ARCHITECTURE.md` | Kiến trúc |
| `docs/CLI.md` | Hướng dẫn CLI |
| `docs/CORPUS_SURVEY.md` | Khảo sát 13 nguồn |
| `docs/SC_CBETA_BRIDGE.md` | Cầu nối và giới hạn resolver |
| `docs/REMOTE_AGENT.md` | Quy trình GitHub Connector |
| `.codex/skills/buddhist-corpus-research/SKILL.md` | Quy trình nghiên cứu cho agent |
| `derived/` | DB/báo cáo dẫn xuất, không commit |
| `remote/corpus/` | Export legacy có raw text, không commit ở main repo |
| `remote/pointer-poc/` | POC con trỏ, không commit ở main repo |
| `.m/` | Log/cache vận hành, không commit |

---

## 15. Thuật ngữ

- **Repository / repo**: kho Git chứa mã nguồn hoặc dữ liệu.
- **Main repository / main repo**: kho chính chứa mã và kiến trúc chuẩn của dự án.
- **Remote repository / remote repo**: kho từ xa; trong dự án này còn chỉ kho
  riêng chứa artefact cho GitHub Connector.
- **Branch / nhánh**: dòng phát triển riêng trong Git.
- **Commit**: một mốc thay đổi đã được Git ghi lại.
- **`main`**: tên nhánh chính.
- **`origin/main`**: tham chiếu local tới trạng thái nhánh `main` của remote đã
  được biết ở lần đồng bộ gần nhất; không tự chứng minh trạng thái live trên mạng.
- **Checkout**: bản làm việc local của repository tại một nhánh hoặc commit.
- **Corpus**: tập hợp văn bản/dữ liệu có cùng nguồn hoặc mục đích.
- **Submodule**: repository Git con được ghim tại một commit.
- **SHA**: mã định danh commit Git.
- **Raw / dữ liệu thô**: dữ liệu nguồn giữ nguyên để đối chiếu.
- **Source-of-truth / nguồn chuẩn**: nơi được xem là căn cứ gốc; dữ liệu dẫn xuất
  không được thay thế nguồn chuẩn.
- **Local**: nằm và chạy trên máy hiện tại, không cần truy cập mạng.
- **Remote**: nằm ở kho hoặc môi trường từ xa.
- **Offline**: không dùng mạng.
- **CLI**: command-line interface, giao diện dòng lệnh.
- **API**: giao diện có hợp đồng đầu vào/đầu ra để phần mềm gọi.
- **SQLite**: cơ sở dữ liệu dạng file dùng làm chỉ mục local.
- **JSON**: định dạng dữ liệu có cấu trúc.
- **JSONL**: mỗi dòng là một đối tượng JSON, thuận tiện để chia và đọc tuần tự.
- **XML**: định dạng đánh dấu có cấu trúc.
- **Provenance**: thông tin xuất xứ để truy ngược bằng chứng.
- **Witness / nhân chứng**: bản chép, ấn bản hoặc nguồn văn bản cụ thể.
- **Record / bản ghi**: một đơn vị dữ liệu văn bản trong chỉ mục.
- **Work / tác phẩm**: đơn vị tác phẩm/kinh/luận được nhận diện bằng ID.
- **Relation / quan hệ**: liên kết metadata giữa tác phẩm, đoạn hoặc nhân chứng.
- **Variant / dị bản**: cách đọc khác nhau giữa các nhân chứng.
- **Lemma**: dạng từ gốc dùng để quy các biến thể ngữ pháp về cùng mục từ.
- **Morphology**: thông tin hình thái học/ngữ pháp của từ.
- **Metadata**: dữ liệu mô tả dữ liệu khác, như ID, tiêu đề hoặc quan hệ.
- **TEI**: chuẩn XML mô tả cấu trúc văn bản học thuật.
- **RDF**: định dạng biểu diễn dữ liệu quan hệ.
- **FTS**: full-text search, tìm kiếm toàn văn.
- **Trigram**: chuỗi ba ký tự liên tiếp dùng để lập chỉ mục chuỗi con.
- **CJK**: Chinese–Japanese–Korean; trong dự án chủ yếu liên quan tìm Hán văn.
- **Index / chỉ mục**: cấu trúc giúp tìm dữ liệu nhanh hơn.
- **Parser / bộ phân tích**: mã đọc định dạng nguồn và chuyển thành cấu trúc chung.
- **Profile / hồ sơ build**: nhóm nguồn và mức chi tiết được chọn cho một lần build.
- **Build / dựng dữ liệu**: quá trình tạo hoặc cập nhật chỉ mục dẫn xuất.
- **Migration / chuyển đổi**: thay đổi dữ liệu/schema cũ sang cấu trúc mới.
- **Schema / lược đồ**: định nghĩa bảng, cột, ràng buộc và chỉ mục của cơ sở dữ liệu.
- **Cache / bộ nhớ đệm**: dữ liệu tạm giúp tránh tính hoặc tải lại.
- **Workspace / vùng làm việc**: thư mục tạm dùng trong quá trình xử lý.
- **Runtime / thời gian chạy**: giai đoạn hệ thống phục vụ truy vấn người dùng.
- **Locator**: chỉ mục định tuyến query tới shard hoặc pointer.
- **Shard**: mảnh dữ liệu được chia thành file nhỏ.
- **Pointer**: con trỏ chứa thông tin để mở đúng file nguồn, không chứa toàn văn.
- **POC**: proof of concept, bản nhỏ chứng minh ý tưởng hoạt động.
- **Query / truy vấn**: từ, cụm từ hoặc ID người dùng muốn tìm.
- **Candidate / ứng viên**: kết quả tiềm năng cần được mở và kiểm chứng.
- **Ranking / xếp hạng**: cách sắp ứng viên theo mức ưu tiên.
- **Tie-break / phá hòa**: quy tắc sắp thứ tự khi các ứng viên có cùng điểm.
- **Fallback / phương án dự phòng**: cách xử lý thay thế khi cách chính không dùng
  được.
- **Malformed / sai định dạng**: dữ liệu không đúng cấu trúc được yêu cầu.
- **Dependency / phần phụ thuộc**: thư viện hoặc dịch vụ mà hệ thống cần để chạy.
- **Consumer / bên sử dụng**: chương trình, agent hoặc người đang dùng một đầu ra.
- **Deprecated / không còn khuyến nghị**: vẫn còn hoạt động nhưng dự kiến bị bỏ.
- **Precompute / tính trước**: tạo sẵn kết quả trước khi có truy vấn người dùng.
- **Test / kiểm thử**: phép kiểm tra tự động hoặc thủ công về hành vi hệ thống.
- **Acceptance test / kiểm thử chấp nhận**: kiểm thử luồng chính trên mẫu dữ liệu
  thật, nhỏ và cố định.
- **Deterministic output / đầu ra xác định**: cùng đầu vào và trạng thái thì sinh
  cùng nội dung và thứ tự.
- **Fail closed**: khi thiếu bằng chứng thì từ chối kết luận thay vì đoán.
- **Deterministic**: cùng input, DB, SHA và code thì sinh cùng output.
- **Incremental build**: chỉ build lại phần thay đổi.
- **User scope**: phạm vi corpus/tác phẩm do người dùng chỉ định.
- **Cross-corpus balancing**: chọn ứng viên cân bằng theo corpus khi nghiên cứu
  đa nguồn.
- **Cherry-pick**: lấy một commit riêng từ nhánh khác áp vào nhánh hiện tại.
- **Rebase**: đặt lại chuỗi commit lên một nền commit mới.
- **Symbolic link / liên kết tượng trưng**: đường dẫn trỏ tới file ở vị trí khác.
- **WAL**: write-ahead log, file nhật ký ghi trước của SQLite.
- **WSL**: môi trường Linux chạy trên Windows.
- **NTFS**: hệ thống file phổ biến của Windows.
- **Artefact / sản phẩm dẫn xuất**: file được sinh từ nguồn và mã, có thể tạo lại.
- **`raw_text`**: trường chứa toàn văn của một record trong chỉ mục/export cũ.

---

## 16. Kết luận bàn giao

Dự án đã vượt qua giai đoạn “kho dữ liệu thô” và hiện có một hệ nghiên cứu
offline, có provenance, có phân cấp bằng chứng và có kiểm thử. Các thay đổi lớn
đều nhằm giảm khả năng AI đưa ra kết luận không có căn cứ:

- ghim nguồn;
- tách loại bằng chứng và vai trò văn bản;
- giữ quan hệ riêng khỏi câu chữ;
- giải định danh bằng metadata rõ ràng;
- ưu tiên nguồn mạnh nhưng không hòa trộn nhân chứng;
- fail closed khi thiếu dữ liệu;
- dùng cùng một ranking cho local và remote;
- chuyển Connector từ sao chép văn bản sang mở file nguồn gốc.

Phần đã hoàn thành chắc chắn là **pointer-only POC cho 11 key**, cân bằng
candidate theo corpus và có `source_blob_sha`, cùng toàn bộ test liên quan. Phần
chưa hoàn thành là **một giải pháp pointer-only có độ bao
phủ rộng thay thế hoàn toàn legacy remote export**. AI tiếp nhận không được mô
tả POC hiện tại như một chỉ mục hoàn chỉnh của 13 nguồn.

---

## 17. Benchmark độ mở rộng pointer (25/09/2026)

Sau POC vòng 2, dự án không thiết kế lại kiến trúc mà đo đúng pipeline đã có:

```text
query thật từ SQLite
→ search()/score_record_match()/record_rank_key() hiện có
→ theo corpus
→ collapse (work_id, source_path)
→ pointer có source_blob_sha
```

Mã mới: `tools/corpus_research/pointer_benchmark.py`; CLI:

```text
bin/buddhist-corpus export-pointer-benchmark
```

Không có schema/index/ranking/vector DB/API mới. Benchmark tạo artefact riêng:

```text
remote/pointer-benchmark/
```

và không ghi đè `remote/pointer-poc/`.

### Lấy mẫu deterministic

- 200 key Latin/romanized: `lemmas.lemma`, lọc key có chữ cái và không có CJK;
- 200 key CJK: trigram có thật từ `records.raw_text` của một sample cố định 5.000
  record `lzh`/`zh`;
- 100 identifier: `records.work_id` từ sample cố định theo từng corpus;
- sau normalize, chọn theo thứ tự SHA-256 của
  `category + NUL + key`.

Lý do dùng ba nguồn này: chúng đã có trong index, không cần tạo vocabulary,
schema hoặc index mới. `benchmark-queries.json` ghi toàn bộ 500 key và nguồn
lấy mẫu để Connector kiểm tra.

### Kết quả benchmark thật

Lệnh chạy:

```text
bin/buddhist-corpus export-pointer-benchmark \
  --latin-keys 200 --cjk-keys 200 --identifier-keys 100 \
  --limit 20 --max-total-bytes 33554432 \
  --output remote/pointer-benchmark
```

Kết quả:

| Chỉ số | Toàn bộ | Latin/romanized | CJK | Identifier |
|---|---:|---:|---:|---:|
| Query | 500 | 200 | 200 | 100 |
| Pointer | 12.108 | 4.331 | 7.274 | 503 |
| Pointer/query trung bình | 24,216 | 21,655 | 36,370 | 5,030 |
| Median pointer/query | 10 | 12 | 43 | 6 |
| P95 pointer/query | 63 | 64 | 64 | 8 |
| Query không kết quả | 4 | 4 | 0 | 0 |
| Corpus/query trung bình | 2,836 | 3,040 | 3,140 | 1,820 |
| Bytes/query trung bình | 13.483 | 12.907 | 19.183 | 3.233 |
| Median bytes/query | 6.129 | 7.134 | 22.956 | 3.705 |
| P95 bytes/query | 34.987 | 37.719 | 33.884 | 4.967 |
| Max bytes/query | 67.461 | 67.461 | 42.118 | 5.238 |

Artefact:

- 368 file;
- 6.935.403 byte tổng;
- 6.741.307 byte locator;
- dưới ngưỡng an toàn 33.554.432 byte;
- 0 `raw_text` field;
- 0 duplicate `(query, corpus, work_id, source_path)`;
- 0 `source_blob_sha` null;
- 5.356 distinct `(corpus, work_id, source_path)` trên toàn bộ benchmark.

Thời gian generation đo được: 8 phút 36 giây; peak RSS (bộ nhớ tiến trình cao
nhất) khoảng 68.044 KiB.

Ước lượng tuyến tính thuần từ 6.935.403 byte / 500 key:

| Số key | Kích thước ước tính |
|---:|---:|
| 10.000 | 138.708.060 byte |
| 50.000 | 693.540.300 byte |
| 100.000 | 1.387.080.600 byte |

Đây chỉ là extrapolation (ngoại suy) tuyến tính từ benchmark; không phải quyết
định triển khai production locator.

Điểm bất thường cần nhớ:

- CJK tốn bytes/pointer nhiều hơn Latin vì có số pointer/query cao hơn.
- Benchmark hiện chỉ đo 500 key; nó không chứng minh coverage của toàn bộ
  vocabulary.

---

## 18. POC compact serialization (25/09/2026)

Mục tiêu của bước này chỉ là đo metadata pointer bị lặp giữa 500 query benchmark,
không chạy lại retrieval và không đổi pipeline:

```text
benchmark locator hiện có
→ pointer metadata dùng chung có pointer_id
→ locator reference giữ rank/score/match_reasons
→ tái dựng lại benchmark để kiểm chứng
```

Artefact mới, tách biệt:

```text
remote/pointer-compact-poc/
```

Commit artefact remote:

```text
4958530427681dd3845492cc54ff39316c8a7806
Add compact pointer serialization POC
```

### Format

`pointers/part-000001.jsonl` có một dòng cho mỗi metadata pointer đầy đủ và
`pointer_id` ổn định. `pointer_id` là SHA-256 của canonical JSON metadata.
Pointer table giữ `record_id`, corpus, repository, source SHA/blob SHA, path,
work/segment, sequence, evidence class, text role và witness.

Locator giữ:

```text
pointer_id
rank
score
match_reasons
```

Do `rank`, `score` và `match_reasons` có thể khác theo query, chúng không được
đưa vào pointer table dùng chung. Resolver compact trộn metadata từ table với
các trường ranking từ reference theo đúng thứ tự trong locator.

### Kiểm chứng tương đương

- 500/500 query giống benchmark;
- 12.108/12.108 pointer occurrence giống benchmark;
- candidate, thứ tự, score, `match_reasons`, metadata và `source_blob_sha` đều
  tái dựng giống hệt;
- 0 dangling `pointer_id`;
- 0 `raw_text`;
- output deterministic.

### Kết quả đo

| Chỉ số | Benchmark thường | Compact POC |
|---|---:|---:|
| Tổng byte | 6.935.403 | 8.783.402 |
| Số file | 368 | 369 |
| Pointer occurrence | 12.108 | 12.108 reference |
| Shared pointer metadata record | — | 12.010 |
| Bytes locator | 6.771.429 | 1.696.050 |
| Bytes pointer table | — | 6.981.715 |

Compact POC **tăng 26,6459% dung lượng**, nên không tiết kiệm đáng kể.

Lý do đo được, không phải suy đoán: metadata đầy đủ phải giữ `segment_id` và các
trường nguồn/nhân chứng. Trong 12.108 occurrence chỉ có 98 occurrence lặp cùng
metadata đầy đủ; có 12.010 pointer record riêng, và 97 record được dùng lại ít
nhất hai lần. Phần locator giảm mạnh, nhưng bảng pointer đầy đủ cộng thêm
`pointer_id` lớn hơn metadata lặp đã tiết kiệm.

Ước lượng tuyến tính từ compact POC (chỉ để so sánh, không làm production):

| Số key | Byte compact ước tính |
|---:|---:|
| 10.000 | 175.668.040 |
| 50.000 | 878.340.200 |
| 100.000 | 1.756.680.400 |

Kết luận của POC này: với định nghĩa pointer phải chứa full metadata tới mức
segment hiện tại, pointer-table/reference đơn giản không phải hướng giảm kích
thước. Dự án dừng tại phép đo này, không tự thiết kế thêm layer/nén/production
locator.

---

## 19. Phân tích lặp metadata source/file (25/09/2026)

Sau compact POC, dự án **không tạo format hay artefact mới**. Chỉ thêm lệnh
read-only:

```text
bin/buddhist-corpus analyze-pointer-repetition \
  --benchmark remote/pointer-benchmark
```

Lệnh chỉ đọc 500 query benchmark đã commit; không chạy SQLite retrieval, không
resample, không ghi `remote/`, không đổi ranking/candidate/source SHA.

### Kết quả group repetition

| Group | Identity | Unique | Duplicate occurrence | Dedup ratio | Avg reuse | Median | P95 | Max |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | `(repository, source_sha, source_path, source_blob_sha)` | 4.932 | 7.176 | 59,2666% | 2,4550 | 1 | 9 | 189 |
| B | A + `indexed_source_path` | 4.932 | 7.176 | 59,2666% | 2,4550 | 1 | 9 | 189 |
| C | `(corpus, work_id)` | 4.974 | 7.134 | 58,9197% | 2,4343 | 1 | 8 | 143 |
| D | source + work | 5.356 | 6.752 | 55,7648% | 2,2606 | 1 | 7 | 143 |
| E | Full static segment pointer | 12.010 | 98 | 0,8094% | 1,0082 | 1 | 1 | 3 |

Tổng pointer occurrence: **12.108**. A và B có cùng số unique trong benchmark
này, nhưng mô phỏng source table giữ cả `indexed_source_path` để bảo toàn đầy đủ
metadata pointer.

Top source/file reuse:

| Reuse | Repository | Source path |
|---:|---|---|
| 189 | `cbeta-org/BM_u8` | `T/T01/new.txt` |
| 142 | `cbeta-org/xml-p5` | `T/T01/T01n0001.xml` |
| 77 | `cbeta-org/BM_u8` | `B/B06/new.txt` |
| 55 | `bdhrs/pts-archive` | `texts/09-mn-i.txt` |
| 47 | `cbeta-org/BM_u8` | `T/T03/new.txt` |
| 45 | `bdhrs/pts-archive` | `texts/01-vin-i.txt` |
| 45 | `cbeta-org/BM_u8` | `T/T02/new.txt` |
| 39 | `cbeta-org/BM_u8` | `B/B08/new.txt` |
| 38 | `BuddhaNexus/segmented-pali` | `inputfiles_cut_segments_on_typography/atk-s0201a.json` |
| 37 | `cbeta-org/xml-p5` | `B/B15/B15n0088.xml` |

Lệnh JSON có đủ top 20; bảng này ghi top 10 để bàn giao dễ đọc.

### Byte contribution

Đếm byte UTF-8 của JSON field fragment theo dạng `"field":value` (không tính dấu
phẩy/ngoặc JSON):

| Nhóm field | Byte |
|---|---:|
| Source/file (`repository`, SHA, blob SHA, path, indexed path) | 3.415.280 |
| Work/segment (`record_id`, corpus, work/segment, sequence, evidence/text role, witness) | 2.472.763 |
| Query-specific (`rank`, `score`, `match_reasons`) | 598.180 |
| Tổng field fragment | 6.486.223 |
| JSON syntax ngoài field fragment | 217.944 |
| Tổng pointer object JSONL | 6.704.167 |

### Mô phỏng source table trong bộ nhớ

Mô phỏng dùng source ID ổn định 64-hex SHA-256 và giữ nguyên non-locator file
của benchmark. Đây chỉ là tính byte JSONL, không tạo serialization artefact.

| Biến thể | Tổng byte ước tính | Thay đổi so với 6.935.403 byte |
|---|---:|---:|
| A. Dedup source/file (bao gồm `indexed_source_path`) | 6.455.625 | giảm 6,9178% |
| B. Dedup source/file + work identity | 7.604.382 | tăng 9,6459% |

Biến thể A có 4.932 record source table; B có thêm 4.974 work record. Các số
này bảo toàn 12.108 occurrence và không đổi semantics theo định nghĩa mô phỏng.

Theo ngưỡng đã đặt trong prompt:

> **Không đáng để thêm một layer source table chỉ để tiết kiệm dung lượng.**

Lý do: giảm source/file-only là 6,9178%, thấp hơn 10%; thêm work table còn làm
tổng byte tăng. Không có production locator, source table, compression hoặc
layout repository mới được tạo từ kết quả này.
