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
specs/gates.toml              hackathon        NOW.md, specs/milestones.toml, specs/review-paths.toml   project
changes/                      done notes
.github/workflows/ci.yml  .github/pull_request_template.md  .github/ISSUE_TEMPLATE/needs-human.md
```

## `.agents/config.toml`
Every key except `profile` is optional. The defaults are shown.

```toml
profile = "hackathon"          # hackathon | project
size = "full"                  # lite | full

[paths]
specs = "specs"
changes = "changes"
reports = "reports"            # deploy receipts, final report

[ownership]
frozen = ["AGENTS.md", "CLAUDE.md", ".agents/", ".github/"]   # only [C<n>] PRs may change these
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

## Feature spec front matter (`specs/features/<ID>-<slug>/spec.md`)
```yaml
---
id: F03                        # F<number>, unique
name: One line
lane: A                        # full size only
agent: builder                 # a role or worker name
phase: 1                       # gates can block a phase
depends_on: [F01]
owns: [src/report/, tests/test_report]   # path prefixes, not globs; no overlaps
cut: ok                        # ok | never
milestone: v1                  # project, optional
bootstrap: false               # exactly one feature may be true; it may change anything
---
```

## PR titles
| Prefix | Meaning | May change |
|---|---|---|
| `[F<n>] name` | Build feature n; a draft PR is the claim | its `owns`, `changes/F<n>.md`, `specs/features/F<n>-*`, `specs/decisions/F<n>-*`, `open` paths |
| `[FIX-F<n>] ...` | Repair after merge | same as `[F<n>]` |
| `[C<n>] ...` | Contract change, additive only | `frozen` paths + `specs/` |
| `[PLAN] ...` | Planner's batch; a person merges it | `specs/features/`, `specs/roadmap.md` |
| `[REVERT-<sha>] ...` | Plain `git revert` | exactly that commit's files |

## GitHub labels (created by `sync_issues.py` on the first push to `main`)
| Label | Filed by | Means |
|---|---|---|
| `feature` | `sync_issues.py` | One per feature spec; closes when `changes/<ID>.md` lands |
| `needs-human` | agents | A judgment call: context, options, default taken, how to undo |
| `one-way-door` | agents | With `needs-human`: expensive to undo, so no default was taken |
| `blocked` | agents | Can't continue until something else happens |
| `main-red` | `watchdog.py` | `main` CI red past `main_red_minutes`; closed when green |
| `contract-change` | agents | A frozen file needs an additive change |
| `status` | `status.py --issue` | The one pinned Status issue, rewritten after every merge |

## Other files
| File | Format |
|---|---|
| `changes/<ID>.md` | Done marker, 3–8 lines: shipped, cut, known gaps. Written last. |
| `specs/decisions/<ID>-<slug>.md` | Context, options, choice, how to undo. `000-*.md` = project-wide defaults. |
| `STOP` (repo root, on `main`) | Exists = every agent stops at its next check. |
| `<git common dir>/agent-heartbeats/<worker>` | Touched by each agent every loop (first line: its worktree path). Shared by all worktrees; never committed. |

## `specs/gates.toml` (hackathon)
Only the latest gate whose time has passed applies.
```toml
run_start = ""                 # "2026-10-10T09:00:00-04:00" in the launch commit; "" = gates off

[[gate]]
at = "0:00"                    # H:MM after run_start
only = ["F00"]

[[gate]]
at = "1:00"                    # no kind = open

[[gate]]
at = "20:00"
no_new_phase = 3               # phase >= 3 features not started before this may not start

[[gate]]
at = "30:00"
freeze = true                  # no [F<n>] except `allow`; FIX/REVERT/C fine
allow = []

[[gate]]
at = "34:00"
report = true                  # only FIX, REVERT and `allow`

[[gate]]
at = "35:30"
hard_stop = true
```

## `specs/milestones.toml` (project)
```toml
[[milestone]]
name = "v1"
ship = "2026-11-15"            # YYYY-MM-DD, or "" for no date (no freeze)
freeze_days = 3                # in [ship - freeze_days, ship], only `features` merge
features = ["F01", "F02"]
cut = ["F05"]                  # rejected once the freeze starts
```

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
All scripts take `--help` and `--root PATH`. Exit codes: `0` ok, `1` findings/failure, `2` usage error.

| Script | Usage |
|---|---|
| `install.py` (kit root) | `[TARGET] --profile hackathon\|project [--lite\|--full] [--overwrite-agents]` |
| `check_ownership.py` | `--lint-specs` · `--title T [--base REF]` |
| `check_markers.py` | `--staged` · `--base REF` · `--all` |
| `check_gates.py` | `--title T [--base REF] [--now ISO]` |
| `status.py` | `--issue` · `--out FILE\|-` · `[--offline] [--now ISO]` |
| `sync_issues.py` | `[--dry-run]` |
| `watchdog.py` | `[--once] [--interval SECONDS] [--dry-run]` |
| `verify_release.py` (hackathon) | `--commit SHA [--url URL]` |
| `demo_snapshot.py` (hackathon) | `--out DIR [--url URL]` |
