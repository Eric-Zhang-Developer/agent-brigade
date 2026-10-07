# Upgrading

Re-run the installer. It refreshes `.agents/scripts` and `.agents/hooks`, switches `profile`/`size` in
`.agents/config.toml`, and adds any missing files. It never overwrites `AGENTS.md`, `specs/` or `NOW.md`, so pass
`--overwrite-agents` if you want the rules regenerated for a new profile or size.

## Lite → full (more agents)
```bash
python3 ~/tools/agent-brigade/install.py --profile <same> --full --overwrite-agents .
```
Then raise `[agents].max_parallel`, name a `reporter`, give features a `lane`, and check that no two features' `owns`
overlap (`.agents/scripts/check_ownership.py --lint-specs`). Start the watchdog if you'll be away.

## Hackathon prototype → maintained project
The weekend's over and you want to keep going. Keep the repo: your specs, decisions and done notes are the context.
```bash
python3 ~/tools/agent-brigade/install.py --profile project --lite --overwrite-agents .
```
This adds `NOW.md`, `specs/milestones.toml` and `specs/review-paths.toml`. Then:
1. **Relax the clock.** `gates.toml` is now ignored. Set a first milestone with a real ship date and a cut list.
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
4. `python3 <kit>/install.py --profile <same> --<size> --overwrite-agents .`
5. Remove the `.agent-brigade/` line from `.gitignore`, and any "Built with" line from the README.
6. Turn each `specs/inbox/` file into a `needs-human` issue (add `one-way-door` where it says so), then delete the
   folder.
7. `git grep -n -i "core/scripts\|kit.toml"` should find nothing that's yours to fix. Push, and the first CI run on
   `main` creates the labels and issues.
