---
name: The watchdog judges progress by commits, caps restarts and can't run twice
depends_on: []
owns: ["tests/test_watchdog_hardening.py"]
assignee: ""
---

# The watchdog judges progress by commits, caps restarts and can't run twice

From the pstack review (`dev/specs/pstack-lessons.md`).

## Plan
1. Flag a worker whose heartbeat is fresh but whose worktree has no new commit for `[watchdog].stuck_minutes` (alert only).
2. Cap restarts at `[watchdog].max_restarts` per worker per hour, then alert instead.
3. Single-instance lock (`O_EXCL` pidfile with stale-PID takeover) and atomic state writes (`os.replace`).

## Requirements
- New config keys have defaults, so schema 3 configs keep working.

## Validation
`python3 -m unittest tests.test_watchdog tests.test_watchdog_hardening`

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Keep the installed `AGENTS.md` about one page.
