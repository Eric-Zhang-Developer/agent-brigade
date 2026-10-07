---
name: Search
depends_on: [add-list]
owns: [jotter/search.py, tests/test_search]
---

# Search
`search(notes, word)`: case-insensitive substring match, newest first. Wired into the CLI as `search WORD` (add-list
owns the CLI and added the subcommand stub).
