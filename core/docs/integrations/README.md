# Integrations (optional)

Core never depends on a particular agent tool. These notes show how to plug common tools into the kit: what file
they read on start, how to launch one non-interactively, and a `[watchdog].restart` template. CLIs change fast,
so check your tool's `--help` and docs for the exact flags in your version.

| Tool | Reads on start | Notes |
|---|---|---|
| Claude Code | `CLAUDE.md` (the kit's says `@AGENTS.md`) | [claude-code.md](claude-code.md) |
| Codex | `AGENTS.md` | [codex.md](codex.md) |
| Cursor | `AGENTS.md` / project rules | [cursor.md](cursor.md) |
| Orchestrators and terminal managers | n/a | [orchestrators.md](orchestrators.md) |

Every tool gets the same launch prompt:

> Read AGENTS.md and follow it exactly. Your worker name is `<name>`. At the start of each task, write your
> heartbeat (`mkdir -p .agent-brigade/heartbeats && pwd > .agent-brigade/heartbeats/<name>`). Pick your next ready
> feature and never wait for a human.
