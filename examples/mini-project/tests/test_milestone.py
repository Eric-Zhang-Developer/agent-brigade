"""The milestone freeze, replayed: tags (on the cut list) can merge before the freeze, but not during it."""

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
        self.git("checkout", "-qb", "tags")
        (self.root / "jotter/tags.py").write_text("def tags_of(note):\n    return note.get('tags', [])\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "feat(tags): tags")

    def tearDown(self):
        self._tmp.cleanup()

    def gate(self, now):
        return subprocess.run([sys.executable, str(SCRIPTS / "check_gates.py"), "--root", str(self.root),
                               "--title", "feat(tags): tags", "--base", "main", "--now", now], capture_output=True, text=True)

    def test_before_freeze_ok(self):
        self.assertEqual(self.gate("2026-10-25T12:00:00+00:00").returncode, 0)

    def test_cut_feature_blocked_in_freeze(self):
        r = self.gate("2026-10-31T12:00:00+00:00")
        self.assertEqual(r.returncode, 1)
        self.assertIn("cut list", r.stdout)

    def test_status_shows_the_milestone(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "status.py"), "--root", str(self.root), "--offline",
                            "--out", "-", "--now", "2026-10-20T12:00:00+00:00"], capture_output=True, text=True)
        self.assertIn("next milestone first-ship ships in 12d 12h, freeze in 10d 12h", r.stdout)

    def test_ship_archives_the_done_features(self):
        self.git("checkout", "-q", "main")
        r = subprocess.run([sys.executable, str(SCRIPTS / "ship.py"), "--root", str(self.root), "first-ship"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tags has no done note; it stays", r.stdout)
        page = (self.root / "specs/shipped/first-ship/README.md").read_text()
        self.assertIn("## Search (`search`)", page)
        lint = subprocess.run([sys.executable, str(SCRIPTS / "check_ownership.py"), "--root", str(self.root),
                               "--lint-specs"], capture_output=True, text=True)
        self.assertEqual(lint.returncode, 0, lint.stdout)


if __name__ == "__main__":
    unittest.main()
