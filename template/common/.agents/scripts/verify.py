#!/usr/bin/env python3
"""Run the project's verifier, so an agent sees its own change running instead of a person checking it by hand.

  verify.py --slug map-data [--worktree PATH]

Runs [verify].command from .agents/config.toml (a shell template with {slug} and {worktree}) in the worktree, shows
its output, then prints one result line. Put that line under `## How to check it` in the done note:
  verify: `<command>` pass
  verify: `<command>` FAIL (exit N)
  verify: not set up ([verify].command is empty); the done note says `not verified`
Exit codes: 0 pass or not set up, 1 fail or a broken command template, 2 usage.
"""

import shlex
import subprocess
import sys
from pathlib import Path

from lib import load_config, parser, root_from, slug_error


def main(argv=None) -> int:
    ap = parser(__doc__)
    ap.add_argument("--slug", required=True, help="the feature being verified")
    ap.add_argument("--worktree", help="where to run it (default: the repo root)")
    args = ap.parse_args(argv)
    if err := slug_error(args.slug):
        print(f"verify: --slug {args.slug!r}: {err}")
        return 2
    root = root_from(args)
    template = load_config(root)["verify"]["command"].strip()
    if not template:
        print("verify: not set up ([verify].command is empty); the done note says `not verified`")
        return 0
    worktree = Path(args.worktree).resolve() if args.worktree else root
    try:
        command = template.format(slug=args.slug, worktree=shlex.quote(str(worktree)))
    except (KeyError, IndexError, ValueError) as e:
        print(f"verify: [verify].command has a bad placeholder ({e}); use only {{slug}} and {{worktree}}")
        return 1
    sys.stdout.flush()
    rc = subprocess.run(command, shell=True, cwd=worktree).returncode
    print(f"verify: `{command}` pass" if rc == 0 else f"verify: `{command}` FAIL (exit {rc})")
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
