---
name: Tokenize
depends_on: [bootstrap]
owns: [wordfreq/tokenize.py, tests/test_tokenize]
assignee: codex-1
---

# Tokenize

## Requirements
- `words(text) -> list[str]`: lowercase, then every maximal run of `a`–`z` (mission rule). Digits and punctuation
  separate words.

## Validation
`tests/test_tokenize.py`: apostrophes, digits, empty input, uppercase.

## Defaults
Non-ASCII letters are separators (logged in `decisions/tokenize-ascii.md`).
