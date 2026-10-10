---
name: Every project has a visible slot for how an agent checks its own running software
depends_on: []
owns: ["docs/verification.md"]
assignee: ""
---

# Every project has a visible slot for how an agent checks its own running software

From the v1.0 handoff (2026-10-10).

## Plan
1. `[verify].command` in config: a shell template with `{slug}` and `{worktree}`; empty means not set up, and that is reported.
2. Bootstrap spec template asks for a verifier.
3. Loop step 4 runs it after the Checks; the done note's `How to check it` holds the command and its one-line result, or `not verified`.
4. CI warns, never fails, when a `feat(<slug>)` done note has no command under `How to check it`.
5. `docs/verification.md`: what a good verifier is, stack-neutral examples, where `verify_release.py` fits.

## Requirements
- No schema bump: a missing `[verify]` table reads as empty.

## Validation
Unit tests for the config default and the done-note warning; both examples still pass.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
