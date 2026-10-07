#!/usr/bin/env python3
"""Keep an unattended run alive: restart dead sessions, release stale claims, alert on red main and low resources.

  watchdog.py [--once] [--interval 300] [--dry-run]

Each check, every interval:
  STOP       STOP file present: alert once and exit.
  sessions   a heartbeat file older than [watchdog].heartbeat_minutes = dead session: run [watchdog].restart
             (a shell template with {worker} and {worktree}), or alert if no restart command is set.
  claims     full size only: draft PRs with no push for stale_claim_minutes get a comment; at
             close_claim_minutes they're closed. (Lite opens PRs when the work is ready, so there are no claims.)
  main       main CI red for longer than main_red_minutes: alert and open a `main-red` issue; closed when green.
  resources  free disk / RAM below min_free_disk_gb / min_free_ram_gb: alert.
Alerts run [watchdog].alert (a shell template with {message}), or print. --dry-run prints actions only.
Heartbeats live in <git common dir>/agent-heartbeats/, shared by every worktree. Settings: .agents/config.toml [watchdog].
"""

import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from lib import gh, gh_json, heartbeat_dir, load_config, parser, root_from


def run_template(template: str, dry: bool, **values) -> None:
    cmd = template.format(**{k: shlex.quote(str(v)) for k, v in values.items()})
    if dry:
        print(f"watchdog: would run: {cmd}")
    else:
        subprocess.run(cmd, shell=True, check=False)


def free_ram_gb() -> float | None:
    try:
        if Path("/proc/meminfo").exists():
            m = re.search(r"MemAvailable:\s+(\d+) kB", Path("/proc/meminfo").read_text())
            return int(m.group(1)) / 1024**2 if m else None
        if platform.system() == "Darwin":
            out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
            page = int(re.search(r"page size of (\d+)", out).group(1))
            pages = sum(int(n) for n in re.findall(r"Pages (?:free|inactive|speculative):\s+(\d+)", out))
            return pages * page / 1024**3
    except (OSError, AttributeError, ValueError):
        return None
    return None


def minutes_since(iso: str, now: datetime) -> float:
    return (now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds() / 60


class Watchdog:
    def __init__(self, root: Path, cfg: dict, dry: bool):
        self.root, self.cfg, self.dry = root, cfg["watchdog"], dry
        self.claims = cfg["size"] == "full"
        self.hb_dir = heartbeat_dir(root)
        self.state_path = self.hb_dir.parent / "watchdog-state.json"
        try:
            self.state = json.loads(self.state_path.read_text())
        except (OSError, ValueError):
            self.state = {"commented": [], "alerted": []}

    def save(self):
        if not self.dry:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(self.state))

    def alert(self, message: str, key: str | None = None):
        """Alert; with a key, only once until the condition clears (see clear())."""
        if key and key in self.state["alerted"]:
            return
        print(f"watchdog: ALERT: {message}")
        if self.cfg["alert"]:
            run_template(self.cfg["alert"], self.dry, message=message)
        if key:
            self.state["alerted"].append(key)

    def clear(self, key: str):
        if key in self.state["alerted"]:
            self.state["alerted"].remove(key)

    def check_stop(self) -> bool:
        if (self.root / "STOP").exists():
            self.alert("STOP file present: run is stopping", key="stop")
            return True
        return False

    def check_sessions(self, now: float):
        if not self.hb_dir.is_dir():
            return
        for hb in sorted(self.hb_dir.iterdir()):
            age = (now - hb.stat().st_mtime) / 60
            if age < self.cfg["heartbeat_minutes"]:
                self.clear(f"dead:{hb.name}")
                continue
            worktree = (hb.read_text().strip().splitlines() or [""])[0]
            if self.cfg["restart"]:
                print(f"watchdog: {hb.name} silent {age:.0f} min: restarting")
                run_template(self.cfg["restart"], self.dry, worker=hb.name, worktree=worktree)
                if not self.dry:
                    hb.touch()  # give the restarted session a full heartbeat window
            else:
                self.alert(f"session {hb.name} silent {age:.0f} min and no restart command set", key=f"dead:{hb.name}")

    def check_claims(self, now: datetime):
        prs = gh_json(self.root, "pr", "list", "--state", "open", "--draft", "--json", "number,title,updatedAt")
        for pr in prs or []:
            age, n = minutes_since(pr["updatedAt"], now), pr["number"]
            if age >= self.cfg["close_claim_minutes"]:
                msg = f"Closing stale claim: no push for {age:.0f} min (watchdog). The feature is free to reclaim."
                print(f"watchdog: closing #{n} {pr['title']}")
                if not self.dry:
                    subprocess.run(["gh", "pr", "close", str(n), "--comment", msg], cwd=self.root, check=False)
            elif age >= self.cfg["stale_claim_minutes"] and n not in self.state["commented"]:
                msg = f"Stale claim: no push for {age:.0f} min. It closes at {self.cfg['close_claim_minutes']} min."
                print(f"watchdog: commenting on #{n}")
                if not self.dry:
                    subprocess.run(["gh", "pr", "comment", str(n), "--body", msg], cwd=self.root, check=False)
                self.state["commented"].append(n)

    def check_main(self, now: datetime):
        runs = gh_json(self.root, "run", "list", "--branch", "main", "--limit", "20",
                       "--json", "conclusion,status,createdAt")
        if not runs:
            return
        red = []
        for r in runs:  # newest first
            if r.get("status") != "completed":
                continue
            if r.get("conclusion") not in ("failure", "timed_out"):
                break
            red.append(r)
        if not red:
            self.clear("main-red")
            self.close_main_red_issues()
            return
        mins = minutes_since(red[-1]["createdAt"], now)
        if mins > self.cfg["main_red_minutes"]:
            msg = f"main has been red for {mins:.0f} min: land a FIX or REVERT"
            if "main-red" not in self.state["alerted"]:
                self.open_main_red_issue(msg)
            self.alert(msg, key="main-red")

    def open_main_red_issue(self, msg: str):
        if gh_json(self.root, "issue", "list", "--state", "open", "--label", "main-red", "--json", "number"):
            return
        print("watchdog: opening a main-red issue")
        if not self.dry:
            gh(self.root, "issue", "create", "--label", "main-red", "--title", "main is red",
               "--body", f"{msg}. The owner of the breaking change lands `fix(<slug>): ...`; after that anyone "
                         "may `git revert` it (title `revert: ...`). Opened by the watchdog; it closes this when main is green.")

    def close_main_red_issues(self):
        for i in gh_json(self.root, "issue", "list", "--state", "open", "--label", "main-red", "--json", "number") or []:
            print(f"watchdog: main is green, closing #{i['number']}")
            if not self.dry:
                gh(self.root, "issue", "close", str(i["number"]), "--comment", "main is green again (watchdog).")

    def check_resources(self):
        disk = shutil.disk_usage(self.root).free / 1024**3
        if disk < self.cfg["min_free_disk_gb"]:
            self.alert(f"low disk: {disk:.1f} GB free", key="disk")
        else:
            self.clear("disk")
        ram = free_ram_gb()
        if ram is not None and ram < self.cfg["min_free_ram_gb"]:
            self.alert(f"low RAM: {ram:.1f} GB free: close browsers or run fewer agents", key="ram")
        elif ram is not None:
            self.clear("ram")

    def tick(self) -> bool:
        """One pass. False means stop."""
        if self.check_stop():
            self.save()
            return False
        now = datetime.now(timezone.utc)
        self.check_sessions(time.time())
        if self.claims:
            self.check_claims(now)
        self.check_main(now)
        self.check_resources()
        self.save()
        return True


def main(argv=None) -> int:
    ap = parser(__doc__)
    ap.add_argument("--once", action="store_true", help="run one pass and exit")
    ap.add_argument("--interval", type=int, default=300, help="seconds between passes (default 300)")
    ap.add_argument("--dry-run", action="store_true", help="print actions, change nothing")
    args = ap.parse_args(argv)
    root = root_from(args)
    dog = Watchdog(root, load_config(root), args.dry_run)
    print(f"watchdog: watching {root} (pid {os.getpid()})")
    while dog.tick() and not args.once:
        time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
