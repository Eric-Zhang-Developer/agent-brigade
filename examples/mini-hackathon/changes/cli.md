## What shipped
`python3 -m wordfreq FILE --top N`. A missing file prints a message and exits 1.
## Where it lives
`wordfreq/__main__.py`, `tests/test_cli.py`
## How to check it
verify: `f=$(mktemp) && printf "the cat the hat\n" > "$f" && python3 -m wordfreq "$f" --top 1 | grep -q "^the"` pass
`python3 -m unittest tests.test_cli`
## Gaps
Default `--top 10` was raised as a `needs-human` issue; default taken: 10.
