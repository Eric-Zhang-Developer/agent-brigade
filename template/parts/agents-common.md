# Agent rules

The spec is the source of truth. Chat and memory aren't. Everything you need is in files on `origin/main`.

## Every run
1. `git fetch origin`. If a `STOP` file exists on `origin/main`, stop: comment on your open PR and push nothing.
2. Write your heartbeat: `d="$(git rev-parse --git-common-dir)/agent-heartbeats"; mkdir -p "$d"; pwd > "$d/<your-worker-name>"`.
3. Read from `origin/main`: `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`, then your feature's
   `specs/features/<ID>-<slug>/spec.md`.__PROFILE_READ__
4. Finish your own open PRs first (fix red ones). Then pick new work.

## Picking work
- A feature is **done** when `changes/<ID>.md` is on `main`. Nothing else counts.
- A feature is **ready** when everything in `depends_on` is done and no open PR title starts with `[<ID>]`.
  Take the lowest-numbered ready feature assigned to you (or unassigned). One feature at a time.
- **Blocked?** Don't wait. File a `needs-human` issue (below), leave your PR as a draft with a note, and take the
  next ready feature.
- **Nothing ready?** Say so in your PR or in an issue and stop. Never invent scope.

## The loop
1. Work in a worktree outside the project folder:
   `git worktree add ~/.worktrees/<repo>/<id> -b <id>-<slug> origin/main`.
2. Push and open a **draft PR** titled `[<ID>] <name>` right away. The draft is your claim. Put `Closes #<n>` (the
   feature's issue) and your worker name in the body.
3. Build. Commit small; messages say *why*.
4. Run the spec's Validation and the Checks in `specs/tech-stack.md`. Report failures honestly.
5. Write `changes/<ID>.md` **last**: 3–8 lines covering what shipped, what was cut, and known gaps.
6. Mark the PR ready. When CI is green and the branch is up to date, squash-merge it yourself, except for `[PLAN]`
   PRs and PRs a CODEOWNERS rule assigns to a person.

**PR titles:** `[F<n>]` feature · `[FIX-F<n>]` repair after merge · `[C<n>]` change to a frozen file (additive only)
· `[PLAN]` new specs from the planner (a person merges) · `[REVERT-<sha>]` a plain `git revert`.

## When something needs a person
File an issue, then keep working:
```bash
gh issue create --label needs-human --title "<one-line question>" --body "Feature: <ID>
Context: <2-4 lines, links>
Options: <A / B / C>
Default taken: <option, or none: parked>
How to undo: <one line>"
```
Add `--label one-way-door` for decisions that are expensive to undo. For those, take **no** default: park the work
and switch tasks. Use `--label blocked` for something you can't continue, and `--label contract-change` when you
need a frozen file changed. If the spec is silent on something minor, take the smaller, reversible option and log it
in `specs/decisions/<ID>-<slug>.md` (context, options, choice, how to undo). It doesn't need an issue.

## Must (checks enforce these)
- Only change files your PR title allows: your feature's `owns`, its done note, decisions and spec. Frozen files
  change only through `[C<n>]`.
- Never merge with red CI. If `main` is red, merge nothing but the fix. The owner has 20 minutes, then anyone may
  revert.
- No conflict markers or debug leftovers. The pre-commit hook runs the same checks; don't bypass it.
- Never commit secrets or `.env` files, or put a server secret where a browser can read it.
- Never invent data: numbers, dates, names, quotes, coordinates. Unknown stays empty and visible.

## Prefer (engineering judgment)
- Keep PRs reviewable. Past a few hundred changed lines, split along logical seams (schema, then logic, then UI) if
  that helps the reviewer, or say in the description why it's one piece. CI warns; it doesn't block.
- If your own spec is wrong, fix it in the same PR as the code. If another feature's spec is wrong, file an issue.
- Never resolve a conflict in a file you don't own. Abort, file a `blocked` issue for the owner, and switch tasks.
- Force-push only your own branch, with `--force-with-lease`.
- Keep `merged`, `checked by CI`, `verified live` and `tried by a user` apart whenever you report status.
