import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

import helpers


def fresh_copy(dest: Path) -> Path:
    """What `npx degit` gives you: the kit's files, no .git."""
    shutil.copytree(helpers.KIT, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agent-brigade"))
    return dest


def init(root: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "core/scripts/init.py"), "--root", str(root), *args],
                          capture_output=True, text=True)


def check(root: Path, script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "core/scripts" / script), "--root", str(root), *args],
                          capture_output=True, text=True)


class Init(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = fresh_copy(Path(self._tmp.name) / "my-project")

    def tearDown(self):
        self._tmp.cleanup()

    def test_hackathon_full_on_fresh_copy(self):
        start = time.monotonic()
        r = init(self.root, "--profile", "hackathon", "--full")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertLess(time.monotonic() - start, 10)
        self.assertFalse((self.root / "dev").exists())
        cfg = tomllib.loads((self.root / "kit.toml").read_text())
        self.assertEqual((cfg["profile"], cfg["size"], cfg.get("kit_dev")), ("hackathon", "full", None))
        for rel in ("specs/mission.md", "specs/roadmap.md", "specs/features/_template/spec.md", "specs/gates.toml",
                    "specs/inbox/needs-human.md", "specs/decisions/000-defaults.md", "changes/.gitkeep",
                    ".github/workflows/ci.yml", ".github/pull_request_template.md"):
            self.assertTrue((self.root / rel).exists(), rel)
        self.assertFalse((self.root / "NOW.md").exists())
        self.assertEqual((self.root / ".github/workflows/ci.yml").read_text(),
                         (helpers.KIT / "core/ci/ci.yml").read_text())   # user CI, not the kit's own
        self.assertFalse((self.root / "degit.json").exists())
        self.assertIn("not a git repo yet", r.stdout)
        # the copy passes its own checks straight away
        self.assertEqual(check(self.root, "check_ownership.py", "--lint-specs").returncode, 0)
        self.assertEqual(check(self.root, "status_report.py", "--offline", "--out", "-").returncode, 0)

    def test_project_lite_in_git_repo_installs_hook(self):
        helpers.sh(self.root, "git", "init", "-q", "-b", "main")
        r = init(self.root, "--profile", "project", "--lite")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cfg = tomllib.loads((self.root / "kit.toml").read_text())
        self.assertEqual((cfg["size"], cfg["agents"]["max_parallel"], cfg["ownership"]["open"]), ("lite", 1, ["NOW.md"]))
        for rel in ("NOW.md", "specs/milestones.toml", "specs/review-paths.toml"):
            self.assertTrue((self.root / rel).exists(), rel)
        self.assertEqual(helpers.sh(self.root, "git", "config", "core.hooksPath").strip(), "core/hooks")
        self.assertFalse((self.root / ".github/CODEOWNERS").exists())  # no review paths yet

    def test_rerun_never_overwrites_and_upgrades_profile(self):
        init(self.root, "--profile", "hackathon", "--lite")
        (self.root / "specs/mission.md").write_text("# Mission: mine\n")
        (self.root / "specs/review-paths.toml").parent.mkdir(exist_ok=True)
        r = init(self.root, "--profile", "project", "--full")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.root / "specs/mission.md").read_text(), "# Mission: mine\n")
        self.assertIn("now project/full (was hackathon/lite)", r.stdout)
        self.assertTrue((self.root / "NOW.md").exists())
        self.assertTrue((self.root / "specs/gates.toml").exists())  # kept, just no longer enforced

    def test_codeowners_from_review_paths(self):
        init(self.root, "--profile", "project")
        (self.root / "specs/review-paths.toml").write_text(
            '[[path]]\nprefix = "db/migrations/"\nowners = ["@me"]\nwhy = "schema"\n')
        init(self.root, "--profile", "project")
        text = (self.root / ".github/CODEOWNERS").read_text()
        self.assertIn("/db/migrations/ @me", text)

    def test_refuses_the_kit_source_repo(self):
        helpers.sh(self.root, "git", "init", "-q", "-b", "main")
        helpers.sh(self.root, "git", "-c", "user.email=t@e.st", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "1")
        helpers.sh(self.root, "git", "-c", "user.email=t@e.st", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "2")
        r = init(self.root, "--profile", "hackathon")
        self.assertEqual(r.returncode, 2)
        self.assertTrue((self.root / "dev").exists())


if __name__ == "__main__":
    unittest.main()
