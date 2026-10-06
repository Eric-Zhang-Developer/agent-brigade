# Needs-human inbox

A judgment call an agent shouldn't settle alone goes here, as **one file per item**:
`dev/specs/inbox/<ID>-<slug>.md`. Write it, take the default (unless it's a one-way door), and keep working.

```markdown
# <one-line question>
- Feature: <ID>   Raised: <ISO date>   One-way door: yes|no
- Context: <2–4 lines, with links>
- Options: <A / B / C>
- Default taken: <option, or "none: parked" for a one-way door>
- How to undo: <one line>
```

Eric clears the inbox at checkpoints. A resolved item gets deleted in a later PR, with the answer recorded in
`dev/specs/decisions/`.
