## What shipped
`docs/stability.md`: the 1.x promise (D13), every public surface read from the code with the file that defines it,
what is not promised, the rough edges carried into 1.0, and the deprecation and schema policy.
## Where it lives
`docs/stability.md`, linked from the README's docs row.
## How to check it
`python3 -m unittest tests.test_contract` (parses the page's tables and compares them with the code both ways).
## Gaps
Exit codes are documented but only exit 2 (usage) is pinned for every script; the others rely on each script's own
tests. Not verified by `verify.py` (the kit has no `[verify].command`).
