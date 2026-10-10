import io
import unittest
from contextlib import redirect_stdout

import helpers
from check_gates import main

MILESTONES = '''start = "2026-10-10T09:00:00-04:00"
[[milestone]]
name = "core"
ship = "+24:00"
features = ["boot", "alpha"]
[[milestone]]
name = "submission"
ship = "+35:30"
freeze = "5:30"
final = true
report_before = "1:30"
features = ["beta"]
cut = ["beta"]
allow = ["reporter"]
'''


def at(hhmm):  # ISO time hhmm after the start
    h, m = map(int, hhmm.split(":"))
    day, h = 10 + (9 + h) // 24, (9 + h) % 24
    return f"2026-10-{day:02d}T{h:02d}:{m:02d}:00-04:00"


class Base(helpers.RepoCase):
    def gate(self, title, now, files=None):
        if helpers.sh(self.root, "git", "branch", "--show-current").strip() == "main":
            self.branch("work")
        self.commit("work", files or {"src/x.py": "x\n"})
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.root), "--title", title, "--base", "main", "--now", now])
        return rc, out.getvalue()


class Hackathon(Base):
    files = {
        ".agents/config.toml": 'profile = "hackathon"\n[pr]\nwarn_lines = 20\nexclude = ["data/"]\n',
        "specs/milestones.toml": MILESTONES,
        "specs/features/boot/spec.md": helpers.spec([], extra="bootstrap: true\n"),
        "specs/features/alpha/spec.md": helpers.spec(["src/"]),
        "specs/features/beta/spec.md": helpers.spec(["lib/"]),
        "specs/features/gamma/spec.md": helpers.spec(["etc/"]),
        "specs/features/reporter/spec.md": helpers.spec(["reports/"]),
        "changes/boot.md": "done\n",
    }

    def test_open_before_the_freeze(self):
        self.assertEqual(self.gate("feat(gamma): g", at("5:00"))[0], 0)       # backlog may merge; it's just not picked

    def test_freeze_only_its_features_and_allow(self):
        rc, out = self.gate("feat(gamma): g", at("31:00"))
        self.assertEqual(rc, 1)
        self.assertIn("submission freeze", out)
        self.assertEqual(self.gate("fix(alpha): a", at("31:00"))[0], 0)
        self.assertEqual(self.gate("feat(reporter): r", at("31:00"))[0], 0)

    def test_exactly_at_freeze_time_applies(self):
        self.assertEqual(self.gate("feat(gamma): g", at("30:00"))[0], 1)

    def test_cut_list_in_freeze(self):
        rc, out = self.gate("fix(beta): b", at("31:00"))
        self.assertEqual(rc, 1)
        self.assertIn("cut list", out)

    def test_no_plans_in_final_freeze(self):
        self.assertEqual(self.gate("plan: more", at("31:00"))[0], 1)

    def test_done_note_without_a_check_warns_but_passes(self):
        note = "## What shipped\nA.\n\n## How to check it\n{}\n\n## Gaps\nNone.\n"
        for body, warns in (("Looked at it.", True), ("", True), ("verify: `make smoke` pass", False),
                            ("not verified: no verifier yet", False)):
            with self.subTest(body=body):
                rc, out = self.gate("feat(alpha): a", at("5:00"), {"src/x.py": "x\n", "changes/alpha.md": note.format(body)})
                self.assertEqual(rc, 0, out)
                self.assertEqual("How to check it" in out, warns, out)
        rc, out = self.gate("fix(alpha): a", at("5:00"), {"src/y.py": "y\n"})   # fixes and no-note PRs: no warning
        self.assertNotIn("How to check it", out)

    def test_report_window_and_hard_stop(self):
        self.assertEqual(self.gate("feat(reporter): r", at("34:30"))[0], 0)
        self.assertEqual(self.gate("fix(alpha): a", at("34:30"))[0], 0)
        rc, out = self.gate("contract: late", at("34:30"))
        self.assertEqual(rc, 1)
        self.assertIn("report window", out)
        rc, out = self.gate("fix(alpha): a", at("35:30"))
        self.assertEqual(rc, 1)
        self.assertIn("hard stop", out)

    def test_large_pr_warns_never_fails(self):
        big = "".join(f"{i}\n" for i in range(50))
        rc, out = self.gate("feat(alpha): a", at("5:00"), {"src/big.py": big})
        self.assertEqual(rc, 0, out)
        self.assertIn("large PR (50 changed lines, guideline 20)", out)  # ::warning:: in Actions

    def test_excluded_paths_dont_count(self):
        big = "".join(f"{i}\n" for i in range(50))
        rc, out = self.gate("feat(alpha): a", at("5:00"), {"data/big.json": big})
        self.assertNotIn("large PR", out)

    def test_summary(self):
        out = self.gate("feat(alpha): a", at("5:00"))[1]
        self.assertIn("elapsed 5:00, next milestone core ships in 19:00", out)

    def test_bad_title(self):
        self.assertEqual(self.gate("[F01] old", at("5:00"))[0], 1)


class BootstrapFirst(Base):
    files = {
        ".agents/config.toml": 'profile = "project"\n',
        "specs/features/boot/spec.md": helpers.spec([], extra="bootstrap: true\n"),
        "specs/features/alpha/spec.md": helpers.spec(["src/"]),
    }

    def test_nothing_before_bootstrap(self):
        rc, out = self.gate("feat(alpha): a", "2026-10-10T12:00:00+00:00")
        self.assertEqual(rc, 1)
        self.assertIn("bootstrap first: boot", out)
        self.assertEqual(self.gate("feat(boot): skeleton", "2026-10-10T12:00:00+00:00")[0], 0)
        self.assertEqual(self.gate("fix: typo", "2026-10-10T12:00:00+00:00")[0], 0)


class Project(Base):
    files = {
        ".agents/config.toml": 'profile = "project"\n[pr]\nwarn_lines = 0\n',
        "specs/milestones.toml": '[[milestone]]\nname = "v1"\nship = "2026-11-15"\nfreeze = "3d"\n'
                                 'features = ["alpha", "gamma"]\ncut = ["gamma"]\n[[milestone]]\nname = "later"\nship = ""\n',
    }

    def test_outside_freeze_anything(self):
        self.assertEqual(self.gate("feat(beta): b", "2026-11-01T12:00:00+00:00")[0], 0)

    def test_inside_freeze(self):
        self.assertEqual(self.gate("feat(alpha): a", "2026-11-13T12:00:00+00:00")[0], 0)
        rc, out = self.gate("feat(beta): b", "2026-11-13T12:00:00+00:00")
        self.assertEqual(rc, 1)
        self.assertIn("v1 freeze", out)

    def test_freeze_covers_the_whole_ship_day(self):
        self.assertEqual(self.gate("feat(beta): b", "2026-11-15T23:30:00+00:00")[0], 1)
        self.assertEqual(self.gate("feat(beta): b", "2026-11-12T23:30:00+00:00")[0], 0)

    def test_cut_list(self):
        rc, out = self.gate("fix(gamma): c", "2026-11-13T12:00:00+00:00")
        self.assertEqual(rc, 1)
        self.assertIn("cut list", out)

    def test_after_ship_no_freeze(self):
        self.assertEqual(self.gate("feat(beta): b", "2026-11-20T12:00:00+00:00")[0], 0)


class EmptyStart(Base):
    files = {".agents/config.toml": 'profile = "hackathon"\n',
             "specs/milestones.toml": 'start = ""\n[[milestone]]\nname = "end"\nship = "+0:00"\nfinal = true\n'}

    def test_empty_start_means_deadlines_off(self):
        rc, out = self.gate("fix: x", "2026-10-10T12:00:00+00:00")
        self.assertEqual(rc, 0, out)
        self.assertIn("no upcoming milestone", out)


class Missing(Base):
    files = {".agents/config.toml": 'profile = "hackathon"\n'}

    def test_no_milestones_file(self):
        self.assertEqual(self.gate("fix: x", "2026-10-10T12:00:00+00:00")[0], 0)


class Broken(Base):
    files = {".agents/config.toml": 'profile = "project"\n',
             "specs/milestones.toml": '[[milestone]]\nname = "v1"\nship = "next week"\n'}

    def test_bad_value_fails_loudly(self):
        rc, out = self.gate("fix: x", "2026-10-10T12:00:00+00:00")
        self.assertEqual(rc, 1)
        self.assertIn("milestones.toml", out)


if __name__ == "__main__":
    unittest.main()
