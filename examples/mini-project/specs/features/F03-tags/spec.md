---
id: F03
name: Tags
phase: 2
depends_on: [F01]
owns: [jotter/tags.py, tests/test_tags]
cut: ok
---

# F03 Tags
`add "text" --tag work`, then `list --tag work`.

## Defaults
How tags are stored is a **one-way door** (it changes the frozen storage format). Don't pick a default; see the
inbox.
