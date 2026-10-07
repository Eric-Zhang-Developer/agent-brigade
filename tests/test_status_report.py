import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from unittest import mock

import helpers
import status_report
from kitlib import load_config

NOW = datetime.fromisoformat("2026-10-10T12:00:00-04:00")


class Status(helpers.RepoCase):
    files = {
        "kit.toml": 'profile = "hackathon"\n[agents]\nmax_parallel = 2\n',
        "specs/gates.toml": 'run_start = "2026-10-10T09:00:00-04:00"\n[[gate]]\nat = "30:00"\nfreeze = true\n',
        "specs/features/F01-a/spec.md": helpers.spec("F01", ["a/"]),
        "specs/features/F02-b/spec.md": helpers.spec("F02", ["b/"], ["F01"]),
        "specs/features/F03-c/spec.md": helpers.spec("F03", ["c/"], ["F02"]),
        "specs/features/F04-d/spec.md": helpers.spec("F04", ["d/"]),
        "changes/F01.md": "# F01\nShipped the a thing.\n",
        "specs/inbox/needs-human.md": "# instructions\n",
        "specs/inbox/F02-schema.md": "# Which ID format?\n- One-way door: yes\n",
    }

    def build(self, offline=True, prs=None, runs=None):
        cfg = load_config(self.root)
        with mock.patch.object(status_report, "gh_json", side_effect=[prs, runs]):
            return status_report.build(self.root, cfg, NOW, offline)

    def test_offline_sections(self):
        text = self.build()
        self.assertIn("next: freeze at 30:00 (in 27:00)", text)
        self.assertIn("- F01 Feature F01: Shipped the a thing.", text)
        self.assertIn("## Ready next\n- F02 Feature F02\n- F04 Feature F04", text)
        self.assertIn("- F03: waiting on ['F02']", text)
        self.assertIn("`F02-schema.md`: Which ID format? **one-way door**", text)
        self.assertNotIn("needs-human.md", text)
        self.assertIn("PR state unknown", text)
        self.assertIn("## main CI\n- unknown", text)
        self.assertIn("STOP: not present", text)

    def test_online_claims_and_stale(self):
        prs = [{"number": 7, "title": "[F02] b", "isDraft": True, "updatedAt": "2026-10-10T14:50:00Z", "url": "u7"},
               {"number": 8, "title": "[F04] d", "isDraft": True, "updatedAt": "2026-10-10T15:59:00Z", "url": "u8"}]
        runs = [{"status": "completed", "conclusion": "success", "createdAt": "2026-10-10T15:30:00Z", "url": "r"}]
        text = self.build(offline=False, prs=prs, runs=runs)
        self.assertIn("[#7](u7) [F02] b · draft · updated 70 min ago **STALE: close**", text)
        self.assertIn("[#8](u8) [F04] d · draft · updated 1 min ago\n", text)
        self.assertIn("## Ready next\n- none", text)
        self.assertIn("**Backlog low**", text)
        self.assertIn("- success · 30 min ago · r", text)

    def test_main_writes_file(self):
        with redirect_stdout(io.StringIO()):
            rc = status_report.main(["--root", str(self.root), "--offline", "--now", NOW.isoformat()])
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / "reports/status.md").read_text().startswith("# Status"))


if __name__ == "__main__":
    unittest.main()
