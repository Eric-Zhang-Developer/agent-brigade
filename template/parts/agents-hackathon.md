
## Hackathon rules
- **Milestones** in `specs/milestones.toml` are enforced by CI: the bootstrap feature first, then each milestone in
  order, then the final milestone's **freeze** (only its own features and `allow`, plus fixes; no `plan:`), its report
  window (fixes, reverts, docs and `allow` only), and a hard stop. Don't start what can't merge before the freeze.
- **Demo early, and write feedback into `specs/context/`.** Feedback becomes requirements through specs, not chat.
- **Production is a one-way door.** Before judging, check the deploy:
  `python3 .agents/scripts/verify_release.py --commit $(git rev-parse origin/main)`. Keep a fallback with
  `demo_snapshot.py`.
- **The reporter** (if one is named in `.agents/config.toml`) runs `python3 .agents/scripts/status.py --issue` every
  30 minutes. The watchdog comments on draft PRs with no push for 45 minutes and closes them at 60.
