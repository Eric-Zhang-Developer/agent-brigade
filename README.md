# agent-brigade

A template for building with AI coding agents from a shared spec: agents work for hours unattended, humans make
the decisions at checkpoints, and the rules are enforced by checks, not memory. Markdown protocol, Python
standard-library scripts, any agent tool.

```bash
npx agent-brigade --profile project --lite      # in your repo; or --profile hackathon, --full for parallel agents
```

Like a kitchen brigade: the chef writes the menu (the spec), each cook owns a station (`owns`), every plate goes
through the pass (a pull request), and nothing leaves without tasting (CI).

## Why this exists

I showed up to ShellHacks 2026 without a team, met three strangers on Discord, and we won first place. Our coding
agents merged 349 pull requests in 32 hours, working from a shared spec. The win was real, and so were the cracks:
the agents needed me every 10–30 minutes, I slept about an hour, and our demo crashed in front of a judge. This kit is
everything that worked, plus fixes for everything that broke, packaged so you can start in minutes, whether you're
racing a hackathon deadline or trying to finally finish a side project.

→ [The full story](docs/story.md)

## Choose a profile and a size

| | **lite**: one agent, least ceremony | **full**: parallel agents, claims, a reporter |
|---|---|---|
| **hackathon**: a deadline, milestones, an unbreakable demo | Solo hacker | A team of 2–4, agents running overnight |
| **project**: continuity, `NOW.md`, milestones, one-way doors | Weekend side project | Side project with agents working while you sleep or are in class |

You can switch later ([upgrading](docs/upgrading.md)), including turning a hackathon prototype into a maintained project.

## Quickstart (5 minutes)

```bash
cd ~/code/my-project
npx agent-brigade --profile hackathon --full     # or: --profile project --lite
```
Works on a new or an existing repo. Needs Python 3.11+, git and Node (or clone this repo and run
`python3 install.py` instead); `gh` is how agents open, claim and merge PRs and file issues. The project gets about 25 neutral files (`AGENTS.md`,
`.agents/`, `specs/`, CI and GitHub templates) and nothing that names this kit. Then:
1. Fill in `specs/mission.md`, `tech-stack.md`, `roadmap.md`, and one spec per feature (copy
   `specs/features/_template/`). Hackathon: run the [plan bake-off](docs/hackathon/plan-bakeoff.md) first.
2. Push. The first push to `main` creates the labels, one issue per feature, and a pinned **Status** issue. Make
   `ci` a required check ([preflight](docs/hackathon/preflight.md)).
3. Start each agent with: *"Read AGENTS.md and follow it exactly. Your worker name is `<name>`. Pick your next ready
   feature and never wait for a human."*
4. Check in at checkpoints, in **one place, GitHub Issues**: filter `needs-human`, read the pinned Status, and merge
   or trim the planner's `plan:` PR.

Full walkthrough: [docs/quickstart.md](docs/quickstart.md).

## How it works

- **Specs are the source of truth.** `specs/` holds the mission, the stack, the roadmap and one spec per feature,
  versioned with the code. Agents reload them every run.
- **Issues are the human's view.** Each feature spec gets an issue (a link, never a copy) that closes when the
  feature is done. Agents file `needs-human` issues for judgment calls, and take no default on `one-way-door` ones.
  The watchdog files `main-red`.
- **Names people can read.** A feature's ID is its folder name (`specs/features/map-data/`), and PR titles are
  Conventional Commits: `feat(map-data): ...`, `fix(map-data): ...`, `fix: ...`, `docs:`, `contract:`, `plan:`.
  `specs/milestones.toml` says what ships when, in priority order, for both profiles; each milestone is also a
  GitHub milestone, and `ship.py` turns a finished one into a one-page walkthrough.
- **The loop** (in the installed [AGENTS.md](template/parts/agents-common.md)): pick the first ready feature, build
  in a worktree (full size claims it with a draft PR first), pass CI, write a done note, merge. **Must** rules each name the check that enforces them (ownership, a green
  PR, no conflict markers or debug leftovers, a warning on Validation edits), or say *on you* where no check can
  (never inventing data or committing secrets). **Prefer** rules are engineering judgment (PR size, splitting along seams).

## What's in this repo

| Path | What |
|---|---|
| `install.py` | Installs into a project, or switches its profile/size later |
| `package.json`, `bin/agent-brigade.js` | The `npx agent-brigade` wrapper: finds Python 3.11+ and runs `install.py` |
| `template/` | Exactly what gets installed: `common/` plus one profile overlay, and `parts/` that become `AGENTS.md` |
| `template/common/.agents/scripts/` | `check_ownership` · `check_markers` · `check_gates` · `status` · `sync_issues` · `ship` · `watchdog` (+ `verify_release` · `demo_snapshot` for hackathons). Stdlib Python, all tested |
| `docs/` | Guides for people, never installed: [quickstart](docs/quickstart.md), [config reference](docs/config.md), [glossary](docs/glossary.md), [roles](docs/roles.md), [planner](docs/planner.md), [review rubric](docs/review.md), [briefing](docs/briefing.md), [budget](docs/budget.md), [remote mode](docs/remote.md), [upgrading](docs/upgrading.md), [stability (1.x promise)](docs/stability.md), [integrations](docs/integrations/) |
| `docs/hackathon/` | [Overnight run](docs/hackathon/overnight.md), [preflight](docs/hackathon/preflight.md), [plan bake-off](docs/hackathon/plan-bakeoff.md), [judge agent](docs/hackathon/judge-agent.md), [demo snapshot](docs/hackathon/demo-snapshot.md), [pitch](docs/hackathon/pitch.md) |
| `docs/project/` | [One-way doors](docs/project/one-way-doors.md), [weekly routine](docs/project/weekly.md), [budget](docs/project/budget.md) |
| `tests/` | Unit tests for `install.py` and every script |
| `dev/`, `.agents/config.toml` | The kit's own mission, decisions and milestone, linted by its CI |
| `CHANGELOG.md`, `LICENSE` | Release notes; MIT |
| `examples/` | [mini-hackathon](examples/mini-hackathon/) and [mini-project](examples/mini-project/): toy projects whose tests replay the loop against the real checks |

## What each failure turned into

| At ShellHacks | In the kit |
|---|---|
| Agents ran out of work every 10–30 min | The planner drafts the next batch into a `plan:` PR, and blocked agents file an issue and switch tasks |
| Sessions died; laptops ran out of RAM and disk | `watchdog.py` (heartbeats, restarts, resource alerts) + remote mode |
| A human merged conflict markers into `main` | `check_markers.py` in the pre-commit hook **and** CI, plus `enforce_admins` ([preflight](docs/hackathon/preflight.md); the installer's one-line protection command leaves it off) |
| An untested 1,191-line feature merged 4 min before the deadline | `check_gates.py`: the final milestone's freeze, enforced in CI |
| The live demo throttled on a free-tier database | Production load test in preflight, `demo_snapshot.py`, `verify_release.py` |
| The team couldn't explain the code to judges | A briefing and judge agent scheduled hours before judging |
| What needed a human was scattered | GitHub Issues: `needs-human`, `one-way-door`, `main-red`, and a pinned Status |

## Bringing it to a hackathon

This is process tooling, like your editor config. It contains no project code. Most events allow pre-existing
tooling; check the rules, and disclose it. Suggested line for your submission:

> We used agent-brigade (github.com/Eric-Zhang-Developer/agent-brigade), an open process template for coordinating
> coding agents. All project code was written during the event.

## Credits

Built from the protocol the ShellHacks 2026 "Common Ground" team ran on Sperry Tech's Gridlock track:
[Daniel](https://github.com/fradicus), [Kiro](https://github.com/kirolosmaikel-ops),
[Sharan](https://github.com/iKnow24) and [Eric Zhang](https://github.com/Eric-Zhang-Developer).
The spec-driven method is adapted from the DeepLearning.AI × JetBrains spec-driven development course.

## License

[MIT](LICENSE). To contribute, see [CONTRIBUTING.md](CONTRIBUTING.md).
