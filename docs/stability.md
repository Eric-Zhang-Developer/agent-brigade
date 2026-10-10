# Stability: what 1.x will not break

From 1.0 on, a project installed with this kit keeps working on every 1.x release without manual migration
(decision D13). This page lists exactly what that covers. Everything here is read from the code, and each item names
the file that defines it. `tests/test_contract.py` parses the tables on this page and fails CI when the code and
this page disagree; `tests/test_upgrade.py` installs v0.4.0, upgrades it to the current kit and checks the project
still works.

## The promise

- **1.x keeps working.** Re-running the installer from any later 1.x release (`npx agent-brigade@latest --profile
  <same> ...`) on a 1.0 project needs no manual steps, and the project's `.agents/config.toml`, specs, milestones,
  done notes, PR titles and labels keep meaning what they meant.
- **Breaking anything on this page means 2.0.** Removing or renaming a flag, config key, script, label, PR-title
  type, done-note heading or specs path; changing a default; changing an exit code's meaning; narrowing an accepted
  format. Adding is not breaking: new flags, keys (with defaults that keep the old behavior), scripts, labels and
  accepted formats can arrive in any 1.x.
- **Reading version numbers.** `MAJOR.MINOR.PATCH` (`package.json`): PATCH fixes bugs, MINOR adds things, MAJOR
  breaks something on this page. `schema` in `.agents/config.toml` is a separate number: the layout version the
  installer checks (below).
- **What an upgrade touches.** The installer refreshes only the kit-owned folders `.agents/scripts/` and
  `.agents/hooks/` (`KIT_OWNED` in `install.py`) and creates files that are missing. It never rewrites
  `AGENTS.md`, `CLAUDE.md`, `.agents/config.toml` (beyond `profile`/`size`/`schema`), `specs/`, `NOW.md`,
  `.github/workflows/ci.yml` or the PR and issue templates. So a 1.x release that improves the rules in `AGENTS.md`
  or the CI workflow reaches an existing project only through `--overwrite-agents` (which regenerates `AGENTS.md`
  and drops local edits) or by hand. The promise is that the old copy keeps working, not that it updates itself.

## Public surface

### Command line: the installer

`npx agent-brigade [target] --profile hackathon|project [--lite | --full] [--overwrite-agents] [--upgrade]` runs
`install.py` (`bin/agent-brigade.js` finds Python 3.11+ and passes every argument through). `python3 install.py`
from a clone takes the same arguments.

| Script | Flags | Exit codes |
|---|---|---|
| `install.py` | `--profile`, `--lite`, `--full`, `--overwrite-agents`, `--upgrade` | 0 installed; 1 stopped before touching anything (older schema without `--upgrade`, newer schema, a v0.1 `kit.toml` layout, Python older than 3.11, or no Python 3.11+ found by `bin/agent-brigade.js`); 2 usage (bad flag, target not a folder, target is the kit itself) |

- `target` is optional and defaults to the current directory. `--lite` and `--full` are exclusive; with neither, the
  size already in `.agents/config.toml` is kept, else `full`.
- Re-running with the same arguments is safe: files that exist are kept, kit-owned files that already match are not
  rewritten.

### Installed scripts

Every script lives in `.agents/scripts/`, runs as `python3 .agents/scripts/<name>`, takes `--root` (default: the
nearest parent with `.agents/config.toml`, `lib.parser`/`lib.find_root`) and `--help`, and exits 2 on a usage error
(argparse). Common to both profiles: `template/common/.agents/scripts/`; hackathon only:
`template/hackathon/.agents/scripts/`. `lib.py` is a shared module, not a command; its function names are not
promised.

| Script | Flags | Exit codes |
|---|---|---|
| `check_gates.py` | `--root`, `--title`, `--base`, `--now` | 0 may merge (warnings never fail); 1 rejected, unknown title, or bad `milestones.toml`; 2 usage |
| `check_markers.py` | `--root`, `--staged`, `--base`, `--all` | 0 clean; 1 a conflict marker or debug leftover; 2 usage (exactly one mode is required) |
| `check_ownership.py` | `--root`, `--lint-specs`, `--title`, `--base` | 0 ok; 1 spec lint errors, a file outside what the title allows, or an unusable title; 2 neither `--lint-specs` nor `--title` |
| `pr_ready.py` | `--root` | 0 ready; 1 `gh` missing or a query failed; 2 usage; 3 closed, merged or draft; 4 merge conflicts; 5 changes requested; 6 unresolved review threads; 7 failing checks; 8 checks pending |
| `ship.py` | `--root`, `--dry-run` | 0 archived (or would); 1 no such milestone, or nothing in it is done; 2 usage |
| `status.py` | `--root`, `--out`, `--issue`, `--now`, `--offline` | 0 written; 1 `--issue` could not update the issue; 2 usage (pass `--out` or `--issue`) |
| `sync_issues.py` | `--root`, `--dry-run` | 0 in sync; 1 `gh` unavailable, or a change failed; 2 usage |
| `verify.py` | `--root`, `--slug`, `--worktree` | 0 pass, or not set up; 1 fail, timeout, or a bad command template; 2 usage (including a bad slug) |
| `watchdog.py` | `--root`, `--once`, `--interval`, `--dry-run` | 0 stopped by `STOP` or `--once` finished; 1 another watchdog holds the lock; 2 usage |
| `demo_snapshot.py` | `--root`, `--out`, `--url` | 0 every path saved; 1 a path failed; 2 no usable URL |
| `verify_release.py` | `--root`, `--commit`, `--url` | 0 every check passed; 1 a check failed; 2 no usable URL |

Positional arguments: `pr_ready.py [PR]` (number, URL or branch) and `ship.py <milestone>`.

The pre-commit hook (`.agents/hooks/pre-commit`, enabled with `git config core.hooksPath .agents/hooks`) runs
`check_markers.py --staged` and `check_ownership.py --lint-specs`, and exits 0 with a note when no Python 3.11+ is
found.

### `.agents/config.toml`

Every key is optional; a missing key or table takes its default from `DEFAULTS` in
`template/common/.agents/scripts/lib.py` (`load_config` merges the file over it). "Agents" in the last column means
no script reads the key: the installed `AGENTS.md` or a person does.

| Key | Default | Read by |
|---|---|---|
| `schema` | `3` | `install.py` |
| `profile` | `"hackathon"` | `install.py`, `status.py` |
| `size` | `"full"` | `install.py`, `status.py`, `watchdog.py` |
| `paths.specs` | `"specs"` | every script that reads specs |
| `paths.changes` | `"changes"` | every script that reads done notes |
| `paths.reports` | `"reports"` | `verify_release.py` |
| `ownership.frozen` | `["AGENTS.md", "CLAUDE.md", ".agents/", ".github/"]` | `check_ownership.py` |
| `ownership.open` | `[]` | `check_ownership.py` |
| `agents.max_parallel` | `3` | `status.py` |
| `agents.reporter` | `""` | agents |
| `pr.warn_lines` | `400` | `check_gates.py` |
| `pr.exclude` | `[]` | `check_gates.py` |
| `markers.debug_patterns` | `['^\s*debugger;?\s*$', '^\s*breakpoint\(\)', '^\s*import pdb', 'console\.log\(']` | `check_markers.py` |
| `markers.ignore` | `[]` | `check_markers.py` |
| `watchdog.heartbeat_minutes` | `20` | `watchdog.py` |
| `watchdog.stuck_minutes` | `60` | `watchdog.py` |
| `watchdog.max_restarts` | `2` | `watchdog.py` |
| `watchdog.stale_claim_minutes` | `45` | `watchdog.py` |
| `watchdog.close_claim_minutes` | `60` | `watchdog.py` |
| `watchdog.main_red_minutes` | `20` | `watchdog.py` |
| `watchdog.min_free_disk_gb` | `10` | `watchdog.py` |
| `watchdog.min_free_ram_gb` | `2` | `watchdog.py` |
| `watchdog.restart` | `""` | `watchdog.py` |
| `watchdog.alert` | `""` | `watchdog.py` |
| `release.url` | `""` | `verify_release.py`, `demo_snapshot.py` |
| `release.health_path` | `"/api/health"` | `verify_release.py`, `demo_snapshot.py` |
| `release.smoke_paths` | `["/"]` | `verify_release.py` |
| `release.snapshot_paths` | `["/"]` | `demo_snapshot.py` |
| `release.secret_patterns` | `["sk-", "sk_live_", "AIza", "ghp_", "github_pat_", "xox", "mongodb+srv://", "postgres://", "-----BEGIN"]` | `verify_release.py` |
| `budget.monthly_usd` | `0` | agents |
| `budget.reserve_final_hours` | `3` | agents |
| `verify.command` | `""` | `verify.py`, `status.py` |
| `verify.timeout` | `300` | `verify.py` |

- The installer writes `max_parallel = 1` for lite and `open = ["NOW.md"]` for the project profile
  (`render_config` in `install.py`); the table shows the defaults a missing key falls back to.
- Shell templates and their placeholders are promised: `watchdog.restart` (`{worker}`, `{worktree}`),
  `watchdog.alert` (`{message}`), `verify.command` (`{slug}`, `{worktree}`, `{out}`).

**`schema`.** The kit writes `SCHEMA` from `lib.py` (3). On install, `install.py` (`schema_problem`) stops when the
project's schema is older and `--upgrade` wasn't passed, or newer than the kit's; a config with no `schema` key
reads as 2. With `--upgrade` it stamps the kit's number. Schema stays 3 for 1.0 (issue #7, default A).

### `specs/` layout

Relative to `paths.specs` (`lib.py`: `load_specs`, `load_shipped`; `check_ownership.py`: `allowed`).

| Path | What it is |
|---|---|
| `specs/features/<slug>/spec.md` | A feature. The folder name is its ID. Folders starting with `_` (the `_template`) are skipped. |
| `specs/shipped/<milestone>/<slug>/spec.md` | A shipped feature, moved there by `ship.py`, which also writes `specs/shipped/<milestone>/README.md`. |
| `specs/decisions/<slug>-<topic>.md` | A decision record; a feature's PR may add its own. |
| `specs/milestones.toml` | Milestones (below). |
| `specs/review-paths.toml` | Project profile: `[[path]]` entries with `prefix` and `owners`, turned into `.github/CODEOWNERS` by the installer. |
| `specs/context/findings.md` | Hackathon profile: a `plan:` PR may change it. |
| `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md` | Read by agents every run; `roadmap.md` is changed by `plan:` PRs. |

### Slugs and spec front matter

Slugs (`lib.SLUG`, `lib.slug_error`): lowercase letters and digits in hyphen-separated words
(`^[a-z0-9]+(?:-[a-z0-9]+)*$`), at most 32 characters, and not one of `shipped`, `contract`, `plan`, `docs`, `revert`.

Front matter (`lib.front_matter`) is a `---` block of top-level `key: value` lines, `key: [a, b]` lists, or
`key:` followed by `  - item` lines; `true`/`false`, integers and quoted strings; `#` comments.

| Key | Meaning |
|---|---|
| `name` | One line describing the outcome; the issue title and walkthrough heading. |
| `depends_on` | Slugs that must be done first. |
| `owns` | Path prefixes (not globs) this feature alone may change while in flight. |
| `bootstrap` | `true` on at most one feature: it may change anything and merges before any other feature. |
| `assignee` | A worker name, or empty for anyone (read by agents, not scripts). |

### `specs/milestones.toml`

`lib.load_milestones` and the comments in `template/*/specs/milestones.toml`.

| Field | Accepted values |
|---|---|
| `start` | Top level. An ISO time with a UTC offset, or `""` (no start; offsets resolve to no date). |
| `name` | The milestone's name: a GitHub milestone title and the `ship.py` argument. |
| `ship` | `"+H:MM"`, `"+36h"` or `"+2d"` after `start`; `"YYYY-MM-DD"` (through the end of that day, UTC); an ISO time with a UTC offset; `""` = no date. |
| `freeze` | A span before `ship`: `"H:MM"`, `"36h"` or `"2d"`. |
| `final` | `true` on the last milestone: enables `report_before` and the hard stop at `ship`. |
| `report_before` | A span before `ship` (final milestone only). |
| `features` | Slugs in priority order. A spec in no milestone is backlog. |
| `cut` | Slugs from `features` rejected during the freeze. |
| `allow` | Slugs that may still merge as `feat` during the freeze and report window. |

The gate rules these drive are in the `check_gates.py` docstring and are part of the promise: bootstrap first,
freeze, report window, hard stop.

### Done notes

`changes/<slug>.md` on `main` marks a feature done (`lib.done_ids`). Its headings, in this order
(`template/parts/agents-common.md`, loop step 5; read by `lib.note_section`, `status.py`, `check_gates.py`):

- `## What shipped`
- `## Where it lives`
- `## How to check it`
- `## Gaps`

**The `verify:` line** (`verify.py`, the last line it prints, pasted under `## How to check it`). One of:

```
verify: `<command>` pass at <sha>[ (uncommitted changes)][ (evidence: <dir>)]
verify: `<command>` FAIL (exit <N>) at <sha>[ (uncommitted changes)][ (evidence: <dir>)]
verify: `<command>` FAIL (timed out after <seconds>s) at <sha>[ (uncommitted changes)][ (evidence: <dir>)]
verify: not set up ([verify].command is empty); the done note says `not verified`
```

`<sha>` is a short commit hash, or `unknown commit` outside git. `status.py` counts a note as verified when a line
matches `` verify: `...` pass `` and no line has `FAIL` or `not verified`; `check_gates.py` warns when a `feat` note
has neither a `verify: ` line nor `not verified`.

### PR titles

Conventional Commits (`lib.TITLE`, `lib.KINDS`, `lib.parse_title`); a `!` before the colon is accepted. GitHub's
revert button title, `Revert "..."`, counts as `revert`. What each may change is enforced by `check_ownership.py`
(`allowed`) and summarized in the installed `AGENTS.md`.

| Type | Scope | May change |
|---|---|---|
| `feat` | required: `feat(<slug>)` | the feature's `owns`, its spec folder, `changes/<slug>.md`, `specs/decisions/<slug>-*`, open paths; anything if it's the bootstrap feature |
| `fix` | optional | with a slug: the same as `feat`, for a feature in flight, done or shipped; without: anything not frozen, not in `specs/` (except `decisions/`) or `changes/`, and not owned by a feature in flight |
| `refactor` | optional | same as `fix` |
| `perf` | optional | same as `fix` |
| `test` | optional | same as `fix` |
| `chore` | optional | same as `fix` |
| `style` | optional | same as `fix` |
| `docs` | ignored | open paths, and Markdown outside `specs/`, `changes/`, frozen paths and in-flight features' `owns` |
| `contract` | ignored | frozen paths, `specs/`, open paths |
| `plan` | ignored | `specs/features/`, `specs/shipped/`, `specs/milestones.toml`, `specs/roadmap.md`, `specs/context/findings.md`, open paths |
| `revert` | ignored | exactly the files the reverted commits changed (`This reverts commit <sha>` in a commit body) |

### Issues and labels

`sync_issues.py` keeps one issue per feature spec, found by the hidden marker `<!-- spec: <slug> -->` in its body
(`MARKER`), never by title. It makes sure these labels exist (`LABELS`); the names are promised, their colors and
descriptions are not.

| Label | Used for |
|---|---|
| `feature` | one issue per feature spec |
| `needs-human` | a judgment call waiting on a person |
| `one-way-door` | a decision that's expensive to undo |
| `blocked` | work that can't continue yet |
| `main-red` | `main` CI is failing (opened and closed by `watchdog.py`) |
| `contract-change` | a frozen file needs changing |
| `status` | the pinned Status issue `status.py --issue` rewrites |
| `bug` | a bug report |
| `needs-info` | a bug report that couldn't be reproduced |

### Files outside the repo's tree

| Path | Meaning |
|---|---|
| `STOP` at the repo root | Agents stop when it's on `origin/main`; `watchdog.py` alerts and exits when it's in the checkout. |
| `<git common dir>/agent-heartbeats/<worker>` | Heartbeat file; its mtime is the heartbeat, its first line the worker's worktree path (`lib.heartbeat_dir`). |
| `<git common dir>/agent-evidence/<slug>/<UTC time>/` | The `{out}` folder `verify.py` creates and keeps. |
| `<git common dir>/watchdog.pid` | The watchdog's lock: one watchdog per repo. |

## Not promised

These can change in any 1.x release:

- **`AGENTS.md` wording.** The rules may be reworded, reordered and added to. An existing project keeps its own copy
  until it regenerates it (`--overwrite-agents`); the scripts never parse it.
- **Report formatting**: the Status issue body, `status.py --out` text, `ship.py`'s walkthrough page, the
  `deploys.md` receipts and JSON reports.
- **Script output text**, apart from the `verify:` line formats above. Exit codes are the interface; lines may be
  reworded.
- **Label colors and descriptions**, issue bodies `sync_issues.py` writes, and the PR and issue templates.
- **Flags hidden from `--help`** (`--allow-http`, for tests) and the functions inside `lib.py`.
- **Anything in the kit's own repo** that isn't installed: `docs/`, `examples/`, `dev/`, `tests/`.
- **`watchdog-state.json`** in the git common dir: internal state, rebuilt if missing.

## Known rough edges carried into 1.0

Stated so nobody mistakes them for features, and fixable in 1.x only in ways that keep the promise:

- `agents.reporter`, `budget.monthly_usd`, `budget.reserve_final_hours` and the `assignee` front-matter key are
  read by agents and people through `AGENTS.md`, not by any script. Setting them changes nothing a script does.
- Unknown keys in `.agents/config.toml`, spec front matter and `milestones.toml` are ignored silently
  (`lib._merge`, `.get(...)` reads), so a typo like `warn_line` falls back to the default without a word.
- `--upgrade` (and any re-run) refreshes only `.agents/scripts/` and `.agents/hooks/`. Rule changes in
  `AGENTS.md`, `ci.yml` and the templates reach an existing project only via `--overwrite-agents` or by hand.
- A missing `schema` key reads as 2, so a hand-written config without it stops the installer until `--upgrade`.

## Deprecations

- A renamed config key or flag keeps working under its old name for the rest of 1.x, printing a one-line warning
  that names the new one. It is listed under `## Deprecations` in `CHANGELOG.md` with the release that deprecated it,
  and removed only in 2.0.
- A removed behavior gets the same treatment where it can: warn first, remove in 2.0.
- **Schema.** `schema` stays 3 for 1.0. A bump during 1.x is allowed only if `install.py --upgrade` alone completes
  the migration, with no steps by hand; anything needing manual steps waits for 2.0.
