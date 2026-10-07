---
name: Rank with alphabetical ties
depends_on: [bootstrap]
owns: [wordfreq/rank.py, tests/test_rank]
assignee: claude-1
---

# Rank

## Requirements
- `ranked(counts, n) -> list[tuple[str, int]]`: highest count first, ties alphabetical, at most `n` items; `n <= 0`
  returns `[]`.

## Validation
`tests/test_rank.py` plus the golden test.
