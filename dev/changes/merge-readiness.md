## What shipped
`pr_ready.py`: one pass over GitHub's whole verdict (closed/draft, conflicts, changes requested, unresolved threads,
failing, pending), one exit code per blocker. Loop step 6 runs it between `gh pr checks --watch` and the merge; one
new Prefer line on red CI. Shaped by pstack's `watch-pr`.
## Where it lives
`template/common/.agents/scripts/pr_ready.py`, `template/parts/agents-common.md`, `tests/test_pr_ready.py`, `docs/config.md`, `docs/glossary.md`.
## How to check it
`python3 -m unittest discover -s tests -t tests -p test_pr_ready.py` (fake `gh` on PATH, no network).
## Gaps
Reads the first 100 review threads only. Existing installs get the new step 6 by hand or with `--overwrite-agents`.
