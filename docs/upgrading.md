# Upgrading

Re-run the installer (`npx agent-brigade@latest ...`, or `python3 install.py` from a clone). It refreshes
`.agents/scripts` and `.agents/hooks`, switches `profile`/`size` in `.agents/config.toml`, and adds any missing
files. It never overwrites `AGENTS.md`, `specs/` or `NOW.md`, so pass
`--overwrite-agents` if you want the rules regenerated for a new profile or size. If the project's `schema` (in
`.agents/config.toml`) is older than the kit's, the installer stops and names the section below to follow first.

## Adding the verifier step (v1.0)
v1.0 adds `[verify].command` and `.agents/scripts/verify.py` (both arrive with the refreshed scripts; an empty
command reads as "not set up"). The loop step that runs it lives in `AGENTS.md`, which the installer never
overwrites. Either regenerate it with `--overwrite-agents` (you lose local edits), or add this to step 4 of the loop
and to the done-note headings by hand, in a `contract:` PR:
```
4. ... then see your change running: `python3 .agents/scripts/verify.py --slug <slug> --worktree .`
5. ... `## How to check it` (the line `verify.py` printed, or `not verified` and why) ...
```
Then set `command` in a `contract:` PR (see `docs/verification.md`).

## Lite → full (more agents)
```bash
npx agent-brigade@latest --profile <same> --full --overwrite-agents .
```
Then raise `[agents].max_parallel`, name a `reporter`, set `assignee` on features, and check that no two features' `owns`
overlap (`python3 .agents/scripts/check_ownership.py --lint-specs`). Start the watchdog if you'll be away.

## Hackathon prototype → maintained project
The weekend's over and you want to keep going. Keep the repo: your specs, decisions and done notes are the context.
```bash
npx agent-brigade@latest --profile project --lite --overwrite-agents .
```
This adds `NOW.md` and `specs/review-paths.toml`. It only rewrites `profile` and `size` in
`.agents/config.toml`, so set `open = ["NOW.md"]` (and `max_parallel = 1` for lite) there yourself. Then:
1. **Relax the clock.** In `specs/milestones.toml`, clear `start`, drop the event's milestones, and set a first
   milestone with a real ship date and a cut list. `ship.py` can archive the event's specs first.
2. **Write `NOW.md`**: the current state, the honest gaps, and the next step.
3. **Decide the one-way doors you rushed:** the database, data model and auth. File each as a `needs-human` +
   `one-way-door` issue, and close it with a decision record.
4. **Turn demo shortcuts into feature specs:** fixtures, hardcoded keys, free-tier limits.
5. **Add review paths** for files a person should see before every merge, then re-run the installer to write
   CODEOWNERS.

## From a v0.1 install (the whole kit copied in)
Rehearsed on a clone of a real v0.1 project. Do it on a branch, with no other agents running:
1. Delete what v0.1 copied: `core/`, `profiles/`, `examples/`, `docs/story.md`, and the kit's `CHANGELOG.md` and
   `CONTRIBUTING.md`.
2. `mkdir -p .agents && git mv kit.toml .agents/config.toml`. In it, rename `max_lines` to `warn_lines`, replace
   `"kit.toml", "core/", "profiles/"` in `frozen` with `".agents/"`, and delete comment lines that point at `core/docs`.
3. Move `.github/workflows/ci.yml` aside, let the installer write the new one, then copy your project's own steps
   (tests, build) back into its "Project checks" step. Delete `.github/pull_request_template.md` if you never
   edited it.
4. Do steps 1–4 of "From schema 2" below, then
   `python3 <kit>/install.py --profile <same> --<size> --upgrade --overwrite-agents .`
5. Remove the `.agent-brigade/` line from `.gitignore`, and any "Built with" line from the README.
6. Turn each `specs/inbox/` file into a `needs-human` issue (add `one-way-door` where it says so), then delete the
   folder.
7. Retitle open PRs as in "From schema 2", step 6. `git grep -n -i "core/scripts\|kit.toml"` should find nothing
   that's yours to fix. Push, and the first CI run on
   `main` creates the labels and issues.

## From schema 2 (v0.2: F-numbers and `gates.toml`)
v0.3 names features by slug, titles PRs with Conventional Commits and uses `specs/milestones.toml` for both
profiles. The installer stops on a schema-2 project until these are done. Do it on a branch, with no agents running:
1. **Rename, in a moves-only commit:** `specs/features/F<n>-<slug>/` → `specs/features/<slug>/`,
   `changes/F<n>.md` → `changes/<slug>.md`, `specs/decisions/F<n>-<topic>.md` → `specs/decisions/<slug>-<topic>.md`.
   Slugs are lowercase-kebab, at most 32 characters, and not `shipped`, `contract`, `plan`, `docs` or `revert`.
2. **Specs:** delete `id`, `lane`, `phase`, `cut` and `milestone` from the front matter; rename `agent` to
   `assignee` (a worker name, or empty); write `depends_on` as slugs.
3. **Milestones:** put every scheduled slug in a milestone's `features`, in priority order. Anything left out is
   backlog and won't be picked.
   - Hackathon: write `specs/milestones.toml` from `gates.toml` (the installed template shows the shape).
     `run_start` → `start`; the `freeze` gate → the final milestone's `freeze` (ship minus that time); `report` →
     `report_before`; `hard_stop` → the final milestone's `ship`. Drop `only` (bootstrap first is built in) and
     `no_new_phase` (use a later milestone or a cut list). Delete `gates.toml`.
   - Project: `freeze_days = N` → `freeze = "Nd"`, which now means the last N days through the end of the ship
     day (it was N + 1 days). Write `features` and `cut` as slugs; `cut` must be a subset of `features`.
4. Delete `.github/pull_request_template.md` and `specs/features/_template/` if you never edited them, so the
   installer writes the new ones. The installer never rewrites `ci.yml`: in it, change `actions/checkout@v4` to
   `@v5` and `actions/setup-python@v5` to `@v6` (GitHub deprecated their Node 20 runtime).
5. `python3 <kit>/install.py --profile <same> --upgrade --overwrite-agents .` (leave out `--overwrite-agents` if
   you edited `AGENTS.md`, and copy its new "Picking work", "The loop" and "PR titles" sections by hand).
6. Retitle open PRs: `[F07] x` → `feat(<slug>): x`, `[FIX-F07]` → `fix(<slug>):`, `[C3]` → `contract:`,
   `[PLAN]` → `plan:`. Feature issues from v0.2 have no `<!-- spec: <slug> -->` line: add it to an issue's body to
   keep it, or close it and let the next sync open a fresh one.
7. `python3 .agents/scripts/check_ownership.py --lint-specs` passes, and `git grep -nE "\[F[0-9]+\]|FIX-F|gates.toml"`
   finds only history (old done notes and commit messages keep their F-numbers).
