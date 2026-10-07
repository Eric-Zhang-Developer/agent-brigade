# Hackathon preflight (about 45 minutes, before launch)

Humans do this; agents can check it. Work top to bottom.

## 1. Spec on `main`
Merge `specs/` (constitution, feature specs, `000-defaults.md`) to `main` before turning on protection. Review the
defaults now: agents will follow them literally.

## 2. Repo protection (repo admin)
Put the repo under the deploy owner's account; the person who owns hosting should own the repo too.
```bash
OWNER_REPO=you/your-repo
gh api -X PATCH repos/$OWNER_REPO -F allow_squash_merge=true -F allow_merge_commit=false \
  -F allow_rebase_merge=false -F delete_branch_on_merge=true
gh api -X PUT repos/$OWNER_REPO/branches/main/protection --input - <<'JSON'
{
  "required_status_checks": { "strict": true, "contexts": ["ci"] },
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```
`enforce_admins: true` holds humans to the same rule as agents: nobody pushes straight to `main`. (At ShellHacks a
direct push put conflict markers on `main`.) In a real emergency, an admin can lift it for one minute and put it
back. Branch protection on private repos may need a paid GitHub plan; if it's unavailable, CI and the pre-commit
hook still catch most mistakes, and the rule is social.

## 3. Every machine
```bash
python3 --version && git --version && gh auth status      # Python 3.11+
git config core.hooksPath core/hooks                       # init.py did this on the first machine; do it on every clone
df -h . && echo "free disk: keep 20 GB+"                   # agents, worktrees and builds eat disk
```
- Decide how many agents each machine can carry (`[agents].max_parallel`). A 16 GB laptop: 2–3, with the browser
  closed. More agents than that: use `core/docs/remote.md`.
- Log in to each agent tool. Check your usage limits and reset times, and write them into the plan
  (`core/docs/budget.md`).

## 4. Secrets
| Secret | Where it goes | Never |
|---|---|---|
| Product API keys | The server/runtime that calls them (CI secrets, the host's env) | In chat, specs, PRs, or browser-exposed variables |
| Database credentials | Separate read-only (app) and read-write (loader) users | Shared admin user |
| Agent tool logins | Each machine | In the repo |

Test every key with one real request now, not at 3 a.m.

## 5. Production: the one-way door
The database and host you demo on are a decision to make now, not mid-run.
- [ ] Deploy a "hello" build to the real host and check it loads on venue Wi-Fi and a phone hotspot.
- [ ] **Load-test the real backend** with the payload the demo will load: time the first load cold, then hit it
      20 times in a row. Free tiers throttle connections and requests. If it's slow or flaky, change plans now.
- [ ] Add the health endpoint (`{"commit": "<sha>"}`, `core/docs/config.md`) and set `[release]` in `kit.toml`.
- [ ] Plan the fallback: `demo_snapshot.py` (`demo-snapshot.md`).

## 6. Launch
1. In the launch commit, set `run_start` in `specs/gates.toml` and scale the gates to the event.
2. Start the bootstrap agent first. Start the others after its done note lands.
3. Start the watchdog if anyone's going to sleep (`core/docs/remote.md`).
4. Write down who owns what:

| Role | Person | Machine / agents |
|---|---|---|
| Lead | | |
| Deploy owner | | |
| Demo owner | | |
| Reporter (agent) | | |

## Emergency stop
GitHub web → `main` → Add file → `STOP` → commit. Agents stop at their next check.
