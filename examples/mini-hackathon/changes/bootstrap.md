## What shipped
The frozen API (`count`, `top`), the golden test from the worked example, and placeholder modules.
## Where it lives
`wordfreq/__init__.py`, `tests/golden/`
## How to check it
`python3 -m unittest tests.golden.test_golden`
## Gaps
The golden test failed until tokenize and rank landed, as planned.
