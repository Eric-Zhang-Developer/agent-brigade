---
name: One line describing the outcome
depends_on: []
owns: []
assignee: ""
---

<!-- Copy this folder to features/<slug>/ (lowercase-kebab, at most 32 characters): the folder name is the
feature's ID, used in PR titles (`feat(<slug>): ...`), its done note (changes/<slug>.md) and its branch.
owns = path prefixes (not globs) this feature alone may change while it's in flight; no entry may overlap another
in-flight feature's or a frozen path. assignee: a worker name, or empty for anyone. Add `bootstrap: true` to exactly
one feature, which may change anything and merges first. Schedule it by adding the slug to a milestone in
specs/milestones.toml; until then it's backlog. Size it so it merges as one reviewable PR, or plan it in parts. -->

# Name

## Plan
1.

## Requirements
<!-- Exact and testable. Name inputs, outputs and the rule. Say what must stay unknown rather than guessed. -->
-

## Validation
<!-- Commands that prove it works, and what output means pass. -->

## Defaults
<!-- What to do when this spec is silent. "Prefer the smaller, reversible option" is the fallback. -->
