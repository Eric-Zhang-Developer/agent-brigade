# watchdog-hardening: defaults taken

| Topic | Choice | Other option | Undo |
|---|---|---|---|
| What counts as progress | The worktree's last commit time or the newest mtime among its uncommitted files (`git status -z -uall`). No state needed. | Fingerprint `git status` per pass in the state file (misses edits to an already-dirty file) | Swap `last_activity()` |
| Stuck action | Alert once per episode, never restart: a stuck agent may still be thinking, and a restart loses its context. | Restart after N stuck minutes | Call the restart template from `check_stuck()` |
| Restart cap window | Rolling hour of restart times per worker in `watchdog-state.json`; the cap alert re-arms when the heartbeat is fresh again or a restart is allowed. | Counter reset on the clock hour | Change the window in `check_sessions()` |
| Lock and `--dry-run` | A dry run takes no lock, so it can look while the real watchdog runs (it changes nothing). | Lock every run | Drop the `if not args.dry_run` guard |
| Lock on Windows | A pidfile always counts as live: `os.kill(pid, 0)` signals the process there. A human deletes a stale `watchdog.pid`. | Check liveness with `tasklist` | Add a Windows branch to `pid_alive()` |
| STOP | Still exits 0; now prints why on every run, and the STOP alert re-arms once `STOP` is gone (it used to fire once per state file, ever). | Exit 1 on STOP | Remove the print and the `clear("stop")` |
