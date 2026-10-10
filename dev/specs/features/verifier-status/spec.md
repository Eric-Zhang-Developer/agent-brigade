---
name: The Status report counts verified, unverified and no-verifier features
depends_on: ["verifier-slot"]
owns: []
assignee: ""
---

# The Status report counts verified, unverified and no-verifier features

From the v1.0 handoff (2026-10-10).

## Plan
1. `status.py` reads each done note's `How to check it` and counts verified / not verified / no verifier configured.

## Requirements
- Counts come from done notes on main only; nothing is inferred.

## Validation
`tests/test_status_report.py` covers each count.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
