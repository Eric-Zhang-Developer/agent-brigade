# Hackathon: the overnight run

Everything in `core/docs/method.md`, plus a clock. Read this after `AGENTS.md` on every run.

## The shape of the weekend
| When | What | Who |
|---|---|---|
| Hours 0–2 | Read the sponsor material, run the plan bake-off (`plan-bakeoff.md`), write the constitution and specs. Turn any worked example into the golden test. | Humans + agents drafting |
| ~45 min | Preflight (`preflight.md`): repo protection, keys, the database load test. | Deploy owner |
| Launch | Bootstrap feature first. Everything else waits for its done note. | One agent |
| The long middle | The loop. The planner keeps the backlog at 2×. Demo early to mentors/sponsors, and write their feedback into `specs/context/`. | Agents; humans at checkpoints |
| Freeze − 3 h | Judge review (`judge-agent.md`) and briefing (`core/docs/briefing.md`). Fix only what they find. | Judge, briefer |
| Freeze | No new features. FIX and REVERT only, under a tighter size cap. | Gate (CI) |
| Freeze → submit | `verify_release.py` against prod, `demo_snapshot.py`, rehearse the pitch (`pitch.md`), submit early. | Demo + deploy owners |

## Gates (enforced by `check_gates.py` in CI)
`specs/gates.toml` sets `run_start` and the gates. Scale every `at` to your event: a 24-hour event isn't a
36-hour one. The template's defaults assume 36 hours:
- `only` at 0:00: bootstrap only.
- `no_new_phase` at about 55%: nothing new from the late phases starts.
- `freeze` at about 85%: no new features, and the PR cap drops to 150 lines.
- `report` near the end: the reporter writes `reports/final.md` and commits `STOP`.
- `hard_stop`: nothing merges.

The gate is a CI failure, not a reminder. At ShellHacks, an untested 1,191-line feature merged four minutes
before the deadline and had to be reverted with a minute to spare. With a freeze, that PR can't merge.

## Every 30 minutes (the reporter)
1. `python3 core/scripts/status_report.py`, then merge `reports/status.md` as `[F<reporter's ID>] status HH:MM`.
2. Comment on stale claims, and close them at the limit (`method.md` §7), or let `watchdog.py` do it.
3. Backlog low? Run the planner (`core/docs/planner.md`).

## Checkpoints for humans (the goal is hours apart, not minutes)
Read `reports/status.md` → clear `specs/inbox/` → merge or trim the `[PLAN]` PR → check `main` is green →
go back to sleep. If you find yourself checking more often than that, the specs or the planner need work, not more
babysitting.

## Escape hatches
| Snag | Do this |
|---|---|
| Need a shared field or file | Issue labelled `contract-change`; the contract owner ships an additive `[C<n>]`. Keep working on something else. |
| Bug found after merge | `[FIX-<ID>]` PR. At ShellHacks, 114 of 307 commits were fixes. That's normal. |
| `main` red | The owner gets 20 minutes, then anyone may `[REVERT-<sha>]`. |
| Spec silent | Take the default, log a decision, move on. |
| A rule turns out too strict to finish | Change it in the open with a decision record (for example, add labelled confidence tiers), never quietly. |
| Agent stuck or dead | The watchdog restarts it; the spec on `main` carries the context. |
| Need everyone to stop | Commit `STOP` to `main` (phone works: GitHub web → Add file). |

## The demo is part of the build
- **One core loop,** about 45 seconds, that shows the value. Everything else is backup.
- **Production is a one-way door.** Load-test the real host and database before you demo on them. Keep a
  `demo_snapshot.py` copy ready (`demo-snapshot.md`).
- **Verify the deploy, not the merge:** `verify_release.py --commit <reviewed sha>` right before judging.
