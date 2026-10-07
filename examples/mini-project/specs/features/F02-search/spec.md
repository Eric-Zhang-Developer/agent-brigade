---
id: F02
name: Search
phase: 1
depends_on: [F01]
owns: [jotter/search.py, tests/test_search]
cut: ok
milestone: first-ship
---

# F02 Search
`search(notes, word)`: case-insensitive substring match, newest first. Wired into the CLI as `search WORD` (F01
owns the CLI and added the subcommand stub).
