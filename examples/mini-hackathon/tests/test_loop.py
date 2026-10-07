"""Replays the agent loop for F03 against the kit's real checks, in a throwaway git repo.

main = the project before F03. A branch builds F03 as an agent would; we then run the same commands CI runs.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[1]
SCRIPTS = EXAMPLE.parents[1] / "template" / "common" / ".agents" / "scripts"
F03_FILES = ["wordfreq/__main__.py", "tests/test_cli.py", "changes/F03.md"]
DURING_RUN, AFTER_FREEZE, TOO_EARLY = "2026-01-10T14:00:00-05:00", "2026-01-11T06:00:00-05:00", "2026-01-10T09:30:00-05:00"


def run(root, *args):
    return subprocess.run(list(args), cwd=root, capture_output=True, text=True)


def check(root, script, *args):
    return run(root, sys.executable, str(SCRIPTS / script), "--root", str(root), *args)


class Loop(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "wordfreq"
        shutil.copytree(EXAMPLE, self.root, ignore=shutil.ignore_patterns("__pycache__"))
        stash = Path(self._tmp.name) / "f03"
        for rel in F03_FILES:  # main starts without F03
            (stash / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(self.root / rel, stash / rel)
        g = ["git", "-c", "user.email=agent@example.com", "-c", "user.name=agent", "-c", "core.hooksPath=/dev/null"]
        self.git = lambda *a: run(self.root, *g, *a)
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "main before F03", "--date", "2026-01-10T10:00:00-05:00")
        self.git("checkout", "-q", "-b", "f03-cli")
        for rel in F03_FILES:  # the agent builds F03 in its branch
            shutil.copy(stash / rel, self.root / rel)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "[F03] CLI", "--date", "2026-01-10T13:00:00-05:00")

    def tearDown(self):
        self._tmp.cleanup()

    def test_status_before_shows_f03_ready(self):
        self.git("checkout", "-q", "main")
        out = check(self.root, "status.py", "--offline", "--out", "-", "--now", DURING_RUN).stdout
        self.assertIn("## Ready next\n- F03 Command-line interface", out)

    def test_the_pr_passes_every_ci_check(self):
        for script, args in [("check_ownership.py", ["--lint-specs"]),
                             ("check_ownership.py", ["--title", "[F03] CLI", "--base", "main"]),
                             ("check_gates.py", ["--title", "[F03] CLI", "--base", "main", "--now", DURING_RUN]),
                             ("check_markers.py", ["--base", "main"])]:
            r = check(self.root, script, *args)
            self.assertEqual(r.returncode, 0, f"{script}: {r.stdout}{r.stderr}")

    def test_editing_another_features_file_fails_ownership(self):
        (self.root / "wordfreq/rank.py").write_text("# drive-by edit\n")
        self.git("commit", "-qam", "oops")
        r = check(self.root, "check_ownership.py", "--title", "[F03] CLI", "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("wordfreq/rank.py is outside", r.stdout)

    def test_gates_block_too_early_and_after_freeze(self):
        early = check(self.root, "check_gates.py", "--title", "[F03] CLI", "--base", "main", "--now", TOO_EARLY)
        self.assertIn("only ['F00']", early.stdout)
        late = check(self.root, "check_gates.py", "--title", "[F03] CLI", "--base", "main", "--now", AFTER_FREEZE)
        self.assertIn("freeze", late.stdout)
        self.assertEqual((early.returncode, late.returncode), (1, 1))
        # after the freeze, a small fix on top of the merged feature still goes through
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--ff-only", "f03-cli")
        self.git("checkout", "-q", "-b", "fix-f03")
        (self.root / "wordfreq/__main__.py").write_text((self.root / "wordfreq/__main__.py").read_text().replace(
            "Most frequent words", "The most frequent words"))
        self.git("commit", "-qam", "[FIX-F03] wording")
        fix = check(self.root, "check_gates.py", "--title", "[FIX-F03] wording", "--base", "main", "--now", AFTER_FREEZE)
        self.assertEqual(fix.returncode, 0, fix.stdout)

    def test_conflict_marker_is_caught(self):
        with open(self.root / "wordfreq/__main__.py", "a") as f:
            f.write("<" * 7 + " HEAD\n")
        self.git("commit", "-qam", "bad merge")
        self.assertEqual(check(self.root, "check_markers.py", "--base", "main").returncode, 1)


if __name__ == "__main__":
    unittest.main()
