---
id: F01
name: Add and list
phase: 1
depends_on: [F00]
owns: [jotter/__main__.py, tests/test_cli]
cut: never
milestone: first-ship
---

# F01 Add and list
`add TEXT` appends a note. `list` prints them newest first as `<created>  <text>`. The file comes from
`$JOTTER_FILE`, defaulting to `~/.jotter.jsonl`.
