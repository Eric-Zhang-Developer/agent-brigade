---
name: A release checklist and a drafted v1.0.0 changelog, ready for Eric to ship
depends_on: []
owns: ["dev/release-checklist.md"]
assignee: ""
---

# A release checklist and a drafted v1.0.0 changelog, ready for Eric to ship

From the v1.0 handoff (2026-10-10).

## Plan
1. Checklist: CI green, CHANGELOG final, package.json version, `npm pack` contents, install from the tarball for all four profile/size combinations, tag, publish, release notes.
2. Draft the v1.0.0 CHANGELOG entry from the merged PRs' changelog lines.

## Requirements
- Eric bumps the version, tags and publishes. Nothing here does.

## Validation
Doc review.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
