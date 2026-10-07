# Agent rules (developing this kit)

This repo is the kit itself, not a project that uses it. Its plan and decisions live in `dev/`.

- `template/` is exactly what `install.py` writes into a project: `common/` plus one profile overlay, with
  `template/parts/` assembled into the installed `AGENTS.md`. **Nothing under `template/` may name the kit**
  (`tests/test_install.py` enforces it).
- `docs/` holds the human guides, which stay here and are never installed.
- Scripts: Python 3.11+, standard library only, with `--help`, `--root`, exit codes 0/1/2, and a test in `tests/`.
- Checks before a PR: `python3 -m unittest discover -s tests -t tests`, plus what `.github/workflows/ci.yml` runs.
- Never invent data. Examples stay toys. Commit messages say why. No commit trailers.
