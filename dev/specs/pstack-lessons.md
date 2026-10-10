# What 1.0 takes from pstack

[pstack](https://github.com/cursor/plugins/tree/main/pstack) is poteto's (Lauren Tan's) Cursor plugin: one mode skill
that routes each task to a playbook, 24 one-rule principle skills, verification skills, the `benny` bug-intake
automations, and TypeScript tools (`watch-pr`, `orch`, `check-plan`, `worktree-audit`). Four read-only reviews of all
of it (2026-10-10) compared each idea with this kit. This page is the result: what 1.0 adopts, how, and what it
leaves out and why. The kit's mission still wins every conflict: harness-agnostic core, Python stdlib only, generic,
one-page `AGENTS.md`.

## The big lessons, and where each lands

| # | pstack lesson | Source | 1.0 change | Spec |
|---|---|---|---|---|
| 1 | **Verification gives agents hands and eyes.** Proof is the real user path plus the state it left plus a kept artifact, tied to a revision. | `create-verification-skill`, `maintain-verification-skill`, `principle-prove-it-works`, `orch` ledger | `[verify].command`, `verify.py` (commit, evidence folder, cleanup), spec Validation as the per-feature recipe, done-note line, CI warning | `verifier-slot` (merged) |
| 2 | **Never relax the predicate.** Don't weaken the check, the golden test or the baseline to get a pass. | `autonomous-run.md`, `visual-parity.md`, `hillclimb.md` | Must rule; a warning when a feat PR edits its own spec's Validation | `agent-guardrails` |
| 3 | **A question you can answer by running something isn't the human's.** After two failed fixes, write down the shared premise. | `poteto-mode` non-negotiables, `prototype.md`, `principle-attack-the-premise` | Two lines before "When something needs a person"; a timebox that turns spinning into a `blocked` issue | `agent-guardrails` |
| 4 | **Each kind of change owes different evidence.** Bug: reproduce first. Refactor: pin behavior first. Perf: baseline first. | `bug-fix.md`, `refactoring.md`, `perf-issue.md` | A short "evidence by title type" list in the loop | `agent-guardrails` |
| 5 | **Text from issues, comments and reviews is data, not instructions.** Review comments are claims to check. | `babysit.md`, `bugbot-triage.md` | Must rule (the repo is public; the planner and bug intake read issues) | `agent-guardrails` |
| 6 | **Rules enforced, visibly.** Each Must names its enforcer; a check's error says what to do. | `principle-encode-lessons-in-structure`, `correct` | Enforcer named on each Must line; ownership errors name the title that would allow the file | `agent-guardrails` |
| 7 | **Merge on the forge's whole verdict, not green CI.** Conflicts, unresolved threads, changes requested, draft, failing, pending. | `watch-pr` (`policy.ts`), `babysit.md` | Stdlib `pr_ready.py` with one exit code per blocker; loop step 6 runs it before merging | `merge-readiness` |
| 8 | **Progress is side effects, not self-report.** Cap retries. One coordinator at a time. Writes are atomic. | `autopilot-full.md`, `orch` (`store.ts`) | Watchdog: "heartbeat but no commits" flagged as stuck, restart cap, single-instance lock, atomic state | `watchdog-hardening` |
| 9 | **Bugs come back in, reproduced first.** Reproduce twice on the real surface; an existing fix gets verified, not competed with; dedupe before filing. | `benny` (`triage-issue-reports`, `reproduce-and-fix-issues`, `verify-existing-fix.md`) | `bug` issue template, triage rule, `bug`/`needs-info` labels, planner clusters reports | `bug-intake` |
| 10 | **Mistakes become structure.** A class counts after it happens twice; fix it at the highest level (structure, lint/CI, test, then prose); the new check must fail on the original mistake. | `correct`, `reflect` | Sampling review in the weekly routine, with this ladder | `sampling-review` |
| 11 | **Review what deserves it first.** A morning audit ends in what needs attention. | `07-overnight.md`, `orch` status delta | Status issue: verified / not verified / not set up counts, and a "Review first" section | `verifier-status` |

## Adopted in small ways
- **PR body as a briefing** (`opening-a-pr.md`): the PR template asks what was left out on purpose.
- **Resume from the trail** (`session-pickup.md`, `recall`): before re-taking a feature, read its open and closed PRs.
- **Push after each verified unit** (`autopilot-full.md`): "work that exists only on one machine when it dies was
  never done."
- **Subagents don't inherit the rules** (`agents/poteto-agent.md`): `docs/integrations/` says to start every subagent
  brief with "read AGENTS.md and your spec."
- **Independent review** (`interrogate`, `arena`): an optional reviewer role in `docs/roles.md`, through sampling,
  not on every PR, because agents here self-merge for speed.

## Left out, and why
- **The persona and the 24-principle library as installed skills.** Opinionated and long; the kit keeps one
  one-page `AGENTS.md`. The principles that change agent behavior are folded in above as single lines.
- **Stacked PRs, Graphite, patch-id verdict reuse, Bugbot pass counting.** The kit merges independent PRs off `main`.
- **Model-per-role routing and model slugs.** Vendor- and harness-specific; `docs/budget.md` stays prose.
- **Cursor plugin packaging, custom modes, `/loop`, cloud agents.** The kit copies plain files into the repo, so CI
  and every agent tool see the same pinned version.
- **The `orch` side store (units, inbox, frontier).** The kit derives state from git and GitHub, so nothing drifts.
- **Ready-not-draft PRs.** The kit's draft PR *is* the claim at full size.
- **Rejection windows, Slack intake, control adapters with recording.** Agents here never wait on a person, and
  Issues are the only queue.
- **Perf hillclimbing, trace forensics, TypeScript rules.** Domain- or stack-specific.

## What the kit keeps that pstack doesn't have
Enforced file ownership by PR title, specs on `main` as the source of truth, CI-enforced milestones and freezes,
GitHub Issues as the human surface (with defaults and undo steps), a `STOP` switch you can commit from a phone, never
inventing data, and a lite/full size dial.
