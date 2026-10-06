# The method

How agents and humans build from a shared spec without waiting on each other. Both profiles run this loop. The
profile docs only add a clock (`profiles/hackathon/overnight.md`) or continuity (`profiles/project/`). Words in
**bold** are defined in `glossary.md`.

## The idea in four lines
- **The spec is the brain, the agent is the muscle.** Everything an agent needs is in files on `main`, never in
  chat or memory. (Adapted from the DeepLearning.AI × JetBrains spec-driven development course.)
- **Humans decide, agents do.** People write specs and make judgment calls at checkpoints. Agents build, and they
  never sit waiting on a question.
- **Rules live in checks.** If something must always happen, a script, hook or CI job enforces it, for humans
  too.
- **Never invent.** Every number traces to a source. Unknowns stay visible. Say what isn't done.

## What the agent reads
Every run starts by reading these from `origin/main`, in order. A file read earlier in the session doesn't count:
1. `kit.toml`: profile, size, paths.
2. `<specs>/mission.md`, `tech-stack.md`, `roadmap.md`: the **constitution**.
3. The profile's entry file: `profiles/hackathon/overnight.md`, or `NOW.md` then
   `profiles/project/one-way-doors.md`.
4. Your feature's `<specs>/features/<ID>-<slug>/spec.md`.

If the spec conflicts with anything else (old plans, chat, a README), the spec wins on facts and this file wins on
process.

## 1. Start of every run
1. `git fetch origin`. If `STOP` exists on `origin/main`, comment "stopped" on your open PR, push nothing, and end.
2. Touch your heartbeat file (`[watchdog].heartbeat_dir/<your-worker-name>`).
3. If `main` CI is red, merge nothing except the fix (section 6).
4. Finish your own open PRs first: fix them if red, finish them if in progress. Then pick new work.

## 2. Picking work
- A feature is **done** when `<changes>/<ID>.md` exists on `main`. Nothing else counts.
- A feature is **ready** when every ID in `depends_on` is done, no open PR title starts with `[<ID>]`, the gates
  allow it (`check_gates.py`), and it's assigned to you (or unassigned, in lite size).
- Take the lowest-numbered ready feature. One feature at a time per agent, each in its own **worktree**.
- **Blocked?** Don't wait. Write an inbox item (section 5), leave your PR as a draft with a note, and take the next
  ready feature.
- **Nothing ready?** Run the planner (`planner.md`) if you're the planner. Otherwise write "no ready work" to your
  PR or heartbeat and stop. Never invent scope.

## 3. Claim, build, merge
1. `git worktree add ../<repo>-<id> -b <id>-<slug> origin/main`. Never switch branches in another agent's folder.
2. Push right away and open a **draft PR** titled `[<ID>] <name>`. That draft is your claim; there's no other
   signup. Put your worker name and tool in the PR body.
3. Edit only what your title allows (`core/docs/config.md`, "PR titles").
4. Commit small. Messages say *why*.
5. Run your spec's Validation plus the repo's checks (`tech-stack.md`). Paste results or link green CI for the
   exact revision. Report failures honestly.
6. Write `<changes>/<ID>.md` **last**: 3–8 lines, covering what shipped, what was cut, and known gaps.
7. Mark the PR ready. When the required `ci` check is green and the branch is up to date, merge it yourself
   (squash). Exceptions: `[PLAN]` PRs and PRs touching review paths wait for a human.
8. Rebase only when there's a conflict or branch protection requires it. Force-push only your own branch, with
   `--force-with-lease`.
9. A big feature ships in parts: `[<ID>] part 1/3`, one open PR at a time. Only the last part writes the done
   note. Keep each PR under `[pr].max_lines`.
10. Never resolve a conflict in a file you don't own. Abort, file an issue for the owner, and switch tasks.

## 4. Ownership
`check_ownership.py` runs on every PR and fails any file outside what the title allows.
- **Frozen** files (shared contracts, CI, the kit itself) change only through a `[C<n>]` contract PR. Contract
  changes are **additive only**: add optional fields and new files, never rename or remove.
- Need a frozen file changed? Open an issue labelled `contract-change` naming the exact change, and keep working
  on something else.
- Exactly one feature is `bootstrap: true`. It creates the skeleton, contracts and CI, and everything else waits
  for it. It may create placeholder files inside other features' folders.
- No shared append-only files. Done notes, decisions and inbox items are one file per feature.

## 5. When the spec is silent or wrong
Resolve it in this order: your spec's **Defaults** → `<specs>/decisions/000-*.md` → the smaller, reversible option
that keeps every rule in `mission.md`. Log the choice in `<specs>/decisions/<ID>-<slug>.md` (context, options,
choice, how to undo).

**Judgment calls** a human should see go in the **inbox**: `<specs>/inbox/<ID>-<slug>.md`, with the default you
took. **One-way doors** (project profile: schema, auth, data model, public APIs, anything listed in
`one-way-doors.md`) get **no default**. Park them in the inbox and switch tasks.

If your own spec was wrong, fix it in the same PR. If another feature's spec is wrong, file an issue; don't edit
it.

## 6. Keeping `main` green
- `main` is the product. If its CI is red, nobody merges except the fix.
- The first to notice opens an issue labelled `main-red` that names the suspect commit.
- The owner has `[watchdog].main_red_minutes` to land `[FIX-<ID>]`. After that, anyone may open `[REVERT-<sha>]`
  (a plain `git revert`).

## 7. Stale claims
A draft PR with no push for `stale_claim_minutes` gets a comment. At `close_claim_minutes`, the reporter (or
`watchdog.py`) closes it and logs why. Reassign a feature only after its old agent has stopped. Two agents never
work on one feature.

## 8. Budgets
At 75% of any budget you can see (API spend, subscription limits), start no new feature work. The routing table is
in `budget.md`. Billing alerts are not caps.

## 9. Keep docs aligned
A change to behavior or claims updates its spec and acceptance criteria in the same PR. Status and pitch text must
keep four things apart: *merged*, *checked by CI*, *verified live*, and *tried by a real user*. Say which one you
mean.
