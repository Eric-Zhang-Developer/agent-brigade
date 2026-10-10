# Agent rules

The spec is the source of truth. Chat and memory aren't. Everything you need is in files on `origin/main`.

## Every run
1. `git fetch origin`. If a `STOP` file exists on `origin/main`, stop: comment on your open PR and push nothing.
2. Write your heartbeat: `d="$(git rev-parse --git-common-dir)/agent-heartbeats"; mkdir -p "$d"; pwd > "$d/<your-worker-name>"`.
3. Read from `origin/main`: `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`, `specs/milestones.toml`,
   then your feature's `specs/features/<slug>/spec.md`.__PROFILE_READ__
4. Finish your own open PRs first (fix red ones). Then pick new work.

## Picking work
- A feature's ID is its folder name, the **slug**: `specs/features/map-data/` is `map-data`.
- A feature is **done** when `changes/<slug>.md` is on `main`. Nothing else counts.
- A feature is **ready** when everything in `depends_on` is done and no open PR is titled `feat(<slug>): ...`.
- Take the **first ready feature in `specs/milestones.toml` order** (milestones top to bottom, skipping ones whose
  ship time has passed; features left to right) whose `assignee` is you or empty. Specs in no milestone are backlog:
  don't pick them. `python3 .agents/scripts/status.py --out -` prints the order.
- **Blocked?** Don't wait. File a `needs-human` issue (below), note it on your PR, and take the next ready feature.
- **Nothing ready?** Say so in your PR or in an issue and stop. Never invent scope.

## The loop
1. Work in a worktree outside the project folder:
   `git worktree add ~/.worktrees/<repo>/<slug> -b <slug> origin/main`.
__CLAIM__
3. Build. Commit small; messages say *why*.
4. Run the spec's Validation and the Checks in `specs/tech-stack.md`, then see your change running:
   `python3 .agents/scripts/verify.py --slug <slug> --worktree .`. Report failures honestly.
5. Write `changes/<slug>.md` **last**, 3–8 lines under these headings, so a person can follow the release later:
   `## What shipped` · `## Where it lives` (paths) · `## How to check it` (the line `verify.py` printed, or
   `not verified` and what's missing) · `## Gaps` (cut, untested, unknown, and any Validation step you skipped, with
   the reason).
6. Wait for CI, then squash-merge it yourself: `gh pr checks --watch && gh pr merge --squash --delete-branch`.
   Not for `plan:` PRs or PRs a CODEOWNERS rule assigns to a person: those wait for a human.

**PR titles** ([Conventional Commits](https://www.conventionalcommits.org/)); CI checks the files against the title:

| Title | May change |
|---|---|
| `feat(<slug>): ...` | the feature's `owns`, its spec folder, `changes/<slug>.md`, `specs/decisions/<slug>-*` |
| `fix(<slug>): ...` (also `refactor`, `perf`, `test`, `chore`, `style`) | the same, for a feature in flight, done or shipped |
| `fix: ...` with no scope (same types) | anything not frozen, not in `specs/` or `changes/`, and not owned by a feature in flight |
| `docs: ...` | open paths (like `NOW.md`), and Markdown outside `specs/`, `changes/`, frozen paths and features in flight |
| `contract: ...` | frozen paths and `specs/`: additive changes only |
| `plan: ...` | `specs/features/`, `specs/shipped/`, `specs/milestones.toml`, `specs/roadmap.md`; a person merges it |
| `revert: ...` | exactly what the reverted commit changed; make it with `git revert` |

The bootstrap feature (`bootstrap: true`) may change anything.

## When something needs a person
File an issue, then keep working:
```bash
gh issue create --label needs-human --title "<one-line question>" --body "Feature: <slug>
Context: <2-4 lines, links>
Options: <A / B / C>
Default taken: <option, or none: parked>
How to undo: <one line>"
```
Add `--label one-way-door` for decisions that are expensive to undo. For those, take **no** default: park the work
and switch tasks. Use `--label blocked` for something you can't continue, and `--label contract-change` when you
need a frozen file changed. If the spec is silent on something minor, take the smaller, reversible option and log it
in `specs/decisions/<slug>-<topic>.md` (context, options, choice, how to undo). It doesn't need an issue.

## Must (checks enforce these)
- Only change files your PR title allows (the table above). Frozen files change only through `contract:`.
- Never merge with red CI. If `main` is red, merge nothing but the fix. The owner has 20 minutes, then anyone may
  revert.
- No conflict markers or debug leftovers. The pre-commit hook runs the same checks; don't bypass it.
- Never commit secrets or `.env` files, or put a server secret where a browser can read it.
- Never invent data: numbers, dates, names, quotes, coordinates. Unknown stays empty and visible.

## Prefer (engineering judgment)
- One feature at a time. A second is fine while the first waits on review or CI.
- Keep PRs reviewable. Past a few hundred changed lines, split along logical seams (schema, then logic, then UI) if
  that helps the reviewer, or say in the description why it's one piece. CI warns; it doesn't block.
- Not everything needs a spec. A small bug in shared code is a `fix: ...` PR (file an issue if it's worth tracking).
  New behavior gets a spec.
- If your own spec is wrong, fix it in the same PR as the code. If another feature's spec is wrong, file an issue.
- Never resolve a conflict in a file you don't own. Abort, file a `blocked` issue for the owner, and switch tasks.
- Force-push only your own branch, with `--force-with-lease`.
- Keep `merged`, `checked by CI`, `verified live` and `tried by a user` apart whenever you report status.
