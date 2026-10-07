# tokenize: Non-ASCII letters are separators

- Date: 2026-01-10   Decided by: codex-1   Feature: tokenize
- **Context:** the mission says "a–z"; `café` is ambiguous.
- **Options:** A) treat é as a separator; B) Unicode letters.
- **Choice:** A. It's exactly what the mission says, and the smaller change.
- **How to undo:** change the regex in `wordfreq/tokenize.py` to `[^\W\d_]+`.
