## What shipped
Bug reports come back into the loop: a neutral `bug` issue template, `bug`/`needs-info` labels, and a 6-line "Bug
reports" rule in the installed AGENTS.md (dedupe, reproduce twice on origin/main, verify an existing fix instead of
competing, `fix(<slug>)` with failing then passing line, cross-feature bugs go to the planner). Lite gets both.
## Where it lives
`template/common/.github/ISSUE_TEMPLATE/bug.md`, `template/parts/agents-common.md`, `sync_issues.py` LABELS,
`docs/config.md`, `docs/planner.md` (clustering), `docs/verification.md` (verifying someone else's fix).
## How to check it
`python3.11 -m unittest discover -s tests -t tests` (install test sees the template; sync_issues creates both labels).
## Gaps
No `reproduced` label (the rule doesn't need one). The rule is prose for agents; nothing enforces it. No Slack/email intake.
