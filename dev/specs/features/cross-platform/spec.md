---
name: Install and the scripts work on macOS and Windows, or the gaps are written down
depends_on: []
owns: []
assignee: ""
---

# Install and the scripts work on macOS and Windows, or the gaps are written down

From the v1.0 handoff (2026-10-10).

## Plan
1. CI matrix on macOS and Windows where cheap.
2. Every script degrades with one line when `gh` is missing or unauthenticated.
3. Installer: idempotent re-run, complete `--help`, unknown flag exits 2, existing `.github/` files left alone.

## Requirements
- Anything unsupported is stated in the README.

## Validation
Green CI on each OS in the matrix; tests for the `gh` paths.

## Defaults
Take the smaller, reversible option and log it in `dev/specs/decisions/<topic>.md`. Schema, installed `AGENTS.md` contract or public CLI flags: open an issue for Eric.
