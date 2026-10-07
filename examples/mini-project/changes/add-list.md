## What shipped
`add` and `list` (newest first), plus the `search` subcommand wired to search.
## Where it lives
`jotter/__main__.py`, `tests/test_cli.py`
## How to check it
`python3 -m unittest tests.test_cli`
## Gaps
No way to delete a note (not in the mission; would need a decision about append-only).
