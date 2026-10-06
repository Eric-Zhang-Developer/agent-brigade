# Quickstart

About five minutes of commands, then the time it takes to write a good spec.

## 1. Copy the kit
```bash
npx degit <owner>/agent-brigade my-project      # or GitHub: "Use this template"
cd my-project && git init -b main
```
You need Python 3.11+ and git. `gh` (GitHub CLI) is optional, but it makes the status report and watchdog smarter.

## 2. Pick a profile and size
| You are… | Run |
|---|---|
| A team at a hackathon, several agents in parallel | `python3 core/scripts/init.py --profile hackathon --full` |
| Solo at a hackathon, one agent | `python3 core/scripts/init.py --profile hackathon --lite` |
| A side project, one agent | `python3 core/scripts/init.py --profile project --lite` |
| A side project, several agents while you sleep | `python3 core/scripts/init.py --profile project --full` |

`init.py` writes `kit.toml`, copies the spec templates into `specs/`, installs CI and the pre-commit hook, and adds
the profile's files. Re-running it never overwrites your edits.

## 3. Write the constitution (the part that matters)
Fill in `specs/mission.md`, `specs/tech-stack.md` and `specs/roadmap.md`, then one spec per feature in
`specs/features/F<n>-<slug>/spec.md` (copy `_template/`). An agent can draft these with you. You approve them.
- Hackathon: run the plan bake-off first (`profiles/hackathon/plan-bakeoff.md`).
- Project: write `NOW.md` and list your one-way doors (`profiles/project/one-way-doors.md`).

## 4. Push, protect, launch
```bash
git add -A && git commit -m "Spec on main" && gh repo create --private --source . --push
```
Then follow `profiles/hackathon/preflight.md` (branch protection, keys, load test) or, for a project, set up
branch protection the same way. Start your agents with:

> Read AGENTS.md and follow it exactly. Your worker name is `<name>`. Pick your next ready feature and never wait
> for a human.

## 5. Check in at checkpoints, not constantly
- `python3 core/scripts/status_report.py` tells you what's done, in progress, ready, blocked and waiting on you.
- Clear `specs/inbox/` in one batch, and merge or trim the planner's `[PLAN]` PR.
- `python3 core/scripts/watchdog.py` keeps the run alive while you're away (`remote.md`).
