# Tech stack: agent-brigade

| Layer | Choice |
|---|---|
| Protocol, templates, docs | Markdown. Plain language; define jargon once in `core/docs/glossary.md`. |
| Config | TOML (`kit.toml`, `gates.toml`, `milestones.toml`, `review-paths.toml`), read with `tomllib`. Every format is defined in `core/docs/config.md` (frozen contract). |
| Scripts | Python 3.11+, **standard library only**. No third-party imports, ever. Shell out only to `git`, and to `gh` where noted. A missing `gh` degrades gracefully and never crashes. |
| Tests | `unittest` (stdlib). One `core/tests/test_<script>.py` per script. Tests that need a repo build a throwaway git repo in a temp dir via `core/tests/helpers.py`. Never use the network in tests; fake HTTP with a local `http.server` thread. |
| CI | GitHub Actions, one required job named `ci`, on Python 3.11 (the floor). Local dev may run newer Python, so never use syntax newer than 3.11. |
| Harness | Any agent that reads files and runs git. |

## Repository layout (created by F00)
```
AGENTS.md  CLAUDE.md  kit.toml  degit.json  .gitignore        [frozen]
.github/workflows/ci.yml  .github/pull_request_template.md    [frozen]  the kit's own CI
core/docs/method.md     the shared loop                       [frozen]
core/docs/config.md     every config format + script CLI contract  [frozen]
core/scripts/kitlib.py  shared helpers: config, front matter, git, gh  [frozen]
core/scripts/check_ownership.py                               [frozen]
core/tests/helpers.py  core/tests/test_kitlib.py  core/tests/test_check_ownership.py  [frozen]
core/ci/                CI + PR templates copied into user repos by init  [frozen]
core/scripts/<name>.py  one script per feature;  core/tests/test_<name>.py
core/docs/<topic>.md    core/specs/ (templates)   core/hooks/
profiles/hackathon/     profiles/project/
examples/mini-hackathon/  examples/mini-project/
README.md CHANGELOG.md CONTRIBUTING.md docs/story.md
dev/                    the kit's OWN specs, done notes, reports (removed from user copies)
```

## Script conventions
- Every script has a module docstring, `--help`, and `--root PATH` (default: the nearest parent directory that
  contains `kit.toml`, else the current directory). Exit codes: `0` ok, `1` findings/failure, `2` usage error.
- Import shared code from `kitlib.py`. Don't re-implement config loading, front-matter parsing or git calls.
- Print one line per finding, then a one-line summary. No color, no emoji.
- Keep scripts small. If one passes ~300 lines, say why in the done note.

## Checks (before marking a PR ready)
```bash
python3 -m unittest discover -s core/tests -t core/tests
python3 core/scripts/check_ownership.py --lint-specs
python3 core/scripts/check_ownership.py --title "<PR title>" --base origin/main
python3 core/scripts/check_markers.py --base origin/main      # once F01 lands
```
CI runs these plus every check against each `examples/*/`. Successful CI on the exact PR revision counts; don't
repeat it locally. Report failures honestly.
