---
id: F00
name: Bootstrap - API contract, golden test, CI
lane: A
agent: claude-1
phase: 0
depends_on: []
owns: []
cut: never
bootstrap: true
---

# F00 Bootstrap

## Plan
1. `wordfreq/__init__.py`: the frozen public API, `count(text)` and `top(counts, n)`, delegating to F01/F02 modules.
2. `tests/golden/test_golden.py` from the worked example in `specs/context/worked-example.md`.
3. Placeholder modules for F01–F03 so the package imports.

## Validation
The golden test runs. It fails until F01 and F02 land, and that's expected.
