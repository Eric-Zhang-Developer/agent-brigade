# Changelog

## v0.3.0 (unreleased)

Readable names and one deadline model, from Raze 2's first 37 PRs (27% of them process overhead) and a live check
of v0.2 on a smoke-test repo. Schema 3: v0.2 projects follow "From schema 2" in `docs/upgrading.md`.
- **The slug is the ID.** `specs/features/map-data/` is `map-data`: its done note, branch, decisions and PR scope.
  No more F-numbers.
- **PR titles are Conventional Commits:** `feat(<slug>)`, `fix(<slug>)` (also `refactor`, `perf`, `test`, `chore`,
  `style`), scope-less `fix:` for shared code with no spec, `docs:` for status edits like `NOW.md`, `contract:`,
  `plan:`, `revert:` (or GitHub's `Revert "..."`). `feat` on a done feature points you to `fix`.
- **One `specs/milestones.toml` for both profiles** replaces `gates.toml`, `phase`, stages and `cut: ok|never`.
  Order comes from each milestone's `features`; specs in no milestone are backlog. Hackathons use `start` plus
  `+H:MM` offsets and a final milestone with a report window and hard stop. Bootstrap-first is a built-in rule.
- **Ownership is exclusive only while a feature is in flight**, and shipped specs still scope fixes, so a long-lived
  app can extend old code without a contract PR.
- **GitHub milestones:** `sync_issues.py` creates one per milestone (with its due date), files each feature's issue
  on it, and matches issues by a hidden `<!-- spec: <slug> -->` line, so people can retitle them.
- **`ship.py <milestone>`** moves a finished milestone's specs to `specs/shipped/<milestone>/` and writes a
  one-page release walkthrough from the done notes, which now use fixed headings.
- **Status reports loop health:** PRs by type, process overhead, median time open, most-fixed features, reverts,
  minutes `main` was red. Also new: Missed and Backlog sections.
- **Lite has no claims:** open the PR when the work is ready. The merge step waits for CI
  (`gh pr checks --watch && gh pr merge ...`). "One feature at a time" is now a Prefer rule.
- **Schema stamp:** `.agents/config.toml` carries `schema = 3`; the installer stops on an older one until
  `--upgrade`.
- Fixes from the v0.2 live check: the pre-commit hook no longer writes `__pycache__` (it got committed and failed
  the ownership check), installs ignore it, status no longer reports its own in-progress run as `main` CI, the
  install prints the command that makes `ci` required, and the workflow moves to the Node 24 actions.

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
