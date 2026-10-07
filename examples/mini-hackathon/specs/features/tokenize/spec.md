---
id: F01
name: Tokenize
lane: A
agent: codex-1
phase: 1
depends_on: [F00]
owns: [wordfreq/tokenize.py, tests/test_tokenize]
cut: never
---

# F01 Tokenize

## Requirements
- `words(text) -> list[str]`: lowercase, then every maximal run of `a`–`z` (mission rule). Digits and punctuation
  separate words.

## Validation
`tests/test_tokenize.py`: apostrophes, digits, empty input, uppercase.

## Defaults
Non-ASCII letters are separators (logged in `decisions/F01-ascii.md`).
