# Glossary

Every term the kit uses, in one line each.

| Term | Meaning |
|---|---|
| Agent | An AI coding tool that reads files, runs commands and commits (Claude Code, Codex, Cursor, ...). |
| Worker | One running agent session, with a name like `claude-1`. |
| Spec | Plain-text files that say what to build and the rules. The agents' shared memory. |
| Constitution | The three specs every agent reloads each run: `mission.md`, `tech-stack.md`, `roadmap.md`. |
| Feature | One unit of work with its own spec and owned paths. Its ID is the spec's folder name, a slug like `map-data`. |
| `owns` | The path prefixes a feature alone may change. CI fails anything outside them. |
| Frozen path | A shared file (CI, schemas, the kit itself) that only a contract PR may change. |
| Contract PR | A `contract:` PR that changes frozen files, additively only. |
| Bootstrap | The one feature that builds the skeleton, contracts and CI. Everything else waits for it. |
| Claim | Full size only: a draft PR titled `feat(<slug>): ...`. It means "I'm on this"; there's no other signup. |
| Worktree | A separate checkout of the same repo (`git worktree add`), so agents don't trip over each other. |
| Done note | `changes/<slug>.md`, 3–8 lines under fixed headings, written last. The only thing that marks a feature done (its issue then closes). |
| Decision record | `specs/decisions/<slug>-<topic>.md`: context, options, choice, how to undo. |
| Default | What an agent does when the spec is silent: the smaller, reversible option, logged. |
| `needs-human` issue | A judgment call an agent filed as a GitHub issue, with the default it took (or none, for a one-way door). Cleared at checkpoints. |
| Status issue | One pinned GitHub issue, rewritten after every merge: done, in progress, ready, blocked, needs human. |
| One-way door | A decision that's expensive to undo (schema, auth, data model, public API). Agents never take a default on one. |
| Checkpoint | A moment a human checks in: reads the Status issue, clears the `needs-human` issues, approves the planner's batch. |
| Planner | The agent role that drafts new feature specs into a `plan:` PR, keeping the backlog full. |
| Reporter | The agent role that writes the Status issue on a schedule. |
| Milestone | A named deadline in `specs/milestones.toml` with its features in priority order, enforced in CI. A hackathon's milestones are offsets from its start. |
| Backlog | A spec in no milestone: listed in status, never picked until a milestone lists it. |
| Walkthrough | `specs/shipped/<milestone>/README.md`, stitched from the done notes by `ship.py`: one page per release. |
| Freeze | The window before a milestone ships when only its own features merge. In the final milestone: no new feature work, only fixes and reverts. |
| Golden test | A test built from a known worked example (often the sponsor's), so the core math can never silently drift. |
| `main` red | The latest CI run on `main` failed. Nobody merges except the fix. |
| Heartbeat | A file each agent touches every loop, inside the repo's git folder so every worktree shares it. If it goes quiet, the watchdog restarts that session. |
| Lite / full | The size dial: one agent with minimal ceremony, or parallel agents with claims. |
| Lane | A group of related features (data, app, quality) owned by the same agents. Full size only. |
| Briefing | `docs/briefing.md`: one page on the problem, architecture, honest numbers and what changed. |
