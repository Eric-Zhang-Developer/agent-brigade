## What shipped
Tests that fail when the 1.x promise breaks: a contract test that holds `docs/stability.md` and the code to the same
flags, config keys and defaults, PR-title types, labels, done-note headings and `verify:` line; and an upgrade test
that installs v0.4.0 from git for all four profile/size combos and upgrades it with the current installer.
## Where it lives
`tests/test_contract.py`, `tests/test_upgrade.py`.
## How to check it
`python3 -m unittest tests.test_contract tests.test_upgrade`
## Gaps
The upgrade test skips (with the reason) in a clone without the `v0.4.0` tag; the kit's CI fetches tags. Not verified
by `verify.py` (the kit has no `[verify].command`).
