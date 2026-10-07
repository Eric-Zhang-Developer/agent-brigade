import io
import subprocess
import unittest
from contextlib import redirect_stdout

import helpers
from check_markers import main

LT, EQ, GT = "<" * 7, "=" * 7, ">" * 7   # built here so this repo never holds a literal marker
CONFLICT = f"a\n{LT} HEAD\nmine\n{EQ}\ntheirs\n{GT} branch\n"


def run(root, *args):
    out = io.StringIO()
    with redirect_stdout(out):
        rc = main(["--root", str(root), *args])
    return rc, out.getvalue()


class Markers(helpers.RepoCase):
    files = {"kit.toml": 'profile = "project"\n[markers]\nignore = ["vendor/"]\n', "clean.py": "x = 1\n"}

    def test_staged_conflict(self):
        helpers.write(self.root, {"bad.txt": CONFLICT})
        helpers.sh(self.root, "git", "add", "bad.txt")
        rc, out = run(self.root, "--staged")
        self.assertEqual(rc, 1)
        self.assertEqual(out.count("conflict marker"), 3)
        self.assertIn("bad.txt:2:", out)

    def test_base_only_added_lines(self):
        self.commit("old debug", {"old.js": "console" + ".log(1)\n"})   # already on main: not this PR's problem
        self.branch("work")
        self.commit("new", {"new.py": "ok = True\n" + "break" + "point()\n"})
        rc, out = run(self.root, "--base", "main")
        self.assertEqual(rc, 1)
        self.assertIn("new.py:2: debug leftover", out)
        self.assertNotIn("old.js", out)

    def test_all_with_ignore_allow_and_binary(self):
        self.commit("files", {
            "vendor/lib.js": "console" + ".log(1)\n",
            "docs.md": f"{EQ}  markers: allow\n",
            "img.bin": "\0\0" + LT + " x\n",
        })
        rc, out = run(self.root, "--all")
        self.assertEqual(rc, 0, out)

    def test_clean_passes(self):
        self.assertEqual(run(self.root, "--all")[0], 0)

    def test_hook_blocks_commit(self):
        hooks = self.root / "core" / "hooks"
        hooks.mkdir(parents=True)
        (hooks / "pre-commit").write_bytes((helpers.KIT / "core/hooks/pre-commit").read_bytes())
        (hooks / "pre-commit").chmod(0o755)
        scripts = self.root / "core" / "scripts"
        scripts.mkdir()
        for name in ("kitlib.py", "check_markers.py", "check_ownership.py"):
            (scripts / name).write_bytes((helpers.SCRIPTS / name).read_bytes())
        helpers.sh(self.root, "git", "config", "core.hooksPath", "core/hooks")
        helpers.write(self.root, {"bad.txt": CONFLICT})
        helpers.sh(self.root, "git", "add", "-A")
        r = subprocess.run(["git", "commit", "-q", "-m", "x"], cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("conflict marker", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
