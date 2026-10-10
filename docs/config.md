# Config and file formats

The reference for every file the installed scripts read. The installed `.agents/config.toml` carries the same
defaults as comments, so a project needs no link back here.

## What an install writes
```
AGENTS.md                     rules + the loop (from template/parts/), never overwritten once it exists
CLAUDE.md                     @AGENTS.md
.agents/config.toml           settings (below)
.agents/scripts/*.py          refreshed on every re-install
.agents/hooks/pre-commit      enabled with git config core.hooksPath .agents/hooks
specs/                        mission, tech-stack, roadmap, features/_template, decisions/
specs/milestones.toml         what ships when (both profiles)
NOW.md, specs/review-paths.toml   project only
changes/                      done notes
.github/workflows/ci.yml  .github/pull_request_template.md  .github/ISSUE_TEMPLATE/needs-human.md
```

## `.agents/config.toml`
Every key is optional. The defaults are shown. `agents.reporter` and `[budget]` are read by agents and people,
not by the scripts.

```toml
schema = 3                     # layout version, written by the installer; it stops on an older one
profile = "hackathon"          # hackathon | project
size = "full"                  # lite | full

[paths]
specs = "specs"
changes = "changes"
reports = "reports"            # deploy receipts, final report

[ownership]
frozen = ["AGENTS.md", "CLAUDE.md", ".agents/", ".github/"]   # only `contract:` PRs may change these
open = []                      # any PR may change these (project: ["NOW.md"])

[agents]
max_parallel = 3               # lite: 1
reporter = ""                  # worker that refreshes the Status issue

[pr]
warn_lines = 400               # CI warns (never fails) above this; 0 = off
exclude = []                   # prefixes not counted

[markers]
debug_patterns = ['^\s*debugger;?\s*$', '^\s*breakpoint\(\)', '^\s*import pdb', 'console\.log\(']
ignore = []

[watchdog]
heartbeat_minutes = 20
stale_claim_minutes = 45
close_claim_minutes = 60
main_red_minutes = 20
min_free_disk_gb = 10
min_free_ram_gb = 2
restart = ""                   # shell template: {worker} {worktree}
alert = ""                     # shell template: {message}

[release]
url = ""
health_path = "/api/health"    # must return JSON {"commit": "<sha>"}
smoke_paths = ["/"]
snapshot_paths = ["/"]
secret_patterns = ["sk-", "sk_live_", "AIza", "ghp_", "github_pat_", "xox", "mongodb+srv://", "postgres://", "-----BEGIN"]

[budget]
monthly_usd = 0
reserve_final_hours = 3
```

## Feature spec front matter (`specs/features/<slug>/spec.md`)
The folder name is the feature's ID: lowercase-kebab, at most 32 characters, not `shipped`, `contract`, `plan`,
`docs` or `revert`. It names the PR scope (`feat(<slug>)`), the done note (`changes/<slug>.md`) and the branch.
```yaml
---
name: One line
depends_on: [map-data]         # slugs, in features/ or shipped/
owns: [src/report/, tests/test_report]   # path prefixes, not globs; no overlap with another in-flight feature
assignee: ""                   # a worker name; empty = anyone
bootstrap: false               # at most one feature may be true; it may change anything and merges first
---
```
What ships when, and in what order, is in `specs/milestones.toml`, not in the spec.

## PR titles ([Conventional Commits](https://www.conventionalcommits.org/))
| Title | Meaning | May change |
|---|---|---|
| `feat(<slug>): ...` | Build the feature (full size: a draft PR is the claim) | its `owns`, its spec folder, `changes/<slug>.md`, `specs/decisions/<slug>-*`, `open` paths |
| `fix(<slug>): ...` | Repair a feature in flight, done or shipped; also `refactor`, `perf`, `test`, `chore`, `style` | same as `feat` |
| `fix: ...` (no scope) | Shared code with no spec; same types | anything except `frozen`, `specs/` (decisions allowed), `changes/` and in-flight features' `owns` |
| `docs: ...` | Status and prose | `open` paths, plus Markdown outside `specs/`, `changes/`, `frozen` and in-flight `owns` |
| `contract: ...` | Contract change, additive only | `frozen` paths + `specs/` + `open` |
| `plan: ...` | Planner's batch or a ship; a person merges it | `specs/features/`, `specs/shipped/`, `specs/milestones.toml`, `specs/roadmap.md`, `open` paths |
| `revert: ...` or `Revert "..."` | `git revert`, found by its "This reverts commit" line | exactly the reverted commits' files |

`feat` on a feature whose done note is already on the base branch fails: use `fix(<slug>)`. A `!` after the type
(`feat(api)!:`) is accepted and means nothing extra.

## GitHub labels (created by `sync_issues.py` on the first push to `main`)
| Label | Filed by | Means |
|---|---|---|
| `feature` | `sync_issues.py` | One per feature spec, matched by a hidden `<!-- spec: <slug> -->` line, on its milestone; closes when `changes/<slug>.md` lands |
| `needs-human` | agents | A judgment call: context, options, default taken, how to undo |
| `one-way-door` | agents | With `needs-human`: expensive to undo, so no default was taken |
| `blocked` | agents | Can't continue until something else happens |
| `main-red` | `watchdog.py` | `main` CI red past `main_red_minutes`; closed when green |
| `contract-change` | agents | A frozen file needs an additive change |
| `status` | `status.py --issue` | The one pinned Status issue, rewritten after every merge |

## Other files
| File | Format |
|---|---|
| `changes/<slug>.md` | Done marker, written last: 3–8 lines under `## What shipped`, `## Where it lives`, `## How to check it`, `## Gaps`. |
| `specs/decisions/<slug>-<topic>.md` | Context, options, choice, how to undo. `000-*.md` = project-wide defaults. |
| `specs/shipped/<milestone>/` | Written by `ship.py`: the milestone's done specs plus `README.md`, the release walkthrough. |
| `STOP` (repo root, on `main`) | Exists = every agent stops at its next check (they `git fetch`). The watchdog stops once `STOP` is in its own checkout. |
| `<git common dir>/agent-heartbeats/<worker>` | Touched by each agent every loop (first line: its worktree path). Shared by all worktrees; never committed. |

## `specs/milestones.toml` (both profiles)
Agents pick the first ready feature in file order: milestones top to bottom, skipping ones whose ship time has
passed, then features left to right. A spec in no milestone is backlog: listed in status, never picked. Each
milestone also becomes a GitHub milestone (with its due date) holding its features' issues.
```toml
start = ""                     # hackathon: "2026-10-10T09:00:00-04:00" in the launch commit; enables "+H:MM"

[[milestone]]
name = "v1"
ship = "2026-11-15"            # "YYYY-MM-DD" (through the end of that day, UTC) · "+H:MM" after start ·
                               # an ISO time with offset · "" = no date (no freeze, never passed)
freeze = "2d"                  # "2d", "36h" or "H:MM" before ship: only `features` + `allow` merge as feat;
                               # fixes still merge
features = ["map-data", "bots"]   # slugs, in priority order
cut = ["bots"]                 # a subset of features; rejected (feat and fix) once the freeze starts
allow = []                     # extra slugs that may merge as feat in the freeze or report window
final = false                  # the last milestone: see below
report_before = ""             # final only: from ship minus this, only fixes, reverts, docs and `allow`
```
Rules for every profile: no `feat` merges before the bootstrap feature's done note is on `main`. A final milestone
also blocks `plan:` during its freeze, allows only fixes, reverts, docs and `allow` from `report_before`, and stops
every merge at `ship`. With an empty `start`, `+H:MM` times resolve to nothing, so a hackathon's deadlines stay off
until the launch commit sets it.

## `specs/review-paths.toml` (project)
```toml
[[path]]
prefix = "db/migrations/"
owners = ["@your-github-handle"]
why = "schema is a one-way door"
```
The installer turns this into `.github/CODEOWNERS`. Turn on "Require review from Code Owners" in branch protection.

## Health endpoint (for `verify_release.py`)
`GET <url><health_path>` → `200` with JSON `{"commit": "<git sha>"}`, at least 7 hex characters.

## Script CLI
All `.agents/scripts` take `--help` and `--root PATH`. Exit codes: `0` ok, `1` findings/failure, `2` usage error.

| Script | Usage |
|---|---|
| `install.py` (kit root) | `[TARGET] --profile hackathon\|project [--lite\|--full] [--overwrite-agents] [--upgrade]` |
| `check_ownership.py` | `--lint-specs` · `--title T [--base REF]` |
| `check_markers.py` | `--staged` · `--base REF` · `--all` |
| `check_gates.py` | `--title T [--base REF] [--now ISO]` |
| `status.py` | `--issue` · `--out FILE\|-` · `[--offline] [--now ISO]` |
| `sync_issues.py` | `[--dry-run]` |
| `ship.py` | `MILESTONE [--dry-run]` |
| `watchdog.py` | `[--once] [--interval SECONDS] [--dry-run]` |
| `verify_release.py` (hackathon) | `--commit SHA [--url URL]` |
| `demo_snapshot.py` (hackathon) | `--out DIR [--url URL]` |
