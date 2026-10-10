## What shipped
A non-required `platforms` CI job (macOS, Windows: unit tests + a packed install), an installer that keeps existing
git hooks and `.github/` files, and one clear line instead of a traceback when gh is missing or logged out, when
`milestones.toml` is bad, or when `--now` is bad.
## Where it lives
`.github/workflows/ci.yml`, `install.py`, `ship.py`, `sync_issues.py`, `check_gates.py`, `status.py`, `watchdog.py`
(gh line only), `tests/test_no_gh.py`, `tests/test_install.py`, README "Platforms", `dev/specs/decisions/cross-platform.md`.
## How to check it
`cd tests && python3.11 -m unittest test_install test_no_gh`; the CI `platforms` job for macOS and Windows.
## Gaps
Windows: `verify.py` and watchdog templates assume `sh`; no process-group cleanup; no free-RAM reading; the logged-out
gh stub test is POSIX-only. Issue #9 stays open for Eric.
