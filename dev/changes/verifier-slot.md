## What shipped
A verifier slot: `[verify].command` in config, `verify.py` to run it with one pasteable result line, a loop step that
runs it, a done-note line for the result, and a CI warning when a feat done note has no check.
## Where it lives
`template/common/.agents/scripts/verify.py`, `lib.py` (`note_section`, default), `check_gates.py` (warning),
`template/parts/agents-common.md` (loop steps 4–5), `docs/verification.md`, both examples' `[verify]`.
## How to check it
`python3 -m unittest tests.test_verify tests.test_check_gates`; CI runs `verify.py` on both examples.
## Gaps
Status counts (verified / not verified / not set up) are `verifier-status`. Existing installs need the loop step
added to `AGENTS.md` by hand or with `--overwrite-agents` (docs/upgrading.md). Not dogfooded with a real agent yet.
