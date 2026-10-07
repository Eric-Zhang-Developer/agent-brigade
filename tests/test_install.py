import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

import helpers

INSTALL = helpers.KIT / "install.py"


def install(target: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(INSTALL), str(target), *args], capture_output=True, text=True)


def script(target: Path, name: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(target / ".agents/scripts" / name), "--root", str(target), *args],
                          capture_output=True, text=True)


def tracked_files(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                  if p.is_file() and ".git" not in p.relative_to(root).parts)


class Install(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "my-project"
        self.root.mkdir()
        helpers.sh(self.root, "git", "init", "-q", "-b", "main")
        (self.root / "app.py").write_text("print('the existing project')\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_project_lite_is_small_neutral_and_works(self):
        start = time.monotonic()
        r = install(self.root, "--profile", "project", "--lite")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertLess(time.monotonic() - start, 10)
        files = tracked_files(self.root)
        installed = [f for f in files if f not in ("app.py", ".gitignore")]
        self.assertLessEqual(len(installed), 25, installed)  # v0.3 added ship.py
        for rel in ("AGENTS.md", "CLAUDE.md", "NOW.md", ".agents/config.toml", ".agents/hooks/pre-commit",
                    ".agents/scripts/sync_issues.py", ".agents/scripts/ship.py", "specs/milestones.toml", ".github/workflows/ci.yml",
                    ".github/ISSUE_TEMPLATE/needs-human.md", "changes/.gitkeep", "app.py"):
            self.assertIn(rel, files)
        for absent in (".agents/scripts/verify_release.py", "specs/gates.toml", "README.md", "docs", "examples"):
            self.assertFalse(any(f.startswith(absent) for f in files), absent)
        # no fingerprint: nothing installed names the kit
        for f in files:
            text = (self.root / f).read_text(errors="replace").lower()
            self.assertNotIn("agent-brigade", text, f)
            self.assertNotIn("brigade", text, f)
        cfg = tomllib.loads((self.root / ".agents/config.toml").read_text())
        self.assertEqual((cfg["profile"], cfg["size"], cfg["agents"]["max_parallel"], cfg["ownership"]["open"]),
                         ("project", "lite", 1, ["NOW.md"]))
        agents = (self.root / "AGENTS.md").read_text()
        self.assertIn("## Project rules", agents)
        self.assertIn("## Lite mode", agents)
        self.assertIn("Lite has no claims", agents)
        self.assertNotIn("draft PR", agents)
        self.assertNotIn("__", agents)
        self.assertEqual(cfg["schema"], 3)
        self.assertIn("__pycache__/", (self.root / ".gitignore").read_text().splitlines())
        self.assertEqual(helpers.sh(self.root, "git", "config", "core.hooksPath").strip(), ".agents/hooks")
        # the installed scripts run in place
        self.assertEqual(script(self.root, "check_ownership.py", "--lint-specs").returncode, 0)
        self.assertEqual(script(self.root, "status.py", "--offline", "--out", "-").returncode, 0)

    def test_hackathon_full_gets_release_scripts_and_milestones(self):
        r = install(self.root, "--profile", "hackathon", "--full")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        files = tracked_files(self.root)
        for rel in (".agents/scripts/verify_release.py", ".agents/scripts/demo_snapshot.py", "specs/milestones.toml",
                    "specs/context/.gitkeep"):
            self.assertIn(rel, files)
        self.assertNotIn("NOW.md", files)
        self.assertNotIn("specs/gates.toml", files)
        self.assertIn('start = ""', (self.root / "specs/milestones.toml").read_text())
        agents = (self.root / "AGENTS.md").read_text()
        self.assertIn("## Hackathon rules", agents)
        self.assertIn("**draft PR**", agents)
        self.assertNotIn("## Lite mode", agents)
        self.assertEqual(script(self.root, "check_ownership.py", "--lint-specs").returncode, 0)

    def test_rerun_refreshes_scripts_keeps_edits_and_switches_profile(self):
        install(self.root, "--profile", "hackathon", "--lite")
        (self.root / "AGENTS.md").write_text("# mine\n")
        (self.root / "specs/mission.md").write_text("# Mission: mine\n")
        (self.root / ".agents/scripts/lib.py").write_text("# stale\n")
        r = install(self.root, "--profile", "project", "--full")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("refreshed .agents/scripts/lib.py", r.stdout)
        self.assertIn("switched .agents/config.toml to project/full (was hackathon/lite)", r.stdout)
        self.assertIn("kept your AGENTS.md", r.stdout)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "# mine\n")
        self.assertEqual((self.root / "specs/mission.md").read_text(), "# Mission: mine\n")
        self.assertTrue((self.root / "NOW.md").exists())
        r = install(self.root, "--profile", "project", "--overwrite-agents")
        self.assertIn("## Project rules", (self.root / "AGENTS.md").read_text())
        self.assertNotIn("## Lite mode", (self.root / "AGENTS.md").read_text())  # size kept from config: full

    def test_second_run_changes_nothing(self):
        install(self.root, "--profile", "project")
        r = install(self.root, "--profile", "project")
        self.assertEqual([l for l in r.stdout.splitlines() if "created" in l or "refreshed" in l], [])

    def test_codeowners_from_review_paths(self):
        install(self.root, "--profile", "project")
        (self.root / "specs/review-paths.toml").write_text('[[path]]\nprefix = "db/"\nowners = ["@me"]\nwhy = "schema"\n')
        install(self.root, "--profile", "project")
        self.assertIn("/db/ @me", (self.root / ".github/CODEOWNERS").read_text())

    def test_older_schema_stops_until_upgrade(self):
        install(self.root, "--profile", "project", "--lite")
        cfg = self.root / ".agents/config.toml"
        cfg.write_text(cfg.read_text().replace("schema = 3", "").replace("# layout version", "# was"))
        (self.root / ".agents/scripts/lib.py").write_text("# stale\n")
        r = install(self.root, "--profile", "project")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Follow "From schema 2"', r.stdout + r.stderr)
        self.assertEqual((self.root / ".agents/scripts/lib.py").read_text(), "# stale\n")   # nothing touched
        r = install(self.root, "--profile", "project", "--upgrade")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("stamped .agents/config.toml with schema = 3", r.stdout)
        self.assertEqual(tomllib.loads(cfg.read_text())["schema"], 3)
        self.assertIn("refreshed .agents/scripts/lib.py", r.stdout)

    def test_upgrade_flags_a_leftover_gates_file(self):
        install(self.root, "--profile", "hackathon")
        (self.root / "specs/gates.toml").write_text('run_start = ""\n')
        r = install(self.root, "--profile", "hackathon")
        self.assertIn("specs/gates.toml is no longer read", r.stdout)

    def test_v01_layout_stops(self):
        (self.root / "kit.toml").write_text('profile = "project"\n')
        r = install(self.root, "--profile", "project")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("From a v0.1 install", r.stdout + r.stderr)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_refuses_to_install_into_the_kit(self):
        r = install(helpers.KIT, "--profile", "project")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
