# Orchestrators and terminal managers

- **Agent orchestrators** (Paperclip and similar) run agents as a "company" of roles with heartbeats and budgets.
  They work with this kit if each agent's instructions start with "Follow AGENTS.md; it overrides any conflicting
  skill." Turn on their heartbeat timers for unattended runs. Never let an orchestrator agent and a local session
  own the same feature: assign features to one or the other with each spec's `assignee`.
- **Terminal managers** (tmux, and tools that gather many agent terminals into one view) make it easy to watch many
  workers at once. They pair well with `watchdog.py`: name each session after its worker, so `{worker}` in the
  restart template matches.
- **Cloud agent runners:** same rules. Each run reads `AGENTS.md`, claims with a draft PR (full size), and passes CI.
