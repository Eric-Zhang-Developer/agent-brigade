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
Delete what v0.1 copied (`core/`, `profiles/`, `examples/`, `docs/story.md`, the kit's `CHANGELOG.md`/`CONTRIBUTING.md`
if they're the kit's), rename `kit.toml` to `.agents/config.toml` (and rename `max_lines` to `warn_lines`), and run the
installer with `--overwrite-agents`. Turn any `specs/inbox/` files into `needs-human` issues, then delete the
folder.
