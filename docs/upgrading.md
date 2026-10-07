# Upgrading

`init.py` is safe to re-run: it changes `profile`/`size` in `kit.toml` and adds any missing files, without
overwriting your edits.

## Lite → full (more agents)
```bash
python3 core/scripts/init.py --profile <same> --full
```
Then raise `[agents].max_parallel`, name a `reporter`, give each feature a `lane`, and make sure no two features'
`owns` overlap (`check_ownership.py --lint-specs`). Start the watchdog if you'll be away.

## Hackathon prototype → maintained project
The weekend's over and you want to keep going. Don't start a new repo: your specs, decisions and done notes are
the context.
```bash
python3 core/scripts/init.py --profile project --lite      # or --full
```
This adds `NOW.md`, `specs/milestones.toml` and `specs/review-paths.toml`. Then:
1. **Relax the clock.** `gates.toml` is now ignored. Set a first milestone with a real ship date and a cut list.
2. **Write `NOW.md`**: the current state, the honest gaps from the final report, and the next step.
3. **List your one-way doors.** Whatever you rushed on the weekend (database choice, data model, auth) goes into
   `profiles/project/one-way-doors.md` thinking: decide it deliberately now, with a decision record.
4. **Pay down the demo shortcuts.** Fixtures, hardcoded keys, free-tier limits: make each one a feature spec.
5. **Add review paths** for the files you want a human to see before every merge.
6. Add `"NOW.md"` to `[ownership].open` if init didn't.

## Updating the kit itself
Copy a newer `core/` and `profiles/` over yours in a `[C<n>]` PR, then re-run `init.py` to pick up new templates.
Read the kit's CHANGELOG first.
