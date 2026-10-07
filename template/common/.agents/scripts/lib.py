"""Shared helpers for agent-brigade scripts: config, spec front matter, git, gh. Stdlib only."""

import argparse
import copy
import json
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

DEFAULTS = {
    "profile": "hackathon",
    "size": "full",
    "kit_dev": False,
    "paths": {"specs": "specs", "changes": "changes", "reports": "reports"},
    "ownership": {"frozen": ["AGENTS.md", "kit.toml", ".github/", "core/", "profiles/"], "open": []},
    "agents": {"max_parallel": 3, "reporter": ""},
    "pr": {"max_lines": 400, "exclude": []},
    "markers": {
        "debug_patterns": [r"^\s*debugger;?\s*$", r"^\s*breakpoint\(\)", r"^\s*import pdb", r"console\.log\("],
        "ignore": [],
    },
    "watchdog": {
        "heartbeat_dir": ".agent-brigade/heartbeats",
        "heartbeat_minutes": 20,
        "stale_claim_minutes": 45,
        "close_claim_minutes": 60,
        "main_red_minutes": 20,
        "min_free_disk_gb": 10,
        "min_free_ram_gb": 2,
        "restart": "",
        "alert": "",
    },
    "release": {
        "url": "",
        "health_path": "/api/health",
        "smoke_paths": ["/"],
        "snapshot_paths": ["/"],
        "secret_patterns": ["sk-", "sk_live_", "AIza", "ghp_", "github_pat_", "xox", "mongodb+srv://", "postgres://", "-----BEGIN"],
    },
    "budget": {"monthly_usd": 0, "reserve_final_hours": 3},
}


# --- config ---------------------------------------------------------------------------------------------------------

def find_root(start=None) -> Path:
    """Nearest parent directory containing kit.toml, else the start directory."""
    here = Path(start or Path.cwd()).resolve()
    for d in (here, *here.parents):
        if (d / "kit.toml").is_file():
            return d
    return here


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(root: Path) -> dict:
    path = Path(root) / "kit.toml"
    data = tomllib.loads(path.read_text()) if path.is_file() else {}
    return _merge(DEFAULTS, data)


def specs_dir(root: Path, cfg: dict) -> Path:
    return Path(root) / cfg["paths"]["specs"]


def load_toml(path: Path) -> dict | None:
    return tomllib.loads(path.read_text()) if path.is_file() else None


# --- spec front matter (the YAML subset our specs use) ----------------------------------------------------------------

def _scalar(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v in ("true", "false"):
        return v == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def _strip_comment(line: str) -> str:
    out, quote = [], None
    for ch in line:
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch == "#":
            break
        out.append(ch)
    return "".join(out).rstrip()


def front_matter(text: str) -> dict:
    """Top-level `key: value`, `key: [a, b]`, and `key:` followed by `  - item` lines."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return {}
    data, current = {}, None
    for raw in m.group(1).splitlines():
        line = _strip_comment(raw)
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            key, _, val = line.partition(":")
            current = key.strip()
            data[current] = _scalar(val) if val.strip() else []
        elif current is not None and line.strip().startswith("- ") and isinstance(data[current], list):
            data[current].append(_scalar(line.strip()[2:]))
    return data


def as_list(v) -> list:
    return [x for x in (v if isinstance(v, list) else [v] if v not in (None, "") else []) if x not in (None, "")]


def load_specs(root: Path, cfg: dict) -> dict[str, list[dict]]:
    """{id: [front matter, ...]} for every features/*/spec.md. A list so duplicates can be reported."""
    features: dict[str, list[dict]] = {}
    for p in sorted((specs_dir(root, cfg) / "features").glob("*/spec.md")):
        if p.parent.name.startswith("_"):
            continue  # _template
        fm = front_matter(p.read_text())
        fm["_path"] = p.relative_to(root).as_posix()
        features.setdefault(fm.get("id") or "", []).append(fm)
    return features


def done_ids(root: Path, cfg: dict) -> set[str]:
    d = Path(root) / cfg["paths"]["changes"]
    return {p.stem for p in d.glob("*.md")} if d.is_dir() else set()


# --- PR titles ------------------------------------------------------------------------------------------------------

TITLE = re.compile(
    r"^\[(?:(?P<fix>FIX-)?(?P<id>F\d+)|(?P<contract>C\d+)|(?P<plan>PLAN)|REVERT-(?P<sha>[0-9a-fA-F]{7,40}))\]"
)


def parse_title(title: str) -> dict | None:
    """{'kind': feature|fix|contract|plan|revert, 'id': 'F3' or 'C2' or None, 'sha': ...} or None."""
    m = TITLE.match((title or "").strip())
    if not m:
        return None
    if m["id"]:
        return {"kind": "fix" if m["fix"] else "feature", "id": m["id"], "sha": None}
    if m["contract"]:
        return {"kind": "contract", "id": m["contract"], "sha": None}
    if m["plan"]:
        return {"kind": "plan", "id": None, "sha": None}
    return {"kind": "revert", "id": None, "sha": m["sha"]}


# --- git / gh -------------------------------------------------------------------------------------------------------

def git(root: Path, *args: str, check: bool = True) -> str:
    return subprocess.run(["git", *args], cwd=root, check=check, capture_output=True, text=True).stdout


def git_lines(root: Path, *args: str) -> list[str]:
    return [line for line in git(root, *args).splitlines() if line.strip()]


def changed_files(root: Path, base: str) -> list[str]:
    return git_lines(root, "diff", "--name-only", "--no-renames", f"{base}...HEAD")


def gh_json(root: Path, *args: str):
    """Run `gh ... --json` and parse it. None if gh is missing, unauthenticated or fails."""
    if not shutil.which("gh"):
        return None
    try:
        r = subprocess.run(["gh", *args], cwd=root, capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


# --- CLI ------------------------------------------------------------------------------------------------------------

def parser(doc: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", help="repo root (default: nearest parent with kit.toml)")
    return p


def root_from(args) -> Path:
    return Path(args.root).resolve() if args.root else find_root()
