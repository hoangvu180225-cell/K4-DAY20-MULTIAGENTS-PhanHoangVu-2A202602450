---
name: robust-file-output-generation
description: Use when a data analysis or processing task requires outputting specific summary or cleaned files.
---
- Always verify the required output file paths (such as `answer.json`, `clean.csv`, or error summaries) and ensure they are successfully written to disk before finishing the task.
- When cleaning data records, strictly canonicalize categories, convert monetary values to integer cents to avoid floating-point inaccuracies, and handle missing or invalid sentinel values correctly.
- Ensure proper datetime parsing and normalization to UTC (e.g. `YYYY-MM-DDTHH:MM:SSZ`) for all timestamp fields.
