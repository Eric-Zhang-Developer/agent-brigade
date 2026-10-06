# Claude Code

- **Instructions:** reads `CLAUDE.md`. The kit ships one containing `@AGENTS.md`, so both tools share the same
  rules.
- **Long runs:** auto-accept (or a permissions allowlist) removes prompt waits. Its looping and scheduling
  features (for example `/loop`) can keep a session picking work, but the kit's loop works without them, because
  the next task always comes from the roadmap.
- **One session per worktree:** `cd ../app-f03 && claude`.
- **Restart template** (in tmux; `--continue` resumes the most recent conversation in that folder):
  ```toml
  restart = "tmux kill-session -t {worker}; tmux new -d -s {worker} -c {worktree} 'claude --continue'"
  ```
  A resumed session should re-read `AGENTS.md`. The spec on `main`, not the conversation, carries the context.
- **Subagents:** fine within one feature. They share the feature's `owns` and its single PR.
