# Verification: let agents see their own work

An agent that can only run unit tests can't see what its change does. Someone has to open the app, click around and
report back. That person becomes a relay between the agent and the software, and every relay is a wait. The
verifier removes it: one command, set up once, that runs the software and shows the agent the result.

This page borrows heavily from poteto's [pstack](https://github.com/cursor/plugins/tree/main/pstack) (its
`create-verification-skill`, `maintain-verification-skill` and "prove it works" principle), cut down to what works
with any agent tool and a standard-library script.

## How it fits the loop
1. **The bootstrap feature sets `[verify].command`** in `.agents/config.toml`, next to CI, and runs it once before
   merging. A verifier that has never run is a draft.
2. **Each spec's `## Validation` is that feature's recipe:** every way a user reaches it, the steps as
   `action -> visible result`, and what to keep as proof.
3. **Every agent runs it** after the spec's Validation and the Checks (loop step 4):
   `python3 .agents/scripts/verify.py --slug <slug> --worktree .`
4. **The done note records the result.** `verify.py` prints one line, such as
   ``verify: `./scripts/verify.sh search` pass at 3f2a9c1 (evidence: ...)``. It goes under `## How to check it`.
   With no verifier, the note says `not verified` and what's missing.
5. **CI warns, and never fails,** when a `feat(<slug>)` done note has neither that line nor `not verified`. A
   unit-test command alone doesn't count: tests belong in Checks.

An empty `command` is reported as "not set up". It is never hidden and never counted as passing. That keeps the rule
in `AGENTS.md` honest: *merged*, *checked by CI*, *verified live* and *tried by a user* are four different things.

## What `verify.py` handles for you
- **The commit.** The result line names the commit it ran on, and says so if there were uncommitted changes. A
  newer commit means the line is out of date.
- **Evidence.** `{out}` in the command becomes a fresh folder for this run, inside the repo's git folder (shared by
  every worktree, never committed). Put screenshots, responses and logs there. It's kept after the run.
- **Cleanup.** The command runs in its own process group. When it ends, or after `[verify].timeout` seconds
  (default 300), everything it started is stopped, including a server it put in the background.

## Shape of a good verifier script
Most projects point `command` at one script in the repo, like `./scripts/verify.sh {slug} {out}`. It does five
things, in order:
1. **Launch** the real software from this worktree, with its own scratch data (a temp folder, a test database).
   Never drive an instance this run didn't start.
2. **Wait until it's ready** by polling a health check or a log line, never a fixed `sleep`. If it isn't healthy,
   fail fast and say why.
3. **Drive** the feature the way a user does: the CLI, the page, the API route. Not internal functions or
   test-only endpoints. Use stable handles (labels, test IDs, exact command output), never screen coordinates.
4. **Check and keep evidence.** Check the action *and* the state it left (the file, the row, the message). Save
   what you saw to `{out}`. Exit non-zero on a wrong answer, not only on a crash.
5. **Clean up** what it started, but never the evidence. (`verify.py` stops the process group anyway.)

It also needs to be:
- **Deterministic.** Same code, same result. If it's flaky, agents learn to ignore it.
- **One command.** Agents shouldn't each write a throwaway harness every run.
- **Fast.** Seconds, not minutes, because every agent runs it on every feature.
- **Helpful when it fails.** Its error says what to do next, and `--help` shows how to run one feature.

The script does the repeatable part. Judging whether what it showed is right for *this* feature stays with the agent.

## Examples
`{slug}`, `{worktree}` and `{out}` are filled in. The command runs in the worktree.

```toml
# A CLI: a known input and one known output. Both examples in this repo do this, and the kit's CI runs them.
command = 'f=$(mktemp) && printf "the cat the hat\n" > "$f" && python3 -m wordfreq "$f" --top 1 | grep -q "^the"'

# Anything bigger: one script in the repo that follows the five steps above
command = "./scripts/verify.sh {slug} {out}"
```

A sketch of that script for a web API:
```bash
#!/bin/sh
set -eu
slug=$1 out=$2
data=$(mktemp -d)
APP_DATA=$data ./run-server --port 8765 > "$out/server.log" 2>&1 &
for i in $(seq 1 50); do curl -fsS localhost:8765/health > /dev/null && break; sleep 0.2; done
curl -fsS localhost:8765/health > /dev/null || { echo "server never became healthy: see $out/server.log"; exit 1; }
curl -fsS -X POST localhost:8765/api/items -d '{"name": "milk"}' > "$out/create.json"
curl -fsS localhost:8765/api/items | tee "$out/list.json" | grep -q '"milk"'
```
Browser recipes for particular tools go in `docs/integrations/`.

## Rules that keep it honest
- **Proof is the real path plus the state it left,** not a log line that says it worked.
- **A path you skipped is not verified through another.** If the spec lists three ways in and you drove one, the
  other two are `not verified`.
- **Never weaken the check to get a pass.** Don't loosen the verifier, a golden test or the spec's Validation to
  make your change go green. If one is wrong, change it in its own PR and say why.
- **Inconclusive is not a pass.** A run that couldn't reach the feature, or ran against the wrong thing, is
  `not verified`, and the note says what was missing.

## Verifying someone else's fix
When a `bug` issue already has an open PR or a commit that claims to fix it, the agent checks that fix instead of
writing a competing one (from pstack's `benny`, `verify-existing-fix.md`). Run the same recipe twice on the baseline
(the PR's base, or the commit before the fix), then twice on the fix, and comment one of three outcomes on the issue:
- **Confirmed:** the baseline fails both times and the fix passes both times. Link the fix; open no PR.
- **Insufficient:** it fails on both. Link the fix and say it didn't resolve the symptom; still no competing PR.
- **Inconclusive:** the baseline didn't fail, the fix couldn't run, or the evidence doesn't show the end state that
  tells broken from fixed. Say which half couldn't be measured. It is not a pass.

## Keeping it current
Recipes go stale as features change. In the weekly routine, run `verify.py` for each recently shipped feature and
sort any failure into one of three kinds:
- **The recipe drifted:** fix the spec's Validation in a `fix(<slug>)` PR.
- **The script broke:** fix the verifier in a `contract:` PR.
- **The product regressed:** file an issue, and fix it like any bug.

## Per feature vs. production
`verify.py` checks one change on one machine, before merge. The hackathon profile's `verify_release.py` checks
something else: that the **deployed** site runs the commit you think it does (health endpoint, smoke paths, no
leaked secrets). Use both. The verifier catches a broken feature before it merges, and `verify_release` catches a
broken deploy before the demo.
