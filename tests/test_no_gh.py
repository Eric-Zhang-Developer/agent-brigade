"""Scripts degrade with one clear line, never a traceback: gh missing or logged out, a bad milestones.toml, a bad --now."""

import os
import shutil
import subprocess
import sys
import unittest

import helpers

GH_LINES = {
    ("sync_issues.py",): "sync_issues: gh unavailable, not authenticated, or no GitHub remote; nothing synced",
    ("status.py", "--issue"): "status: gh unavailable or not authenticated; nothing updated",
    ("watchdog.py", "--once"): "watchdog: gh unavailable or not authenticated: skipping the claims and main CI checks",
}


class Degrades(helpers.RepoCase):
    def run_script(self, name, *args, path=None):
        env = dict(os.environ, PATH=path or os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, str(helpers.SCRIPTS / name), "--root", str(self.root), *args],
                              capture_output=True, text=True, env=env)

    def path_without_gh(self) -> str:
        """PATH minus every folder holding gh; git is linked in from a scratch folder if it shared one with gh."""
        keep = [d for d in os.environ["PATH"].split(os.pathsep) if d and not shutil.which("gh", path=d)]
        if not shutil.which("git", path=os.pathsep.join(keep)):
            bin_dir = self.root / ".git/no-gh-bin"
            bin_dir.mkdir()
            os.symlink(shutil.which("git"), bin_dir / "git")
            keep.insert(0, str(bin_dir))
        return os.pathsep.join(keep)

    def assert_one_line(self, r, line, code=1):
        self.assertNotIn("Traceback", r.stdout + r.stderr)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        self.assertIn(line, r.stdout + r.stderr)

    def test_gh_missing(self):
        path = self.path_without_gh()
        for (name, *args), line in GH_LINES.items():
            with self.subTest(name):
                r = self.run_script(name, *args, path=path)
                self.assert_one_line(r, line, code=0 if name == "watchdog.py" else 1)

    @unittest.skipIf(os.name == "nt", "a shell-script stub can't stand in for gh.exe on Windows")
    def test_gh_logged_out(self):
        stub = self.root / ".git/stub-bin"
        stub.mkdir()
        (stub / "gh").write_text("#!/bin/sh\necho 'To get started with GitHub CLI, please run:  gh auth login' >&2\n"
                                 "exit 4\n")
        (stub / "gh").chmod(0o755)
        for (name, *args), line in GH_LINES.items():
            with self.subTest(name):
                r = self.run_script(name, *args, path=f"{stub}{os.pathsep}{os.environ['PATH']}")
                self.assert_one_line(r, line, code=0 if name == "watchdog.py" else 1)

    def test_bad_milestones_toml(self):
        helpers.write(self.root, {"specs/milestones.toml": 'start = "2026-10-10T09:00"\n'})
        for name, *args in (("ship.py", "v1"), ("sync_issues.py",)):
            with self.subTest(name):
                self.assert_one_line(self.run_script(name, *args), "milestones.toml: ")

    def test_bad_now_is_a_usage_error(self):
        r = self.run_script("check_gates.py", "--title", "docs: x", "--now", "tomorrow")
        self.assert_one_line(r, "invalid fromisoformat value: 'tomorrow'", code=2)
        r = self.run_script("status.py", "--out", "-", "--offline", "--now", "tomorrow")
        self.assert_one_line(r, "invalid fromisoformat value: 'tomorrow'", code=2)


if __name__ == "__main__":
    unittest.main()
