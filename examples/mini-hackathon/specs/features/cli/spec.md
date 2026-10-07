---
name: Command-line interface
depends_on: [tokenize, rank]
owns: [wordfreq/__main__.py, tests/test_cli]
assignee: codex-1
---

# CLI

## Requirements
- `python3 -m wordfreq FILE [--top N]` (default 10) prints `word<TAB>count` lines. A missing file exits 1 with a
  message, never a traceback.

## Validation
`tests/test_cli.py` runs the module on a temp file.
