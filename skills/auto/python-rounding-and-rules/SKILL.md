---
name: python-rounding-and-rules
description: Use when implementing financial or precision arithmetic and strict code rules in Python packages.
---
- When rounding decimal numbers according to commercial rules (e.g. round half up), explicitly use `Decimal.ROUND_HALF_UP` with `quantize()`.
- Ensure all public functions (names not starting with `_`) have complete type annotations on all parameters and return values.
- Verify that original test files are never modified; always create new test files (e.g. `tests/test_regressions.py`) for bug fixes and regression tests.
- Record each bug fix in `CHANGELOG.md` under `## Unreleased` using the format `- fix(<function name>): <short description>`.
