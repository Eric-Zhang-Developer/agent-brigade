# Example: mini-project (toy, lite)

A deliberately tiny side project, `jotter` (one-line notes from the terminal), set up the way
`install.py --profile project --lite` would set it up, a few sessions in. A teaching example.

| Look at | To see |
|---|---|
| `NOW.md` | The resume file: where things stand, the one next step, open questions |
| `specs/milestones.toml` | One milestone with a ship date, a freeze and a cut list |
| `specs/features/tags/spec.md` | A **one-way door**: no default, so `tags` waits on a `needs-human` issue |
| `specs/review-paths.toml` | The frozen storage file needs a human review (becomes CODEOWNERS) |
| `.agents/config.toml` | Lite size: one agent, `NOW.md` open to every PR |
| `tests/test_milestone.py` | The milestone freeze, replayed: the cut feature merges before the freeze, not during it; then `ship.py` archives the milestone |

Run it from the kit root:
```bash
python3 -m unittest discover -s examples/mini-project -t examples/mini-project -v
python3 template/common/.agents/scripts/status.py --root examples/mini-project --offline --out -
```
