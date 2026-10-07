---
name: Tags
depends_on: [add-list]
owns: [jotter/tags.py, tests/test_tags]
---

# Tags
`add "text" --tag work`, then `list --tag work`.

## Defaults
How tags are stored is a **one-way door** (it changes the frozen storage format). Take no default: it's a
`needs-human` + `one-way-door` issue.
