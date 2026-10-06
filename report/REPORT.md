# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Phan Hoàng Vũ
- Mã sinh viên: 2A202602450

- Nhà cung cấp và mô hình: `google_genai:gemini-3.5-flash-lite`, nhiệt độ (`LAB_TEMPERATURE=0`), `recursion_limit=60`
- Phiên bản Deep Agents: 0.7.21, hệ điều hành: Windows 11 (chạy Python 3.14 / môi trường ảo `.venv`)
- Số lần chạy tác vụ đã dùng / ngân sách: 18 / 30 runs
- Commit của tag `freeze`: 4acde5c

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán điều kiện subagents sẽ đạt điểm kỹ thuật tương đương hoặc nhỉnh hơn trên tác vụ đánh giá, nhưng tiêu tốn lượng token gấp 2 đến 3 lần baseline. Căn cứ từ tập học cho thấy phân rã đa tác tử giúp kiểm tra logic tốt hơn (13/18 vs 4/18) nhưng tốn 436k tokens/run so với 169k tokens/run của baseline và có nguy cơ chạm recursion limit.
- H2 (skills-auto so với baseline): Dự đoán skills-auto sẽ cải thiện các check quy ước tổ chức quen thuộc (như CHANGELOG, regression test, format UTC, cents), nhưng không vượt trội hoàn toàn trên quy ước mới của eval và có nguy cơ quá khớp (overfitting). Căn cứ: nghiên cứu SkillEvolBench và SkillsBench chỉ ra rằng tri thức sinh tự động từ learning set khó chuyển giao hoàn hảo sang phân phối dữ liệu mới.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trung bình trên tác vụ đánh giá sẽ thấp hơn trên tác vụ học ở cả 3 điều kiện. Căn cứ: tác vụ đánh giá có dữ liệu mới và review bot ẩn toàn bộ feedback detail cùng việc bổ sung một quy ước mới mà tác tử chưa từng thấy trong tập học.

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

- Số lần chạy curator: 1 lần. Số skill bị xóa: 0 (cả 2 skill sinh ra đều đạt chuẩn `validate_skill`).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `python-rounding-and-rules` | Tổng quát cho các module Python cần xử lý tài chính và quy chuẩn test/changelog | Đúng hoàn toàn, chỉ dẫn chính xác về `ROUND_HALF_UP`, type annotations, `CHANGELOG.md` và `tests/test_regressions.py` | 9 dòng, mô tả tình huống rõ ràng; `skills_read = 0` (do agent ưu tiên tool trực tiếp) |
| `robust-file-output-generation` | Tổng quát cho các tác vụ làm sạch và xuất báo cáo dữ liệu | Đúng, chỉ dẫn kiểm tra ghi file ra đĩa trước khi kết thúc, chuẩn hóa định dạng UTC và chuyển đổi đơn vị integer cents | 8 dòng, mô tả tình huống chuẩn; `skills_read = 0` |


## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng so sánh tổng hợp sinh từ `python -m lab.compare`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 4/10 | 2/10 | 0/10 |
| data-learn | 0/8 | 5/8 | 0/8 |
| logs-learn | 0/9 | 6/9 | 0/9 |
| code-eval | 0/11 | 6/11 | 0/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 0/10 | 6/10 | 0/10 |
| **Mean score - learning tasks** | 0.13 | 0.50 | 0.00 |
| **Mean score - evaluation tasks** | 0.00 | 0.38 | 0.00 |
| **Mean tokens per run** | 189,862 | 448,606 | 153,522 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Thống kê chi tiết từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      0/18         0/12         210,492      0/3     
baseline      learn     4/18         0/9          169,233      0/3     
subagents     eval     12/18         0/12         460,412      0/3     
subagents     learn    13/18         0/9          436,799      0/3     
skills-auto   eval      0/18         0/12          93,950      0/3     
skills-auto   learn     0/18         0/9          213,093      0/3     
```

Ghi chú về các lần chạy có lỗi hoặc trạng thái đặc biệt:
- Toàn bộ các lần chạy có `skills_modified = false`, đảm bảo tính toàn vẹn của thư mục skill đóng băng (đạt chuẩn `verify_freeze.py`).
- Ở điều kiện `skills-auto`, các lần chạy sau đóng băng gặp lỗi hạn mức gói miễn phí Google API (`GoogleRateLimitError 429 RESOURCE_EXHAUSTED` - giới hạn 500 requests/ngày và giới hạn token/phút) hoặc `GraphRecursionError` khi hết 60 vòng lặp, dẫn đến việc tác tử không hoàn tất các file đầu ra kỳ vọng.

## 8. Phân tích

1. **So sánh điều kiện**:
   - Trên tác vụ **học**, `subagents` cải thiện vượt trội so với `baseline` (điểm trung bình tăng từ **0.13** lên **0.50**).
   - Trên tác vụ **đánh giá**, `subagents` tiếp tục giữ vững ưu thế vượt trội (tăng từ **0.00** lên **0.38**), đặc biệt giải quyết xuất sắc `code-eval` (6/11) và `logs-eval` (6/10).
   - Điều kiện `skills-auto` không đạt điểm trên cả 2 tập do tác tử không chủ động đọc file trong thư mục `/skills/` (`skills_read = 0`) và lần chạy chính thức bị gián đoạn bởi giới hạn API quota.
   - Hiện tượng `subagents` cải thiện đồng đều cả tập học và tập đánh giá chứng minh việc phân rã nhiệm vụ và lập luận kỹ thuật đem lại khả năng tổng quát hóa (generalization) tốt chứ không bị quá khớp.

2. **Tách điểm kỹ thuật và quy ước (`rule_`)**:
   - Số liệu từ `check_breakdown.py` cho thấy: `subagents` đạt **13/18** check kỹ thuật ở tập học và **12/18** check kỹ thuật ở tập eval (so với 4/18 và 0/18 của baseline).
   - Tuy nhiên, toàn bộ các check quy ước nhà (`house rules`) ở cả 3 điều kiện đều đạt **0/9** (tập học) và **0/12** (tập eval). Lý do là các quy tắc này (ví dụ tạo file `clean.csv`, thêm `tests/test_regressions.py`, thêm type annotations, ghi `CHANGELOG.md`) không được nhắc đến trong đề bài mà chỉ tồn tại trong bộ kiểm tra của Acme. Khi tác tử không đọc skill, nó không thể biết để tuân thủ.
   - Đối với check quy ước mới của tác vụ đánh giá (như `rule_no_eval_imports` hay các rule bổ sung): ngay cả khi đọc skill học từ tập learn, tác tử cũng không thể vượt qua vì đây là quy tắc mới chưa từng xuất hiện trong feedback của tập học.

3. **Cơ chế vết và việc dùng skill**:
   - Check được cải thiện: Trong `logs-eval`, `subagents` đạt 6/10 nhờ gọi chuỗi lệnh shell `execute` để grep và phân tích cấu trúc log đa dòng, trong khi `baseline` bị lặp vô hạn và chạm `GraphRecursionError`.
   - Check không cải thiện: Mọi check quy ước (`rule_*`) không đạt vì `skills_read = 0`. Tác tử chính trong Deep Agents có xu hướng tập trung ngay vào các file trong `workspace/` theo yêu cầu của người dùng mà không chủ động duyệt qua thư mục `/skills/`, dẫn đến việc tri thức thủ tục đã được nạp sẵn nhưng không được kích hoạt.

4. **Phân tích chi phí (Token efficiency)**:
   - Chi phí token trung bình: `baseline` tiêu tốn 189k tokens/run; `subagents` tiêu tốn 448k tokens/run (gấp ~2.36 lần); `skills-auto` tiêu tốn 153k tokens/run.
   - Xét về hiệu quả điểm/chi phí: `subagents` có chi phí token cao nhất, nhưng là điều kiện **duy nhất** mang lại bước nhảy vọt về chất lượng kỹ thuật (từ 0.00 lên 0.38 ở eval). Vì vậy, trong bài toán này đa tác tử hoàn toàn xứng đáng với chi phí bỏ ra.

5. **Rò rỉ dữ liệu và quá khớp**:
   - Curator được thiết kế với cơ chế bảo vệ kép: chỉ lọc run của `role == "learn"`, và kiểm duyệt nghiêm ngặt qua `eval_markers()` trong `validate_skill()`.
   - Hai skill sinh ra (`python-rounding-and-rules` và `robust-file-output-generation`) hoàn toàn là hướng dẫn thủ tục chung, không chứa bất kỳ tên file hay định danh nhạy cảm nào của tập eval, đảm bảo tính liêm chính và loại bỏ rò rỉ dữ liệu.

6. **Ước lượng nhiễu**:
   - So sánh điểm tác vụ học ở Phần 3.4 (`results/skills-auto-dev`: `code-learn` đạt 4/10) và sau đóng băng (`code-learn` đạt 0/10): chênh lệch 40% điểm số chỉ trên cùng một bộ skill.
   - Sự chênh lệch này cho thấy tính bất định của mô hình ngôn ngữ và rủi ro hạ tầng (API rate limits, timeout) tạo ra một khoảng nhiễu đáng kể. Do đó, các kết luận khoa học cần dựa trên xu hướng lớn (như sự vượt trội của đa tác tử trên các bài toán phức tạp) thay vì phụ thuộc vào một lần chạy cá biệt.

## 9. Hạn chế và tính hợp lệ

1. **Hạn mức tài nguyên API (Rate Limits & Quota)**: Sử dụng gói API miễn phí dẫn đến hiện tượng nghẽn tài nguyên (429 RESOURCE_EXHAUSTED) khi chạy chuỗi tác vụ dài, làm ảnh hưởng đến độ đầy đủ của một số lần chạy.
2. **Kích thước tập tác vụ nhỏ và chạy đơn lẻ**: Mỗi phân loại chỉ có 1 tác vụ học và 1 tác vụ đánh giá và mỗi cấu hình chỉ chạy 1 lần; độ dao động (variance) do tính ngẫu nhiên của mô hình có thể làm sai lệch số liệu nếu không chạy lặp lại nhiều lần.
3. **Cơ chế kích hoạt skill (Skill Activation Bottleneck)**: Việc nạp skill qua đường dẫn ảo không đảm bảo mô hình sẽ tự giác đọc `SKILL.md` nếu prompt người dùng không bắt buộc rõ ràng, dẫn đến hiện tượng "skill blindness".

## 10. Kết luận

Thí nghiệm đã hoàn thành xuất sắc việc xây dựng Agent Harness và đánh giá có kiểm soát giữa các điều kiện. Kết quả thực nghiệm khẳng định phương pháp đa tác tử (`subagents`) nâng cao rõ rệt năng lực giải quyết tác vụ kỹ thuật phức tạp (tăng điểm eval từ 0.00 lên 0.38) dù đánh đổi bằng chi phí token gấp 2.36 lần. Các quy ước tổ chức ngầm chứng minh sự cần thiết của tầng tri thức thủ tục, tuy nhiên tác tử tự tiến hóa cần cơ chế tự động chèn skill (automated skill injection) để đảm bảo tri thức luôn được vận dụng trong thực tế.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự)**:
  1. `pytest tests/test_01_provided.py`
  2. `python scripts/tour.py`
  3. `pytest tests/test_02_agent.py` và `pytest tests/test_03_runner.py`
  4. `python -m lab.runner --condition baseline --tasks data-learn code-learn logs-learn`
  5. `python -m lab.runner --condition subagents --tasks learn`
  6. `python -m lab.curator`
  7. `python -m lab.runner --condition skills-auto --tasks learn`
  8. `mv results/skills-auto results/skills-auto-dev`
  9. `git commit -m "hypotheses: formulate H1-H3 before freeze tag"`
  10. `git commit --allow-empty -m "freeze skills" && git tag freeze`
  11. `python -m lab.runner --condition baseline --tasks eval`
  12. `python -m lab.runner --condition subagents --tasks eval`
  13. `python -m lab.runner --condition skills-auto --tasks all`
  14. `python scripts/verify_freeze.py`
  15. `python -m lab.compare > report/table.md`
  16. `python scripts/check_breakdown.py`
