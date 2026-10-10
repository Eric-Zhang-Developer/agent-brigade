## What shipped
A verifier slot, shaped by pstack's verification skills: `[verify].command` (+ `timeout`), `verify.py` (one result
line naming the commit, a kept `{out}` evidence folder, process-group cleanup), the spec's Validation as the
per-feature recipe, a loop step that runs it, and a CI warning when a feat done note has no verify line.
## Where it lives
`template/common/.agents/scripts/verify.py`, `lib.py`, `check_gates.py`, `template/parts/agents-common.md`, the spec
and PR templates, `docs/verification.md`, both examples' `[verify]`.
## How to check it
`python3 -m unittest tests.test_verify tests.test_check_gates`; CI runs `verify.py` on both examples.
## Gaps
Status counts are `verifier-status`. Existing installs add the loop step by hand or with `--overwrite-agents`.
Not yet run by a real agent through the full loop. Windows: no process-group cleanup (it only kills on timeout).
