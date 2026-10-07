# Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+, standard library only |
| Tests | `unittest`; golden test in `tests/golden/` (frozen) |

## Layout
```
wordfreq/__init__.py   [frozen] public API: count(text) -> dict, top(counts, n) -> list
wordfreq/tokenize.py   tokenize
wordfreq/rank.py       rank
wordfreq/__main__.py   cli
tests/golden/          [frozen] the worked example
```

## Checks
```bash
python3 -m unittest discover -s . -t .
```
