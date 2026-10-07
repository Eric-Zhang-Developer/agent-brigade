---
name: Add and list
depends_on: [bootstrap]
owns: [jotter/__main__.py, tests/test_cli]
---

# Add and list
`add TEXT` appends a note. `list` prints them newest first as `<created>  <text>`. The file comes from
`$JOTTER_FILE`, defaulting to `~/.jotter.jsonl`.
