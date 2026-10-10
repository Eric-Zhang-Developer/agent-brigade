#!/usr/bin/env python3
"""Install the agent workflow into a project, or switch its profile/size later.

  python3 install.py --profile project --lite  ~/code/my-project
  python3 install.py --profile hackathon --full .

Writes only what the project runs: AGENTS.md, CLAUDE.md, .agents/ (config, scripts, pre-commit hook), specs/
templates, changes/, CI, a PR template and an issue template. Nothing in the result names this kit.

Re-running is safe: .agents/scripts and .agents/hooks are refreshed (the kit owns them); every other file is only
created if missing, so your AGENTS.md, specs and NOW.md are never overwritten (use --overwrite-agents to regenerate
AGENTS.md). Labels and issues are created by CI on the first push to main.

`schema` in .agents/config.toml says which layout a project uses. If it's older than this kit's, the installer
stops and points at the steps in docs/upgrading.md; re-run with --upgrade once they're done.
"""

import sys

if sys.version_info < (3, 11):  # tomllib; checked first so an older python3 gets this line, not a traceback
    sys.exit(f"install: needs Python 3.11+, found {sys.version.split()[0]} (macOS: brew install python)")

import argparse
import re
import shutil
import stat
import subprocess
import tomllib
from pathlib import Path

KIT = Path(__file__).resolve().parent
TEMPLATE = KIT / "template"
KIT_OWNED = (".agents/scripts/", ".agents/hooks/")
SCHEMA = int(re.search(r"(?m)^SCHEMA = (\d+)", (TEMPLATE / "common/.agents/scripts/lib.py").read_text())[1])
CODEOWNERS_HEADER = "# Generated from specs/review-paths.toml by the installer. Edit that file and re-run it."


def render_agents(profile: str, size: str) -> str:
    parts = TEMPLATE / "parts"
    text = (parts / "agents-common.md").read_text()
    read_now = "\n   Project: read `NOW.md` before all of these." if profile == "project" else ""
    text = text.replace("__PROFILE_READ__", read_now)
    if size == "lite":
        claim = ("2. No claim in lite: build first, then open the PR at step 6, titled `feat(<slug>): <name>`, with\n"
                 "   `Closes #<n>` (the feature's issue) in the body.")
    else:
        claim = ("2. Push and open a **draft PR** titled `feat(<slug>): <name>` right away. The draft is your claim. Put\n"
                 "   `Closes #<n>` (the feature's issue) and your worker name in the body. Mark it ready at step 6.")
    text = text.replace("__CLAIM__", claim)
    text += (parts / f"agents-{profile}.md").read_text()
    if size == "lite":
        text += (parts / "agents-lite.md").read_text()
    return text


def render_config(profile: str, size: str) -> str:
    return ((TEMPLATE / "common/.agents/config.toml").read_text()
            .replace("__SCHEMA__", str(SCHEMA)).replace("__PROFILE__", profile).replace("__SIZE__", size)
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
    # Setting core.hooksPath silently turns off hooks the project already has (its own .git/hooks, husky), so don't.
    current = subprocess.run(["git", "config", "core.hooksPath"], cwd=target, capture_output=True, text=True).stdout.strip()
    if current == ".agents/hooks":
        return "pre-commit hook on"
    git_path = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=target, capture_output=True,
                              text=True).stdout.strip()  # absolute in a linked worktree
    hooks = target / git_path
    own = sorted(p.name for p in hooks.iterdir() if not p.name.endswith(".sample")) if hooks.is_dir() else []
    if current or own:
        why = f"core.hooksPath is {current}" if current else f"{git_path} has {', '.join(own)}"
        return f"kept your git hooks ({why}): to add the checks, run `sh .agents/hooks/pre-commit` from your pre-commit hook"
    r = subprocess.run(["git", "config", "core.hooksPath", ".agents/hooks"], cwd=target, capture_output=True, text=True)
    return "pre-commit hook on" if r.returncode == 0 else f"hook not enabled: {r.stderr.strip()}"


def schema_problem(target: Path, old: dict | None, upgrade: bool) -> str | None:
    """Why the install must stop before touching anything, or None."""
    if (target / "kit.toml").exists():
        return ("this project uses the v0.1 layout (kit.toml). Follow \"From a v0.1 install\" in docs/upgrading.md "
                "first; it ends by running this installer.")
    have = (old or {}).get("schema", 2) if old is not None else SCHEMA
    if have < SCHEMA and not upgrade:
        return (f"this project uses schema {have}; this kit writes schema {SCHEMA}. Follow \"From schema {have}\" in "
                "docs/upgrading.md, then re-run with --upgrade.")
    if have > SCHEMA:
        return f"this project uses schema {have}, newer than this kit ({SCHEMA}): update your copy of the kit."
    return None


def install(target: Path, profile: str, size: str | None, overwrite_agents: bool, upgrade: bool = False) -> list[str]:
    log: list[str] = []
    config = target / ".agents/config.toml"
    old = tomllib.loads(config.read_text()) if config.is_file() else None
    if problem := schema_problem(target, old, upgrade):
        raise SystemExit(f"install: stopped: {problem}")
    size = size or (old or {}).get("size", "full")

    for src, rel in template_files(profile):
        dest = target / rel
        if dest.exists() and (not rel.startswith(KIT_OWNED) or dest.read_bytes() == src.read_bytes()):
            if rel.startswith(".github/") and dest.read_bytes() != src.read_bytes():
                log.append(f"kept your {rel}")
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
    if old is not None and old.get("schema", 2) < SCHEMA:
        text = config.read_text()
        if re.search(r"(?m)^schema\s*=", text):
            text = re.sub(r"(?m)^schema\s*=.*$", f"schema = {SCHEMA}", text)
        else:
            text = f"schema = {SCHEMA}\n" + text
        config.write_text(text)
        log.append(f"stamped .agents/config.toml with schema = {SCHEMA}")
    if (target / "specs/gates.toml").exists():
        log.append("specs/gates.toml is no longer read: move its deadlines into specs/milestones.toml and delete it")

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
    missing = [x for x in (".env", ".env.*", "__pycache__/") if x not in lines]
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
    ap.add_argument("--profile", required=True, choices=["hackathon", "project"],
                    help="hackathon: a deadline and a demo; project: ongoing work with NOW.md")
    size = ap.add_mutually_exclusive_group()
    size.add_argument("--lite", dest="size", action="store_const", const="lite", help="one agent, least ceremony")
    size.add_argument("--full", dest="size", action="store_const", const="full", help="parallel agents (default)")
    ap.add_argument("--overwrite-agents", action="store_true", help="regenerate AGENTS.md even if it exists")
    ap.add_argument("--upgrade", action="store_true", help="the upgrade steps are done: refresh and stamp the schema")
    args = ap.parse_args(argv)
    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"install: {target} is not a folder")
        return 2
    if target == KIT:
        print("install: that's the kit itself; pass your project's folder")
        return 2
    for line in install(target, args.profile, args.size, args.overwrite_agents, args.upgrade):
        print(f"install: {line}")
    nxt = "NOW.md and specs/mission.md" if args.profile == "project" else "specs/mission.md, then set start in specs/milestones.toml"
    print(f"install: done. Next: fill in {nxt}; push; make `ci` a required check on main:")
    print('install:   gh api -X PUT repos/{owner}/{repo}/branches/main/protection --input - <<< '
          '\'{"required_status_checks":{"strict":false,"contexts":["ci"]},"enforce_admins":false,'
          '"required_pull_request_reviews":null,"restrictions":null}\'')
    return 0


if __name__ == "__main__":
    sys.exit(main())
