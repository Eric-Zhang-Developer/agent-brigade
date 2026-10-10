# Verification: let agents see their own work

An agent that can only run unit tests can't see what its change does. Someone has to open the app, click around and
report back. That person becomes a relay between the agent and the software, and every relay is a wait. The
verifier removes it: one command, set up once, that runs the software and shows the agent the result.

## How it fits the loop
1. **The bootstrap feature sets `[verify].command`** in `.agents/config.toml`, next to CI.
2. **Every agent runs it** after the spec's Validation and the Checks (loop step 4):
   `python3 .agents/scripts/verify.py --slug <slug> --worktree .`
3. **The done note records the result.** `verify.py` prints one line, such as ``verify: `make smoke` pass``. It goes
   under `## How to check it`. With no verifier, the note says `not verified` and why.
4. **CI warns, and never fails,** when a `feat(<slug>)` PR's done note has neither a command nor `not verified` under
   that heading.

An empty `command` is reported as "not set up". It is never hidden and never counted as passing. That keeps the rule
in `AGENTS.md` honest: *merged*, *checked by CI*, *verified live* and *tried by a user* are four different things.

## What makes a good verifier
- **It runs the real thing.** It runs the CLI, the server or the page, not just the functions underneath. Unit tests
  belong in Checks; the verifier is the step after them.
- **It's deterministic.** Same code, same result. Use fixed inputs, a scratch data file and a local server on a
  fixed port. If it's flaky, agents learn to ignore it.
- **It's one command.** Agents shouldn't each write a throwaway harness every run. Put the setup in a script in the
  repo, and point `command` at it.
- **It's fast.** Seconds, not minutes. Every agent runs it on every feature.
- **It fails loudly.** It exits non-zero on a wrong answer, not just on a crash. Check one known output.
- **It leaves judgment to the agent.** The script does the repeatable part: start the app, drive it, capture the
  output, a screenshot or a response. Deciding whether the result is right for *this* feature stays with the agent,
  which reads what the script showed it.

## Stack-neutral examples
`{slug}` and `{worktree}` are filled in. The command runs in the worktree, so relative paths work.

```toml
# A CLI: run it on a known input and check one known output
command = 'f=$(mktemp) && printf "the cat the hat\n" > "$f" && python3 -m wordfreq "$f" --top 1 | grep -q "^the"'

# A web app: a script in the repo starts the server, drives a headless browser through the main flow, saves
# screenshots to /tmp/verify/{slug}/, and exits non-zero if an expected element is missing
command = "./scripts/verify.sh {slug}"

# An API: start it, wait for health, check one real response
command = "./scripts/serve-test.sh & sleep 2 && curl -fsS localhost:8000/api/items | grep -q '\"id\"'"
```

Both examples in this repo use the first pattern (`examples/*/.agents/config.toml`), and the kit's CI runs them.
Tool-specific recipes (a particular browser driver, a harness's built-in browser) go in `docs/integrations/`.

## Per feature vs. production
`verify.py` checks one change on one machine, before merge. The hackathon profile's `verify_release.py` checks
something else: that the **deployed** site runs the commit you think it does (health endpoint, smoke paths, no
leaked secrets). Use both. The verifier catches a broken feature before it merges, and `verify_release` catches a
broken deploy before the demo.
