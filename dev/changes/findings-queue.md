## What shipped
An optional gardener role (full size) that appends bad patterns to `specs/context/findings.md` instead of fixing
each, and a planner step that turns any pattern seen twice into one spec. `plan:` PRs may now change that file.
## Where it lives
`docs/roles.md`, `docs/planner.md`, `docs/config.md`, `template/common/.agents/scripts/check_ownership.py`,
`tests/test_check_ownership.py`, `dev/specs/decisions/findings-queue.md`.
## How to check it
`python3 -m unittest discover -s tests -t tests -k test_plan_may_add` (fails without the ownership change).
## Gaps
The installed `AGENTS.md` `plan:` row doesn't list `specs/context/findings.md` yet (another workstream owns that
file). No gardener has run on a real project.
