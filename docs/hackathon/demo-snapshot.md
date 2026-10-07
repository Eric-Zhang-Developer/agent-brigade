# Demo snapshot: a demo that can't throttle

At ShellHacks the live database (a free tier) throttled during judging. The site timed out, the paid upgrade took
20 minutes to deploy, and the first judge saw an error page. A static copy of the demo's data would have kept it
on screen.

## The pattern
1. Your app reads its data through one function (or one API base URL). Give that function a switch: when
   `SNAPSHOT=1` (or a `?snapshot` query), read from a static folder instead of the backend.
2. On every release, save the responses the core demo loop needs:
   ```bash
   # .agents/config.toml [release] snapshot_paths = ["/", "/api/items", "/api/items/featured"]
   python3 .agents/scripts/demo_snapshot.py --out public/snapshot
   ```
   This writes each response plus `manifest.json` (source URL, commit, time, checksums). Commit it in a
   `[FIX-]` or release PR, so the snapshot always matches a reviewed commit.
3. Deploy with the snapshot switch available, and practice the demo once in snapshot mode.
4. If the live backend fails during judging, flip the switch. Say so if asked ("this is a cached copy from commit
   abc123, taken at 9:40"): it's honest, and judges respect it.

## Rules
- The snapshot is a fallback, not a fake. Same data, same commit, labelled.
- Snapshot only what the core loop needs. Keep it small enough to load instantly.
- Never snapshot anything with secrets or personal data.
