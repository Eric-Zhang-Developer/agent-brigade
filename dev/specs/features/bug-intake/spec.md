---
name: Bug reports come back into the loop through a template and a reproduce-first rule
depends_on: []
owns: ["template/common/.github/ISSUE_TEMPLATE/bug.md"]
assignee: ""
---

# Bug reports come back into the loop through a template and a reproduce-first rule

From the v1.0 handoff (2026-10-10).

## Plan
1. `bug` issue template: what happened, steps, expected, version or commit.
2. Triage rule in the installed AGENTS.md: reproduce on origin/main first; `needs-info` if not reproducible; `fix(<slug>)` if it has a spec; a planner spec if it spans features.
3. The planner clusters related bug issues into one spec.

## Requirements
- GitHub Issues only. No other connectors.

## Validation
Install test sees the template; `sync_issues` creates the `bug` and `needs-info` labels.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
