"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use to explore the workspace, inspect directory structures, read instructions, "
                "README files, docstrings, log files, schema formats, or sample data, and report "
                "findings without modifying any files."
            ),
            "system_prompt": (
                "You are an exploratory research assistant. Your task is to investigate files, "
                "read documentation, inspect data samples, and identify root causes or relevant "
                "configurations. Report your findings clearly and accurately with exact file paths. "
                "Do NOT create, modify, or delete any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use to implement code fixes, write data processing or log analysis scripts, "
                "modify files, and execute verification commands or tests."
            ),
            "system_prompt": (
                "You are an implementation specialist. Your task is to write clean, correct code, "
                "edit files accurately, execute tests and verification scripts, and report the "
                "exact changes made along with test results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use to independently inspect output files, verify data formats and edge cases, "
                "check compliance with instructions and organizational rules, and validate test passes."
            ),
            "system_prompt": (
                "You are an independent quality reviewer. Your task is to inspect generated outputs, "
                "verify schema formats, check edge cases and rule compliance, and confirm that all "
                "checks pass. Report any issues found without modifying files."
            ),
        },
    ]

