# agent-brigade

A template for building with AI coding agents from a shared spec: agents work for hours unattended, humans make
the decisions at checkpoints, and the rules are enforced by checks, not memory. Markdown protocol, Python
standard-library scripts, any agent tool.

Like a kitchen brigade: the chef writes the menu (the spec), each cook owns a station (`owns`), every plate goes
through the pass (a pull request), and nothing leaves without tasting (CI).

## Why this exists

I showed up to ShellHacks 2026 without a team, met three strangers on Discord, and we won first place. Our coding
agents merged 349 pull requests in 32 hours, working from a shared spec. The win was real, and so were the cracks:
the agents needed me every 30 minutes, I slept about an hour, and our demo crashed in front of a judge. This kit is
everything that worked, plus fixes for everything that broke, packaged so you can start in minutes, whether you're
racing a hackathon deadline or trying to finally finish a side project.

→ [The full story](docs/story.md)

## Choose a profile and a size

| | **lite**: one agent, least ceremony | **full**: parallel agents, lanes, claims |
|---|---|---|
| **hackathon**: a deadline, gates, an unbreakable demo | Solo hacker | A team of 2–4, agents running overnight |
| **project**: continuity, `NOW.md`, milestones, one-way doors | Weekend side project | Side project with agents working while you sleep or are in class |

You can switch later (`core/docs/upgrading.md`), including turning a hackathon prototype into a maintained project.

## Quickstart (5 minutes)

```bash
npx degit Eric-Zhang-Developer/agent-brigade my-project    # or GitHub: "Use this template"
cd my-project && git init -b main
python3 core/scripts/init.py --profile hackathon --full    # or: --profile project --lite
```
Needs Python 3.11+ and git; `gh` is optional. Then:
1. Fill in `specs/mission.md`, `tech-stack.md`, `roadmap.md`, and one spec per feature (copy
   `specs/features/_template/`). Hackathon: run the [plan bake-off](profiles/hackathon/plan-bakeoff.md) first.
2. Push, and protect `main` with the required `ci` check ([preflight](profiles/hackathon/preflight.md)).
3. Start each agent with: *"Read AGENTS.md and follow it exactly. Your worker name is `<name>`. Pick your next ready
   feature and never wait for a human."*
4. Check in at checkpoints: `python3 core/scripts/status_report.py`, clear `specs/inbox/`, merge the planner's
   `[PLAN]` PR.

Full walkthrough: [core/docs/quickstart.md](core/docs/quickstart.md).

## What's inside

| Path | What |
|---|---|
| `AGENTS.md` | Rules every agent loads first |
| `kit.toml` | Profile, size, paths, frozen paths, PR cap, watchdog, release, budget ([reference](core/docs/config.md)) |
| `core/docs/` | [The method](core/docs/method.md) (the loop), [quickstart](core/docs/quickstart.md), [glossary](core/docs/glossary.md), [roles](core/docs/roles.md), [planner](core/docs/planner.md), [briefing](core/docs/briefing.md), [budget](core/docs/budget.md), [remote mode](core/docs/remote.md), [upgrading](core/docs/upgrading.md), [integrations](core/docs/integrations/) |
| `core/specs/` | Templates: mission, tech stack, roadmap, feature spec, decision, inbox |
| `core/scripts/` | `init` · `check_ownership` · `check_markers` · `check_gates` · `status_report` · `watchdog` · `verify_release` · `demo_snapshot`. All have `--help` and tests |
| `core/ci/`, `core/hooks/` | The CI workflow and PR template init installs; the pre-commit hook (same checks, for humans too) |
| `profiles/hackathon/` | [Overnight run](profiles/hackathon/overnight.md), [preflight](profiles/hackathon/preflight.md), `gates.toml`, [plan bake-off](profiles/hackathon/plan-bakeoff.md), [judge agent](profiles/hackathon/judge-agent.md), [demo snapshot](profiles/hackathon/demo-snapshot.md), [pitch](profiles/hackathon/pitch.md) |
| `profiles/project/` | `NOW.md`, [one-way doors](profiles/project/one-way-doors.md), `milestones.toml`, `review-paths.toml`, [weekly routine](profiles/project/weekly.md), [budget](profiles/project/budget.md) |
| `examples/` | [mini-hackathon](examples/mini-hackathon/) and [mini-project](examples/mini-project/): toy projects whose tests replay the loop against the real checks |

## What each failure turned into

| At ShellHacks | In the kit |
|---|---|
| Agents ran out of work every 10–30 min | The planner drafts the next batch into a `[PLAN]` PR, and blocked agents switch tasks |
| Sessions died; laptops ran out of RAM and disk | `watchdog.py` (heartbeats, restarts, resource alerts) + remote mode |
| A human merged conflict markers into `main` | `check_markers.py` in the pre-commit hook **and** CI, plus `enforce_admins` |
| An untested 1,191-line feature merged 4 min before the deadline | `check_gates.py`: an enforced freeze and a PR size cap that tightens |
| The live demo throttled on a free-tier database | Production load test in preflight, `demo_snapshot.py`, `verify_release.py` |
| The team couldn't explain the code to judges | A briefing and judge agent scheduled hours before judging |

## Bringing it to a hackathon

This is process tooling, like your editor config. It contains no project code. Most events allow pre-existing
tooling; check the rules, and disclose it. Suggested line for your submission:

> We used agent-brigade (github.com/Eric-Zhang-Developer/agent-brigade), an open process template for coordinating
> coding agents. All project code was written during the event.

## Credits

Built from the protocol the ShellHacks 2026 "Common Ground" team ran on Sperry Tech's Gridlock track:
[Daniel](https://github.com/<daniel-handle>), [Kyro](https://github.com/<kyro-handle>),
[Sharan](https://github.com/<sharan-handle>) and [Eric Zhang](https://github.com/Eric-Zhang-Developer).
The spec-driven method is adapted from the DeepLearning.AI × JetBrains spec-driven development course.

## License

No license yet. Until one is added, all rights are reserved, which means others can't legally reuse this code.
See [CONTRIBUTING.md](CONTRIBUTING.md).
