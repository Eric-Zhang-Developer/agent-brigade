# Quickstart

About five minutes of commands, then the time it takes to write a good spec.

## 1. Check the tools
Python 3.11+ (macOS ships 3.9: `brew install python`), git, and Node for `npx`. `gh` (GitHub CLI) is what turns
issues on.

## 2. Install into a project (new or existing)
From the project's folder:

| You are… | Run |
|---|---|
| A team at a hackathon, several agents in parallel | `npx agent-brigade --profile hackathon --full` |
| Solo at a hackathon, one agent | `npx agent-brigade --profile hackathon --lite` |
| A side project, one agent | `npx agent-brigade --profile project --lite` |
| A side project, several agents while you sleep | `npx agent-brigade --profile project --full` |

No Node? Clone the kit once and run the same thing with Python:
`git clone https://github.com/Eric-Zhang-Developer/agent-brigade ~/tools/agent-brigade`, then
`python3 ~/tools/agent-brigade/install.py --profile project --lite`. Either way, pass a folder at the end to
install somewhere other than the current one.

That writes about 25 files: `AGENTS.md`, `CLAUDE.md`, `.agents/` (settings, scripts, pre-commit hook), `specs/`
templates, `changes/`, CI and the GitHub templates. None of them mention the kit. Re-running never overwrites
your edits.

## 3. Write the specs (the part that matters)
Fill in `specs/mission.md`, `tech-stack.md` and `roadmap.md`, then one spec per feature in
`specs/features/<slug>/spec.md` (copy `_template/`; the folder name is the feature's ID), and list the slugs in
`specs/milestones.toml` in priority order. An agent can draft these with you; you approve them.
- Hackathon: run the plan bake-off first (`docs/hackathon/plan-bakeoff.md`).
- Project: write `NOW.md`, and list your one-way doors (`docs/project/one-way-doors.md`).

## 4. Push, protect, launch
```bash
git add -A && git commit -m "Specs and agent workflow" && git push
```
The first push to `main` creates the labels, one issue per feature, and the pinned Status issue. Make `ci` a
required check on `main` (`docs/hackathon/preflight.md` has the commands). Then start each agent with:

> Read AGENTS.md and follow it exactly. Your worker name is `<name>`. Pick your next ready feature and never wait
> for a human.

## 5. Check in at checkpoints, not constantly
Open the repo's **Issues**: filter `needs-human`, read the pinned **Status**, and merge or trim the planner's
`plan:` PR. `python3 .agents/scripts/watchdog.py` keeps the run alive while you're away (`docs/remote.md`).
