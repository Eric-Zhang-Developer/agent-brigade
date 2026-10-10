## What shipped
A weekly sampling review (full size): a prompt that turns mistakes seen twice in recent PRs into the highest fix
that works (structure, check, test, rule), each new check shown failing on the bad commit. Plus the verifier drift
pass, a review rubric (`docs/review.md`), an optional reviewer role, and arena lines in the plan bake-off.
## Where it lives
`docs/project/weekly.md`, `docs/review.md`, `docs/roles.md`, `docs/planner.md`, `docs/project/one-way-doors.md`,
`docs/hackathon/plan-bakeoff.md`, `docs/glossary.md`, `README.md`.
## How to check it
not verified: docs only, no verifier runs prose. The prompt hasn't been run by a real agent on a real project yet.
## Gaps
The `status.py` counter for features with many `fix(<slug>)` PRs was skipped; the prompt counts them with `gh`
instead. Add the counter if reviewers keep missing it.
