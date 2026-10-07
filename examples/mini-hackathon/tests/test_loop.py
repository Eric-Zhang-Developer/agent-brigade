"""Replays the agent loop for the `cli` feature against the kit's real checks, in a throwaway git repo.

main = the project before cli. A branch builds cli as an agent would; we then run the same commands CI runs.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[1]
SCRIPTS = EXAMPLE.parents[1] / "template" / "common" / ".agents" / "scripts"
CLI_FILES = ["wordfreq/__main__.py", "tests/test_cli.py", "changes/cli.md"]
TITLE = "feat(cli): command-line interface"
DURING_RUN, AFTER_FREEZE = "2026-01-10T14:00:00-05:00", "2026-01-11T06:00:00-05:00"


def run(root, *args):
    return subprocess.run(list(args), cwd=root, capture_output=True, text=True)


def check(root, script, *args):
    return run(root, sys.executable, str(SCRIPTS / script), "--root", str(root), *args)


class Loop(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "wordfreq"
        shutil.copytree(EXAMPLE, self.root, ignore=shutil.ignore_patterns("__pycache__"))
        stash = Path(self._tmp.name) / "cli"
        for rel in CLI_FILES:  # main starts without cli
            (stash / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(self.root / rel, stash / rel)
        g = ["git", "-c", "user.email=agent@example.com", "-c", "user.name=agent", "-c", "core.hooksPath=/dev/null"]
        self.git = lambda *a: run(self.root, *g, *a)
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "main before cli", "--date", "2026-01-10T10:00:00-05:00")
        self.git("checkout", "-q", "-b", "cli")
        for rel in CLI_FILES:  # the agent builds cli in its branch
            shutil.copy(stash / rel, self.root / rel)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", TITLE, "--date", "2026-01-10T13:00:00-05:00")

    def tearDown(self):
        self._tmp.cleanup()

    def test_status_before_shows_cli_ready(self):
        self.git("checkout", "-q", "main")
        out = check(self.root, "status.py", "--offline", "--out", "-", "--now", DURING_RUN).stdout
        self.assertIn("## Ready next (pick order)\n- cli Command-line interface", out)

    def test_the_pr_passes_every_ci_check(self):
        for script, args in [("check_ownership.py", ["--lint-specs"]),
                             ("check_ownership.py", ["--title", TITLE, "--base", "main"]),
                             ("check_gates.py", ["--title", TITLE, "--base", "main", "--now", DURING_RUN]),
                             ("check_markers.py", ["--base", "main"])]:
            r = check(self.root, script, *args)
            self.assertEqual(r.returncode, 0, f"{script}: {r.stdout}{r.stderr}")

    def test_editing_another_features_file_fails_ownership(self):
        (self.root / "wordfreq/rank.py").write_text("# drive-by edit\n")
        self.git("commit", "-qam", "oops")
        r = check(self.root, "check_ownership.py", "--title", TITLE, "--base", "main")
        self.assertEqual(r.returncode, 1)
        self.assertIn("wordfreq/rank.py is outside", r.stdout)

    def test_nothing_merges_before_bootstrap(self):
        self.git("checkout", "-q", "main")
        self.git("rm", "-q", "changes/bootstrap.md")  # pretend bootstrap hasn't landed yet
        self.git("commit", "-qm", "before bootstrap")
        self.git("checkout", "-q", "cli")
        early = check(self.root, "check_gates.py", "--title", TITLE, "--base", "main", "--now", DURING_RUN)
        self.assertEqual(early.returncode, 1)
        self.assertIn("bootstrap first", early.stdout)

    def test_final_freeze_blocks_features_but_not_fixes(self):
        late = check(self.root, "check_gates.py", "--title", TITLE, "--base", "main", "--now", AFTER_FREEZE)
        self.assertEqual(late.returncode, 1)
        self.assertIn("submission freeze", late.stdout)
        # after the freeze, a small fix on top of the merged feature still goes through
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--ff-only", "cli")
        self.git("checkout", "-q", "-b", "fix-cli")
        (self.root / "wordfreq/__main__.py").write_text((self.root / "wordfreq/__main__.py").read_text().replace(
            "Most frequent words", "The most frequent words"))
        self.git("commit", "-qam", "fix(cli): wording")
        own = check(self.root, "check_ownership.py", "--title", "fix(cli): wording", "--base", "main")
        gates = check(self.root, "check_gates.py", "--title", "fix(cli): wording", "--base", "main", "--now", AFTER_FREEZE)
        self.assertEqual((own.returncode, gates.returncode), (0, 0), own.stdout + gates.stdout)

    def test_conflict_marker_is_caught(self):
        with open(self.root / "wordfreq/__main__.py", "a") as f:
            f.write("<" * 7 + " HEAD\n")
        self.git("commit", "-qam", "bad merge")
        self.assertEqual(check(self.root, "check_markers.py", "--base", "main").returncode, 1)


if __name__ == "__main__":
    unittest.main()
