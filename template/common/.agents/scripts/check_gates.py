#!/usr/bin/env python3
"""Enforce time gates in CI, so a deadline is a rule instead of a suggestion. Warn on large PRs.

  check_gates.py --title "[F07] Export" --base origin/main [--now 2026-10-11T08:00:00-04:00]

hackathon: <specs>/gates.toml (only, no_new_phase, freeze, report, hard_stop).
project:   <specs>/milestones.toml (milestone freeze windows and cut lists).
Both:      a PR over [pr].warn_lines changed lines gets a warning, never a failure: split along logical seams,
           or say in the PR why it's one piece.
Formats: the comments in specs/gates.toml and specs/milestones.toml.
"""

import os
import sys
from datetime import date, datetime, timedelta, timezone

from lib import as_list, git_lines, load_config, load_specs, load_toml, parse_title, parser, root_from, specs_dir


def offset(at: str) -> timedelta:
    h, _, m = str(at).partition(":")
    return timedelta(hours=int(h), minutes=int(m or 0))


def fmt(td: timedelta) -> str:
    mins = int(td.total_seconds() // 60)
    return f"{mins // 60}:{mins % 60:02d}"


def first_commit_time(root, base: str) -> datetime | None:
    times = git_lines(root, "log", "--format=%aI", f"{base}..HEAD")
    return min((datetime.fromisoformat(t) for t in times), default=None)


def hackathon_rule(t: dict, gates: dict, now: datetime, phase_of, started_at) -> tuple[str | None, dict | None, str]:
    """(rejection reason or None, active gate, summary line)."""
    start = datetime.fromisoformat(gates["run_start"])
    if start.tzinfo is None:
        return "gates.toml run_start must include a UTC offset", None, ""
    elapsed = now - start
    ordered = sorted(gates.get("gate", []), key=lambda g: offset(g["at"]))
    active = next((g for g in reversed(ordered) if offset(g["at"]) <= elapsed), None)
    upcoming = next((g for g in ordered if offset(g["at"]) > elapsed), None)
    summary = f"elapsed {fmt(elapsed) if elapsed >= timedelta(0) else '-' + fmt(-elapsed)}"
    if upcoming:
        summary += f", next gate at {upcoming['at']} in {fmt(offset(upcoming['at']) - elapsed)}"
    if active is None:
        return None, None, summary + ", no gate active"
    summary += f", active gate at {active['at']}"
    kind, fid = t["kind"], t["id"]
    if active.get("hard_stop"):
        return "hard stop: nothing merges", active, summary
    if active.get("report"):
        if kind in ("fix", "revert") or (kind == "feature" and fid in as_list(active.get("allow"))):
            return None, active, summary
        return "report gate: only FIX, REVERT and the reporter's allowed IDs", active, summary
    if active.get("freeze"):
        if kind == "plan" or (kind == "feature" and fid not in as_list(active.get("allow"))):
            return f"freeze: no new feature work ({t['kind']} {fid or ''})".strip(), active, summary
        return None, active, summary
    if "only" in active and kind in ("feature", "fix") and fid not in as_list(active["only"]):
        return f"only {as_list(active['only'])} may run now", active, summary
    if "no_new_phase" in active and kind == "feature":
        phase = phase_of(fid)
        gate_time = start + offset(active["at"])
        if phase is not None and int(phase) >= int(active["no_new_phase"]) and not (started_at and started_at < gate_time):
            return f"no new phase {active['no_new_phase']}+ work after {active['at']} ({fid} is phase {phase})", active, summary
    return None, active, summary


def project_rule(t: dict, milestones: dict, today: date) -> tuple[str | None, str]:
    for m in sorted(milestones.get("milestone", []), key=lambda m: str(m.get("ship") or "9999")):
        if not m.get("ship"):
            continue
        ship = date.fromisoformat(str(m["ship"]))
        if ship < today:
            continue
        freeze_start = ship - timedelta(days=int(m.get("freeze_days", 0)))
        summary = f"next milestone {m['name']} ships {ship} ({(ship - today).days} days), freeze from {freeze_start}"
        if not (freeze_start <= today <= ship) or t["kind"] not in ("feature", "fix"):
            return None, summary
        if t["id"] in as_list(m.get("cut")):
            return f"{t['id']} is on {m['name']}'s cut list", summary
        if t["kind"] == "feature" and t["id"] not in as_list(m.get("features")):
            return f"milestone freeze: only {m['name']} features {as_list(m.get('features'))}", summary
        return None, summary
    return None, "no upcoming milestone with a ship date"


def changed_lines(root, base: str, exclude: list[str]) -> int:
    total = 0
    for row in git_lines(root, "diff", "--numstat", "--no-renames", f"{base}...HEAD"):
        added, removed, path = row.split("\t", 2)
        if added == "-" or any(path.startswith(e) for e in exclude):
            continue  # binary or excluded
        total += int(added) + int(removed)
    return total


def main(argv=None) -> int:
    ap = parser(__doc__)
    ap.add_argument("--title", required=True, help="PR title")
    ap.add_argument("--base", default="origin/main", help="base ref (default origin/main)")
    ap.add_argument("--now", help="ISO time with offset, for testing (default: now)")
    args = ap.parse_args(argv)
    root = root_from(args)
    cfg = load_config(root)
    t = parse_title(args.title)
    if t is None:
        print(f"gates: title {args.title!r} has no known prefix")
        return 1
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    reason, gate, summary = None, None, ""
    if cfg["profile"] == "hackathon":
        gates = load_toml(specs_dir(root, cfg) / "gates.toml")
        if gates is None or not gates.get("run_start"):
            summary = "no gates.toml or empty run_start: time gates not enforced"
        else:
            specs = load_specs(root, cfg)

            def phase_of(fid):
                return specs[fid][0].get("phase") if fid in specs else None

            started = first_commit_time(root, args.base) if t["kind"] == "feature" else None
            reason, gate, summary = hackathon_rule(t, gates, now, phase_of, started)
    else:
        ms = load_toml(specs_dir(root, cfg) / "milestones.toml")
        if ms is None:
            summary = "no milestones.toml: milestone freezes not enforced"
        else:
            reason, summary = project_rule(t, ms, now.date())

    warn = int(cfg["pr"]["warn_lines"])
    big = None
    if reason is None and warn and t["kind"] not in ("plan", "revert"):
        n = changed_lines(root, args.base, as_list(cfg["pr"]["exclude"]))
        summary += f"; {n} changed lines"
        if n > warn:
            big = (f"large PR ({n} changed lines, guideline {warn}): split along logical seams if it helps review, "
                   "or say in the description why it's one piece")

    print(f"gates: {summary}")
    if big:
        print(f"::warning::{big}" if os.environ.get("GITHUB_ACTIONS") else f"gates: warning: {big}")
    if reason:
        print(f"gates: REJECTED: {reason}")
        return 1
    print("gates: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
