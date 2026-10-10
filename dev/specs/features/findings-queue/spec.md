---
name: An optional gardener appends bad patterns to a queue the planner batches
depends_on: ["sampling-review"]
owns: ["docs/roles.md"]
assignee: ""
---

# An optional gardener appends bad patterns to a queue the planner batches

From the v1.0 handoff (2026-10-10).

## Plan
1. Gardener role in `docs/roles.md` appends findings to `specs/context/findings.md` instead of fixing each.
2. The planner reads the queue and turns clusters into specs.

## Requirements
- Optional and full size only.

## Validation
Doc review.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
