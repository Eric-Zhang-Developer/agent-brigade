## What shipped
The watchdog judges progress by side effects (pstack lesson 8): a fresh heartbeat whose worktree has no new commit or
file change for `stuck_minutes` gets one alert, restarts stop at `max_restarts` per worker per hour, an `O_EXCL`
pidfile keeps it to one instance (stale pids taken over), state writes are atomic, claim actions go through `lib.gh`.
## Where it lives
`template/common/.agents/scripts/watchdog.py`, `lib.py`, `config.toml`; `docs/config.md`, `docs/remote.md`.
## How to check it
`python3 -m unittest discover -s tests -t tests -p "test_watchdog*.py"`
## Gaps
Windows can't check the pid, so a stale `watchdog.pid` needs deleting by hand. Not yet run against a real overnight session.
