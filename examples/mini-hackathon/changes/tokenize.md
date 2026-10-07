## What shipped
`words()`: lowercase, then runs of a–z. Non-ASCII letters separate words (decision tokenize-ascii).
## Where it lives
`wordfreq/tokenize.py`, `tests/test_tokenize.py`
## How to check it
`python3 -m unittest tests.test_tokenize`
## Gaps
`café` counts as `caf`. That matches the mission, but may surprise users.
