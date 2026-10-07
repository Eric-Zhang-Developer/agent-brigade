# Example: mini-hackathon (toy)

A deliberately tiny project, `wordfreq` (the most common words in a file), set up the way
`init.py --profile hackathon --full` would set it up, with the run already finished. It's a teaching example,
not a project to submit.

| Look at | To see |
|---|---|
| `specs/mission.md` | Non-negotiables written as exact rules |
| `specs/context/worked-example.md` → `tests/golden/` | The "answer key" turned into a frozen golden test |
| `specs/features/*/spec.md` | 3 features + bootstrap, with disjoint `owns` |
| `specs/gates.toml` | Bootstrap-only start, freeze, hard stop |
| `specs/decisions/F01-ascii.md` | A default taken and logged instead of asking |
| `specs/inbox/F03-default-top.md` | A judgment call parked for a human, with the default taken |
| `changes/` | Done notes, including a known gap |
| `tests/test_loop.py` | **The loop, replayed:** F03 built on a branch, then every CI check run on it, including the failures (a drive-by edit, a too-early start, a post-freeze PR, a conflict marker) |

Run it from the kit root:
```bash
python3 -m unittest discover -s examples/mini-hackathon -t examples/mini-hackathon -v
python3 core/scripts/status_report.py --root examples/mini-hackathon --offline --out -
```
