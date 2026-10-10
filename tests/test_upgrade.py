"""Upgrading a real v0.4.0 install to the current kit keeps the project working and leaves the user's files alone.

The v0.4.0 template comes from git history (`git archive v0.4.0`), not npm, so this needs the tag: the kit's CI checks
out with fetch-depth: 0, which brings tags. Without it the test skips and says why.
"""

import subprocess
import sys
import tarfile
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

import helpers

OLD = "v0.4.0"
COMBOS = [(p, s) for p in ("hackathon", "project") for s in ("lite", "full")]
USER_FILES = {  # what a team edits right after installing; an upgrade must never touch these
    "AGENTS.md": "\n- House rule: our own line.\n",
    "specs/mission.md": "\nWe build a toy.\n",
    "specs/milestones.toml": "\n# our note\n",
    ".github/workflows/ci.yml": "\n# our own step goes here\n",
}


def has_tag() -> bool:
    r = subprocess.run(["git", "rev-parse", "-q", "--verify", f"{OLD}^{{commit}}"], cwd=helpers.KIT,
                       capture_output=True)
    return r.returncode == 0


def run(*args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True)


def snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts}


class Upgrade(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def project(self, name: str) -> Path:
        root = self.tmp / name
        root.mkdir()
        helpers.sh(root, "git", "init", "-q", "-b", "main")
        return root

    @unittest.skipUnless(has_tag(), f"tag {OLD} not in this clone (fetch with `git fetch --tags`; CI uses fetch-depth: 0)")
    def test_v040_install_upgrades_cleanly(self):
        old_kit = self.tmp / "old-kit"
        old_kit.mkdir()
        archive = subprocess.run(["git", "archive", OLD, "install.py", "template"], cwd=helpers.KIT,
                                 capture_output=True, check=True).stdout
        with tarfile.open(fileobj=BytesIO(archive)) as tar:
            tar.extractall(old_kit, filter="data")
        for profile, size in COMBOS:
            with self.subTest(profile=profile, size=size):
                root = self.project(f"{profile}-{size}")
                r = run(old_kit / "install.py", "--profile", profile, f"--{size}", root)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertFalse((root / ".agents/scripts/verify.py").exists(), f"{OLD} predates verify.py")
                for rel, extra in USER_FILES.items():
                    with (root / rel).open("a") as f:
                        f.write(extra)
                before = {rel: (root / rel).read_bytes() for rel in USER_FILES}

                r = run(helpers.KIT / "install.py", "--profile", profile, f"--{size}", "--upgrade", root)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                for rel, text in before.items():
                    self.assertEqual((root / rel).read_bytes(), text, f"{rel} changed")
                for new in ("verify.py", "pr_ready.py"):
                    self.assertTrue((root / ".agents/scripts" / new).is_file(), new)
                for script in (helpers.SCRIPTS / "lib.py", helpers.SCRIPTS / "status.py"):
                    self.assertEqual((root / ".agents/scripts" / script.name).read_bytes(), script.read_bytes())

                s = root / ".agents/scripts"
                r = run(s / "check_ownership.py", "--root", root, "--lint-specs")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                r = run(s / "status.py", "--root", root, "--offline", "--out", "-")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                r = run(s / "verify.py", "--root", root, "--slug", "bootstrap")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("not set up", r.stdout)

    def test_reinstalling_the_current_kit_changes_nothing(self):
        for profile, size in COMBOS:
            with self.subTest(profile=profile, size=size):
                root = self.project(f"again-{profile}-{size}")
                args = (helpers.KIT / "install.py", "--profile", profile, f"--{size}", root)
                self.assertEqual(run(*args).returncode, 0)
                first = snapshot(root)
                r = run(*args)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(snapshot(root), first)
                self.assertNotRegex(r.stdout, r"install: (created|refreshed|rewrote|switched|stamped|added|wrote) ")


if __name__ == "__main__":
    unittest.main()
