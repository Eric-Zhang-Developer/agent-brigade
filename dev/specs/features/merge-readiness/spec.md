---
name: Agents merge on the forge's whole verdict, not just green CI
depends_on: []
owns: ["template/common/.agents/scripts/pr_ready.py", "tests/test_pr_ready.py"]
assignee: ""
---

# Agents merge on the forge's whole verdict, not just green CI

From the pstack review (`dev/specs/pstack-lessons.md`).

## Plan
1. `pr_ready.py` (stdlib + `gh`): one pass over the PR, in order: conflicts, unresolved review threads, changes requested, draft/closed, failing checks, pending; a distinct exit code per blocker.
2. Loop step 6 becomes `gh pr checks --watch && python3 .agents/scripts/pr_ready.py && gh pr merge --squash --delete-branch`.
3. A Prefer line on CI failures: read the log, rerun at most once, a failure in code you didn't touch means rebase.

## Requirements
- No network in tests: fake `gh` on PATH.
- Missing or unauthenticated `gh`: one clear line, exit 1.

## Validation
`python3 -m unittest discover -s tests -t tests -p test_pr_ready.py`

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Keep the installed `AGENTS.md` about one page.
