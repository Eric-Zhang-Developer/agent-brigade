# Roles

People decide, agents do. One person can hold several roles, and so can one agent.

## Humans
| Role | Does | Doesn't |
|---|---|---|
| **Lead** | Owns the constitution, approves `[PLAN]` batches, clears the inbox, merges contract PRs, picks cuts | Write most of the code |
| **Builder** (each teammate) | Owns one lane: steers its agents, reviews what they ship, demos it | Push to `main`, or edit outside the lane |
| **Demo owner** | Owns the live demo, the pitch and the 45-second core loop (`profiles/hackathon/pitch.md`) | Merge features after the freeze |
| **Deploy owner** | Owns the repo settings, hosting and secrets; runs `verify_release.py` | Share secrets in chat |

At ShellHacks, people mostly stopped writing code and started writing decisions. That's the job change.

## Agents
| Role | Does | Cadence |
|---|---|---|
| **Builder** | The loop in `method.md`: claim, build, check, done note, merge | Continuous |
| **Planner** | Reads status, decisions and the inbox; drafts specs in a `[PLAN]` PR (`planner.md`) | Hourly (hackathon) / weekly (project) |
| **Reporter** | `status_report.py`, stale-claim comments, final report | Every 30 min (hackathon) / per session (project) |
| **Judge** | Scores the live build like a judge, writes the 5 hardest questions (`profiles/hackathon/judge-agent.md`) | Hours before judging |
| **Briefer** | Keeps `docs/briefing.md` current (`briefing.md`) | Before judging / weekly |

## Your first hour (for a newer teammate)
1. Read `AGENTS.md` and `core/docs/method.md` sections 2–4. That's the whole game.
2. Take **one** feature the lead assigns you. Open it in its own worktree.
3. Tell your agent: "Read AGENTS.md and follow it. You're building F<n>." Let it open the draft PR.
4. Watch what it does, and ask it to explain anything you don't understand. You'll demo this feature, so you need
   to be able to explain it.
5. Never `git push` to `main`, and never use `--no-verify`. If the hook or CI blocks you, it's doing its job: ask the
   lead.
