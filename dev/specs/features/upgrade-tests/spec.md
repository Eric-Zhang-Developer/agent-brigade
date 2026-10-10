---
name: Tests fail when someone breaks the 1.x promise by accident
depends_on: ["stability-contract"]
owns: ["tests/test_contract.py", "tests/test_upgrade.py"]
assignee: ""
---

# Tests fail when someone breaks the 1.x promise by accident

From the v1.0 handoff (2026-10-10).

## Plan
1. Contract test: every documented flag parses, every documented config key is read, every label is the documented one.
2. Upgrade test: install the v0.4.0 template, upgrade to the current one, run `check_ownership --lint-specs` and `status --offline`.

## Requirements
- No network. The v0.4.0 template comes from git history, not npm.

## Validation
`python3 -m unittest discover -s tests -t tests`

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
