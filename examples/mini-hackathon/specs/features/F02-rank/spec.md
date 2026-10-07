---
id: F02
name: Rank with alphabetical ties
lane: A
agent: claude-1
phase: 1
depends_on: [F00]
owns: [wordfreq/rank.py, tests/test_rank]
cut: never
---

# F02 Rank

## Requirements
- `ranked(counts, n) -> list[tuple[str, int]]`: highest count first, ties alphabetical, at most `n` items; `n <= 0`
  returns `[]`.

## Validation
`tests/test_rank.py` plus the golden test.
