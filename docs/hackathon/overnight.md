# Hackathon: the overnight run

A guide for the humans running a hackathon. The agents' rules are in the installed `AGENTS.md`; this is the shape of
the weekend around them.

## The shape of the weekend
| When | What | Who |
|---|---|---|
| Hours 0–2 | Read the sponsor material, run the plan bake-off (`plan-bakeoff.md`), write the constitution and specs. Turn any worked example into the golden test. | Humans + agents drafting |
| ~45 min | Preflight (`preflight.md`): repo protection, keys, the database load test. | Deploy owner |
| Launch | Bootstrap feature first. Everything else waits for its done note. | One agent |
| The long middle | The loop. The planner keeps the backlog at 2×. Demo early to mentors/sponsors, and write their feedback into `specs/context/`. | Agents; humans at checkpoints |
| Freeze − 3 h | Judge review (`judge-agent.md`) and briefing (`docs/briefing.md`). Fix only what they find. | Judge, briefer |
| Freeze | Only the final milestone's own features and `allow`, plus fixes, reverts and docs; no `plan:`. From `report_before`: fixes, reverts, docs and `allow`. | CI |
| Freeze → submit | `verify_release.py` against prod, `demo_snapshot.py`, rehearse the pitch (`pitch.md`), submit early. | Demo + deploy owners |

## Milestones (enforced by `check_gates.py` in CI)
`specs/milestones.toml` sets `start` and the milestones as offsets from it. Scale them to your event: a 24-hour
event isn't a 36-hour one. The template's defaults assume 36 hours:
- The bootstrap feature merges first. Nothing else can merge before its done note: a built-in rule.
- `safe-demo` (+12:00) and `core` (+24:00): list features in priority order; agents take them top to bottom. Put
  late ideas in a later milestone, or on a cut list, so they don't start late.
- `submission` (+35:30), the final milestone: `freeze` from +30:00 (no new features), `report_before` from +34:00
  (the reporter writes `reports/final.md` and adds `STOP` in a `fix:` PR), and at ship nothing merges.

The freeze is a CI failure, not a reminder. At ShellHacks, an untested 1,191-line feature merged four minutes
before the deadline and had to be reverted with a minute to spare. With a freeze, that PR can't merge.

## Every 30 minutes (the reporter, or just CI)
1. CI already rewrites the pinned Status issue after every merge. Between merges, the reporter runs
   `python3 .agents/scripts/status.py --issue` so time left and stale claims stay current.
2. Comment on stale claims, and close them at the limit, or let `watchdog.py` do it.
3. Backlog low? Run the planner (`docs/planner.md`).

## Checkpoints for humans (the goal is hours apart, not minutes)
Read the pinned Status issue → clear the `needs-human` issues → merge or trim the `plan:` PR → check `main` is green →
go back to sleep. If you find yourself checking more often than that, the specs or the planner need work, not more
babysitting.

## Escape hatches
| Snag | Do this |
|---|---|
| Need a shared field or file | Issue labelled `contract-change`; the contract owner ships an additive `contract:` PR. Keep working on something else. |
| Bug found after merge | `fix(<slug>): ...` PR. At ShellHacks, 114 of 307 commits were fixes. That's normal. |
| `main` red | The watchdog opens a `main-red` issue. The owner gets 20 minutes, then anyone may `git revert` it (`revert: ...`). |
| Spec silent | Take the default, log a decision, move on. |
| A rule turns out too strict to finish | Change it in the open with a decision record (for example, add labelled confidence tiers), never quietly. |
| Agent stuck or dead | The watchdog alerts, and restarts it if `[watchdog].restart` is set; the spec on `main` carries the context. |
| Need everyone to stop | Commit `STOP` to `main` (phone works: GitHub web → Add file). |

## The demo is part of the build
- **One core loop,** about 45 seconds, that shows the value. Everything else is backup.
- **Production is a one-way door.** Load-test the real host and database before you demo on them. Keep a
  `demo_snapshot.py` copy ready (`demo-snapshot.md`).
- **Verify the deploy, not the merge:** `verify_release.py --commit <reviewed sha>` right before judging.
