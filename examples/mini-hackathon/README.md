# Example: mini-hackathon (toy)

A deliberately tiny project, `wordfreq` (the most common words in a file), set up the way
`install.py --profile hackathon --full` would set it up, with the run already finished. It's a teaching example,
not a project to submit.

| Look at | To see |
|---|---|
| `specs/mission.md` | Non-negotiables written as exact rules |
| `specs/context/worked-example.md` → `tests/golden/` | The "answer key" turned into a frozen golden test |
| `specs/features/*/spec.md` | 3 features + bootstrap, with disjoint `owns` |
| `specs/milestones.toml` | Three milestones: a safe demo, the usable CLI, then a frozen final milestone |
| `specs/decisions/tokenize-ascii.md` | A default taken and logged instead of asking |
| `changes/` | Done notes under fixed headings, including a known gap |
| `tests/test_loop.py` | **The loop, replayed:** `cli` built on a branch, then every CI check run on it, including the failures (a drive-by edit, a start before bootstrap, a post-freeze PR, a conflict marker) |

Run it from the kit root:
```bash
python3 -m unittest discover -s examples/mini-hackathon -t examples/mini-hackathon -v
python3 template/common/.agents/scripts/status.py --root examples/mini-hackathon --offline --out -
```
