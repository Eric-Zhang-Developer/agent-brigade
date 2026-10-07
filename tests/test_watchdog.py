import io
import os
import time
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from unittest import mock

import helpers
import watchdog
from lib import heartbeat_dir, load_config


class Dog(helpers.RepoCase):
    files = {".agents/config.toml": 'profile = "project"\n[watchdog]\nrestart = "echo restart {worker} {worktree}"\n'
                         'min_free_disk_gb = 0\nmin_free_ram_gb = 0\n'}

    def dog(self, dry=True):
        return watchdog.Watchdog(self.root, load_config(self.root), dry)

    def heartbeat(self, name, minutes_ago, worktree="/tmp/wt"):
        hb = heartbeat_dir(self.root) / name
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text(worktree + "\n")
        t = time.time() - minutes_ago * 60
        os.utime(hb, (t, t))

    def test_dead_session_restarted_live_one_not(self):
        self.heartbeat("claude-1", 30)
        self.heartbeat("codex-1", 5)
        out = io.StringIO()
        with redirect_stdout(out):
            self.dog().check_sessions(time.time())
        self.assertIn("would run: echo restart claude-1 /tmp/wt", out.getvalue())
        self.assertNotIn("codex-1", out.getvalue())

    def test_dead_session_without_restart_alerts_once(self):
        helpers.write(self.root, {".agents/config.toml": 'profile = "project"\n'})
        self.heartbeat("a", 30)
        d, out = self.dog(), io.StringIO()
        with redirect_stdout(out):
            d.check_sessions(time.time())
            d.check_sessions(time.time())
        self.assertEqual(out.getvalue().count("ALERT"), 1)

    def test_stop_ends_loop(self):
        (self.root / "STOP").write_text("")
        with redirect_stdout(io.StringIO()):
            self.assertFalse(self.dog().tick())

    def test_claims(self):
        now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
        prs = [{"number": 1, "title": "feat(a): a", "updatedAt": "2026-10-10T10:30:00Z"},
               {"number": 2, "title": "feat(b): b", "updatedAt": "2026-10-10T11:10:00Z"},
               {"number": 3, "title": "feat(c): c", "updatedAt": "2026-10-10T11:50:00Z"}]
        d, out = self.dog(), io.StringIO()
        with mock.patch.object(watchdog, "gh_json", return_value=prs), redirect_stdout(out):
            d.check_claims(now)
        self.assertIn("closing #1", out.getvalue())
        self.assertIn("commenting on #2", out.getvalue())
        self.assertNotIn("#3", out.getvalue())
        self.assertEqual(d.state["commented"], [2])

    def test_main_red_past_limit(self):
        now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
        runs = [{"status": "in_progress", "conclusion": None, "createdAt": "2026-10-10T11:59:00Z"},
                {"status": "completed", "conclusion": "failure", "createdAt": "2026-10-10T11:50:00Z"},
                {"status": "completed", "conclusion": "failure", "createdAt": "2026-10-10T11:30:00Z"},
                {"status": "completed", "conclusion": "success", "createdAt": "2026-10-10T11:00:00Z"}]
        d, out = self.dog(), io.StringIO()
        with mock.patch.object(watchdog, "gh_json", side_effect=[runs, []]), redirect_stdout(out):
            d.check_main(now)
        self.assertIn("main has been red for 30 min", out.getvalue())
        self.assertIn("opening a main-red issue", out.getvalue())

    def test_main_green_clears(self):
        d = self.dog()
        d.state["alerted"] = ["main-red"]
        runs = [{"status": "completed", "conclusion": "success", "createdAt": "2026-10-10T11:00:00Z"}]
        out = io.StringIO()
        with mock.patch.object(watchdog, "gh_json", side_effect=[runs, [{"number": 5}]]), redirect_stdout(out):
            d.check_main(datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(d.state["alerted"], [])
        self.assertIn("main is green, closing #5", out.getvalue())

    def test_low_disk_alert(self):
        helpers.write(self.root, {".agents/config.toml": 'profile = "project"\n[watchdog]\nmin_free_disk_gb = 1000000\nmin_free_ram_gb = 0\n'})
        out = io.StringIO()
        with redirect_stdout(out):
            self.dog().check_resources()
        self.assertIn("low disk", out.getvalue())

    def test_free_ram_is_number_or_none(self):
        ram = watchdog.free_ram_gb()
        self.assertTrue(ram is None or ram >= 0)


if __name__ == "__main__":
    unittest.main()
