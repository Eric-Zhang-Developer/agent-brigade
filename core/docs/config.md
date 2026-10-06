# Config and file formats

The reference for every file the scripts read. If a doc and this file disagree, this file wins.

## `kit.toml` (repo root)

Every key is optional except `profile`. The defaults are shown.

```toml
profile = "hackathon"          # hackathon | project
size = "full"                  # lite | full

[paths]
specs = "specs"                # mission.md, tech-stack.md, roadmap.md, features/, decisions/, inbox/
changes = "changes"            # done notes: <changes>/<ID>.md
reports = "reports"            # status.md, deploys.md, final.md

[ownership]
frozen = ["AGENTS.md", "kit.toml", ".github/", "core/", "profiles/"]  # only [C<n>] PRs may change these
open = []                      # any PR may change these (e.g. "NOW.md")

[agents]
max_parallel = 3               # agents running at once on one machine
reporter = ""                  # who writes <reports>/status.md in full size

[pr]
max_lines = 400                # added+removed lines per [F<n>] PR; 0 = no cap
exclude = []                   # prefixes not counted (lockfiles, generated data)

[markers]
debug_patterns = ['^\s*debugger;?\s*$', '^\s*breakpoint\(\)', '^\s*import pdb', 'console\.log\(']
ignore = []                    # prefixes never scanned

[watchdog]
heartbeat_dir = ".agent-brigade/heartbeats"  # gitignored; one file per worker, touched every loop
heartbeat_minutes = 20         # older heartbeat = dead session
stale_claim_minutes = 45       # draft PR with no push: comment
close_claim_minutes = 60       # draft PR with no push: close
main_red_minutes = 20          # main red longer than this: alert
min_free_disk_gb = 10
min_free_ram_gb = 2
restart = ""                   # command template: {worker} {worktree}; empty = alert only
alert = ""                     # command template: {message}; empty = print only

[release]
url = ""                       # production origin, https://...
health_path = "/api/health"    # must return JSON {"commit": "<sha>"}
smoke_paths = ["/"]
snapshot_paths = ["/"]         # what demo_snapshot.py saves
secret_patterns = ["sk-", "sk_live_", "AIza", "ghp_", "github_pat_", "xox", "mongodb+srv://", "postgres://", "-----BEGIN"]

[budget]
monthly_usd = 0                # project profile: cap; 0 = none set
reserve_final_hours = 3        # hackathon profile: keep this much budget for the end
```

The kit's own development repo also sets `kit_dev = true`. `init.py` treats that as "this is a fresh copy of the
kit": it removes `dev/` and writes a new `kit.toml`.

## Feature spec front matter (`<specs>/features/<ID>-<slug>/spec.md`)

```yaml
---
id: F03                        # F<number>, unique
name: One line
lane: A                        # full size only; any label
agent: builder                 # a role or worker name
phase: 1                       # integer; gates can block a phase
depends_on: [F01]              # IDs that must be done first
owns: [src/report/, tests/test_report]   # path prefixes this feature may change
cut: ok                        # ok | never
milestone: v1                  # project profile, optional
bootstrap: false               # exactly one feature may be true; it may change anything
---
```

`owns` entries are **path prefixes**, not globs: `src/report/` covers a folder, `tests/test_report` covers every
file starting with that. No entry may be a prefix of another feature's entry or of a frozen path.

## PR titles

| Prefix | Meaning | May change |
|---|---|---|
| `[F<n>] name` | Build feature n. A draft PR is the claim. | its `owns`, `<changes>/F<n>.md`, `<specs>/features/F<n>-*`, `<specs>/decisions/F<n>-*`, `<specs>/inbox/F<n>-*`, `open` paths |
| `[FIX-F<n>] ...` | Repair feature n after merge | same as `[F<n>]` |
| `[C<n>] ...` | Contract change: frozen files, additive only | `frozen` paths + `<specs>/` |
| `[PLAN] ...` | Planner's proposed batch; a human merges it | `<specs>/features/`, `<specs>/roadmap.md`, `<specs>/inbox/` |
| `[REVERT-<sha>] ...` | Plain `git revert` | exactly the files that commit touched |

## Other files

| File | Format |
|---|---|
| `<changes>/<ID>.md` | Done marker, 3–8 lines: shipped, cut, known gaps. Written last. |
| `<specs>/decisions/<ID>-<slug>.md` | Context, options, choice, how to undo. `000-*.md` = project-wide defaults. |
| `<specs>/inbox/<ID>-<slug>.md` | One judgment call per file; see `core/specs/inbox/needs-human.md`. |
| `STOP` (repo root, on `main`) | Exists = every agent stops at its next check. |
| `<heartbeat_dir>/<worker>` | Touched by each agent once per loop. First line: worktree path (optional). |

## `gates.toml` (hackathon, at `<specs>/gates.toml`)

```toml
run_start = "2026-10-10T09:00:00-04:00"   # must include a UTC offset

[[gate]]
at = "0:00"                    # H:MM after run_start
only = ["F00"]                 # only these IDs may run

[[gate]]
at = "20:00"
no_new_phase = 2               # features in phase >= 2 not started yet may not start

[[gate]]
at = "30:00"
freeze = true                  # no [F<n>] except `allow`; FIX/REVERT/C still fine
allow = []
max_lines = 150                # tighter PR cap from here on

[[gate]]
at = "34:00"
report = true                  # only the reporter, FIX and REVERT

[[gate]]
at = "35:30"
hard_stop = true               # nothing merges
```

## `milestones.toml` (project, at `<specs>/milestones.toml`)

```toml
[[milestone]]
name = "v1"
ship = "2026-11-15"            # YYYY-MM-DD, or "" for no date
freeze_days = 3                # only this milestone's features may merge in [ship - freeze_days, ship]
features = ["F01", "F02"]
cut = ["F05"]                  # rejected once the freeze starts
```

## `review-paths.toml` (project, at `<specs>/review-paths.toml`)

```toml
[[path]]
prefix = "db/migrations/"
owners = ["@your-github-handle"]
why = "schema is a one-way door"
```
`init.py` turns this into `.github/CODEOWNERS`. Turn on "Require review from Code Owners" in branch protection.

## Health endpoint contract (for `verify_release.py`)

`GET <url><health_path>` → `200` with JSON containing `"commit": "<git sha>"` (at least 7 hex characters). Most
hosts expose the deployed SHA as an environment variable (e.g. `VERCEL_GIT_COMMIT_SHA`).

## Script CLI

Every script takes `--help` and `--root PATH` (default: nearest parent directory with `kit.toml`). Exit codes:
`0` ok, `1` findings/failure, `2` usage error.

| Script | Usage |
|---|---|
| `init.py` | `--profile hackathon\|project [--lite\|--full]` |
| `check_ownership.py` | `--lint-specs` · `--title T [--base REF]` |
| `check_markers.py` | `--staged` · `--base REF` · `--all` |
| `check_gates.py` | `--title T [--base REF] [--now ISO]` |
| `status_report.py` | `[--out PATH] [--now ISO] [--offline]` |
| `watchdog.py` | `[--once] [--interval SECONDS] [--dry-run]` |
| `verify_release.py` | `--commit SHA [--url URL]` |
| `demo_snapshot.py` | `--out DIR [--url URL]` |
