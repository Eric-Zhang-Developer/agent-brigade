# Agent rules

This repo uses [agent-brigade](core/docs/method.md). The spec is the source of truth; chat and memory aren't.

## Every run
1. Read `kit.toml` for the profile, size and where the specs live (`[paths].specs`, default `specs/`).
2. Follow `core/docs/method.md`: picking work, claiming with a draft PR, ownership, merging, the inbox.
3. Read, from `origin/main`: `<specs>/mission.md`, `tech-stack.md`, `roadmap.md`, then your feature's spec.
4. Profile extras:
   - **hackathon:** `profiles/hackathon/overnight.md` (gates, freeze, status reports).
   - **project:** `NOW.md` first, and update it last when you're the session lead. Also
     `profiles/project/one-way-doors.md`.

## Before marking a PR ready
Run the checks in `<specs>/tech-stack.md` (or link green CI for the exact revision), then `git diff origin/main --stat`:
no secrets, no `.env`, nothing outside what your PR title allows.

## Never
- Invent data: numbers, dates, coordinates, costs, names, quotes. Unknown stays empty and visible.
- Commit secrets, or put a server secret where a browser can read it.
- Wait for a human. Take the default, log it, keep going. One-way doors get parked in the inbox instead.
- Force-push anything but your own branch, edit another feature's spec, or resolve conflicts in files you don't own.
- Merge with red CI, or bypass the pre-commit hook except in an emergency CI will catch anyway.
