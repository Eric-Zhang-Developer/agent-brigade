---
id: F00
name: Bootstrap - storage contract
phase: 0
depends_on: []
owns: []
cut: never
bootstrap: true
---

# F00 Bootstrap
`jotter/store.py`: `append(path, text)` and `load(path) -> list[dict]`, JSON Lines with `text` and `created` (ISO
UTC). Frozen after this: changing the format means migrating people's notes.
