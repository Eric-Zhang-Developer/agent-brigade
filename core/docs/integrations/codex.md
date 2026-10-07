# Codex

- **Instructions:** reads `AGENTS.md` natively.
- **Interactive:** `cd ../app-f04 && codex`. **Non-interactive:** `codex exec "<launch prompt>"` (check
  `codex --help` for your version's flags, including how to resume a session).
- **Restart template** (a fresh run is fine: everything the agent needs is on `main`):
  ```toml
  restart = "tmux kill-session -t {worker}; tmux new -d -s {worker} -c {worktree} 'codex exec \"Read AGENTS.md and follow it. Worker {worker}. Resume your open PR or pick the next ready feature.\"'"
  ```
- Codex and Claude Code can share one repo safely: they coordinate only through PR claims, never chat. Give
  each its own feature assignments, so no feature has two owners.
