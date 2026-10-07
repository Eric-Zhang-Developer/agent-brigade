# Cursor

- **Instructions:** point Cursor's project rules at `AGENTS.md` (or keep a one-line rule saying "Follow
  AGENTS.md").
- **Editor agent:** fine for a lite setup. Open one window per worktree so features don't mix.
- **Background or CLI agents:** if your Cursor version offers them, give each one the standard launch prompt and its
  own branch. The claim is still the draft PR, and CI is still the gate.
- **Restart:** whatever command your Cursor CLI provides, wrapped in the same tmux pattern as
  [claude-code.md](claude-code.md). If there isn't one, leave `restart` empty and let the watchdog alert you.
