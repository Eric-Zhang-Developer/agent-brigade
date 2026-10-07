---
name: Bootstrap - API contract, golden test, CI
depends_on: []
owns: []
assignee: claude-1
bootstrap: true
---

# Bootstrap

## Plan
1. `wordfreq/__init__.py`: the frozen public API, `count(text)` and `top(counts, n)`, delegating to the tokenize and rank modules.
2. `tests/golden/test_golden.py` from the worked example in `specs/context/worked-example.md`.
3. Placeholder modules for tokenize, rank and cli so the package imports.

## Validation
The golden test runs. It fails until tokenize and rank land, and that's expected.
