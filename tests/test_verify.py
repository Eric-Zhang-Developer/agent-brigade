import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import helpers
from lib import note_section
from verify import main


class Verify(helpers.RepoCase):
    def run_verify(self, command, *args, commit=False):
        helpers.write(self.root, {".agents/config.toml": f"[verify]\ncommand = '{command}'\n"})
        if commit:
            self.commit("config")
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.root), *args])
        return rc, out.getvalue()

    def test_not_set_up_is_reported_not_hidden(self):
        rc, out = self.run_verify("", "--slug", "map-data")
        self.assertEqual(rc, 0)
        self.assertIn("not set up", out)
        self.assertIn("not verified", out)

    def last(self, out):
        return out.strip().splitlines()[-1]

    def test_pass_and_fail_give_one_pasteable_line_with_the_commit(self):
        sha = helpers.sh(self.root, "git", "rev-parse", "--short", "HEAD").strip()
        rc, out = self.run_verify("exit 0", "--slug", "map-data")   # config just changed: uncommitted
        self.assertEqual((rc, self.last(out)), (0, f"verify: `exit 0` pass at {sha} (uncommitted changes)"))
        rc, out = self.run_verify("exit 3", "--slug", "map-data", commit=True)
        sha = helpers.sh(self.root, "git", "rev-parse", "--short", "HEAD").strip()
        self.assertEqual((rc, self.last(out)), (1, f"verify: `exit 3` FAIL (exit 3) at {sha}"))

    def test_timeout_fails_and_stops_what_it_started(self):
        marker = self.root / "survived"
        helpers.write(self.root, {".agents/config.toml": f"[verify]\ncommand = '(sleep 2; touch {marker}) & sleep 30'\ntimeout = 0.5\n"})
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.root), "--slug", "a"])
        self.assertEqual(rc, 1)
        self.assertIn("timed out after 0.5s", self.last(out.getvalue()))
        import time
        time.sleep(2.5)
        self.assertFalse(marker.exists(), "a background child outlived the verifier")

    def test_background_server_is_stopped_after_a_pass(self):
        marker = self.root / "leaked"
        rc, _ = self.run_verify(f"(sleep 1; touch {marker}) & true", "--slug", "a")
        self.assertEqual(rc, 0)
        import time
        time.sleep(1.5)
        self.assertFalse(marker.exists())

    def test_out_is_a_fresh_kept_evidence_folder(self):
        rc, out = self.run_verify("echo shot > {out}/screen.txt", "--slug", "map-data")
        self.assertEqual(rc, 0)
        line = self.last(out)
        kept = Path(line.split("(evidence: ")[1].rstrip(")"))
        self.assertEqual((kept / "screen.txt").read_text(), "shot\n")
        self.assertIn("agent-evidence/map-data", str(kept))
        self.assertNotIn("evidence", helpers.sh(self.root, "git", "status", "--porcelain"))

    def test_placeholders_are_filled_and_the_path_is_quoted(self):
        wt = self.root / "a worktree"
        wt.mkdir()
        rc, _ = self.run_verify('test "$(basename {worktree})" = "a worktree" && test {slug} = map-data',
                                "--slug", "map-data", "--worktree", str(wt))
        self.assertEqual(rc, 0)

    def test_runs_in_the_worktree(self):
        wt = self.root / "wt"
        wt.mkdir()
        (wt / "marker").write_text("x")
        self.assertEqual(self.run_verify("test -f marker", "--slug", "a", "--worktree", str(wt))[0], 0)
        self.assertEqual(self.run_verify("test -f marker", "--slug", "a")[0], 1)

    def test_bad_slug_and_bad_placeholder(self):
        self.assertEqual(self.run_verify("true", "--slug", "x; rm -rf /")[0], 2)
        rc, out = self.run_verify("echo {nope}", "--slug", "a")
        self.assertEqual(rc, 1)
        self.assertIn("bad placeholder", out)


class NoteSection(unittest.TestCase):
    NOTE = "# x\n\n## What shipped\nA thing.\n\n## How to check it\nverify: `make smoke` pass\n\n## Gaps\nNone.\n"

    def test_reads_one_section(self):
        self.assertEqual(note_section(self.NOTE, "How to check it"), "verify: `make smoke` pass")
        self.assertEqual(note_section(self.NOTE, "Gaps"), "None.")
        self.assertIsNone(note_section(self.NOTE, "Where it lives"))


if __name__ == "__main__":
    unittest.main()
