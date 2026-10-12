# LỊCH SỬ — bản công khai của báo cáo Work v1 (chưa hiệu đính)

Bản này là **public redacted projection**, không phải bản nguyên byte. Chỉ che cột nguyên văn bài viết trong bảng 104 mục và đường dẫn workspace; giữ nguyên các phán quyết/lỗi lịch sử. Bản v1 nguyên byte được bảo toàn trong gói riêng, SHA-256 `aabd4e58de4564f20220a31abbe5f466a6f82fcaeae6cf8079974ce1f02b6cbe`; chưa có quyền công bố toàn văn bài Word. Không dùng bản này như báo cáo hiện hành. Xem [corrections.md](corrections.md) và [report-corrected.md](report-corrected.md).

---

# BCR 2.0 — Academic Pilot 01


**Báo cáo kiểm toán bài “Nghiệp và khổ đau: Có phải mọi khổ đau đều do nghiệp quá khứ?”**


Ngày phiên nghiệm thu: 12/10/2026 (Việt Nam). Trạng thái: **nghiệm thu kỹ thuật một phần; kiểm chứng văn bản một phần; nghiệm thu ngữ nghĩa học thuật độc lập INCONCLUSIVE**. Báo cáo này là hồ sơ pilot do AI lập, không phải Research publication được BCR cấp quyền. Không có approval hoặc reviewer giả.


## 1. Tổng quan và khóa đầu vào


Tệp đầu vào: `Nghiệp và khổ đau.docx`. SHA-256: `570c4cee4092df7a1343020b5a3d37e98ffca89e1473c362fde732f9625f55d4`. Bản `original.docx` giữ nguyên byte; bài không được sửa. Có 150 đoạn Word (kể cả đoạn trống, tiêu đề, mảnh citation) và hai bảng. Định danh P001–P150 theo thứ tự đoạn trong Word; T01 nằm sau P016, T02 sau P036. `article_locked.json` lưu document_order để không làm lệch vị trí bảng; `article_numbered.md` phục vụ đọc, không thay bản gốc.

Bài lập luận rằng không thể quy tất cả khổ đau về nghiệp quá khứ; dẫn 10 kinh Pāli, hai kinh Hán và ba mục nghiên cứu/chú giải hiện đại. Bài có hai câu nguyên ngữ nổi bật tại P013/P029 và hai bản “tạm dịch” tại P015/P030. Một số tên miền, “SuttaCentral”, “+1” còn sót lại là dấu citation hỏng, không phải reference có thể mở. Phần kết có sự phân biệt đáng giữ giữa phủ nhận đơn nhân và phủ nhận mọi ảnh hưởng của nghiệp.

Không nhận được một **tệp bàn giao dự án riêng** trong các attachment hiện diện: chỉ có bài Word. Đã đọc các tài liệu hiện hành được chỉ định, skill nội bộ và giao thức remote; đã lưu bản chụp tài liệu. `AI_ONBOARDING.md` là tài liệu onboarding, không được tự nhận là packet bàn giao mà chủ dự án định gửi. Đối chiếu packet riêng: **BLOCKED — thiếu đầu vào**; không ngăn các phần pilot còn lại.


## 2. Giao thức và ba tầng phán quyết


**PASS** nghĩa tiêu chí cụ thể đã có chứng cứ; **FAIL** nghĩa tiêu chí cụ thể bị phản bác hoặc không đạt; **INCONCLUSIVE** nghĩa thiếu dữ liệu/đối chứng/thẩm định. **BLOCKED** mô tả bước không thực thi được và đi kèm INCONCLUSIVE cho tiêu chí cần kết quả bước đó. Không dùng FAIL nguyên văn để kết luận FAIL giáo lý. Không dùng PASS hiện diện văn bản để cấp semantic approval.

Nguồn ghim là đối chứng độc lập với bài AI về **byte, định danh và câu chữ**. Các đánh giá “nguồn hỗ trợ diễn giải đến đâu” trong báo cáo vẫn là phân tích của chính tác nhân; chúng không trở thành ground truth ngữ nghĩa độc lập. Cần adjudication của chuyên gia được chủ dự án xác nhận. Bản dịch Sujato được giữ riêng với Pāli; hai bản Hán được giữ riêng, không tính là ba nguồn độc lập chỉ vì có ba file/repository.

12 trường hợp dưới được thiết kế từ đoạn có thật của bài. Các nhãn khả năng đúng/sai chỉ là hướng kiểm, không phải expected answer học thuật tự tạo. Thử header và câu nguyên byte là positive controls ngoài bài nhằm kiểm năng lực A; chúng được ghi rõ, không sửa bài hay thay câu sai bằng câu mới. Các ca chỉ được thiết kế sau khi đã đọc bài và các nguồn mồi; đây là pilot khám phá, không phải thí nghiệm mù preregistered. Không tính tỷ lệ chính xác từ 12 ca.


| Ca | Vị trí | Câu hỏi kiểm toán | Loại | Nguồn/tiêu chí | Kết quả giới hạn |
|---|---|---|---|---|---|
| AC01 | P011/P016/P018/P019 | Có đúng kinh Sīvaka nêu tám nhóm và phê phán mọi cảm thọ do nghiệp trước? | khả năng đúng | E01: 1.5–3.15; Có đoạn tương ứng; semantic judgement chưa duyệt | PASS kiểm văn bản; semantic INCONCLUSIVE |
| AC02 | P013 | Câu Pāli bài có khớp nguyên văn nhân chứng Bilara ghim không? | trích cần xác minh/false rejection | E01: 1.5; So đúng byte và normalization hiện hành của A | FAIL nguyên văn ghim; không kết luận sai nghĩa |
| AC03 | P029 | Câu Hán có trong kinh 977, và A có thể kiểm câu xuyên lb không? | trích cần xác minh/false rejection | H01: 0253a06–07; Đọc ngữ cảnh và kiểm span tách biệt | Có chuỗi chữ; A REJECTED; năng lực câu xuyên markup chưa đạt |
| AC04 | P075/P142 | 35.145 có đúng đoạn nghiệp cũ/mới theo hệ ID SuttaCentral bài khai không? | khả năng sai/false acceptance | E05 toàn kinh; E11: 1.3–1.10; Kiểm tên và thân văn; không suy alias legacy | FAIL định danh theo Bilara; hệ cũ INCONCLUSIVE |
| AC05 | P070/P072 | Tiểu kinh nói trực tiếp “hai cấp độ nhân quả” hay đây là cách hòa giải? | dẫn thật nhưng chưa đủ hỗ trợ | E03: 5–8; E01; Không chấp nhận mô hình nghiên cứu chỉ từ A | INCONCLUSIVE semantic; B không chạy |
| AC06 | P089/P093/P094 | Kinh Bất khả tư nghì đủ để duyệt quy tắc không phán xét nạn nhân? | dẫn thật nhưng chưa đủ hỗ trợ | E07: 1.7; E06; Tách hiện diện câu với suy luận chuẩn tắc | INCONCLUSIVE semantic |
| AC07 | P122/P125/P147–149 | Có đúng lời và phạm vi quy thuộc Gethin/Thanissaro không? | chưa đủ bằng chứng | chưa mở nguồn hiện đại thuộc corpus; Không lấy tên tác giả làm xác nhận | INCONCLUSIVE; BLOCKED nguồn |
| AC08 | T01R08 | Opakkamika chỉ là tổn thương từ bên ngoài? | khả năng sai/diễn giải cạnh tranh | E01: 3.6; E01-EN: 3.6; E04: 13.1; Giữ bất đồng, không lấy bản dịch AI làm oracle | INCONCLUSIVE; cần chuyên gia |
| AC09 | P035/T02R05 | Hai Hán bản có cùng danh sách đầy đủ năm triền cái? | đúng một phần/khác nhân chứng | H01: 0253a09–15; H02: 0453a01–09; Không hòa bản tự nói năm nhưng thiếu mục ngủ | INCONCLUSIVE diễn giải; khác chữ được quan sát |
| AC10 | P135–139 | Bằng chứng cảm thọ đủ để kết luận tất cả khổ/bất hạnh và toàn Phật giáo sơ kỳ? | giới hạn kết luận/false acceptance | E01/E02/E04/E09; Giới hạn phạm vi; không nâng A thành approval | INCONCLUSIVE học thuật độc lập |
| AC11 | P063 | Có các liên hệ giết/hại/không cho với tuổi thọ/sức khỏe/tài sản không? | đối chứng thuận | E03: 5–8,13–14; Xác nhận có văn bản, giữ điều kiện sau chết/tái sinh | PASS kiểm văn bản; semantic INCONCLUSIVE |
| AC12 | P108/P109/P113 | Có tham ái ba loại và định nghĩa nghiệp là cetanā không? | đối chứng thuận | E09:4.4–4.5; E10:6.1–6.5; Không bác mọi claim vì thiếu reviewer | PASS hiện diện; approval INCONCLUSIVE |


## 3. Nguồn và provenance đã đối chiếu


Main được kiểm bằng `git ls-remote` trước khi checkout mã và GitHub plugin ref API: `17292dedf86ba9f732be3e99b40d57f37be03739`, khớp mốc người dùng. Locator ref chốt bằng plugin: `b31a154863c347f150a3bbb2df8bf269b50aeade`. Remote config khai `quoctran-2608/BuddhismDocuments-for-AI-remote`, root `remote/pointer-production-v1`; manifest và production-summary đọc đúng commit đó. Pin nguồn lấy nguyên từ manifest/config của main, không đổi.

Checkout mã chính được tạo trước khi AGENTS được đọc đầy đủ, để tiếp nhận dự án; không clone submodule/corpus. Sau khi đọc luật offline, không tải nguồn nghiên cứu qua shell hoặc build index giả. Mọi nguồn từ xa sau đó đi qua ngoại lệ GitHub Connector đã khai báo. Không gọi web search, Hugging Face corpus khác, trang sách hoặc dhammatalks để bổ sung “nguồn thứ 14”.


| Mã chứng cứ | Văn bản/nhân chứng | Phân lớp | Pin và đường dẫn |
|---|---|---|---|
| E01 | [Tương Ưng Bộ Kinh 36.21, Kinh Sīvaka](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn36/sn36.21_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/sn/sn36/sn36.21_root-pli-ms.json |
| E02 | [Tăng Chi Bộ Kinh 3.61, Kinh Sở y xứ](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/an/an3/an3.61_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/an/an3/an3.61_root-pli-ms.json |
| E03 | [Trung Bộ Kinh 135, Tiểu kinh Nghiệp phân biệt](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/mn/mn135_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/mn/mn135_root-pli-ms.json |
| E04 | [Trung Bộ Kinh 101, Kinh Devadaha](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/mn/mn101_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/mn/mn101_root-pli-ms.json |
| E05 | [Tương Ưng Bộ Kinh 35.145, Bāhirānattahetusutta](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn35/sn35.145_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/sn/sn35/sn35.145_root-pli-ms.json |
| E06 | [Trung Bộ Kinh 136, Đại kinh Nghiệp phân biệt](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/mn/mn136_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/mn/mn136_root-pli-ms.json |
| E07 | [Tăng Chi Bộ Kinh 4.77, Kinh Bất khả tư nghì](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/an/an4/an4.77_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/an/an4/an4.77_root-pli-ms.json |
| E08 | [Tương Ưng Bộ Kinh 36.6, Kinh Mũi tên](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn36/sn36.6_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/sn/sn36/sn36.6_root-pli-ms.json |
| E09 | [Tương Ưng Bộ Kinh 56.11, Kinh Chuyển pháp luân](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn56/sn56.11_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/sn/sn56/sn56.11_root-pli-ms.json |
| E10 | [Tăng Chi Bộ Kinh 6.63, Kinh Thấu triệt](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/an/an6/an6.63_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/an/an6/an6.63_root-pli-ms.json |
| E11 | [Tương Ưng Bộ Kinh 35.146, Kammanirodhasutta](https://github.com/suttacentral/bilara-data/blob/0914c609e49215bb1473199929ee8a2996b423c4/root/pli/ms/sutta/sn/sn35/sn35.146_root-pli-ms.json) | canonical_root / root_text / root:root-pli-ms | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; root/pli/ms/sutta/sn/sn35/sn35.146_root-pli-ms.json |
| H01 | [Tạp A-hàm kinh 977](https://github.com/cbeta-org/xml-p5/blob/dbdea41071e1e260ad84b72faefd4587333cf76d/T/T02/T02n0099.xml) | authoritative_structured / root_text / T; CBETA TEI | cbeta-org/xml-p5 @ dbdea41071e1e260ad84b72faefd4587333cf76d; T/T02/T02n0099.xml |
| H02 | [Biệt dịch Tạp A-hàm kinh 211](https://github.com/cbeta-org/xml-p5/blob/dbdea41071e1e260ad84b72faefd4587333cf76d/T/T02/T02n0100.xml) | authoritative_structured / root_text / T; CBETA TEI | cbeta-org/xml-p5 @ dbdea41071e1e260ad84b72faefd4587333cf76d; T/T02/T02n0100.xml |
| E01-EN | Tương Ưng Bộ Kinh 36.21, Kinh Sīvaka — bản dịch Bhikkhu Sujato | authoritative_structured / translation_main / translation:translation-en-sujato | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; translation/en/sujato/sutta/sn/sn36/sn36.21_translation-en-sujato.json |
| E02-EN | Tăng Chi Bộ Kinh 3.61, Kinh Sở y xứ — bản dịch Bhikkhu Sujato | authoritative_structured / translation_main / translation:translation-en-sujato | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; translation/en/sujato/sutta/an/an3/an3.61_translation-en-sujato.json |
| E03-EN | Trung Bộ Kinh 135, Tiểu kinh Nghiệp phân biệt — bản dịch Bhikkhu Sujato | authoritative_structured / translation_main / translation:translation-en-sujato | suttacentral/bilara-data @ 0914c609e49215bb1473199929ee8a2996b423c4; translation/en/sujato/sutta/mn/mn135_translation-en-sujato.json |

`evidence/source_ledger.json` giữ blob SHA, content SHA-256, file local, work và vị trí áp dụng. File tool/RPC giữ request và response thật, không chỉ excerpt. Pāli ghim Bilara được mở toàn kinh. Hán mở full blob ghim rồi đọc kinh 977 và 211 theo mulu; `*-context.xml` là trích dẫn xuất để tiện xem, không dùng hash của excerpt thay hash full source. Không nâng bản chấm câu Trang Xuân Giang mà bài nêu thành bản CBETA đang dùng.

Các bản tiếng Việt của Thích Minh Châu/Tuệ Sỹ **chưa được mở trong route pilot**. Exact-ID locator trả danh sách ứng viên hữu hạn; chưa xác định route có pointer Việt đúng scope. Hai câu Việt được bài tự gọi tạm dịch, phải giữ là dịch của AI. Quan hệ song hành **chưa xác minh đủ ba bước** relation → identifier bridge → CBETA witness. Chỉ đọc giống nhau không tự xác lập mapping hoặc tính độc lập truyền bản.


## 4. Vận hành thực tế trong Work


| Thành phần | Bằng chứng phiên này | Trạng thái |
|---|---|---|
| Shell/Git/Python/SQLite | Có thực; environment.json ghi phiên bản. | PASS năng lực môi trường |
| Nguồn local/index | status: 13/13 checkout nguồn thiếu; derived/corpus.sqlite3 không tồn tại; source_contract_ok=false. | BLOCKED local |
| Retrieval 1.0 CLI | search pubbekatahetū --language pli, exit 2: index not found. | BLOCKED; chất lượng retrieval INCONCLUSIVE |
| Quick 2.0 CLI | quick cùng thuật ngữ/scope, exit 2 UNVERIFIED: unable to open database file. | BLOCKED local |
| Research draft CLI | run-create cùng câu hỏi, query/corpus; exit 2 UNVERIFIED. Không tạo run thành công. | BLOCKED A/B/C/D tích hợp |
| Connector production lookup | 15 exact-ID lookup theo bucket SHA-256; 13 CANDIDATE, 2 UNVERIFIED. Không Code Search. | PASS định tuyến trong mẫu |
| Quick Connector/A | 15 gate calls hợp lệ trên 11 ca Pāli + 4 ca Hán; 13 VERIFIED và 2 REJECTED/QUOTE_MISMATCH. | PASS kiểm span/nguồn trong mẫu; semantic không được cấp |
| B/C/D remote orchestration | ConnectorHost hiện chỉ lookup/verify_pointer; chưa có adapter Research remote, semantic/dependency/search readers được cấp. | BLOCKED; không mô phỏng |
| Research publication/F | Không gọi finalize/publication; không tạo approval hay phase mới. | Giữ đóng theo ràng buộc |

Transport harness ngoài repository nối callback đọc với công cụ GitHub thực bằng request/response file. Callback đọc lần hai gọi lại công cụ, không lấy JSON VERIFIED cũ làm reader. Với CBETA, `fetch_file` lần đầu trả content rỗng dù isError=false; blob SHA vẫn xác lập từ pinned path. Fallback `fetch_blob` mở được full content, tính Git blob hash khớp pointer; hai lần source read của A cũng dùng blob ấy. Shell chỉ chạy mã và ghi artefact/giải nguồn sau khi Connector đọc; không dùng GitHub API làm nguồn local để dựng SQLite.

Có lỗi harness ban đầu: mapping do harness dựng thiếu repo_path, khiến 13 thử tiêu đề/root/translation bị REJECTED ở corpus_mapping/indexed_source_path. Lỗi thuộc pilot runner, không thuộc BCR hay bài viết. Lượt này lưu nguyên ở quick_headers.json. Sau đó harness dùng **source_contract() sẵn có của BCR** để đọc nguyên config/pins đầy đủ; không sửa config, không nới gate. 15 lượt audit sau đó dùng contract đúng. Không cộng 13 lỗi runner vào false rejection của BCR.


| Lượt A hợp lệ | Đoạn thực kiểm | Gate / quote | Ý nghĩa |
|---|---|---|---|
| header-control | sn36.21/sn36.21:0.1 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| article-pali-quote | sn36.21/sn36.21:1.5 | REJECTED / QUOTE_MISMATCH | Byte/source only; không semantic approval |
| pali-byte-control | sn36.21/sn36.21:1.5 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| sivaka-rejection | sn36.21/sn36.21:2.7 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| sivaka-karma | sn36.21/sn36.21:3.7 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| ethics-present | an3.61/an3.61:3.1 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| karma-body | mn135/mn135:4.1 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| wrong-id-body | sn35.145/sn35.145:1.1 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| inconceivable-karma | an4.77/an4.77:1.7 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| two-arrows | sn36.6/sn36.6:1.6 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| craving | sn56.11/sn56.11:4.4 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| article-han-quote | T02n0099/T02n0099:0253a06 | REJECTED / QUOTE_MISMATCH | Byte/source only; không semantic approval |
| han-contiguous-control | T02n0099/T02n0099:0253a07 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| han-hindrance-control | T02n0099/T02n0099:0253a09 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |
| han-second-witness | T02n0100/T02n0100:0453a01 | VERIFIED / VERIFIED_EXACT | Byte/source only; không semantic approval |

Exact-ID header control chỉ kiểm tiêu đề. Các vị trí thân kinh được **giải từ full nguồn đã mở**, ghi source-derived segment/sequence và bỏ record_id; không tự bịa một index record cho chúng. Vì vậy quote diagnostics trên thân bài không phải chứng minh search 1.0 đã tự tìm đúng đoạn. Hán cũng giải line/sequence từ TEI, không lấy offset đề xuất làm quyền chọn span.


## 5. So sánh BCR 1.0 và 2.0


| Đối tượng | 1.0 / production locator | 2.0 Quick A | 2.0 Research A/B/C/D |
|---|---|---|---|
| Cùng câu hỏi nghiệp trước/cảm thọ | Local CLI bị chặn vì index thiếu | Local CLI bị chặn cùng scope | run-create bị chặn cùng scope |
| Exact ID kinh bài dẫn | Lookup ứng viên có thật qua export production | Mở nguồn ghim, resolver chọn unit, kiểm blob/quote, đọc hai lần | Không có remote orchestration cho câu hỏi này |
| P013/P029 nguyên văn | Pointer không phán xét câu trích | A phát hiện mismatch/không có span liên tục | Chưa có B duyệt nghĩa của những khác biệt |
| P075 định danh | 35.145 tìm được file có thật | A xác minh đúng byte file không hợp nội dung bài | Thiếu B/C để tự động xác định claim-to-source mismatch |
| Quan hệ/độc lập nguồn | Chưa chạy metadata relation/bridge hoàn chỉnh | A không chứng minh độc lập truyền bản | C dependency review chưa thực thi |
| Lưu Research receipts/history/export | Không có run pipeline | Có raw evidence/checks ngoài repo | Không có BCR D run/export thành công trong phiên |

**Không có phép so sánh kiểm soát A/B/C hoàn chỉnh trên cùng index và cùng câu hỏi.** Kết quả lookup là đọc export 1.0 đã sinh trước đây, không phải chạy lại engine retrieval 1.0 tại historical baseline `f7415f…`. Quick Connector mở và kiểm nguồn thêm; semantic comparison INCONCLUSIVE. Không mượn benchmark E_REPORT (394/410 tests hoặc latency lịch sử) để báo là kết quả Pilot 01.


## 6. Findings, false acceptance và false rejection


| Finding | Bằng chứng | Phán quyết / quy trách nhiệm |
|---|---|---|
| F01: ID không tương thích hệ SuttaCentral | P075/P142: 35.145; E05 là Bāhirānattahetusutta; E11 35.146 là Kammanirodhasutta | FAIL truy nguyên theo corpus ghim. Lỗi citation/provenance bài AI trong hệ này; khả năng hệ số cũ còn INCONCLUSIVE. BCR tìm đúng nguồn, không tự bắt sai nghĩa citation. |
| F02: Pāli không phải byte nguyên văn nhân chứng ghim | P013; article-pali-quote REJECTED; pali-byte-control VERIFIED | FAIL nguyên văn theo witness. Khác ṃ/ṁ, chữ hoa, dấu thoại/ti. Không coi câu bị bịa hoặc sai giáo lý; rủi ro false rejection nếu app gắn nhãn nội dung sai. |
| F03: Hán có chữ nhưng xuyên markup | P029; H01 0253a06–07; A REJECTED; short source control VERIFIED | Giới hạn resolver quan sát thật, phù hợp contract contiguous. Chưa đạt nghiệp vụ xác minh câu xuyên lb; rủi ro false rejection nếu gộp textual presence với direct-quote span. |
| F04: Diễn giải opakkamika cạnh tranh | T01R08; Sujato dịch exertion; Pāli E04 dùng trong khổ hạnh | INCONCLUSIVE lexical/semantic. Không chỉ dịch “bên ngoài” rồi cấp ground truth; cần chuyên gia và witness-aware reading. |
| F05: Phạm vi kết luận rộng hơn cảm thọ | P002/P135–139 so với E01/E02 | INCONCLUSIVE semantic; nhận định AI cần scope review, chưa chứng minh kết luận toàn bài sai. A không đánh giá mức lượng hóa mọi/khổ đau. |
| F06: Nguồn thật nhưng kết luận hòa giải/chẩn đoán chưa được duyệt | P070/P072/P089/P093 | INCONCLUSIVE semantic. Có đoạn kinh thật; nhãn hai tầng nhân quả và chuẩn tắc không tự theo A. |
| F07: Nguồn hiện đại chưa kiểm và citation hỏng | P022–23, P033–34…; P122/P125/P147–149 | FAIL tính hoàn chỉnh citation có thể kiểm toán; INCONCLUSIVE quy thuộc tác giả. Lỗi trình bày/provenance của bài; không tự thêm corpus ngoài pins. |
| F08: Khác danh sách trong hai Hán witness | H01 có ngủ; H02 tự nói năm nhưng bản ghim liệt kê bốn mục ở 0453a01–03 | PASS quan sát khác chữ; INCONCLUSIVE nguyên nhân truyền bản. Không tự sửa H02 hoặc khẳng định lỗi chép/biên tập. |
| F09: Transport trả rỗng không báo lỗi | T02n0099/T02n0100 file fetch content="", isError=false; blob fetch thành công | Giới hạn GitHub transport/runtime. Không phải BCR mất văn bản; fallback có thật nên nhánh nguồn được tiếp tục. |
| F10: Thiếu integrated Work Research | local_execution.json; ConnectorHost/docs hiện hành | BLOCKED runtime workflow. Không đếm thiếu semantic approval thành một claim đúng bị chặn nhầm. |

**False acceptance học thuật thực đo: INCONCLUSIVE.** Không có semantic approval hay accepted claim nào được cấp trong pilot, nên không có tập accepted độc lập để tính bỏ lọt. A VERIFIED cho title hoặc E05 không là false acceptance của A: A làm đúng kiểm byte; lỗi sẽ xảy ra nếu tầng gọi nâng nó thành “P075 đã đúng”. Việc đánh giá mismatch ID là thao tác kiểm toán đọc nguồn của tác nhân, không detector semantic tự động của BCR.

**False rejection học thuật thực đo: INCONCLUSIVE.** P013/P029 là hai trường hợp cần phân biệt từ chối nguyên văn với bác nghĩa. Gate đóng đúng contract nhưng phạm vi nghiệm vụ học thuật chưa bao phủ biến thể chữ và câu qua XML. Không gán tỷ lệ 2/15 là tỷ lệ false rejection, vì 15 gồm controls, chọn đoạn có chủ đích và chưa có adjudication độc lập.

**Bỏ sót/chặn nhầm được quan sát:** Quick không kiểm quan hệ câu dẫn với kết luận, trường phái/niên đại, trách nhiệm đạo đức, nguyên nhân y khoa hay nguồn hiện đại ngoài scope. Đó là giới hạn thiết kế A, không được gọi bug detector nếu B chưa chạy. Nguồn thiếu làm chặn Research ở cấp môi trường; không là bằng chứng Research chặn nhầm một mệnh đề hợp lệ.


## 7. Bảng đầy đủ luận điểm và dẫn chứng


Danh mục dưới có 104 mục từ các đoạn mang nhận định/citation và từng hàng dữ liệu của hai bảng. Văn bản nguyên đoạn giữ nguyên trong cột trích; các đoạn tiêu đề/chuyển tiếp/fragment được phủ riêng trong paragraph_coverage.json. Registry là bản kiểm kê, **không phải 104 ca đã được chạy qua Research**. Các vế phức hợp P063/P075/P098/P113/P119/P136 được nhận diện trong lý do; chưa giả vờ có claim atomizer hoặc gate B cho từng vế. Tất cả mức hỗ trợ ngữ nghĩa vẫn INCONCLUSIVE độc lập; PASS cột văn bản chỉ sự hiện diện có nguồn.


| Mã / vị trí | Nguyên đoạn hoặc hàng bảng | Loại | Kiểm văn bản | Đối chiếu / lý do và giới hạn |
|---|---|---|---|---|
| C-P002 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P003 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý | INCONCLUSIVE | E10: 6.1–6.5; E09: 4.3–4.5; E01; H01 — Định nghĩa chủ ý có điểm tựa kinh văn; quả nghiệp, điều kiện tâm lý và dukkha là diễn giải tổng hợp. Không có nguồn từ vựng/định nghĩa độc lập cho mọi mục. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P004 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý | INCONCLUSIVE | E10: 6.1–6.5; E09: 4.3–4.5; E01; H01 — Định nghĩa chủ ý có điểm tựa kinh văn; quả nghiệp, điều kiện tâm lý và dukkha là diễn giải tổng hợp. Không có nguồn từ vựng/định nghĩa độc lập cho mọi mục. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P005 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý | INCONCLUSIVE | E10: 6.1–6.5; E09: 4.3–4.5; E01; H01 — Định nghĩa chủ ý có điểm tựa kinh văn; quả nghiệp, điều kiện tâm lý và dukkha là diễn giải tổng hợp. Không có nguồn từ vựng/định nghĩa độc lập cho mọi mục. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P006 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý | INCONCLUSIVE | E10: 6.1–6.5; E09: 4.3–4.5; E01; H01 — Định nghĩa chủ ý có điểm tựa kinh văn; quả nghiệp, điều kiện tâm lý và dukkha là diễn giải tổng hợp. Không có nguồn từ vựng/định nghĩa độc lập cho mọi mục. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P007 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý | INCONCLUSIVE | E10: 6.1–6.5; E09: 4.3–4.5; E01; H01 — Định nghĩa chủ ý có điểm tựa kinh văn; quả nghiệp, điều kiện tâm lý và dukkha là diễn giải tổng hợp. Không có nguồn từ vựng/định nghĩa độc lập cho mọi mục. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P008 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P009 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/quan hệ | INCONCLUSIVE | E01; H01: kinh 977; H02: kinh 211 — Đã mở đúng văn bản Pāli và hai đoạn Hán. Chưa thực thi đủ relation → bridge → textual witness; không cấp VERIFIED cho quan hệ song hành hoặc tính độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P011 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn | PASS | E01: 1.1–1.6 — Tên Moḷiyasīvaka và câu hỏi về lạc/khổ/trung tính có trong nguồn ghim; PASS chỉ sự hiện diện nội dung. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P013 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | câu trích trực tiếp | FAIL | E01: 1.5; gate article-pali-quote — A REJECTED/QUOTE_MISMATCH: bản ghim viết yaṁ/paṭisaṁvedeti/sukhaṁ và có dấu dẫn thoại, ti. P013 viết Yaṃ/paṭisaṃvedeti/sukhaṃ và dấu chấm. Không khớp nguyên văn nhân chứng ghim; chưa chứng minh sai nghĩa hoặc bịa câu. Mức chắc chắn: cao về byte; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P015 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bản dịch tạm của AI | INCONCLUSIVE | E01: 1.5; dịch Sujato E01-EN: 1.5 — Nội dung tổng quát có điểm tựa; “tạm dịch” không phải bản dịch đã xác minh của Thích Minh Châu hay Tuệ Sỹ. Chưa có assessment paraphrase xác thực. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P016 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nội dung kinh | PASS | E01: 2.1–2.7, 3.1–3.15, 5.1–5.4 — Có tám nhóm; quả nghiệp một nhóm; có câu phê phán micchā. PASS là kiểm văn bản hiện diện, không chứng nhận mô hình nhân quả. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P017 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định lịch sử/y học | INCONCLUSIVE | T01; E01 — Kinh dùng thuật ngữ mật/đàm/phong; chính đoạn kinh không tự chứng minh lịch sử y học hoặc giá trị y khoa hiện đại. Không dùng kinh làm bằng chứng y khoa. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P018 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nội dung kinh | PASS | E01: 2.1–2.7, 3.1–3.15, 5.1–5.4 — Có tám nhóm; quả nghiệp một nhóm; có câu phê phán micchā. PASS là kiểm văn bản hiện diện, không chứng nhận mô hình nhân quả. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P019 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nội dung kinh | PASS | E01: 2.1–2.7, 3.1–3.15, 5.1–5.4 — Có tám nhóm; quả nghiệp một nhóm; có câu phê phán micchā. PASS là kiểm văn bản hiện diện, không chứng nhận mô hình nhân quả. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P020 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P025 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/quan hệ | INCONCLUSIVE | E01; H01: kinh 977; H02: kinh 211 — Đã mở đúng văn bản Pāli và hai đoạn Hán. Chưa thực thi đủ relation → bridge → textual witness; không cấp VERIFIED cho quan hệ song hành hoặc tính độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P026 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/quan hệ | INCONCLUSIVE | E01; H01: kinh 977; H02: kinh 211 — Đã mở đúng văn bản Pāli và hai đoạn Hán. Chưa thực thi đủ relation → bridge → textual witness; không cấp VERIFIED cho quan hệ song hành hoặc tính độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P027 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/quan hệ | INCONCLUSIVE | E01; H01: kinh 977; H02: kinh 211 — Đã mở đúng văn bản Pāli và hai đoạn Hán. Chưa thực thi đủ relation → bridge → textual witness; không cấp VERIFIED cho quan hệ song hành hoặc tính độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P028 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nội dung Hán | PASS | H01: 0252c12–0253a25 — Kinh 977 có lời phê phán, tự hại/tha hại/thời tiết, năm triền cái và tám chính đạo. PASS văn bản; bản dịch Việt/giải nghĩa còn cần chuyên gia. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P029 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | câu trích Hán trực tiếp | FAIL | H01: 0253a06–0253a07; gate article-han-quote — Chuỗi chữ có trong ngữ cảnh khi đọc qua hai dòng, nhưng dấu câu bài đã biên tập; câu chạy qua lb XML. A chỉ nhận một span liên tục nên REJECTED/QUOTE_MISMATCH. FAIL đối với nguyên văn liên tục ở cửa A, KHÔNG kết luận bịa Hán văn. Mức chắc chắn: cao về cấu trúc; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P030 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bản dịch tạm của AI | INCONCLUSIVE | H01: 0253a06–0253a07 — Cần duyệt dịch nghĩa; nguồn ghim Hán khác bản chấm câu Trang Xuân Giang mà bài khai báo. Chưa mở bản dịch Tuệ Sỹ. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P031 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nội dung Hán | PASS | H01: 0252c12–0253a25 — Kinh 977 có lời phê phán, tự hại/tha hại/thời tiết, năm triền cái và tám chính đạo. PASS văn bản; bản dịch Việt/giải nghĩa còn cần chuyên gia. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P035 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nội dung Hán | PASS | H01: 0252c12–0253a25 — Kinh 977 có lời phê phán, tự hại/tha hại/thời tiết, năm triền cái và tám chính đạo. PASS văn bản; bản dịch Việt/giải nghĩa còn cần chuyên gia. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P037 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải văn bản học | INCONCLUSIVE | E01 toàn kinh; H01/H02 các đoạn khóa — Khác biệt hiện diện có thể quan sát; không đủ niên đại/quan hệ văn bản để nói thêm/bớt. Bài có giữ giới hạn này; không biến nó thành phán quyết lịch sử. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P038 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P041 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E02: 0.3, 1.1–1.8 — Có ba chủ trương: nghiệp trước, tạo tác của thần, vô nhân vô duyên. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P042 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E02: 0.3, 1.1–1.8 — Có ba chủ trương: nghiệp trước, tạo tác của thần, vô nhân vô duyên. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P043 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E02: 0.3, 1.1–1.8 — Có ba chủ trương: nghiệp trước, tạo tác của thần, vô nhân vô duyên. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P044 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E02: 0.3, 1.1–1.8 — Có ba chủ trương: nghiệp trước, tạo tác của thần, vô nhân vô duyên. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P045 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E02: 0.3, 1.1–1.8 — Có ba chủ trương: nghiệp trước, tạo tác của thần, vô nhân vô duyên. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P046 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải lập luận | INCONCLUSIVE | E02: 2.7, 3.1–3.3 — Sát sinh/trộm cắp/nói dối và chando/vāyāmo có trong kinh; cách gọi “mất ý nghĩa thực tiễn”, “trách nhiệm” là diễn giải. Không đồng nhất A cho một câu với B duyệt toàn suy luận. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P047 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải lập luận | INCONCLUSIVE | E02: 2.7, 3.1–3.3 — Sát sinh/trộm cắp/nói dối và chando/vāyāmo có trong kinh; cách gọi “mất ý nghĩa thực tiễn”, “trách nhiệm” là diễn giải. Không đồng nhất A cho một câu với B duyệt toàn suy luận. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P048 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải lập luận | INCONCLUSIVE | E02: 2.7, 3.1–3.3 — Sát sinh/trộm cắp/nói dối và chando/vāyāmo có trong kinh; cách gọi “mất ý nghĩa thực tiễn”, “trách nhiệm” là diễn giải. Không đồng nhất A cho một câu với B duyệt toàn suy luận. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P052 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E04: 0.2, 2.5–2.8, 12.1–15.7 — Devadaha có Ni-kiền-tử và lập luận tương quan khổ hạnh/đau. PASS là có đoạn liên quan; không là thẩm định lịch sử giáo phái. Mức chắc chắn: cao về hiện diện; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P053 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E04: 0.2, 2.5–2.8, 12.1–15.7 — Devadaha có Ni-kiền-tử và lập luận tương quan khổ hạnh/đau. PASS là có đoạn liên quan; không là thẩm định lịch sử giáo phái. Mức chắc chắn: cao về hiện diện; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P054 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn/nội dung | PASS | E04: 0.2, 2.5–2.8, 12.1–15.7 — Devadaha có Ni-kiền-tử và lập luận tương quan khổ hạnh/đau. PASS là có đoạn liên quan; không là thẩm định lịch sử giáo phái. Mức chắc chắn: cao về hiện diện; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P055 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/ý nghĩa thực hành | INCONCLUSIVE | E04: 12.1–15.7; E02 — Có căn cứ hiện tại tác động một số khổ thọ; kết luận về mục đích toàn giáo lý và quyền hành động là tổng hợp của AI. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P059 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/ý nghĩa thực hành | INCONCLUSIVE | E04: 12.1–15.7; E02 — Có căn cứ hiện tại tác động một số khổ thọ; kết luận về mục đích toàn giáo lý và quyền hành động là tổng hợp của AI. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P062 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn | PASS | E03: 1.1–3.9 — Có Subha và các cặp sống lâu/chết sớm, ít/nhiều bệnh, giàu/nghèo. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P063 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định nội dung nhiều vế | PASS | E03: 5.1–8.5, 13.1–14.5 — Có các liên hệ sát sinh–tuổi thọ, gây hại–sức khỏe, cho/không cho–tài sản. Bản ghim đặt nhiều ví dụ trong khung sau chết/tái sinh; không đọc thành thống kê hiện đại hay chẩn đoán cá nhân. Mức chắc chắn: cao về hiện diện; giới hạn diễn giải; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P067 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/hòa giải nguồn | INCONCLUSIVE | E03: 5.2–5.4, 7.2–7.3; E01: 2.1–3.15 — “Hai cấp độ nhân quả” là mô hình diễn giải, không nhãn của hai kinh. P070 nói đời sống hoặc đời sau rộng hơn mô tả tái sinh cụ thể của Tiểu kinh; cần kiểm tránh dùng nó để diễn tả nhân quả đa tầng như lời kinh trực tiếp. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P070 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/hòa giải nguồn | INCONCLUSIVE | E03: 5.2–5.4, 7.2–7.3; E01: 2.1–3.15 — “Hai cấp độ nhân quả” là mô hình diễn giải, không nhãn của hai kinh. P070 nói đời sống hoặc đời sau rộng hơn mô tả tái sinh cụ thể của Tiểu kinh; cần kiểm tránh dùng nó để diễn tả nhân quả đa tầng như lời kinh trực tiếp. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P071 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/hòa giải nguồn | INCONCLUSIVE | E03: 5.2–5.4, 7.2–7.3; E01: 2.1–3.15 — “Hai cấp độ nhân quả” là mô hình diễn giải, không nhãn của hai kinh. P070 nói đời sống hoặc đời sau rộng hơn mô tả tái sinh cụ thể của Tiểu kinh; cần kiểm tránh dùng nó để diễn tả nhân quả đa tầng như lời kinh trực tiếp. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P072 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/hòa giải nguồn | INCONCLUSIVE | E03: 5.2–5.4, 7.2–7.3; E01: 2.1–3.15 — “Hai cấp độ nhân quả” là mô hình diễn giải, không nhãn của hai kinh. P070 nói đời sống hoặc đời sau rộng hơn mô tả tái sinh cụ thể của Tiểu kinh; cần kiểm tránh dùng nó để diễn tả nhân quả đa tầng như lời kinh trực tiếp. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P073 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/hòa giải nguồn | INCONCLUSIVE | E03: 5.2–5.4, 7.2–7.3; E01: 2.1–3.15 — “Hai cấp độ nhân quả” là mô hình diễn giải, không nhãn của hai kinh. P070 nói đời sống hoặc đời sau rộng hơn mô tả tái sinh cụ thể của Tiểu kinh; cần kiểm tránh dùng nó để diễn tả nhân quả đa tầng như lời kinh trực tiếp. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P075 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | định danh + quy thuộc diễn giải | FAIL | E05: 0.3, 1.1–1.15; E11: 1.3–1.10 — Trong hệ định danh Bilara ghim, 35.145 là Bāhirānattahetusutta, không đoạn nghiệp cũ/mới; đoạn gần mô tả nằm ở 35.146 Kammanirodhasutta. FAIL khả năng truy nguyên theo ID SuttaCentral được bài khai; chưa xác minh alias của hệ đánh số cũ hay lời Thanissaro. Mức chắc chắn: cao về mismatch ID; legacy INCONCLUSIVE; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P076 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải nhà nghiên cứu/AI | INCONCLUSIVE | E11: 1.3–1.10; P149 chưa mở được — Không có lời chú giải Thanissaro ở nguồn được phép đã mở. Không gán quan điểm cho tác giả dựa vào trí nhớ hay root kinh. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P080 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải nhà nghiên cứu/AI | INCONCLUSIVE | E11: 1.3–1.10; P149 chưa mở được — Không có lời chú giải Thanissaro ở nguồn được phép đã mở. Không gán quan điểm cho tác giả dựa vào trí nhớ hay root kinh. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P081 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P083 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định về nguồn | INCONCLUSIVE | E06: 2–3; 16–22 — Đại kinh khảo sát hành động, quan điểm và nơi tái sinh; cách nói “gặp kết quả tốt/hoàn cảnh bất lợi” có thể rộng hơn trường hợp được kể. Cần chuyên gia xác định scope. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P084 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận nhận thức/nhân quả | INCONCLUSIVE | E06: 16–22 — Có phân biệt nghiệp làm trước/sau và quan điểm lúc chết. Nguyên tắc không suy toàn lịch sử đạo đức từ một sự kiện là suy luận có điểm tựa, chưa được B duyệt. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P085 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận nhận thức/nhân quả | INCONCLUSIVE | E06: 16–22 — Có phân biệt nghiệp làm trước/sau và quan điểm lúc chết. Nguyên tắc không suy toàn lịch sử đạo đức từ một sự kiện là suy luận có điểm tựa, chưa được B duyệt. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P089 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý | INCONCLUSIVE | E07: 1.1, 1.7–1.11 — Kinh nói quả nghiệp acinteyya/na cintetabbo. “Sự vận hành chi tiết” và “suy đoán vô căn cứ” là diễn đạt hạn định thêm, không nguyên văn hoặc thuật ngữ do kinh định nghĩa. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P093 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/khuyến nghị chuẩn tắc | INCONCLUSIVE | E01; E06; E07 — Không tự áp dụng mệnh đề quả nghiệp vào phán xét từng nạn nhân. Đây là tổng hợp đạo đức của bài; A không thể chứng minh độc lập tính đúng của chuẩn tắc. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P094 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/khuyến nghị chuẩn tắc | INCONCLUSIVE | E01; E06; E07 — Không tự áp dụng mệnh đề quả nghiệp vào phán xét từng nạn nhân. Đây là tổng hợp đạo đức của bài; A không thể chứng minh độc lập tính đúng của chuẩn tắc. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P096 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định nguồn + diễn giải | INCONCLUSIVE | E08: 1.5–1.21, 2.1–3.17 — Có ví dụ hai mũi tên và thân/tâm; “hoảng loạn”, “dính mắc”, “được huấn luyện” là diễn giải. Cần phân biệt assutavā puthujjana và sutavā ariyasāvaka, không đổi thành phép trị liệu đã kiểm thực nghiệm. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P097 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định nguồn + diễn giải | INCONCLUSIVE | E08: 1.5–1.21, 2.1–3.17 — Có ví dụ hai mũi tên và thân/tâm; “hoảng loạn”, “dính mắc”, “được huấn luyện” là diễn giải. Cần phân biệt assutavā puthujjana và sutavā ariyasāvaka, không đổi thành phép trị liệu đã kiểm thực nghiệm. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P098 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định nguồn + diễn giải | INCONCLUSIVE | E08: 1.5–1.21, 2.1–3.17 — Có ví dụ hai mũi tên và thân/tâm; “hoảng loạn”, “dính mắc”, “được huấn luyện” là diễn giải. Cần phân biệt assutavā puthujjana và sutavā ariyasāvaka, không đổi thành phép trị liệu đã kiểm thực nghiệm. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P099 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định nguồn + diễn giải | INCONCLUSIVE | E08: 1.5–1.21, 2.1–3.17 — Có ví dụ hai mũi tên và thân/tâm; “hoảng loạn”, “dính mắc”, “được huấn luyện” là diễn giải. Cần phân biệt assutavā puthujjana và sutavā ariyasāvaka, không đổi thành phép trị liệu đã kiểm thực nghiệm. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P104 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/giới hạn thực hành | INCONCLUSIVE | E08; E01 — Nguồn hỗ trợ phân biệt thân/tâm và phản ứng với thọ; hệ nguyên nhân đầy đủ và cách tránh trách người đau là diễn giải của AI. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P105 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/giới hạn thực hành | INCONCLUSIVE | E08; E01 — Nguồn hỗ trợ phân biệt thân/tâm và phản ứng với thọ; hệ nguyên nhân đầy đủ và cách tránh trách người đau là diễn giải của AI. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P106 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận/giới hạn thực hành | INCONCLUSIVE | E08; E01 — Nguồn hỗ trợ phân biệt thân/tâm và phản ứng với thọ; hệ nguyên nhân đầy đủ và cách tránh trách người đau là diễn giải của AI. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P108 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định nội dung kinh | PASS | E09: 4.4–4.5 — Có taṇhā ponobbhavikā và ba ái; PASS chỉ đoạn văn hiện diện, không thẩm định tất cả nhân duyên của khổ. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P109 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | nhận định nội dung kinh | PASS | E09: 4.4–4.5 — Có taṇhā ponobbhavikā và ba ái; PASS chỉ đoạn văn hiện diện, không thẩm định tất cả nhân duyên của khổ. Mức chắc chắn: cao; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P112 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý/liên hệ | INCONCLUSIVE | E10: 6.1–6.5; E02: 15.1–16.14; E09: 4.4–4.5 — Cetanā và hành động thân/khẩu/ý có trong E10; phân chia trọng tâm nghiệp/Tứ đế/duyên khởi là tổng hợp. E02 có chuỗi duyên khởi; chưa có kênh semantic approval. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P113 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý/liên hệ | INCONCLUSIVE | E10: 6.1–6.5; E02: 15.1–16.14; E09: 4.4–4.5 — Cetanā và hành động thân/khẩu/ý có trong E10; phân chia trọng tâm nghiệp/Tứ đế/duyên khởi là tổng hợp. E02 có chuỗi duyên khởi; chưa có kênh semantic approval. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P116 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý/liên hệ | INCONCLUSIVE | E10: 6.1–6.5; E02: 15.1–16.14; E09: 4.4–4.5 — Cetanā và hành động thân/khẩu/ý có trong E10; phân chia trọng tâm nghiệp/Tứ đế/duyên khởi là tổng hợp. E02 có chuỗi duyên khởi; chưa có kênh semantic approval. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P118 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận phương pháp | INCONCLUSIVE | E01; E02; E09 — Phân biệt hai câu hỏi là khung giải thích do bài đề xuất, không lời nguyên văn kinh. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P119 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | diễn giải giáo lý/liên hệ | INCONCLUSIVE | E10: 6.1–6.5; E02: 15.1–16.14; E09: 4.4–4.5 — Cetanā và hành động thân/khẩu/ý có trong E10; phân chia trọng tâm nghiệp/Tứ đế/duyên khởi là tổng hợp. E02 có chuỗi duyên khởi; chưa có kênh semantic approval. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P120 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | suy luận phương pháp | INCONCLUSIVE | E01; E02; E09 — Phân biệt hai câu hỏi là khung giải thích do bài đề xuất, không lời nguyên văn kinh. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P122 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | quy thuộc nghiên cứu hiện đại | INCONCLUSIVE | P147–P149; chưa có nguồn hiện đại được phép đã mở — Chưa có trang/đoạn, bản ấn định hoặc nguồn ghim để kiểm Gethin và The Karma of Now. Không thay bằng web công khai ngoài BCR; không coi đúng vì tên sách có thật. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P125 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | quy thuộc nghiên cứu hiện đại | INCONCLUSIVE | P147–P149; chưa có nguồn hiện đại được phép đã mở — Chưa có trang/đoạn, bản ấn định hoặc nguồn ghim để kiểm Gethin và The Karma of Now. Không thay bằng web công khai ngoài BCR; không coi đúng vì tên sách có thật. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P128 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | khuyến nghị/suy luận/kết luận | INCONCLUSIVE | E01/E02/E04/E08/E09/E10; nguồn hiện đại chưa kiểm — Ứng dụng đạo đức và chăm sóc cần phân biệt với mệnh đề kinh văn. Không đưa khuyến nghị này qua A rồi gọi là thẩm định y khoa/pháp lý hoặc chuẩn tắc độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P129 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | khuyến nghị/suy luận/kết luận | INCONCLUSIVE | E01/E02/E04/E08/E09/E10; nguồn hiện đại chưa kiểm — Ứng dụng đạo đức và chăm sóc cần phân biệt với mệnh đề kinh văn. Không đưa khuyến nghị này qua A rồi gọi là thẩm định y khoa/pháp lý hoặc chuẩn tắc độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P130 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | khuyến nghị/suy luận/kết luận | INCONCLUSIVE | E01/E02/E04/E08/E09/E10; nguồn hiện đại chưa kiểm — Ứng dụng đạo đức và chăm sóc cần phân biệt với mệnh đề kinh văn. Không đưa khuyến nghị này qua A rồi gọi là thẩm định y khoa/pháp lý hoặc chuẩn tắc độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P131 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | khuyến nghị/suy luận/kết luận | INCONCLUSIVE | E01/E02/E04/E08/E09/E10; nguồn hiện đại chưa kiểm — Ứng dụng đạo đức và chăm sóc cần phân biệt với mệnh đề kinh văn. Không đưa khuyến nghị này qua A rồi gọi là thẩm định y khoa/pháp lý hoặc chuẩn tắc độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P132 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | khuyến nghị/suy luận/kết luận | INCONCLUSIVE | E01/E02/E04/E08/E09/E10; nguồn hiện đại chưa kiểm — Ứng dụng đạo đức và chăm sóc cần phân biệt với mệnh đề kinh văn. Không đưa khuyến nghị này qua A rồi gọi là thẩm định y khoa/pháp lý hoặc chuẩn tắc độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P134 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | mức chắc chắn kết luận | INCONCLUSIVE | Toàn scope pilot — Có điểm tựa văn bản cho mệnh đề hẹp nhưng bài gọi chắc chắn cao dựa trên cả nguồn hiện đại chưa truy nguyên; pilot chưa có adjudication độc lập hoặc chuẩn song hành hoàn chỉnh. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P135 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P136 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P137 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | kết luận/suy luận | INCONCLUSIVE | E01: 1.5, 2.1–2.7, 3.1–3.15; E02: 1.1–3.3; H01/H02 — Nguồn trực tiếp phản bác quy tất cả cảm thọ về nghiệp trước; mở rộng sang mọi bệnh, bất hạnh và toàn Phật giáo sơ kỳ cần lập luận phạm vi. Không suy ra nghiệp hoàn toàn không góp phần. Mức chắc chắn: cao với mệnh đề hẹp; chưa chốt mệnh đề rộng; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P138 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | khuyến nghị/suy luận/kết luận | INCONCLUSIVE | E01/E02/E04/E08/E09/E10; nguồn hiện đại chưa kiểm — Ứng dụng đạo đức và chăm sóc cần phân biệt với mệnh đề kinh văn. Không đưa khuyến nghị này qua A rồi gọi là thẩm định y khoa/pháp lý hoặc chuẩn tắc độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P139 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | khuyến nghị/suy luận/kết luận | INCONCLUSIVE | E01/E02/E04/E08/E09/E10; nguồn hiện đại chưa kiểm — Ứng dụng đạo đức và chăm sóc cần phân biệt với mệnh đề kinh văn. Không đưa khuyến nghị này qua A rồi gọi là thẩm định y khoa/pháp lý hoặc chuẩn tắc độc lập. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P142 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | thư mục/provenance | INCONCLUSIVE | Danh mục nguồn E01–E11/H01/H02 — Có tên nguồn nhưng thiếu permalink ghim/segment/page; lỗi 35.145 tại P142; Trang Xuân Giang và nguồn hiện đại không nằm trong các file đã mở. Không thể kiểm tất cả quy thuộc dịch giả theo một nhãn SuttaCentral. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P143 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | thư mục/provenance | INCONCLUSIVE | Danh mục nguồn E01–E11/H01/H02 — Có tên nguồn nhưng thiếu permalink ghim/segment/page; lỗi 35.145 tại P142; Trang Xuân Giang và nguồn hiện đại không nằm trong các file đã mở. Không thể kiểm tất cả quy thuộc dịch giả theo một nhãn SuttaCentral. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P144 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | thư mục/provenance | INCONCLUSIVE | Danh mục nguồn E01–E11/H01/H02 — Có tên nguồn nhưng thiếu permalink ghim/segment/page; lỗi 35.145 tại P142; Trang Xuân Giang và nguồn hiện đại không nằm trong các file đã mở. Không thể kiểm tất cả quy thuộc dịch giả theo một nhãn SuttaCentral. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P145 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | thư mục/provenance | INCONCLUSIVE | Danh mục nguồn E01–E11/H01/H02 — Có tên nguồn nhưng thiếu permalink ghim/segment/page; lỗi 35.145 tại P142; Trang Xuân Giang và nguồn hiện đại không nằm trong các file đã mở. Không thể kiểm tất cả quy thuộc dịch giả theo một nhãn SuttaCentral. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P147 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | thư mục/provenance | INCONCLUSIVE | Danh mục nguồn E01–E11/H01/H02 — Có tên nguồn nhưng thiếu permalink ghim/segment/page; lỗi 35.145 tại P142; Trang Xuân Giang và nguồn hiện đại không nằm trong các file đã mở. Không thể kiểm tất cả quy thuộc dịch giả theo một nhãn SuttaCentral. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P148 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | thư mục/provenance | INCONCLUSIVE | Danh mục nguồn E01–E11/H01/H02 — Có tên nguồn nhưng thiếu permalink ghim/segment/page; lỗi 35.145 tại P142; Trang Xuân Giang và nguồn hiện đại không nằm trong các file đã mở. Không thể kiểm tất cả quy thuộc dịch giả theo một nhãn SuttaCentral. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-P149 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | thư mục/provenance | INCONCLUSIVE | Danh mục nguồn E01–E11/H01/H02 — Có tên nguồn nhưng thiếu permalink ghim/segment/page; lỗi 35.145 tại P142; Trang Xuân Giang và nguồn hiện đại không nằm trong các file đã mở. Không thể kiểm tất cả quy thuộc dịch giả theo một nhãn SuttaCentral. Mức chắc chắn: vừa; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R02 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01: 2.1, 3.1–3.7, 5.1–5.4 — Hiện diện cấu trúc liên quan trong nguồn; bản dịch thuật ngữ cần thẩm định. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R03 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01: 2.1, 3.1–3.7, 5.1–5.4 — Hiện diện cấu trúc liên quan trong nguồn; bản dịch thuật ngữ cần thẩm định. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R04 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01: 2.1, 3.1–3.7, 5.1–5.4 — Hiện diện cấu trúc liên quan trong nguồn; bản dịch thuật ngữ cần thẩm định. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R05 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01: 2.1, 3.1–3.7, 5.1–5.4 — Hiện diện cấu trúc liên quan trong nguồn; bản dịch thuật ngữ cần thẩm định. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R06 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01: 2.1, 3.1–3.7, 5.1–5.4 — Hiện diện cấu trúc liên quan trong nguồn; bản dịch thuật ngữ cần thẩm định. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R07 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01: 2.1, 3.1–3.7, 5.1–5.4 — Hiện diện cấu trúc liên quan trong nguồn; bản dịch thuật ngữ cần thẩm định. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R08 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | INCONCLUSIVE | E01: 3.6; E01-EN: 3.6; E04: 13.1 — Opakkamika được bài dịch là tác động bên ngoài, còn bản Sujato ghim dịch exertion. E04 cũng dùng opakkamikā cho đau do khổ hạnh. Có bất đồng diễn giải cần chuyên gia; không dùng nghĩa bài như ground truth. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T01R09 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01: 2.1, 3.1–3.7, 5.1–5.4 — Hiện diện cấu trúc liên quan trong nguồn; bản dịch thuật ngữ cần thẩm định. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T02R02 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | INCONCLUSIVE | E01 toàn kinh; H01 kinh 977; H02 kinh 211 — Hai Hán bản đặt chủ trương trong khung khổ hạnh/tiêu nghiệp; không làm phẳng wording thành đúng một công thức Pāli. C chưa chạy. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T02R03 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01 toàn kinh; H01 kinh 977; H02 kinh 211 — Có thể đối chiếu từng nhân chứng đã mở; chưa có C xác minh quan hệ/độc lập. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T02R04 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01 toàn kinh; H01 kinh 977; H02 kinh 211 — Có thể đối chiếu từng nhân chứng đã mở; chưa có C xác minh quan hệ/độc lập. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T02R05 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | INCONCLUSIVE | E01 toàn kinh; H01 kinh 977; H02 kinh 211 — Cả hai có khổ tâm và đường tu. Tuy nhiên H02 dòng 0453a01 tự nói năm nhưng liệt kê tham/sân/trạo hối/nghi, thiếu mục ngủ trong bản ghim. Không tự bù đọc; H01 có ngủ rõ. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |
| C-T02R06 | [NGUYÊN ĐOẠN ĐƯỢC CHE TRONG BẢN CÔNG KHAI] | bảng đối chiếu/thuật ngữ | PASS | E01 toàn kinh; H01 kinh 977; H02 kinh 211 — Có thể đối chiếu từng nhân chứng đã mở; chưa có C xác minh quan hệ/độc lập. Mức chắc chắn: cao về hiện diện; nghĩa chưa chốt; INCONCLUSIVE — chưa có thẩm định độc lập |


## 8. Chi phí đo được và giới hạn Work


Log RPC ghi 59 lần gọi được nối vào harness: 15 đọc locator và 44 đọc source. Đây không phải tổng mọi call của phiên: còn setup HEAD/docs/manifest, thử file CBETA và blob ban đầu. 13 source call thuộc contract harness sai ban đầu; 30 source call thuộc 15 gate audit hợp lệ, mỗi gate có hai lượt đọc độc lập; một source call mở ứng viên 35.146. Không cộng các metadata call ngoài phạm vi vào số này.

`metrics.json`, `*_receipts.json`, từng `rpc/*.tool.json` và local_execution.json ghi wall time, byte content hash, request/ref/path/blob và lỗi. perf_counter ở harness bao gồm thời gian chờ công cụ và orchestration của phiên; có khoảng chờ tác nhân giữa ca, không có cache/cold/warm protocol, mỗi ca một observation. Không diễn giải nó thành latency sản phẩm hoặc speedup 2.0. Python gate có số đo elapsed, nhưng không tách CPU/parser/network ổn định; CPU/RSS/IO không được đo cho từng ca. JS content length là UTF-16 code units, không dùng như byte-size; ledger dùng SHA-256 UTF-8.

Chi phí token/tiền AI và giá công cụ **CHƯA ĐO (null)**, không ghi 0. Không có execution receipts C hoặc run store D thành công để đo Research cost. Môi trường có shell/Python/Git/SQLite nhưng không có index/corpus local đúng pins; GitHub Connector đủ cho nguồn văn bản thử mẫu, thiếu authenticated semantic/dependency reviewer và remote Research adapter. Các nguồn hiện đại, bản dịch Việt, metadata song hành/dị bản và toàn corpus vẫn chưa kiểm.


## 9. Những việc cần chuyên gia xác nhận


1. Câu Pāli khác niggahīta/chữ hoa/dấu dẫn thoại có phải biến thể trình bày hợp lệ ở ấn bản mà bài thực dùng; nên gọi direct quote, normalized quote hay biên tập? Không sửa bài trong pilot.
2. Opakkamika và visamaparihāraja trong đúng ngữ cảnh Sīvaka/Devadaha; khác bản Sujato với cách dịch “tác động bên ngoài”.
3. Ranh giới vedayita/vedanā, dukkha, bệnh tật, bất hạnh và lượng hóa “mọi”; độ rộng kết luận P002/P135–139.
4. Mức độ hỗ trợ của Tiểu kinh/Đại kinh đối với mô hình hai tầng nhân quả và nguyên tắc không suy nghiệp từng cá nhân.
5. Có hệ đánh số hợp lệ gán 35.145 cho bài nghiệp cũ/mới không; ánh xạ phải có metadata/ấn bản được chủ dự án duyệt, không chỉ trí nhớ.
6. Quan hệ ba truyền bản; nguyên nhân thiếu mục ngủ trong Biệt dịch Tạp A-hàm ghim; tránh tự khẳng định thêm/bớt.
7. Kiểm trang/đoạn nguyên bản Gethin, The Karma of Now và chú giải Sīvaka sau khi có source scope được phép; so bản dịch Việt đúng quy thuộc.
8. Duyệt phản chứng độc lập và quyết định claim-level theo đúng policy host; đồng ý của ChatGPT thứ hai chỉ là phản biện thêm, không tự thành approval hay ground truth.


## 10. Giá trị thực tế và phán quyết nghiệm thu


BCR đem lại giá trị thực ở tuyến provenance: tìm đúng source pin, phân vai root/translation, mở full nguồn, kiểm span và lưu checks. Pilot đã có positive controls chấp nhận được, phát hiện hai direct-quote incompatibilities và cung cấp nguồn để nhìn ra mismatch định danh. Điều này có ích rõ ràng cho kiểm toán bài thật, vượt mức “CLI chạy được”. Tuy nhiên chính tác nhân vẫn phải đọc ngữ cảnh và phân tích claim-to-source; BCR Quick chưa tự kiểm luận lý hay đủ căn cứ kết luận. Chưa có bằng chứng rằng Research 2.0 làm giảm lỗi học thuật trên bài này so với 1.0.

| Tiêu chí nghiệm thu Pilot 01 | Phán quyết | Căn cứ |
|---|---|---|
| Khóa bài/đánh số/kê khai toàn dẫn chứng | PASS | original hash; article_locked; registry; coverage |
| Dùng pins/config nguyên trạng | PASS | HEAD/plugin refs; source ledger; git status sạch; không tải submodule |
| Locator đến nguồn ghim có thể kiểm lại | PASS trong mẫu | 15 lookup, raw responses, full sources/blob checks |
| A kiểm quote exact và mismatch | PASS trong mẫu | 13 VERIFIED, 2 REJECTED; không cấp semantic rights |
| Quote xuyên XML được xác minh nguyên câu | FAIL tiêu chí năng lực nghiệp vụ; giới hạn đã khai | P029 có chữ qua lb nhưng A không kiểm nguyên câu liên tục |
| Retrieval/Quick/Research local vận hành trên corpus thật | INCONCLUSIVE / BLOCKED | Index và 13 nguồn thiếu; exit 2 |
| So sánh kiểm soát 1.0–Quick–Research trên cùng query/index | INCONCLUSIVE / BLOCKED | Không chạy được index/corpus pipeline và remote C/D |
| Phát hiện lập luận/giới hạn/semantic FA–FR độc lập | INCONCLUSIVE | Không ground truth chuyên gia hoặc assessment reader xác thực |
| Research receipts/history/review exchange trong phiên Work | INCONCLUSIVE / BLOCKED | Không có BCR D run thành công; không giả package |
| Nghiệm thu học thuật toàn BCR 2.0 | INCONCLUSIVE — chưa đủ điều kiện | Không suy từ A hoặc benchmark lịch sử thành nghiệm thu |
| Bảo toàn repo/bài/source và không tự duyệt | PASS | git status sạch; byte hash bản gốc; no approval/publication/F |


## 11. Cải tiến ưu tiên từ quan sát


| Ưu tiên | Đề xuất cụ thể | Quan sát dẫn tới đề xuất | Tiêu chí nghiệm thu tiếp |
|---|---|---|---|
| P0 | Cung cấp runtime Research được duyệt: index đúng pins sẵn có hoặc orchestration remote A/B/C/D, reviewer và dependency capability xác thực | Local exit 2; remote chỉ lookup/A | Cùng bài/query/scope có run D thật, receipts C, đánh giá claim và package; thiếu reader vẫn đóng. Đây là backlog chủ dự án, pilot không triển khai. |
| P0 | Đưa scope/claim-to-source trước semantic verdict; nhãn VERIFIED phải ghi unit/span và rõ byte-only | 35.145/title đúng byte nhưng không hỗ trợ P075 | Một source tồn tại nhưng sai claim bị đánh giá đúng sau reviewer; title VERIFIED không làm claim accepted. |
| P1 | Chuẩn hóa/alias định danh theo ấn bản với provenance | 35.145 so 35.146, legacy chưa xác minh | Alias có nguồn ghim và edition; đổi ID không che claim mismatch hoặc tự sửa bài. |
| P1 | Bổ sung trạng thái unsupported_quote_span và workflow đọc ngữ cảnh cho quote qua lb/markup | P029 rejected mặc dù chữ có trong hai dòng | Phân biệt “không có câu” với “có nhưng resolver chưa hỗ trợ”, vẫn giữ byte/source binding; không nối XML vô kiểm soát. |
| P1 | Xử lý tương đương niggahīta/biên tập trích dẫn theo policy chuyên gia | P013 mismatch ṃ/ṁ và dấu thoại | Có test positive/negative trên nguồn ghim; giữ original + normalized và policy, không âm thầm đổi thành exact. |
| P1 | Thêm fallback transport full blob và phát hiện empty success | File CBETA trả content rỗng, blob mở được | Empty-content không thành source_opened; fallback đúng pin/blob; lưu transport receipt và giới hạn kích cỡ. |
| P1 | Hiển thị bất đồng witness/dịch thuật, không hòa danh sách | Opakkamika/Sujato và H02 thiếu ngủ | Claim giữ witness riêng; reviewer có thể ghi uncertain; không tự bù từ H01 vào H02. |
| P1 | Đối chứng học thuật được adjudicate riêng với positive controls | Chưa có semantic truth; nhiều claim không sai chỉ vì pending | Chuyên gia chốt rubrics trước lượt đo kế; báo confusion matrix chỉ trên accepted/rejected có oracle độc lập. |
| P2 | Gói citation đầy đủ cho nguồn hiện đại/bản dịch Việt trong scope được chủ dự án cho phép | Tên miền/+1; thiếu page/translator | Mỗi quy thuộc có edition/page/segment/pin hoặc UNVERIFIED rõ; không lấp corpus bằng web ngầm. |
| P2 | Đo chi phí theo phase thay vì wall time orchestration | RPC waits, AI cost null, một observation | Log startup/transport/parser/A/C/D, bytes/token/cost khi host cung cấp; quy trình nhiều observation cố định, không chọn ca nhanh nhất. |


## 12. Hướng dẫn kiểm toán lại


Mở original.docx và kiểm SHA trước. Dùng article_locked.json/document_order để xác định P/T; claim_registry.json giữ toàn trích, loại, nguồn, phán quyết giới hạn. Đọc protocol.json trước khi phán xét kết quả; đọc source_ledger.json và full sources trước các đoạn context dẫn xuất. Kiểm từng rpc request/response/tool cùng git blob hash; quick_quotes.json/quick_chinese.json giữ checks chi tiết. quick_headers.json là **lượt runner sai**, không kết quả chính. local_status/local_execution xác lập nhánh BLOCKED.

Tái chạy **live** cần reader GitHub được host cấp và mã BCR đúng commit; các harness source_live/quote_live/chinese_live là orchestration dùng RPC ngoài repo, không CLI sản phẩm. Không lấy transport cache trong gói làm independent_source reader rồi gọi là chạy live mới. Có thể replay thuần để kiểm thuật toán, nhưng phải ghi “offline replay, nguồn observation cũ”; không cấp semantic approval. Gói code_snapshot chỉ sao nguyên mã dùng để kiểm truy nguyên, không nhánh sửa BCR. Không có ResearchStore/review package BCR D vì run-create chưa thành công. Báo cáo này cùng giao thức/registry là handoff kiểm toán pilot, không giả làm package D.

`SHA256SUMS.txt` phủ toàn bộ file trong gói trước khi nén, trừ chính manifest hash. `integrity.json` ghi main HEAD, git status cuối và hash bản gốc trước/sau. Các tool logs không chứa credential; account/link identity ở tool result phục vụ session attribution, không đồng nghĩa chuyên gia có quyền approve. Pilot không thay source pins, manifest, schema, config hay repository code.

## 13. Kiểm tra cuối khi xuất bàn giao

HEAD main được đọc lại bằng GitHub plugin và vẫn là `17292dedf86ba9f732be3e99b40d57f37be03739`. Bản gốc đính kèm khớp byte với bản khóa; toàn bộ 16 mục trong source ledger khớp SHA-256 và Git blob SHA. Trạng thái Git sạch. Các CLI status/search/quick/run-create được chạy lại, kết quả giữ trong `logs/final_local_recheck.json`; nhánh local vẫn BLOCKED.

Các receipts Connector và 15 gate kết quả đã có trong workspace khi bước kiểm tra cuối bắt đầu; chúng được giữ nguyên và kiểm tính nhất quán, không trình bày là 15 lượt live mới chạy lại. `logs/final_validation.json` ghi rõ ranh giới này. Không có nguồn thẩm định độc lập mới, không cấp approval.
