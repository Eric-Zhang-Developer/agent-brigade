---
name: docs/stability.md says what 1.x will not break, and how deprecations work
depends_on: []
owns: ["docs/stability.md"]
assignee: ""
---

# docs/stability.md says what 1.x will not break, and how deprecations work

From the v1.0 handoff (2026-10-10).

## Plan
1. List the public surface from the code: config keys, specs layout and front matter, milestones fields, PR-title table, done-note headings, labels, script names/flags/exit codes, the npx command.
2. Say what is not promised: AGENTS.md wording, report formatting, docs/.
3. Deprecation policy: a renamed key or flag keeps working with a one-line warning for the rest of 1.x; removal waits for 2.0.

## Requirements
- Every item cites where it is defined, so the contract tests can pin it.

## Validation
Read against the code; `upgrade-tests` pins it.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
