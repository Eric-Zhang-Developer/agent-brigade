# Remote mode: run agents on a cloud machine

A laptop is a bad place for an unattended run: it sleeps, runs out of RAM with several agents, fills its disk, and
the browser crashes (all happened at ShellHacks on a 16 GB / 256 GB laptop). Run the agents on a cloud machine
instead, and keep the laptop for watching and demoing.

## Setup (any Linux VM with ~4 vCPU / 16 GB per 3–4 agents)
```bash
# on the VM
sudo apt-get install -y git python3 tmux     # plus your agent CLIs and gh
gh auth login                                # or a fine-grained token
git clone <your repo> ~/work/app && cd ~/work/app
```
1. Start each agent in its own **persistent session**, so closing your laptop doesn't kill it. `tmux` is the
   simplest: `tmux new -d -s claude-1 -c ~/work/app-f03 '<agent command>'`.
2. Have each agent touch its heartbeat every loop. The installed `AGENTS.md` already says to:
   `d="$(git rev-parse --git-common-dir)/agent-heartbeats"; mkdir -p "$d"; pwd > "$d/<name>"`. It lives in the repo's git folder, so every worktree writes to the same place.
3. Configure `[watchdog]` in `.agents/config.toml`:
   ```toml
   [watchdog]
   restart = "tmux kill-session -t {worker}; tmux new -d -s {worker} -c {worktree} '<agent resume command>'"
   alert = "curl -s -d {message} ntfy.sh/<your-private-topic>"
   ```
   The resume command depends on your agent tool (see `integrations/`). `alert` can be any command; a push
   notification service lets it reach your phone.
4. Run the watchdog in its own session: `tmux new -d -s watchdog 'python3 .agents/scripts/watchdog.py'`.

## Honest limits
- The watchdog only restarts what your `restart` template knows how to restart, and it detects a dead session by
  a stale heartbeat, so an agent that's alive but stuck looks the same as a dead one.
- It can't fix an exhausted rate limit. It alerts, and `budget.md` is the plan.
- Keep secrets in the VM's environment or a secrets manager, never in the repo or the launch prompt.

## Stop from your phone
Create a file named `STOP` on `main` through the GitHub web UI. Agents stop at their next check, and the watchdog
exits.
