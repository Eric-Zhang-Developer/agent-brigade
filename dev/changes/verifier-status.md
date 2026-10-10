## What shipped
The Status report now opens with **Review first** (verifier not set up, unverified done features, done notes with
gaps, the most-fixed features; at most 8 lines) and counts done notes as verified / not verified, after pstack's
`orch` ledger (missing means not verified). Offline "In progress" no longer lists `main` or version branches.
## Where it lives
`template/common/.agents/scripts/status.py`, `tests/test_status_report.py`, `docs/glossary.md`, `docs/verification.md`.
## How to check it
`python3.11 -m unittest discover -s tests -t tests -p "test_status*"` (10 tests, ok).
not verified: a report script has no verifier; the examples' `status.py --offline` output was read by eye.
## Gaps
"feat PRs that edited their own Validation" is not in Review first (that warning is `agent-guardrails`' check).
Fix counts read the last 200 first-parent commits only. Offline In progress needs branches named after the slug.
