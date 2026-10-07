# NOW

Updated: 2026-10-20 by the session lead (toy example; dates are illustrative)

## Where things stand
- `jotter add "text"` and `jotter list` work (F01). `jotter search WORD` works (F02).
- Notes live in `~/.jotter.jsonl`, one JSON object per line (`jotter/store.py`, frozen).

## Next step
Decide the tags question (the `needs-human` + `one-way-door` issue for F03). It's a one-way door, so no agent has
picked a default.
Until then, F03 is parked, and there's nothing else ready: run the planner or ship.

## Open questions
- **One-way door:** how tags are stored. Options: an optional `tags` field per note (additive), `#tags` parsed from
  text, or a separate tags file. Filed as an issue; no default taken.

## Next milestone
`first-ship` on 2026-11-01: F01 and F02 are in, and both are done. F03 is on the cut list, so it can't merge during
the freeze.
