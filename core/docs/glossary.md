# Glossary

Every term the kit uses, in one line each.

| Term | Meaning |
|---|---|
| Agent | An AI coding tool that reads files, runs commands and commits (Claude Code, Codex, Cursor, ...). |
| Worker | One running agent session, with a name like `claude-1`. |
| Spec | Plain-text files that say what to build and the rules. The agents' shared memory. |
| Constitution | The three specs every agent reloads each run: `mission.md`, `tech-stack.md`, `roadmap.md`. |
| Feature | One unit of work with its own spec, ID (`F07`) and owned paths. |
| `owns` | The path prefixes a feature alone may change. CI fails anything outside them. |
| Frozen path | A shared file (CI, schemas, the kit itself) that only a contract PR may change. |
| Contract PR | A `[C<n>]` PR that changes frozen files, additively only. |
| Bootstrap | The one feature that builds the skeleton, contracts and CI. Everything else waits for it. |
| Claim | A draft PR titled `[<ID>] name`. It means "I'm on this"; there's no other signup. |
| Worktree | A separate checkout of the same repo (`git worktree add`), so agents don't trip over each other. |
| Done note | `changes/<ID>.md`, 3–8 lines, written last. The only thing that marks a feature done. |
| Decision record | `specs/decisions/<ID>-<slug>.md`: context, options, choice, how to undo. |
| Default | What an agent does when the spec is silent: the smaller, reversible option, logged. |
| Inbox | `specs/inbox/`: one file per judgment call a human should see. Cleared at checkpoints. |
| One-way door | A decision that's expensive to undo (schema, auth, data model, public API). Agents never take a default on one. |
| Checkpoint | A moment a human checks in: reads the status, clears the inbox, approves the planner's batch. |
| Planner | The agent role that drafts new feature specs into a `[PLAN]` PR, keeping the backlog full. |
| Reporter | The agent role that writes `reports/status.md` on a schedule. |
| Gate | A time rule from `gates.toml` (hackathon) or `milestones.toml` (project), enforced in CI. |
| Freeze | A gate after which no new feature work merges; only fixes and reverts. |
| Golden test | A test built from a known worked example (often the sponsor's), so the core math can never silently drift. |
| `main` red | The latest CI run on `main` failed. Nobody merges except the fix. |
| Heartbeat | A file each agent touches every loop. If it goes quiet, the watchdog restarts that session. |
| Lite / full | The size dial: one agent with minimal ceremony, or parallel agents with lanes and claims. |
| Lane | A group of related features (data, app, quality) owned by the same agents. Full size only. |
| Briefing | `docs/briefing.md`: one page on the problem, architecture, honest numbers and what changed. |
