#!/usr/bin/env python3
"""Install the agent workflow into a project, or switch its profile/size later.

  python3 install.py --profile project --lite  ~/code/my-project
  python3 install.py --profile hackathon --full .

Writes only what the project runs: AGENTS.md, CLAUDE.md, .agents/ (config, scripts, pre-commit hook), specs/
templates, changes/, CI, a PR template and an issue template. Nothing in the result names this kit.

Re-running is safe: .agents/scripts and .agents/hooks are refreshed (the kit owns them); every other file is only
created if missing, so your AGENTS.md, specs and NOW.md are never overwritten (use --overwrite-agents to regenerate
AGENTS.md). Labels and issues are created by CI on the first push to main.
"""

import argparse
import re
import shutil
import stat
import subprocess
import sys
import tomllib
from pathlib import Path

KIT = Path(__file__).resolve().parent
TEMPLATE = KIT / "template"
KIT_OWNED = (".agents/scripts/", ".agents/hooks/")
CODEOWNERS_HEADER = "# Generated from specs/review-paths.toml by the installer. Edit that file and re-run it."


def render_agents(profile: str, size: str) -> str:
    parts = TEMPLATE / "parts"
    text = (parts / "agents-common.md").read_text()
    read_now = "\n   Project: read `NOW.md` before all of these." if profile == "project" else ""
    text = text.replace("__PROFILE_READ__", read_now)
    text += (parts / f"agents-{profile}.md").read_text()
    if size == "lite":
        text += (parts / "agents-lite.md").read_text()
    return text


def render_config(profile: str, size: str) -> str:
    return ((TEMPLATE / "common/.agents/config.toml").read_text()
            .replace("__PROFILE__", profile).replace("__SIZE__", size)
            .replace("__OPEN__", '"NOW.md"' if profile == "project" else "")
            .replace("__PARALLEL__", "1" if size == "lite" else "3"))


def template_files(profile: str):
    """(source, relative destination) for every file the profile installs, except AGENTS.md and the config."""
    for layer in ("common", profile):
        base = TEMPLATE / layer
        for src in sorted(p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            rel = src.relative_to(base).as_posix()
            if rel != ".agents/config.toml":
                yield src, rel


def write_codeowners(target: Path) -> str | None:
    path = target / "specs/review-paths.toml"
    entries = tomllib.loads(path.read_text()).get("path", []) if path.is_file() else []
    dest = target / ".github/CODEOWNERS"
    if not entries or (dest.exists() and CODEOWNERS_HEADER not in dest.read_text()):
        return None
    dest.write_text("\n".join([CODEOWNERS_HEADER] + [f"/{e['prefix'].lstrip('/')} {' '.join(e['owners'])}"
                                                      for e in entries]) + "\n")
    return ".github/CODEOWNERS"


def enable_hook(target: Path) -> str:
    hook = target / ".agents/hooks/pre-commit"
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if not (target / ".git").exists():
        return "not a git repo yet: after `git init`, run `git config core.hooksPath .agents/hooks`"
    r = subprocess.run(["git", "config", "core.hooksPath", ".agents/hooks"], cwd=target, capture_output=True, text=True)
    return "pre-commit hook on" if r.returncode == 0 else f"hook not enabled: {r.stderr.strip()}"


def install(target: Path, profile: str, size: str | None, overwrite_agents: bool) -> list[str]:
    log: list[str] = []
    config = target / ".agents/config.toml"
    old = tomllib.loads(config.read_text()) if config.is_file() else None
    size = size or (old or {}).get("size", "full")

    for src, rel in template_files(profile):
        dest = target / rel
        if dest.exists() and (not rel.startswith(KIT_OWNED) or dest.read_bytes() == src.read_bytes()):
            continue
        log.append(f"{'refreshed' if dest.exists() else 'created'} {rel}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    if old is None:
        config.write_text(render_config(profile, size))
        log.append("created .agents/config.toml")
    elif (old.get("profile"), old.get("size")) != (profile, size):
        text = re.sub(r'(?m)^profile\s*=\s*"[^"]*"', f'profile = "{profile}"', config.read_text())
        text = re.sub(r'(?m)^size\s*=\s*"[^"]*"', f'size = "{size}"', text)
        config.write_text(text)
        log.append(f"switched .agents/config.toml to {profile}/{size} (was {old.get('profile')}/{old.get('size')})")

    agents = target / "AGENTS.md"
    if not agents.exists() or overwrite_agents:
        log.append(f"{'rewrote' if agents.exists() else 'created'} AGENTS.md")
        agents.write_text(render_agents(profile, size))
    elif old and (old.get("profile"), old.get("size")) != (profile, size):
        log.append("kept your AGENTS.md: pass --overwrite-agents to regenerate it for the new profile/size")

    for folder in ["changes"] + (["specs/context"] if profile == "hackathon" else []):
        if not (target / folder).exists():
            (target / folder).mkdir(parents=True)
            (target / folder / ".gitkeep").touch()  # so git tracks the empty folder
            log.append(f"created {folder}/")

    gi = target / ".gitignore"
    lines = gi.read_text().splitlines() if gi.exists() else []
    missing = [x for x in (".env", ".env.*") if x not in lines]
    if missing:
        gi.write_text("\n".join(lines + missing) + "\n")
        log.append(f"added {', '.join(missing)} to .gitignore")

    if profile == "project" and (made := write_codeowners(target)):
        log.append(f"wrote {made}")
    log.append(enable_hook(target))
    return log


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?", default=".", help="project folder (default: current directory)")
    ap.add_argument("--profile", required=True, choices=["hackathon", "project"])
    size = ap.add_mutually_exclusive_group()
    size.add_argument("--lite", dest="size", action="store_const", const="lite", help="one agent, least ceremony")
    size.add_argument("--full", dest="size", action="store_const", const="full", help="parallel agents (default)")
    ap.add_argument("--overwrite-agents", action="store_true", help="regenerate AGENTS.md even if it exists")
    args = ap.parse_args(argv)
    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"install: {target} is not a folder")
        return 2
    if target == KIT:
        print("install: that's the kit itself; pass your project's folder")
        return 2
    for line in install(target, args.profile, args.size, args.overwrite_agents):
        print(f"install: {line}")
    nxt = "NOW.md and specs/mission.md" if args.profile == "project" else "specs/mission.md, then set run_start in specs/gates.toml"
    print(f"install: done. Next: fill in {nxt}; push; make `ci` a required check on main.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
