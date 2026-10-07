# How should tags be stored?
- Feature: F03   Raised: 2026-10-19   One-way door: yes
- Context: tags need a place in each stored note. `jotter/store.py` is frozen; every existing note file would carry
  the choice forever.
- Options: A) add an optional `tags: []` field to each JSON line (additive, old notes still load) /
  B) parse `#tags` out of the text at read time (no format change, but `#` becomes special) /
  C) a separate tags file (two files to keep consistent)
- Default taken: none: parked (one-way door)
- How to undo: depends on the choice; A and C need a migration to reverse
