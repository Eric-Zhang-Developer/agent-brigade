# Roadmap: agent-brigade v0.1.0

The kit's own settings are in `kit.toml`, and the milestone is in `dev/specs/milestones.toml`.

## Milestone: v0.1.0
Everything in the brief ships. There's no hard date (Eric, 2026-10-06), so `milestones.toml` leaves `ship` empty
and no freeze applies.

## Checklist (built on one branch, `v0.1.0`; one commit per item)

| # | Item |
|---|---|
| 1 | Contracts: `kit.toml`, `AGENTS.md`, `core/docs/config.md`, `core/docs/method.md` |
| 2 | Scripts + tests: kitlib, check_ownership, check_markers, check_gates, status_report, watchdog, verify_release, demo_snapshot, init |
| 3 | CI: kit's own workflow, `core/ci/` templates, pre-commit hook |
| 4 | Core docs + spec templates |
| 5 | Hackathon profile |
| 6 | Project profile |
| 7 | Examples: mini-hackathon, mini-project |
| 8 | README, story, CHANGELOG, CONTRIBUTING |
| 9 | Final report (`dev/reports/final.md`) |

## How the kit itself is built
Eric chose (2026-10-06) to build v0.1.0 on a single branch in one session, not as per-feature PRs, because
the full loop is overhead for a single builder. The examples demonstrate the full loop instead.

## Not doing (v0.1.0)
- A GUI, dashboard or web app of any kind
- Any third-party Python dependency, or a package on PyPI or npm
- Hosting or running agents for the user (the watchdog drives commands the user configures)
- Paperclip-, Herder- or harness-specific logic in core (notes only, in `core/docs/integrations/`)
- Publishing, going public, choosing a license (Eric decides: no license for now)
