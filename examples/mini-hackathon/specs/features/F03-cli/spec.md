---
id: F03
name: Command-line interface
lane: A
agent: codex-1
phase: 2
depends_on: [F01, F02]
owns: [wordfreq/__main__.py, tests/test_cli]
cut: ok
---

# F03 CLI

## Requirements
- `python3 -m wordfreq FILE [--top N]` (default 10) prints `word<TAB>count` lines. A missing file exits 1 with a
  message, never a traceback.

## Validation
`tests/test_cli.py` runs the module on a temp file.
