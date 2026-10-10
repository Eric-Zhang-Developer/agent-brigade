# Findings queue: which PR title may write `specs/context/findings.md`

**Context.** The gardener appends lines to `specs/context/findings.md` and the planner deletes the lines it batches
into specs. Before this, only a `contract:` PR could change anything under `specs/context/`.

**Options.** (a) The gardener opens `contract:` PRs: works today, but `contract:` means "a frozen file changed" and
would train people to wave those through. (b) Let `plan:` PRs also change `specs/context/findings.md`: one path
added to `check_ownership.py`; `plan:` PRs are already human-merged and already the planner's title. (c) Put the
queue in an `open` path: then any PR could rewrite it, including a feature agent hiding its own finding.

**Choice.** (b), only that one file, not all of `specs/context/`.

**Undo.** Remove the path from the `plan` branch of `allowed()` in `check_ownership.py` and from `docs/config.md`.

**Follow-up.** The installed `AGENTS.md` title table (`template/parts/agents-common.md`, the `plan:` row) should list
the file too; that part is owned by another 1.0 workstream, so it isn't changed here.
