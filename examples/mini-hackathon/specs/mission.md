# Mission: wordfreq (toy example)

## Why
This is a teaching example for agent-brigade, not a real product. A user wants the most common words in a text.

## Who
Anyone with a text file and a terminal.

## What
`python3 -m wordfreq FILE --top N` prints the N most frequent words with their counts.

## Non-negotiables
- A word is a maximal run of letters a–z after lowercasing. `don't` is two words: `don`, `t`.
- Ties break alphabetically. `--top 3` always prints at most 3 lines.
- The golden test (the worked example in `tests/golden/`) must always pass.

## Not doing
- Stemming, languages other than English, a web UI.
