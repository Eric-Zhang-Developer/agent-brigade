import io
import unittest
from contextlib import redirect_stdout

import helpers
from check_gates import main

GATES = '''run_start = "2026-10-10T09:00:00-04:00"
[[gate]]
at = "0:00"
only = ["F00"]
[[gate]]
at = "2:00"
no_new_phase = 2
[[gate]]
at = "30:00"
freeze = true
allow = ["F09"]
max_lines = 5
[[gate]]
at = "34:00"
report = true
allow = ["F09"]
[[gate]]
at = "35:30"
hard_stop = true
'''
START = "2026-10-10T09:00:00-04:00"


def at(hhmm):  # ISO time hhmm after run start (same day or later)
    h, m = map(int, hhmm.split(":"))
    day, h = 10 + (9 + h) // 24, (9 + h) % 24
    return f"2026-10-{day:02d}T{h:02d}:{m:02d}:00-04:00"


class Base(helpers.RepoCase):
    def gate(self, title, now, files=None, date=None):
        if helpers.sh(self.root, "git", "branch", "--show-current").strip() == "main":
            self.branch("work")
        self.commit("work", files or {"src/x.py": "x\n"}, date=date)
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.root), "--title", title, "--base", "main", "--now", now])
        return rc, out.getvalue()


class Hackathon(Base):
    files = {
        "kit.toml": 'profile = "hackathon"\n[pr]\nmax_lines = 20\nexclude = ["data/"]\n',
        "specs/gates.toml": GATES,
        "specs/features/F01-a/spec.md": helpers.spec("F01", ["src/"], phase=1),
        "specs/features/F02-b/spec.md": helpers.spec("F02", ["lib/"], phase=2),
    }

    def test_before_start_no_gate(self):
        self.assertEqual(self.gate("[F01] a", "2026-10-10T08:00:00-04:00")[0], 0)

    def test_only(self):
        rc, out = self.gate("[F01] a", at("0:30"))
        self.assertEqual(rc, 1)
        self.assertIn("only ['F00']", out)

    def test_exactly_at_gate_time_applies(self):
        self.assertEqual(self.gate("[F02] b", at("2:00"), date=at("2:00"))[0], 1)

    def test_no_new_phase_blocks_unstarted(self):
        rc, out = self.gate("[F02] b", at("3:00"), date=at("2:30"))
        self.assertEqual(rc, 1)
        self.assertIn("no new phase 2+", out)

    def test_no_new_phase_allows_started_before(self):
        self.assertEqual(self.gate("[F02] b", at("3:00"), date=at("1:00"))[0], 0)

    def test_freeze(self):
        self.assertEqual(self.gate("[F01] a", at("31:00"))[0], 1)
        self.assertEqual(self.gate("[FIX-F01] a", at("31:00"))[0], 0)

    def test_freeze_allow_and_tighter_cap(self):
        rc, out = self.gate("[F09] report", at("31:00"), {"src/x.py": "1\n2\n3\n4\n5\n6\n"})
        self.assertEqual(rc, 1)
        self.assertIn("cap is 5", out)

    def test_report_and_hard_stop(self):
        self.assertEqual(self.gate("[PLAN] more", at("34:30"))[0], 1)
        self.assertEqual(self.gate("[F09] report", at("34:30"))[0], 0)
        self.assertEqual(self.gate("[FIX-F01] a", at("36:00"))[0], 1)

    def test_size_cap_excludes(self):
        big = "".join(f"{i}\n" for i in range(50))
        self.assertEqual(self.gate("[F01] a", at("5:00"), {"data/big.json": big})[0], 0)
        rc, out = self.gate("[F01] a", at("5:00"), {"src/big.py": big})
        self.assertEqual(rc, 1)
        self.assertIn("split it", out)

    def test_bad_title(self):
        self.assertEqual(self.gate("whatever", at("5:00"))[0], 1)


class Project(Base):
    files = {
        "kit.toml": 'profile = "project"\n[pr]\nmax_lines = 0\n',
        "specs/milestones.toml": '[[milestone]]\nname = "v1"\nship = "2026-11-15"\nfreeze_days = 3\n'
                                 'features = ["F01"]\ncut = ["F03"]\n[[milestone]]\nname = "later"\nship = ""\n',
    }

    def test_outside_freeze_anything(self):
        self.assertEqual(self.gate("[F02] b", "2026-11-01T12:00:00+00:00")[0], 0)

    def test_inside_freeze(self):
        self.assertEqual(self.gate("[F01] a", "2026-11-13T12:00:00+00:00")[0], 0)
        rc, out = self.gate("[F02] b", "2026-11-13T12:00:00+00:00")
        self.assertEqual(rc, 1)
        self.assertIn("milestone freeze", out)

    def test_cut_list(self):
        rc, out = self.gate("[FIX-F03] c", "2026-11-12T12:00:00+00:00")
        self.assertEqual(rc, 1)
        self.assertIn("cut list", out)

    def test_after_ship_no_freeze(self):
        self.assertEqual(self.gate("[F02] b", "2026-11-20T12:00:00+00:00")[0], 0)


class Missing(Base):
    files = {"kit.toml": 'profile = "hackathon"\n'}

    def test_no_gates_file_still_caps(self):
        rc, out = self.gate("[F01] a", "2026-10-10T12:00:00+00:00")
        self.assertEqual(rc, 0)
        self.assertIn("not enforced", out)


if __name__ == "__main__":
    unittest.main()
