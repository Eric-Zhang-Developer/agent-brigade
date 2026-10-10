## What shipped
Case-insensitive substring search, newest first.
## Where it lives
`jotter/search.py`, `tests/test_search.py`
## How to check it
verify: `f=$(mktemp) && JOTTER_FILE=$f python3 -m jotter add "Buy milk" && JOTTER_FILE=$f python3 -m jotter search MILK | grep -q "Buy milk"` pass
`python3 -m unittest tests.test_search`
## Gaps
None known.
