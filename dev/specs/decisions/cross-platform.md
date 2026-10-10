# Cross-platform: Windows is best-effort; existing git hooks win

Settled 2026-10-10 for issue #9 (is Windows official?), which is still open for Eric.

| Topic | Choice | Other option | Undo |
|---|---|---|---|
| Windows | Best-effort: a non-required `platforms` CI job runs the tests and a packed install on macOS and Windows; POSIX-only tests are skipped there with a reason, and the README lists the gaps. | Make Windows official: port `verify.py` and the watchdog templates off `sh`. | Add `windows-latest` to the required check |
| Required check | Stays the ubuntu job named `ci`; the matrix is a separate job, so branch protection is unchanged. | A matrix on `ci` (renames the check). | Rename and update protection |
| Existing git hooks | If `core.hooksPath` is already set or `.git/hooks` holds non-sample hooks, the installer leaves them and prints how to call `.agents/hooks/pre-commit` from them. | Override and warn. | Set `core.hooksPath` unconditionally again |
