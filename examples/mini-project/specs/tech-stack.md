# Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+, standard library only |
| Storage | JSON Lines file, `jotter/store.py` (frozen: changing the format is a one-way door) |
| Tests | `unittest` |

## Checks
```bash
python3 -m unittest discover -s . -t .
```
