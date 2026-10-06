# Final report: agent-brigade v0.1.0

2026-10-06. Branch `v0.1.0`. Status: built and checked locally. Nothing has been published.

## Verified (with the commands that prove it)
- `python3 -m unittest discover -s core/tests -t core/tests`: 64 tests pass on Python 3.11.4 (the floor) and 3.14.
- Both examples pass on 3.11, and their tests replay the loop against the real scripts: a feature PR passes every
  check; a drive-by edit, a too-early start, a post-freeze feature PR, a conflict marker, and a cut feature during
  a milestone freeze are each rejected.
- `init.py` on a fresh copy of the kit (no `.git`, as degit leaves it), for both profiles, in under 10 seconds. The
  copy passes its own checks immediately. A manual run as a new user (copy → `git init` → init → commit a conflict
  marker) was blocked by the hook.
- The kit passes its own checks: `check_markers --all` (it caught two of its own test fixtures, since fixed) and
  `check_ownership --lint-specs`.
- **Not yet verified:** GitHub Actions on the pushed branch, `npx degit` against the real repo, and branch
  protection behavior on the private repo.

## Size
8 scripts, 1,254 lines (largest: `kitlib.py` at 201). Tests: 825 lines. Docs (core + profiles): 916 lines.
`method.md`, the one doc every agent must read, is about 1,100 words.

## Kept from ShellHacks (as-is or nearly)
Spec as the only source of truth · constitution reloaded every run · one spec per feature with the same front
matter · `owns` as path prefixes + the ownership gate (ported almost line for line) · draft PR as the claim ·
`changes/<ID>.md` as the only done marker · `[C<n>]` additive contract PRs, `[FIX-]`, `[REVERT-]` · defaults
instead of questions, with decision records · golden test from a worked example · `main` red rules (20 min, then
revert) · stale claims at 45/60 min · 30-minute status report · `STOP` file · preflight · release verification
(ported from Node to stdlib Python).

## Generalized
- `overnight.md` was split. The loop went to `core/docs/method.md` (both profiles); the clock went to
  `profiles/hackathon/overnight.md`.
- The roadmap front matter (lanes, frozen paths, gates) moved to `kit.toml` + `gates.toml`. The roadmap is now
  only for people.
- `000-overnight-defaults.md` became a template plus the ambiguity rules.
- `verify-deployment.mjs` became `verify_release.py`, with configurable secret patterns and smoke paths.
- Judge-readiness audit → `judge-agent.md`. Plans A–E → `plan-bakeoff.md`. C16's do-not-implement list → a
  "Not doing" section in every roadmap.

## Added (to fix what broke)
| Failure | Fix |
|---|---|
| Agents ran out of work | Planner role + `[PLAN]` PRs (the open PR is the queue; a merge is the approval). Blocked agents switch tasks. The status report flags a low backlog. |
| Sessions died / laptop limits | `watchdog.py` (heartbeats, restart template, stale claims, red main, disk/RAM) + `remote.md` |
| Rate limits mid-run | `budget.md` routing, 75% rule, reserve for the final hours / monthly cap |
| Humans not held to the rules | Pre-commit hook + `check_markers.py` in CI, `enforce_admins: true` in preflight |
| Advisory gates, a late big merge | `check_gates.py` in CI: gates, milestone freezes, cut lists, a PR size cap that tightens |
| Demo died on a free-tier DB | Production load test in preflight, `demo_snapshot.py`, "production is a one-way door" |
| Team couldn't explain the code | `briefing.md` and the judge agent, scheduled before judging; "Your first hour" for newer teammates |
| Projects stall | `NOW.md`, milestones with ship dates, `weekly.md`, one-way doors with no default, review paths → CODEOWNERS |
| Too much to demo | `pitch.md`: a 45-second core loop in a 3-minute pitch |

## Dropped
Everything GridBridge-specific (pipeline, web app, data, schemas, sponsor documents) · Paperclip setup (only a
note in `integrations/orchestrators.md`) · Azure test generation · the MongoDB load workflow · the docs/full CI
scope classifier (replaced by advice in the tech-stack template; the user's CI template is already light).

## Deviations from the brief (and why)
- **The kit wasn't built PR-per-feature.** Eric chose a single branch mid-build ("nothing has to be that
  complicated"). The history is one commit per checklist item with reasons. The examples demonstrate the full loop
  instead.
- **`check_gates.py` lives in `core/scripts/`**, not in the profiles: one script reads either `gates.toml` or
  `milestones.toml` (no duplicated logic).
- **Review paths use CODEOWNERS** instead of a custom checker: GitHub enforces it natively.
- **The inbox is a folder**, one file per item, not one shared file, because parallel agents would conflict on a
  shared file.
- **No LICENSE** (Eric's call). The README says plainly that others can't reuse the code until one is added.

## Known gaps
- The watchdog can't tell a stuck agent from a dead one: both show up as a stale heartbeat. Restart recipes for
  Codex and Cursor are hedged ("check `--help`"), because their CLI flags change fast and I didn't verify them.
- `check_gates` decides "already started" for `no_new_phase` from the earliest commit's author date, which a
  rebase keeps but anyone can fake.
- `demo_snapshot.py` saves listed paths only. It doesn't crawl, and it can't snapshot paths where one is a prefix
  folder of another (`/api/items` and `/api/items/1`).
- Branch protection on a private repo may need a paid GitHub plan. Preflight says so.
- The README's degit command works for a public repo. While the repo is private, it needs `--mode=git` and access.
- No example exercises `watchdog.py` or `verify_release.py` end to end. They're unit-tested only, with a fake HTTP
  server and mocked `gh`.

## Open questions for Eric
1. **License** before going public. Without one, nobody can legally reuse the code. MIT is the usual choice for a
   template.
2. **`docs/story.md`'s `[OPTIONAL: …]` paragraph:** keep, cut, or reword?
3. **Teammate handles** for the README credits (`<daniel-handle>`, `<kyro-handle>`, `<sharan-handle>`).
4. **Going public and the template flag:** `gh repo edit --visibility public` and
   `gh api -X PATCH repos/Eric-Zhang-Developer/agent-brigade -F is_template=true`, when you're ready.
5. Should `dev/` (this report, the plan, the kit's own specs) stay in the public repo as a record of how it was
   built, or move out? It's already removed from user copies.
