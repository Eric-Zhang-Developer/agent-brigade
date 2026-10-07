
## Hackathon rules
- **Gates** in `specs/gates.toml` are enforced by CI: bootstrap first, then late phases close, then a **freeze** (no
  new features; FIX and REVERT only), then a hard stop. Don't start what can't merge before the freeze.
- **Demo early, and write feedback into `specs/context/`.** Feedback becomes requirements through specs, not chat.
- **Production is a one-way door.** Before judging, check the deploy:
  `python3 .agents/scripts/verify_release.py --commit $(git rev-parse origin/main)`. Keep a fallback with
  `demo_snapshot.py`.
- **The reporter** (if one is named in `.agents/config.toml`) runs `python3 .agents/scripts/status.py --issue` every
  30 minutes, and comments on draft PRs with no push for 45 minutes. At 60 minutes, it closes them.
