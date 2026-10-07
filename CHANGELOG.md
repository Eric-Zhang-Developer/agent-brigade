# Changelog

## v0.2.0 (unreleased)

Lessons from the first real install (Raze 2), where the kit took 134 files to add ~8 of the project's own.
- **Install from outside:** `install.py --profile ... TARGET` writes about 20 neutral files into a project, new or
  existing. No kit docs, examples, story or branding, and a test enforces it. The kit stays in its own repo.
- **The loop lives in the installed `AGENTS.md`**, split into Must (enforced by checks) and Prefer (judgment).
- **GitHub Issues is the human's queue:** `sync_issues.py` keeps one issue per feature spec; agents file
  `needs-human` / `one-way-door` / `blocked` issues (replacing `specs/inbox/`); the watchdog files `main-red`;
  `status.py --issue` keeps one pinned Status issue current (replacing the committed status file).
- **PR size is a warning, not a cap** (`[pr].warn_lines`). The freeze stays the hard rule.
- Heartbeats live in the git common dir, so every worktree shares them; worktrees default outside the project
  folder.
- Fix: the staged/base marker scans skip binary files (from Raze 2).
- Layout: `core/` + `profiles/` became `template/` (what's installed) and `docs/` (guides for people).
  `kit.toml` became `.agents/config.toml`.

## v0.1.0 (unreleased)

First version, generalized from the ShellHacks 2026 protocol.
- Core loop (`core/docs/method.md`) and config reference (`core/docs/config.md`).
- Scripts, all stdlib Python 3.11+ with tests: `init`, `check_ownership`, `check_markers`, `check_gates`,
  `status_report`, `watchdog`, `verify_release`, `demo_snapshot`.
- CI workflow and PR template for user repos; pre-commit hook.
- Hackathon profile: overnight run, preflight, gates, plan bake-off, judge agent, demo snapshot, pitch.
- Project profile: `NOW.md`, one-way doors, milestones, review paths, weekly routine, budget.
- Examples: mini-hackathon and mini-project, each replaying the loop in its tests.
