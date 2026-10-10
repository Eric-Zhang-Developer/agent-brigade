# Release checklist

For the person shipping a release (Eric). Agents prepare everything up to step 6 and never run steps 6–9: the
version bump, tag and publish are one-way doors (decision D14).

## Before the release PR
1. **`main` is green** on the exact commit you'll release: `gh run list --branch main --limit 1`.
2. **Every feature in the milestone is done or cut.** `python3 template/common/.agents/scripts/status.py --out -`
   shows nothing in progress or ready for the release's milestone in `dev/specs/milestones.toml`.
3. **The package has only what it should.** Run `npm pack --dry-run`. Expect `bin/`, `install.py`, `template/`,
   `LICENSE`, `README.md`, `package.json`, and no `__pycache__`, `dev/`, `docs/`, `tests/` or `examples/`.
4. **A clean install works for all four combinations**, from the packed tarball rather than the working tree:
   ```bash
   npm pack --pack-destination /tmp
   for combo in "hackathon --lite" "hackathon --full" "project --lite" "project --full"; do
     d=$(mktemp -d) && git -C "$d" init -q
     (cd "$d" && npx --yes --package /tmp/agent-brigade-*.tgz agent-brigade --profile $combo) > /dev/null &&
     python3 "$d/.agents/scripts/check_ownership.py" --root "$d" --lint-specs &&
     python3 "$d/.agents/scripts/status.py" --root "$d" --offline --out - > /dev/null &&
     python3 "$d/.agents/scripts/verify.py" --root "$d" --slug bootstrap &&
     echo "ok: $combo"
   done
   ```
   In zsh, write `${=combo}` instead of `$combo`.
5. **An upgrade from the last release works.** On a scratch install of the previous version, re-run the installer
   from the tarball with `--upgrade` and follow `docs/upgrading.md`. Then run `check_ownership --lint-specs` and
   `status --offline`.

## The release PR (Eric)
6. **One PR, titled `chore: release vX.Y.Z`:**
   - bump `version` in `package.json`
   - in `CHANGELOG.md`, turn `Unreleased` into `## vX.Y.Z (YYYY-MM-DD)`, built from the changelog lines in the merged
     PRs' descriptions (D15). Keep a fresh, empty `Unreleased` heading above it.
   - write any `Deprecations` entries
   - update `docs/upgrading.md` if the release needs a manual step
   Merge it when CI is green.

## Ship (Eric)
7. **Tag** the merge commit: `git tag -a vX.Y.Z -m vX.Y.Z <sha> && git push origin vX.Y.Z`.
8. **Publish:** `npm publish` from a clean checkout of the tag. It asks for your passkey. The registry shows a
   `0.0.0-stage` placeholder for a minute while it processes.
9. **GitHub release:**
   `gh release create vX.Y.Z --title vX.Y.Z --notes-file <the CHANGELOG section> --verify-tag`.

## After
10. **Smoke-test the published package:** `npx agent-brigade@X.Y.Z --profile project --lite` in a new folder, then
    the checks in step 4.
11. **Upgrade the smoke repo** (`agent-brigade-smoke`) and push it, so the next release has a real previous install
    to test against.
