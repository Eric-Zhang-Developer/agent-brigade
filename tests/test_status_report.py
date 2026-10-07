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
        ".agents/config.toml": 'profile = "hackathon"\n[agents]\nmax_parallel = 2\n',
        "specs/gates.toml": 'run_start = "2026-10-10T09:00:00-04:00"\n[[gate]]\nat = "30:00"\nfreeze = true\n',
        "specs/features/F01-a/spec.md": helpers.spec("F01", ["a/"]),
        "specs/features/F02-b/spec.md": helpers.spec("F02", ["b/"], ["F01"]),
        "specs/features/F03-c/spec.md": helpers.spec("F03", ["c/"], ["F02"]),
        "specs/features/F04-d/spec.md": helpers.spec("F04", ["d/"]),
        "changes/F01.md": "# F01\nShipped the a thing.\n",
    }

    def build(self, offline=True, prs=None, asks=None, runs=None):
        cfg = load_config(self.root)
        with mock.patch.object(status_report, "gh_json", side_effect=[prs, asks, runs]):
            return status_report.build(self.root, cfg, NOW, offline)

    def test_offline_sections(self):
        text = self.build()
        self.assertIn("next: freeze at 30:00 (in 27:00)", text)
        self.assertIn("- F01 Feature F01: Shipped the a thing.", text)
        self.assertIn("## Ready next\n- F02 Feature F02\n- F04 Feature F04", text)
        self.assertIn("- F03: waiting on ['F02']", text)
        self.assertIn("## Needs human\n- unknown (offline or gh unavailable)", text)
        self.assertIn("PR state unknown", text)
        self.assertIn("## main CI\n- unknown", text)
        self.assertIn("STOP: not present", text)

    def test_online_claims_and_stale(self):
        prs = [{"number": 7, "title": "[F02] b", "isDraft": True, "updatedAt": "2026-10-10T14:50:00Z", "url": "u7"},
               {"number": 8, "title": "[F04] d", "isDraft": True, "updatedAt": "2026-10-10T15:59:00Z", "url": "u8"}]
        runs = [{"status": "completed", "conclusion": "success", "createdAt": "2026-10-10T15:30:00Z", "url": "r"}]
        asks = [{"number": 9, "title": "Which ID format?", "url": "u9",
                 "labels": [{"name": "needs-human"}, {"name": "one-way-door"}]}]
        text = self.build(offline=False, prs=prs, asks=asks, runs=runs)
        self.assertIn("- [#9](u9) Which ID format? **one-way door**", text)
        self.assertIn("[#7](u7) [F02] b · draft · updated 70 min ago **STALE: close**", text)
        self.assertIn("[#8](u8) [F04] d · draft · updated 1 min ago\n", text)
        self.assertIn("## Ready next\n- none", text)
        self.assertIn("**Backlog low**", text)
        self.assertIn("- success · 30 min ago · r", text)

    def test_main_writes_file(self):
        out = self.root / "status.md"
        with redirect_stdout(io.StringIO()):
            rc = status_report.main(["--root", str(self.root), "--offline", "--out", str(out), "--now", NOW.isoformat()])
        self.assertEqual(rc, 0)
        self.assertTrue(out.read_text().startswith("# Status"))

    def test_issue_mode_edits_existing_status_issue(self):
        calls = []
        ok = mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.object(status_report, "gh_json", return_value=[{"number": 4}]), \
             mock.patch.object(status_report, "gh", side_effect=lambda root, *a: calls.append(a) or ok), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(status_report.update_issue(self.root, "# Status\n"), 0)
        self.assertEqual(calls, [("issue", "edit", "4", "--body", "# Status\n")])

    def test_issue_mode_creates_and_pins_the_first_time(self):
        calls = []
        made = mock.Mock(returncode=0, stdout="https://github.com/o/r/issues/12\n", stderr="")
        with mock.patch.object(status_report, "gh_json", return_value=[]), \
             mock.patch.object(status_report, "gh", side_effect=lambda root, *a: calls.append(a) or made), \
             redirect_stdout(io.StringIO()):
            status_report.update_issue(self.root, "body")
        self.assertEqual(calls[0][:2], ("issue", "create"))
        self.assertEqual(calls[1], ("issue", "pin", "12"))

    def test_needs_out_or_issue(self):
        with self.assertRaises(SystemExit), mock.patch("sys.stderr", io.StringIO()):
            status_report.main(["--root", str(self.root), "--offline"])


if __name__ == "__main__":
    unittest.main()
