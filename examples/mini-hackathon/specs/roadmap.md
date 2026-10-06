# Roadmap

## Stages
| Stage | Goal | Must be true by |
|---|---|---|
| R0 | Golden test passes | 1:00 |
| R1 | CLI usable | 20:00 |

## Features
| ID | Name | Depends on | Stage | Assigned to |
|---|---|---|---|---|
| F00 | Bootstrap: API contract, golden test, CI | | R0 | claude-1 |
| F01 | Tokenize | F00 | R0 | codex-1 |
| F02 | Rank with alphabetical ties | F00 | R0 | claude-1 |
| F03 | Command-line interface | F01, F02 | R1 | codex-1 |

## Not doing
- Stemming, other languages, a web UI
