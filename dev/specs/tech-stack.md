# Tech stack: agent-brigade

| Layer | Choice |
|---|---|
| Protocol, templates, docs | Markdown. Plain language; define jargon once in `docs/glossary.md`. |
| Config | TOML (`.agents/config.toml`, `specs/milestones.toml`, `specs/review-paths.toml`), read with `tomllib`. Every format is defined in `docs/config.md`. |
| Scripts | Python 3.11+, **standard library only**. No third-party imports, ever. Shell out only to `git`, and to `gh` where noted. A missing `gh` degrades gracefully and never crashes. |
| Install | `install.py` (Python). `bin/agent-brigade.js` is only a Node wrapper for `npx`: it finds Python 3.11+ and runs `install.py`. Keep all logic in Python. |
| Tests | `unittest` (stdlib). One `tests/test_<script>.py` per script; throwaway git repos via `tests/helpers.py`. Never use the network in tests; fake HTTP with a local `http.server` thread. |
| CI | GitHub Actions, one required job named `ci`, on Python 3.11 (the floor). Never use syntax newer than 3.11. |
| Harness | Any agent that reads files and runs git. |

## Repository layout
```
install.py  package.json  bin/agent-brigade.js     the installer and its npx wrapper
template/common/  template/<profile>/  template/parts/   exactly what gets installed
docs/        guides for people (never installed)
examples/    two toy projects that replay the loop in their tests
tests/       one test file per script
dev/         this kit's own mission, stack, decisions, milestone
```

## Script conventions
- Every script has a module docstring, `--help`, and `--root PATH` (default: the nearest parent directory that
  contains `.agents/config.toml`, else the current directory). Exit codes: `0` ok, `1` findings/failure, `2` usage
  error.
- Import shared code from `lib.py`. Don't re-implement config loading, front-matter parsing or git calls.
- Print one line per finding, then a one-line summary. No color, no emoji.
- Keep scripts small. If one passes ~300 lines, say why in the commit.

## Checks (before marking a PR ready)
```bash
python3 -m unittest discover -s tests -t tests
```
CI also runs the kit checks, every example end to end, and an install from the packed npm tarball. Successful CI
on the exact PR revision counts; don't repeat it locally.
