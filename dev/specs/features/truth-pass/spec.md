---
name: Every kit doc and dev spec says what is true today
depends_on: []
owns: ["dev/specs/decisions/000-defaults.md"]
assignee: ""
---

# Every kit doc and dev spec says what is true today

From the v1.0 handoff (2026-10-10).

## Plan
1. Rewrite `dev/specs/milestones.toml` as the v1.0.0 milestone, with one spec per item.
2. D12 says the repo is public; add decisions this cycle settles.
3. Add an `Unreleased` section to `CHANGELOG.md`.
4. Read every doc in `docs/` against the scripts and flags; fix what is wrong or stale.

## Requirements
- Every flag, key, path, label and count named in `docs/`, `README.md` and `CONTRIBUTING.md` exists in the code.
- The PR lists each doc fix.

## Validation
`python3 template/common/.agents/scripts/check_ownership.py --lint-specs` passes on the kit; the PR lists the doc fixes.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
