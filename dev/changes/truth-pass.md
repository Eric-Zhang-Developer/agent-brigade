## What shipped
The kit's docs and dev specs say what's true at v0.4.0: 44 fixes from a line-by-line audit against the code, the
v1.0.0 milestone with one spec per item, D12 (public) and D13–D15, and Unreleased/Deprecations in the changelog.
## Where it lives
`dev/specs/`, `docs/`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `template/parts/agents-hackathon.md` (freeze wording).
## How to check it
`python3 template/common/.agents/scripts/check_ownership.py --lint-specs` (12 features, ok); not verified: docs have no verifier.
## Gaps
28 "unclear" audit items were judgment calls; the ones left are minor. README's enforce_admins mismatch is documented, not fixed in install.py.
