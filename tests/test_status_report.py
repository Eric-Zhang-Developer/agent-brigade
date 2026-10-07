import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from unittest import mock

import helpers
import status as status_report
from lib import load_config

NOW = datetime.fromisoformat("2026-10-10T12:00:00-04:00")


class Status(helpers.RepoCase):
    files = {
        ".agents/config.toml": 'profile = "hackathon"\nsize = "full"\n[agents]\nmax_parallel = 2\n',
        "specs/milestones.toml": ('start = "2026-10-10T09:00:00-04:00"\n'
                                  '[[milestone]]\nname = "demo"\nship = "+2:00"\nfeatures = ["early"]\n'
                                  '[[milestone]]\nname = "core"\nship = "+30:00"\nfreeze = "6:00"\n'
                                  'features = ["alpha", "beta", "gamma", "delta"]\n'),
        "specs/features/early/spec.md": helpers.spec(["e/"], name="Early"),
        "specs/features/alpha/spec.md": helpers.spec(["a/"], name="Alpha"),
        "specs/features/beta/spec.md": helpers.spec(["b/"], ["alpha"], name="Beta"),
        "specs/features/gamma/spec.md": helpers.spec(["c/"], ["beta"], name="Gamma"),
        "specs/features/delta/spec.md": helpers.spec(["d/"], name="Delta"),
        "specs/features/idea/spec.md": helpers.spec(["i/"], name="Someday"),
        "specs/shipped/v0/old/spec.md": helpers.spec(["o/"]),
        "changes/alpha.md": "## What shipped\nThe a thing.\n",
    }

    def build(self, offline=True, *responses):
        cfg = load_config(self.root)
        with mock.patch.object(status_report, "gh_json", side_effect=list(responses) or None):
            return status_report.build(self.root, cfg, NOW, offline)

    def test_offline_sections(self):
        self.commit("feat(alpha): the a thing (#1)")
        self.commit("fix(alpha): oops (#2)")
        self.commit("contract: add a field (#3)")
        text = self.build()
        self.assertIn("elapsed 3:00, next milestone core ships in 27:00, freeze in 21:00", text)
        self.assertIn("- alpha Alpha: The a thing.", text)
        self.assertIn("## Ready next (pick order)\n- beta Beta\n- delta Delta\n", text)
        self.assertIn("- gamma: waiting on ['beta']", text)
        self.assertIn("## Missed (milestone passed, not done)\n- demo: early Early", text)
        self.assertIn("## Backlog (in no milestone)\n- idea Someday", text)
        self.assertIn("- shipped: v0 (1)", text)
        self.assertIn("## Needs human\n- unknown (offline or gh unavailable)", text)
        self.assertIn("PR state unknown", text)
        self.assertIn("## main CI\n- unknown", text)
        self.assertIn("STOP: not present", text)
        self.assertIn("_Offline: counted from the last 200 commit subjects", text)
        self.assertIn("- process overhead (contract + plan + docs): 1 of 3 (33%)", text)
        self.assertIn("- most fixed: alpha 1", text)

    def test_online_claims_stale_ci_and_loop(self):
        prs = [{"number": 7, "title": "feat(beta): b", "isDraft": True, "updatedAt": "2026-10-10T14:50:00Z", "url": "u7"},
               {"number": 8, "title": "feat(delta): d", "isDraft": True, "updatedAt": "2026-10-10T15:59:00Z", "url": "u8"}]
        asks = [{"number": 9, "title": "Which format?", "url": "u9",
                 "labels": [{"name": "needs-human"}, {"name": "one-way-door"}]}]
        runs = [{"databaseId": 555, "conclusion": "success", "updatedAt": "2026-10-10T15:59:00Z", "url": "this"},
                {"databaseId": 554, "conclusion": "failure", "updatedAt": "2026-10-10T15:30:00Z", "url": "r"}]
        merged = [{"title": "feat(alpha): a", "createdAt": "2026-10-10T13:00:00Z", "mergedAt": "2026-10-10T13:10:00Z"},
                  {"title": "plan: batch", "createdAt": "2026-10-10T13:00:00Z", "mergedAt": "2026-10-10T13:30:00Z"},
                  {"title": "revert: oops", "createdAt": "2026-10-10T14:00:00Z", "mergedAt": "2026-10-10T14:02:00Z"}]
        loop_runs = [{"conclusion": "failure", "updatedAt": "2026-10-10T14:00:00Z"},
                     {"conclusion": "success", "updatedAt": "2026-10-10T14:25:00Z"},
                     {"conclusion": "failure", "updatedAt": "2026-10-10T15:50:00Z"}]
        with mock.patch.dict("os.environ", {"GITHUB_RUN_ID": "555"}):
            text = self.build(False, prs, asks, runs, merged, loop_runs)
        self.assertIn("- [#9](u9) Which format? **one-way door**", text)
        self.assertIn("[#7](u7) feat(beta): b · draft · updated 70 min ago **STALE: close**", text)
        self.assertIn("[#8](u8) feat(delta): d · draft · updated 1 min ago\n", text)
        self.assertIn("## Ready next (pick order)\n- none", text)
        self.assertIn("**Backlog low**", text)
        self.assertIn("- failure · finished 30 min ago · r", text)          # not this run (555)
        self.assertIn("- by type: feature 1, plan 1, revert 1", text)
        self.assertIn("- median time open: 10 min", text)
        self.assertIn("- reverts: 1", text)
        self.assertIn("- main red: 35 min over the last 3 runs (red now)", text)

    def test_lite_has_no_stale_claims(self):
        helpers.write(self.root, {".agents/config.toml": 'profile = "project"\nsize = "lite"\n'})
        prs = [{"number": 7, "title": "feat(beta): b", "isDraft": True, "updatedAt": "2026-10-10T14:50:00Z", "url": "u7"}]
        text = self.build(False, prs, [], [], [], [])
        self.assertNotIn("STALE", text)

    def test_main_writes_file(self):
        out = self.root / "status.md"
        with redirect_stdout(io.StringIO()):
            rc = status_report.main(["--root", str(self.root), "--offline", "--out", str(out), "--now", NOW.isoformat()])
        self.assertEqual(rc, 0)
        self.assertTrue(out.read_text().startswith("# Status"))

    def test_issue_mode_edits_existing_status_issue(self):
        calls = []
        ok = mock.Mock(returncode=0, stdout="", stderr="")
        out = io.StringIO()
        with mock.patch.object(status_report, "gh_json", return_value=[{"number": 4}]), \
             mock.patch.object(status_report, "gh", side_effect=lambda root, *a: calls.append(a) or ok), \
             redirect_stdout(out):
            self.assertEqual(status_report.update_issue(self.root, "# Status\n"), 0)
        self.assertEqual(calls, [("issue", "edit", "4", "--body", "# Status\n")])
        self.assertIn("updated the Status issue", out.getvalue())

    def test_issue_mode_creates_and_pins_the_first_time(self):
        calls = []
        made = mock.Mock(returncode=0, stdout="https://github.com/o/r/issues/12\n", stderr="")
        out = io.StringIO()
        with mock.patch.object(status_report, "gh_json", return_value=[]), \
             mock.patch.object(status_report, "gh", side_effect=lambda root, *a: calls.append(a) or made), \
             redirect_stdout(out):
            status_report.update_issue(self.root, "body")
        self.assertEqual(calls[0][:2], ("issue", "create"))
        self.assertEqual(calls[1], ("issue", "pin", "12"))
        self.assertIn("created and pinned the Status issue", out.getvalue())

    def test_needs_out_or_issue(self):
        with self.assertRaises(SystemExit), mock.patch("sys.stderr", io.StringIO()):
            status_report.main(["--root", str(self.root), "--offline"])


if __name__ == "__main__":
    unittest.main()
