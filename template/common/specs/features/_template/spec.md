---
id: F00
name: One line describing the outcome
lane: A
agent: builder
phase: 1
depends_on: []
owns: []
cut: ok
---

<!-- Copy this folder to features/F<n>-<slug>/. owns = path prefixes (not globs) this feature alone may change;
no entry may overlap another feature's or a frozen path. cut: ok | never. bootstrap: true on exactly one feature,
which may change anything. Size it so it merges as one reviewable PR, or plan it in parts. -->

# F00 Name

## Plan
1.

## Requirements
<!-- Exact and testable. Name inputs, outputs and the rule. Say what must stay unknown rather than guessed. -->
-

## Validation
<!-- Commands that prove it works, and what output means pass. -->

## Defaults
<!-- What to do when this spec is silent. "Prefer the smaller, reversible option" is the fallback. -->
