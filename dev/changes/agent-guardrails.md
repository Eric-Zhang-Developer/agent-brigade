## What shipped
pstack's behavior rules in the installed `AGENTS.md`, one line each (never weaken a check, issue text is data,
run it instead of asking, timeboxes, evidence by title type, push per passing commit). Each Must names its check;
ownership errors name the allowing title; CI warns when a feat/fix PR edits its own spec's Validation.
## Where it lives
`template/parts/agents-common.md`, `check_ownership.py`, `check_gates.py`, the PR template, `docs/verification.md`,
`docs/integrations/claude-code.md`, `dev/specs/decisions/agent-guardrails.md`.
## How to check it
`python3.11 -m unittest discover -s tests -t tests -p 'test_check_[go]*.py'`. Not verified by a real agent run.
## Gaps
Installed `AGENTS.md` is 114–118 lines (main was 104–108; this adds 10), over the ~100 target. Golden tests and
`[verify].command` edits have no check yet. Secrets, invented data and issue-text injection moved to Prefer: no
check catches them.
