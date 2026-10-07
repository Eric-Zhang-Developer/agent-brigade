"""The milestone freeze, replayed: F03 (on the cut list) can merge before the freeze, but not during it."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[1]
SCRIPTS = EXAMPLE.parents[1] / "template" / "common" / ".agents" / "scripts"


class Milestone(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "jotter"
        shutil.copytree(EXAMPLE, self.root, ignore=shutil.ignore_patterns("__pycache__"))
        g = ["git", "-c", "user.email=a@example.com", "-c", "user.name=a", "-c", "core.hooksPath=/dev/null"]
        self.git = lambda *a: subprocess.run([*g, *a], cwd=self.root, capture_output=True, text=True)
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-qm", "main")
        self.git("checkout", "-qb", "f03-tags")
        (self.root / "jotter/tags.py").write_text("def tags_of(note):\n    return note.get('tags', [])\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "[F03] tags")

    def tearDown(self):
        self._tmp.cleanup()

    def gate(self, now):
        return subprocess.run([sys.executable, str(SCRIPTS / "check_gates.py"), "--root", str(self.root),
                               "--title", "[F03] Tags", "--base", "main", "--now", now], capture_output=True, text=True)

    def test_before_freeze_ok(self):
        self.assertEqual(self.gate("2026-10-25T12:00:00+00:00").returncode, 0)

    def test_cut_feature_blocked_in_freeze(self):
        r = self.gate("2026-10-31T12:00:00+00:00")
        self.assertEqual(r.returncode, 1)
        self.assertIn("cut list", r.stdout)

    def test_status_shows_the_milestone(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "status.py"), "--root", str(self.root), "--offline",
                            "--out", "-", "--now", "2026-10-20T12:00:00+00:00"], capture_output=True, text=True)
        self.assertIn("milestone first-ship ships 2026-11-01 (12 days)", r.stdout)


if __name__ == "__main__":
    unittest.main()
