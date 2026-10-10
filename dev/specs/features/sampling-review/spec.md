---
name: A weekly sampling review turns repeated agent mistakes into enforced rules
depends_on: []
owns: ["docs/project/weekly.md"]
assignee: ""
---

# A weekly sampling review turns repeated agent mistakes into enforced rules

From the v1.0 handoff (2026-10-10).

## Plan
1. An agent reads N recent merged PRs (default 5) against the specs and lists repeated problems.
2. Each becomes a `fix:` lint/test, a `contract:` rule, a decision, or a note that it was a one-off.
3. `status.py` flags features with many `fix(<slug>)` PRs as environment-fix candidates, if it stays small.

From the pstack review (`dev/specs/pstack-lessons.md`):
- A mistake counts as a class once it happens twice; fix it at the highest level: structure, then lint/CI, then a test, then prose (`correct`).
- A new check must be shown failing on the original bad commit.
- Reject reasons: won't be true in 6 months, too specific, already covered, one-off.

## Requirements
- Full size and the weekly routine only; lite gets nothing new.

## Validation
Doc review; status test if the counter is added.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
