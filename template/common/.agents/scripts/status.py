#!/usr/bin/env python3
"""Status: done, in progress, ready next, blocked, needs-human, main CI, time left.

  status.py --issue            rewrite the pinned "Status" issue (CI does this on every push to main)
  status.py --out -            print it;  --out FILE writes a file
  status.py --offline ...      no gh calls: local branches only, and says so

Anything it can't determine prints as `unknown`, never a guess.
"""

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from check_gates import fmt, offset
from lib import as_list, done_ids, gh, gh_json, git, load_config, load_specs, load_toml, parse_title, parser, root_from, specs_dir


def age_minutes(iso: str, now: datetime) -> int:
    return int((now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds() // 60)


def time_left(root, cfg, now: datetime) -> str:
    d = specs_dir(root, cfg)
    if cfg["profile"] == "hackathon":
        g = load_toml(d / "gates.toml")
        if not g or not g.get("run_start"):
            return "gates off (no gates.toml or empty run_start)"
        elapsed = now - datetime.fromisoformat(g["run_start"])
        ahead = sorted((offset(x["at"]), x) for x in g.get("gate", []) if offset(x["at"]) > elapsed)
        if not ahead:
            return f"elapsed {fmt(elapsed)}, no gates left"
        at, gate = ahead[0]
        kind = next((k for k in ("hard_stop", "report", "freeze", "no_new_phase", "only") if k in gate), "gate")
        return f"elapsed {fmt(max(elapsed, timedelta(0)))}, next: {kind} at {gate['at']} (in {fmt(at - elapsed)})"
    ms = load_toml(d / "milestones.toml") or {}
    dated = sorted((date.fromisoformat(str(m["ship"])), m["name"]) for m in ms.get("milestone", []) if m.get("ship"))
    upcoming = [(s, n) for s, n in dated if s >= now.date()]
    if not upcoming:
        return "no deadline (no upcoming milestone with a ship date)"
    s, n = upcoming[0]
    return f"milestone {n} ships {s} ({(s - now.date()).days} days)"


def build(root: Path, cfg: dict, now: datetime, offline: bool) -> str:
    specs = {fid: fms[0] for fid, fms in load_specs(root, cfg).items() if fid}
    done = done_ids(root, cfg)
    wd = cfg["watchdog"]
    sha = (git(root, "rev-parse", "--short", "HEAD", check=False).strip() or "unknown")
    out = [
        "# Status",
        "",
        f"Checkpoint {now.isoformat(timespec='minutes')} · HEAD `{sha}` · profile {cfg['profile']}/{cfg['size']}",
        f"Time: {time_left(root, cfg, now)}",
        f"STOP: {'present: agents must stop' if (root / 'STOP').exists() else 'not present'}",
        "",
    ]

    prs = None if offline else gh_json(root, "pr", "list", "--state", "open", "--limit", "200",
                                       "--json", "number,title,isDraft,updatedAt,url")
    claimed = set()
    out.append("## In progress")
    if prs is None:
        out.append("_From local branches; PR state unknown (offline or gh unavailable)._")
        refs = git(root, "for-each-ref", "refs/heads", "--format=%(refname:short)\t%(committerdate:iso-strict)", check=False)
        for row in refs.splitlines():
            name, when = row.split("\t")
            out.append(f"- `{name}`, last commit {age_minutes(when, now)} min ago")
    else:
        for pr in sorted(prs, key=lambda p: p["number"]):
            t = parse_title(pr["title"])
            if t and t["id"]:
                claimed.add(t["id"])
            age = age_minutes(pr["updatedAt"], now)
            flag = " **STALE: close**" if pr["isDraft"] and age >= wd["close_claim_minutes"] else \
                " **stale**" if pr["isDraft"] and age >= wd["stale_claim_minutes"] else ""
            out.append(f"- [#{pr['number']}]({pr['url']}) {pr['title']} · {'draft' if pr['isDraft'] else 'ready'}"
                       f" · updated {age} min ago{flag}")
        if not prs:
            out.append("- none")

    ready = [f for f in sorted(specs) if f not in done and f not in claimed
             and all(d in done for d in as_list(specs[f].get("depends_on")))]
    blocked = [f for f in sorted(specs) if f not in done and f not in ready and f not in claimed]
    out += ["", "## Done"]
    out += [f"- {f} {specs.get(f, {}).get('name', '')}: {_first_line(root, cfg, f)}" for f in sorted(done)] or ["- none"]
    out += ["", "## Ready next"]
    out += [f"- {f} {specs[f].get('name', '')}" for f in ready] or ["- none"]
    if len(ready) + len(claimed) < 2 * int(cfg["agents"]["max_parallel"]):
        out.append(f"- **Backlog low** ({len(ready)} ready + {len(claimed)} claimed < 2 × {cfg['agents']['max_parallel']} agents): run the planner.")
    out += ["", "## Blocked"]
    out += [f"- {f}: waiting on {[d for d in as_list(specs[f].get('depends_on')) if d not in done]}" for f in blocked] or ["- none"]

    out += ["", "## Needs human"]
    asks = None if offline else gh_json(root, "issue", "list", "--state", "open", "--label", "needs-human",
                                        "--limit", "100", "--json", "number,title,labels,url")
    if asks is None:
        out.append("- unknown (offline or gh unavailable): check issues labelled `needs-human`")
    for i in sorted(asks or [], key=lambda i: i["number"]):
        door = " **one-way door**" if any(lb["name"] == "one-way-door" for lb in i.get("labels", [])) else ""
        out.append(f"- [#{i['number']}]({i['url']}) {i['title']}{door}")
    if asks == []:
        out.append("- none")

    out += ["", "## main CI"]
    runs = None if offline else gh_json(root, "run", "list", "--branch", "main", "--limit", "1",
                                        "--json", "status,conclusion,createdAt,url")
    if not runs:
        out.append("- unknown (offline, gh unavailable, or no runs)")
    else:
        r = runs[0]
        out.append(f"- {r.get('conclusion') or r.get('status')} · {age_minutes(r['createdAt'], now)} min ago · {r['url']}")
    return "\n".join(out) + "\n"


def _first_line(root, cfg, fid) -> str:
    p = root / cfg["paths"]["changes"] / f"{fid}.md"
    lines = [x.strip() for x in p.read_text().splitlines() if x.strip() and not x.startswith("#")]
    return lines[0][:140] if lines else ""


def update_issue(root: Path, text: str) -> int:
    """Rewrite the body of the open issue labelled `status`, creating and pinning it the first time."""
    found = gh_json(root, "issue", "list", "--state", "open", "--label", "status", "--json", "number")
    if found is None:
        print("status: gh unavailable or not authenticated; nothing updated")
        return 1
    if found:
        r = gh(root, "issue", "edit", str(found[0]["number"]), "--body", text)
    else:
        r = gh(root, "issue", "create", "--title", "Status", "--label", "status", "--body", text)
        if r and r.returncode == 0:
            gh(root, "issue", "pin", r.stdout.strip().rsplit("/", 1)[-1])
    ok = bool(r) and r.returncode == 0
    print(f"status: {'updated the Status issue' if ok else 'failed: ' + (r.stderr.strip() if r else 'no gh')}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = parser(__doc__)
    ap.add_argument("--out", help="output file, or '-' for stdout")
    ap.add_argument("--issue", action="store_true", help="rewrite the pinned issue labelled `status`")
    ap.add_argument("--now", help="ISO time with offset (default: now)")
    ap.add_argument("--offline", action="store_true", help="don't call gh")
    args = ap.parse_args(argv)
    root = root_from(args)
    cfg = load_config(root)
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    if not (args.out or args.issue):
        ap.error("pass --issue or --out")
    text = build(root, cfg, now, args.offline)
    if args.issue:
        return update_issue(root, text)
    if args.out == "-":
        sys.stdout.write(text)
        return 0
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"status: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
