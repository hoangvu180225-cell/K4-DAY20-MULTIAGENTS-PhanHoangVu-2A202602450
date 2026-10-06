# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Phan Hoàng Vũ
- Mã sinh viên: 2A202602450

- Nhà cung cấp và mô hình: `google_genai:gemini-3.5-flash-lite`, nhiệt độ (`LAB_TEMPERATURE=0`), `recursion_limit=60`
- Phiên bản Deep Agents: 0.7.21, hệ điều hành: Windows 11 (chạy Python 3.14 / môi trường ảo `.venv`)
- Số lần chạy tác vụ đã dùng / ngân sách: 6 / 30 runs
- Commit của tag `freeze`: (chờ cập nhật ở Phần 4)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline):
- H2 (skills-auto so với baseline):
- H3 (tác vụ học so với tác vụ đánh giá):

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: 7 công cụ tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), 1 công cụ shell (`execute`), và 1 công cụ giao việc cho subagent (`task`). Công cụ duy nhất cho phép chạy lệnh shell là `execute`.
2. Mô tả của công cụ `task` nêu rằng subagent `general-purpose` dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp/nội dung, và thực thi các tác vụ nhiều bước; nó có quyền truy cập mọi công cụ như tác tử chính. Về ngữ cảnh, mỗi lần gọi subagent là phi trạng thái (stateless by default): subagent chỉ nhìn thấy prompt được tác tử chính truyền vào trong lời gọi, không nhìn thấy lịch sử hội thoại trước đó của tác tử chính.
3. Hướng dẫn hành vi trích từ:
   - Mô tả của công cụ `task`: *"Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."*
   - Mô tả của công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | A (Bỏ qua đặc tả) | `the original files in tests/ must not be modified (new test files are allowed)` |
| `code-learn` | `discount_rounds_half_up` | B (Không kiểm chứng) | `wrong for: [('10.05', 10, '9.05'), ('19.99', 15, '16.99'), ('0.05', 50, '0.03'), ('2.665', 0, '2.67')]` |
| `code-learn` | `rule_type_hints` | E (Vi phạm quy ước tổ chức) | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| `code-learn` | `rule_regression_tests` | E (Vi phạm quy ước tổ chức) | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| `code-learn` | `rule_changelog` | E (Vi phạm quy ước tổ chức) | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| `data-learn` | `rule_clean_csv` | E (Vi phạm quy ước tổ chức) | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer cents.` |
| `data-learn` | `rule_money_in_cents` | E (Vi phạm quy ước tổ chức) | `detail: FileNotFoundError: ... answer.json` (do rule yêu cầu đơn vị cents chưa được ghi nhận trong đề) |
| `logs-learn` | `rule_meta_block` | E (Vi phạm quy ước tổ chức) | Check có tên bắt đầu bằng `rule_`: yêu cầu khối `meta` trong JSON nhưng đề không yêu cầu |

Nhận xét: 
- Nhóm lỗi chiếm đa số: **Nhóm E (Vi phạm quy ước tổ chức)** chiếm tuyệt đại đa số lỗi. Thống kê từ `scripts/check_breakdown.py` xác nhận: ở điều kiện baseline, tác tử đạt **4/18** check kỹ thuật nhưng đạt **0/9** check quy ước nhà (`rule_*`). Ở điều kiện subagents, số check kỹ thuật tăng lên **13/18** nhưng check quy ước vẫn giữ nguyên **0/9**.
- Bằng chứng phủ định cho các nhóm A-D: Các hàm logic cốt lõi như `parse_price_all_formats`, `low_stock_follows_docstring`, `csv_quoting_follows_docstring` đều đạt. Tác tử có năng lực lập trình và phân tích tốt, nhưng không thể đoán trước các quy ước ngầm của tổ chức Acme nếu không được cung cấp hướng dẫn.
- Khả năng phòng ngừa của Skill: Một procedural skill do curator sinh ra từ feedback `RULE:` hoàn toàn có thể phòng ngừa triệt để nhóm lỗi E thông qua checklist các file bắt buộc (`clean.csv`, `CHANGELOG.md`, `tests/test_regressions.py`) và quy cách định dạng.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  + `explorer`: Chuyên khảo sát cấu trúc workspace, đọc tài liệu docstring, README, xem mẫu dữ liệu mà không chỉnh sửa file, giúp tác tử chính hiểu bối cảnh trước khi sửa.
  + `implementer`: Chuyên thực thi sửa đổi mã nguồn, làm sạch dữ liệu, xử lý logs và chạy test xác nhận kết quả.
  + `reviewer`: Chuyên rà soát độc lập các file đầu ra, đối chiếu định dạng và kiểm tra các quy chuẩn trước khi kết thúc tác vụ.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  + Cả 3 tác vụ học đều ghi nhận `subagent_calls = 0`.
  + Nhận xét: Tác tử chính Deep Agents tự quyết định luồng hành động dựa trên `SUBAGENTS_NOTE`. Với các tác vụ trong một sandbox thư mục cục bộ, tác tử chính thấy đủ khả năng trực tiếp dùng các công cụ tệp (`read_file`, `write_file`) và shell (`execute`) nên chọn không phân nhánh giao việc cho subagent nhằm tiết kiệm bước chuyển ngữ cảnh.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): Không phát sinh lời giao việc do `subagent_calls = 0`.
- Ảnh hưởng đến token và thời gian:
  + Token trung bình: `baseline` tiêu tốn trung bình 169,233 tokens/tác vụ; `subagents` tiêu tốn trung bình 436,799 tokens/tác vụ (tăng gấp ~2.58 lần do ngữ cảnh prompt lớn hơn khi định nghĩa các subagent).
  + Tuy nhiên, về mặt hiệu quả kỹ thuật, `subagents` đã giúp nâng số check kỹ thuật đạt từ 4/18 lên 13/18 (theo `scripts/check_breakdown.py`).


## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| | | | |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Bạn đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
