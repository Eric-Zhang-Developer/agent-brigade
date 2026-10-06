# NOTES: study and plan for agent-brigade

Step 1 of the build brief. Nothing gets built until Eric approves this file.

Sources read: the ShellHacks repo at `26b3b70` (`AGENTS.md`, `specs/overnight.md`, `specs/preflight.md`,
`specs/roadmap.md` front matter, `specs/tech-stack.md`, `specs/decisions/000-overnight-defaults.md`, feature specs
F00/F09/F18, `scripts/check_ownership.py`, `scripts/ci_scope.py`, `.github/workflows/ci.yml`, `changes/F09.md`,
`release/judge-readiness.md`, `release/verify-deployment.mjs`, `reports/status.md`, `docs/spec-driven-development.md`,
`plans/README.md`, `specs/followup.md`), the post-mortem voice memo (2026-10-04), and the breakdown
"How GridBridge Was Built" (2026-09-28).

The name fits the method. A kitchen brigade is the breakdown's own analogy: the chef writes the menu (the spec),
each cook works one station (`owns`), plates go through the pass (a PR), and a checker tastes every plate (CI).

---

## 1. The problem, in one paragraph

The ShellHacks protocol worked: the spec as the only source of truth, disjoint file ownership, PR-as-claim, done
notes, defaults instead of questions. The parts that broke all depended on a human being awake. Agents ran out of
queued work every 10 to 30 minutes, which is why Eric slept 1h09m (auto-accept was already on, so permission
prompts weren't the cause). Sessions died on a 16 GB laptop. Gates were advisory. A human pushed conflict markers to
main. A 1,191-line feature merged 4 minutes before the deadline. Production was never load-tested and throttled in
front of a judge. The team couldn't explain its own product. Personal projects fail the same way, more slowly:
nothing forces a ship date, context fades between sessions, and big decisions get made casually.

**What success looks like:** the gap between necessary human interventions grows from 10–30 minutes to 5+ hours. The
human's job becomes clearing an inbox and approving a queue at checkpoints, not feeding agents.

## 2. Source inventory

Legend: **core** = shared by both profiles · **hack** = hackathon profile · **proj** = project profile ·
**drop** = not carried over (with a reason).

### Process and constitution

| Source | What it does | Fate |
|---|---|---|
| `AGENTS.md` | Rules every agent loads: spec is truth, never invent, never wait, no trailers | **core**: generalized, points at `kit.toml` |
| `CLAUDE.md` (`@AGENTS.md`) | Claude Code shim | **core** (one line; the Codex/Cursor equivalents go in integration docs) |
| `specs/overnight.md` | The loop: start-of-run checks, picking, claim, branch/PR/merge, ownership, defaults, main-red, budgets, gates, stale claims, reporting | **core** for the loop (sections 1–7, 9); **hack** for time gates and the 30-min report (sections 8, 10); Paperclip specifics → **drop** to an integration doc |
| `specs/preflight.md` | 45-min human setup: branch protection, secrets, accounts, Vercel, choose run mode, launch prompt, phone STOP, morning | **hack** `preflight.md`, made stack-neutral; GridBridge secrets/Atlas/Vercel → **drop** (domain) |
| `specs/mission.md` | Why, who, non-negotiable math | **core** template (content is domain → drop) |
| `specs/tech-stack.md` | Stack, layout, change-scoped Checks | **core** template; the "Checks" section pattern kept |
| `specs/roadmap.md` | Front matter: run_start, lanes, frozen_paths, gates, stretch, local_workers; feature table | Split: machine config → **`kit.toml`**/`gates.toml`; the human table stays in **core** `roadmap.md` |
| `specs/features/*/spec.md` | Front matter (id, name, lane, agent, phase, depends_on, owns, cut, bootstrap) + Plan/Requirements/Validation/Defaults | **core** `_template/spec.md`, unchanged format |
| `specs/decisions/000-overnight-defaults.md` | Project-wide defaults table + ambiguity rules | **core**: ambiguity rules generalized into `method.md`; the table becomes a template |
| `specs/decisions/C*.md`, `F*-*.md` | 135 per-decision records | **core** `decisions/_template.md` (context, options, choice, how to undo) |
| `specs/context/` (demo/sponsor feedback) | Human feedback written into the repo | **hack** pattern: "demo early, write feedback into the spec" in `overnight.md`; folder created by init |
| `specs/followup.md`, `vocabulary.md` | Product direction, shared terms | **drop** (domain); vocabulary → **core** glossary pattern |
| `changes/<ID>.md` | The done marker, 3–8 lines | **core**, unchanged |
| `reports/status.md` | 30-min dated checkpoint | **core** `status_report.py` (hackathon: every 30 min; project: per session) |
| `release/judge-readiness.md` | 70/100 judge-style audit that caught prod serving an unreviewed commit | **hack** `judge-agent.md` (rubric + 5 hardest questions) |
| `release/verify-deployment.mjs` (+test) | Prod serves expected commit, home 200, health 200, bundles have no secret markers | **core** `verify_release.py` (stdlib port, configurable markers and smoke paths) |
| `release/deploys.md` | Dated deploy receipts | **core**: `verify_release.py` appends a receipt |
| `docs/spec-driven-development.md` | Condensed DeepLearning.AI × JetBrains SDD guide | **core** `method.md` (credited, rewritten in our words, not copied) |
| `plans/` A–E | Five competing plans | **drop** content; **hack** gains `plan-bakeoff.md` (score N plans on one table, keep/drop with reasons) |
| `docs/Sperry-Tech-Challenge`, `docs/context` | Sponsor material | **drop** (domain, sponsor-owned) |

### Scripts and CI

| Source | What it does | Fate |
|---|---|---|
| `scripts/check_ownership.py` | Parses spec front matter; lints overlapping `owns`; checks PR title prefix vs changed files; bootstrap/contract/revert rules | **core**, ported almost as-is (stdlib already); frozen paths read from `kit.toml` |
| `scripts/ci_scope.py` | docs-vs-full diff classifier | **core**: folded into the CI workflow as a `--scope` mode, so docs-only PRs stay fast |
| `.github/workflows/ci.yml` | Required `ci` check: scope → spec lint → ownership → parallel jobs | **core** `ci/ci.yml` template with a placeholder project-test step |
| `load.yml`, `azure-pipelines.yml`, `ci/generate_tests.py` | Atlas load, Azure test generation | **drop** (stack-specific) |
| `scripts/dev.sh`, `check_*_traces.mjs` | Domain dev/trace tooling | **drop** |
| `pipeline/`, `web/`, `data/`, `schemas/`, `tests/` | GridBridge product | **drop** (project code; Hard rule 1). Only the *pattern* "golden test from a worked example" survives |

### Not in the repo, but in the memo/breakdown (new)

| Lesson | Becomes |
|---|---|
| Agents idle when their queue empties; "swap tasks on error" | Planner keeps the backlog at ~2× capacity; `overnight.md` rule: a blocked agent logs to the inbox and picks its next ready feature |
| Couldn't sleep without control | `status_report.py` + `docs/briefing.md` good enough to replace checking in; inbox designed for 5-minute batch review |
| Conflict markers pushed to main by a human | `check_markers.py` in pre-commit **and** CI; preflight sets `enforce_admins: true` |
| 1,191-line PR 4 min before deadline | `check_gates.py`: hard freeze + PR size cap that tightens near the deadline |
| Free-tier DB throttled during judging | Preflight load test against prod; `demo-snapshot.md` static fallback; "stack choice is a one-way door" in both profiles |
| 16 GB / 256 GB laptop running 6 agents | `watchdog.py` checks disk/RAM; `kit.toml` caps parallel agents per machine; remote-mode doc |
| Rate limits ran out mid-run | `budget.md` routing + reserve for final hours |
| CI grew to 10 minutes | Change-scoped CI from day one; "CI speed is feature work" in `method.md` |
| Demo needed 5–10 min, slot was 3 | `pitch.md`: 45-second core loop, 3-min pitch, 2-min Q&A; demo-scope list |
| Feature creep (login, mobile app) | Roadmap template gets a `not_doing` list (from C16) |
| Couldn't explain the product to judges | Judge agent + briefing run as a gate hours before judging, not optional |
| Teammate couldn't steer agents | `roles.md` "Your first hour" for a newer teammate: one owned feature, the loop, what not to touch |
| Staged ambition (R0 safe demo … R5 vision) | `roadmap.md` template stages; `gates.toml` ties gates to stages |
| Spec/docs ballooned and drifted | Briefing capped at one page; `method.md` rule: a spec change ships in the same PR as the code |

## 3. Proposed core / profile split

Two dials, not one. **Profile** sets the clock: a deadline, or continuity. **Size** (`lite`/`full`) sets the
ceremony and parallelism. Any profile works with one agent or many, so multi-agent personal projects are
first-class: `project` + `full` runs the same parallel loop as a hackathon, minus the deadline gates.

| Capability | core (shared logic) | hackathon profile | project profile |
|---|---|---|---|
| Constitution | mission / tech-stack / roadmap templates | roadmap has stages R0–R5 + `not_doing` | roadmap has milestones + `not_doing` |
| Feature loop | spec template, claim → build → CI → done note → merge, defaults-then-log | self-merge on green | self-merge on green, except `review-paths` |
| Ownership | `check_ownership.py`, `kit.toml` frozen paths, `[C<n>]` / `[FIX-]` / `[REVERT-]` | same | same (lite: lanes off) |
| Time pressure | `check_gates.py` (one script, reads either file) | `gates.toml`: freeze, hard stop, PR size cap | `milestones.toml`: ship dates, cut lists, milestone freeze |
| Humans held to the rules | `check_markers.py` + `hooks/pre-commit` + CI | preflight: `enforce_admins: true` | same |
| Judgment calls | `inbox/needs-human.md` | inbox reviewed hourly | inbox + `one-way-doors.md` (no default allowed) |
| Planner | `docs/planner.md` prompt → `specs/proposed/` | hourly, 2× backlog | weekly (`weekly.md`) |
| Status | `status_report.py` → `reports/status.md` | every 30 min | per session; feeds `NOW.md` |
| Resume point | n/a | `reports/status.md` | `NOW.md`: read first, update last |
| Briefing | `docs/briefing.md` prompt | before judging (gate) | weekly |
| Keep-alive | `watchdog.py` + `docs/remote.md` | overnight on a cloud box | while you sleep or are in class |
| Budget | `docs/budget.md` routing table | reserve the final hours | monthly cap (`budget.md`) |
| Release | `verify_release.py` | + `judge-agent.md`, `demo-snapshot.md`, `pitch.md` | + review-paths gate |
| Onboarding | `quickstart.md`, `roles.md`, `glossary.md` | `preflight.md`, `plan-bakeoff.md` | n/a |
| Upgrading | `docs/upgrading.md` | lite → full | hackathon → project (switch profile, add NOW.md + doors, relax gates) |

### How the kit lands in a user's repo

`npx degit <owner>/agent-brigade my-project && python core/scripts/init.py --profile hackathon --full`

- `core/` and `profiles/` stay in place. They're the kit, and `AGENTS.md` points at them by path.
- `init.py` writes `kit.toml` and copies templates into `specs/`. It installs `.github/workflows/ci.yml`, the PR
  template and the pre-commit hook. In project mode it adds `NOW.md` and generates `.github/CODEOWNERS` from
  `review-paths.toml`. It never overwrites a file, so re-running it is how you upgrade.
- **The kit's own dogfood specs live in `dev/`, not `specs/`.** Otherwise every degit copy would inherit
  agent-brigade's roadmap. `degit.json` removes `dev/` on copy, and `init.py` removes it too, for repos created with
  GitHub's "Use this template".

## 4. Build plan: the kit builds itself

Profile `project`, size `full`, run as the hackathon method would run it.

| ID | Feature | Owns (prefixes) | Wave |
|---|---|---|---|
| F00 | Bootstrap: layout, `kit.toml`, `AGENTS.md`, `dev/specs` constitution + all feature specs, shared `core/scripts/kitlib.py` (TOML, front matter, git helpers), port `check_ownership.py`, CI, PR template | anything (`bootstrap: true`) | 0, by me |
| F01 | `check_markers.py` + `core/hooks/pre-commit` | `core/scripts/check_markers.py`, `core/hooks/`, its tests | 1 |
| F02 | `check_gates.py` (gates.toml, milestones.toml, PR size cap) | its script, tests | 1 |
| F03 | `status_report.py` | its script, tests | 1 |
| F04 | `verify_release.py` + optional `demo_snapshot.py` | their scripts, tests | 1 |
| F05 | Core docs + templates: method, quickstart, glossary, roles, planner, briefing, budget, spec/decision/inbox templates | `core/docs/`, `core/specs/` | 1 |
| F06 | `watchdog.py` + `remote.md` + `docs/integrations/` (Claude Code, Codex, Cursor, Paperclip, Herder) | its script, tests, those docs | 2 |
| F07 | Hackathon profile | `profiles/hackathon/` | 2 |
| F08 | Project profile | `profiles/project/` | 2 |
| F09 | `init.py` + `upgrading.md` | its script, tests, that doc | 3 |
| F10 | `examples/mini-hackathon` (3 features + golden test, toy domain) | `examples/mini-hackathon/` | 3 |
| F11 | `examples/mini-project` (NOW.md, 1 milestone, 1 one-way door, lite) | `examples/mini-project/` | 3 |
| F12 | README, `docs/story.md`, CHANGELOG v0.1.0, CONTRIBUTING, LICENSE | those files | 4 |
| F13 | Final report: kept / generalized / added / dropped, gaps, questions | `dev/reports/final.md` | 4 |

**Execution.** I build F00 myself. Each later wave runs as parallel subagents, each in its own git worktree, each
running the loop: draft PR `[F0n]` as the claim, build, tests plus the kit's own checks, write
`dev/changes/F0n.md` last, mark ready. Between waves I review each diff and merge (I'm the checkpoint human). Bugs
found after a merge land as `[FIX-F0n]`. Shared-file changes land as `[C<n>]`. The git history shows the whole
protocol.

**Stack for the kit itself.** Python 3.11+, stdlib only (`tomllib`, `unittest`, `urllib`, `subprocess`). Every
script gets `--help` and a `--root` argument, so CI can run it against `examples/*`. CI runs the unit tests, then
runs each check against both examples.

## 5. Decisions I'm taking unless you object (logged in `dev/specs/decisions/` once built)

1. **Profile × size are separate dials**, so multi-agent works in project mode. Counter: solo users see claim
   ceremony they don't need. Lite hides it; it costs a few seconds per PR.
2. **review-paths → CODEOWNERS.** GitHub's native "require code owner review" enforces this better than a script,
   so no custom checker.
3. **Watchdog restarts through a command template** in `kit.toml` (for example a `tmux send-keys …` or
   `claude --continue …` line). The script stays harness-agnostic; per-harness recipes live in integration docs.
   It detects dead sessions via heartbeat files that agents touch each loop.
4. **One `check_gates.py`** reads `gates.toml` or `milestones.toml`, depending on the profile.
5. **`demo_snapshot.py`** fetches a listed set of URLs or API routes into a static folder, with a manifest pinned
   to the commit. The pattern doc explains how an app falls back to it. It doesn't try to crawl SPAs.
6. **The toy domain for the examples** is generic (a word-frequency CLI, or similar). No hackathon-shaped project
   code.
7. **No trailers on commits** (your global rule wins over tooling defaults).

## 6. Risks

| Risk | Mitigation |
|---|---|
| Watchdog "restart" can't be truly harness-agnostic | Command template + heartbeat files; honest limits written into `remote.md` |
| Kit looks like pre-written hackathon code | Zero domain logic; README states it's process tooling; disclosure snippet for Devpost |
| Docs bloat (the ShellHacks failure) | Every doc has a reading-time target; glossary instead of repeated definitions; F13 counts lines |
| Scripts work on the kit but not on real repos | Every check runs against both examples in CI, plus `init.py` tested on a fresh temp clone for both profiles |
| Self-merge without GitHub (local-only) can't show real PRs | Needs a decision below |
| Personal details leaking from the memo | Only `docs/story.md` text, verbatim apart from typos; nothing from the memo |

## 7. Open questions for Eric

1. **The repo is already public and empty.** To dogfood with real draft PRs and Actions, I need to push. My
   recommendation: make it private now, push and run the loop there, and you flip it public at v0.1.0. Alternative:
   build locally with branches and merge commits, and push once at the end (a real history, but no PR claims).
2. **License:** MIT (proposed). Confirm.
3. **KnightHacks date:** the memo says "next weekend." If it's Oct 9–11, v0.1.0 should be done before then.
4. **`docs/story.md` has an `[OPTIONAL: …]` paragraph** about the job search. Keep it, drop it, or leave the marker
   for later? Default: leave it as written and ask again at F12.
5. **Teammate handles for the credits:** placeholders `[Daniel]`, `[Kyro]`, `[Sharan]` until you send handles.
6. **GitHub template flag + description:** set at publish time, with your approval.
