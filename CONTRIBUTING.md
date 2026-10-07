# Contributing

Thanks for looking. The kit has a few rules of its own:

- **Generic only.** No domain or project logic, and nothing that could pass as pre-written hackathon code. Examples
  stay toys.
- **Standard library only.** Python 3.11+, no third-party imports, config via `tomllib`.
- **Harness-agnostic.** Anything specific to one agent tool goes in `docs/integrations/`.
- **Plain language.** Define a term once in `docs/glossary.md`, and keep docs short enough to actually read.
- **Every script:** a module docstring, `--help`, `--root`, exit codes `0/1/2`, and a `tests/test_<name>.py`.
- **Formats** live in `docs/config.md`. Change them additively, and update that file in the same PR.

## Checks
```bash
python3 -m unittest discover -s tests -t tests
python3 .agents/scripts/check_markers.py --all
for ex in examples/*/; do python3 -m unittest discover -s "$ex" -t "$ex"; done
```
CI runs these on Python 3.11. Commit messages say why, not what.

The repo has no license yet, so contributions can't be accepted until one is chosen.
