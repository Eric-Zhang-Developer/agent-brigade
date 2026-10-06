#!/usr/bin/env python3
"""Write <reports>/status.md: done, in progress, ready next, blocked, needs-human, main CI, time left.

  status_report.py [--out PATH] [--now ISO] [--offline]

Uses `gh` for PRs and CI when available; --offline (or no gh) falls back to local branches and says so.
Anything it can't determine prints as `unknown`, never a guess.
"""

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from check_gates import fmt, offset
from kitlib import as_list, done_ids, gh_json, git, git_lines, load_config, load_specs, load_toml, parse_title, parser, root_from, specs_dir


def age_minutes(iso: str, now: datetime) -> int:
    return int((now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds() // 60)


def time_left(root, cfg, now: datetime) -> str:
    d = specs_dir(root, cfg)
    if cfg["profile"] == "hackathon":
        g = load_toml(d / "gates.toml")
        if not g:
            return "no gates.toml"
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
        for row in git_lines(root, "for-each-ref", "refs/heads", "--format=%(refname:short)\t%(committerdate:iso-strict)"):
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
    inbox = sorted(p for p in (specs_dir(root, cfg) / "inbox").glob("*.md") if p.name != "needs-human.md")
    for p in inbox:
        text = p.read_text()
        door = " **one-way door**" if "one-way door: yes" in text.lower() else ""
        out.append(f"- `{p.name}`: {text.strip().splitlines()[0].lstrip('# ')}{door}")
    if not inbox:
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


def main(argv=None) -> int:
    ap = parser(__doc__)
    ap.add_argument("--out", help="output file (default <reports>/status.md); '-' for stdout")
    ap.add_argument("--now", help="ISO time with offset (default: now)")
    ap.add_argument("--offline", action="store_true", help="don't call gh")
    args = ap.parse_args(argv)
    root = root_from(args)
    cfg = load_config(root)
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    text = build(root, cfg, now, args.offline)
    if args.out == "-":
        sys.stdout.write(text)
        return 0
    out = Path(args.out) if args.out else root / cfg["paths"]["reports"] / "status.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"status: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
