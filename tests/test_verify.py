import io
import unittest
from contextlib import redirect_stdout

import helpers
from lib import note_section
from verify import main


class Verify(helpers.RepoCase):
    def run_verify(self, command, *args):
        helpers.write(self.root, {".agents/config.toml": f"[verify]\ncommand = '{command}'\n"})
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.root), *args])
        return rc, out.getvalue()

    def test_not_set_up_is_reported_not_hidden(self):
        rc, out = self.run_verify("", "--slug", "map-data")
        self.assertEqual(rc, 0)
        self.assertIn("not set up", out)
        self.assertIn("not verified", out)

    def test_pass_and_fail_give_one_pasteable_line(self):
        rc, out = self.run_verify("exit 0", "--slug", "map-data")
        self.assertEqual((rc, out.strip().splitlines()[-1]), (0, "verify: `exit 0` pass"))
        rc, out = self.run_verify("exit 3", "--slug", "map-data")
        self.assertEqual((rc, out.strip().splitlines()[-1]), (1, "verify: `exit 3` FAIL (exit 3)"))

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
