---
name: Bootstrap - storage contract
depends_on: []
owns: []
bootstrap: true
---

# Bootstrap
`jotter/store.py`: `append(path, text)` and `load(path) -> list[dict]`, JSON Lines with `text` and `created` (ISO
UTC). Frozen after this: changing the format means migrating people's notes.
