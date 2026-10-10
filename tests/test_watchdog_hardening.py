import io
import json
import os
import subprocess
import sys
import time
import unittest
from contextlib import redirect_stdout
from unittest import mock

import helpers
import watchdog
from lib import heartbeat_dir, load_config

CONFIG = ('profile = "project"\n[watchdog]\nrestart = "true {worker} {worktree}"\n'
          'min_free_disk_gb = 0\nmin_free_ram_gb = 0\n')


class Base(helpers.RepoCase):
    files = {".agents/config.toml": CONFIG}

    def dog(self, dry=True):
        return watchdog.Watchdog(self.root, load_config(self.root), dry)

    def heartbeat(self, name, at, worktree=None):
        hb = heartbeat_dir(self.root) / name
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text(f"{worktree or self.root}\n")
        os.utime(hb, (at, at))

    def sessions(self, d, now) -> str:
        out = io.StringIO()
        with redirect_stdout(out):
            d.check_sessions(now)
        return out.getvalue()


class Stuck(Base):
    def test_fresh_heartbeat_no_commit_alerts_once_never_restarts(self):
        now = time.time() + 2 * 3600  # the repo's only commit and files are two hours old
        self.heartbeat("w", now - 60)
        d = self.dog()
        out = self.sessions(d, now) + self.sessions(d, now + 60)
        self.assertEqual(out.count("ALERT: w is alive but hasn't committed in 120 min"), 1)
        self.assertNotIn("would run", out)

    def test_recent_uncommitted_change_is_progress(self):
        now = time.time() + 2 * 3600
        self.heartbeat("w", now - 60)
        f = self.root / "work.txt"
        f.write_text("draft")
        os.utime(f, (now - 300, now - 300))
        self.assertNotIn("ALERT", self.sessions(self.dog(), now))

    def test_progress_ends_the_episode(self):
        now = time.time() + 2 * 3600
        self.heartbeat("w", now - 60)
        d = self.dog()
        self.assertIn("ALERT", self.sessions(d, now))
        f = self.root / "work.txt"
        f.write_text("draft")
        os.utime(f, (now, now))
        self.heartbeat("w", now)
        self.assertNotIn("ALERT", self.sessions(d, now + 60))
        self.heartbeat("w", now + 2 * 3600)
        self.assertIn("ALERT: w is alive", self.sessions(d, now + 2 * 3600 + 60))

    def test_missing_worktree_is_skipped(self):
        now = time.time() + 2 * 3600
        self.heartbeat("w", now - 60, worktree=str(self.root / "gone"))
        self.assertEqual(self.sessions(self.dog(), now), "")


class RestartCap(Base):
    def test_cap_per_rolling_hour(self):
        now = time.time()
        self.heartbeat("w", now - 3600)
        d = self.dog()  # dry: the heartbeat is not touched, so every pass finds it dead
        out = "".join(self.sessions(d, now + i) for i in range(4))
        self.assertEqual(out.count("would run: true w"), 2)
        self.assertEqual(out.count("ALERT: restart cap hit for w; not restarting"), 1)
        self.assertIn("would run: true w", self.sessions(d, now + 3601))

    def test_restarts_survive_a_watchdog_restart(self):
        now = time.time()
        self.heartbeat("w", now - 3600)
        d = self.dog(dry=False)
        self.sessions(d, now)
        d.save()
        self.assertEqual(len(self.dog().state["restarts"]["w"]), 1)


class State(Base):
    def test_old_state_file_loads(self):
        self.dog().state_path.write_text(json.dumps({"commented": [], "alerted": ["disk"]}))
        self.assertEqual(self.dog().state["restarts"], {})

    def test_failed_write_keeps_the_old_file(self):
        d = self.dog(dry=False)
        d.save()
        before = d.state_path.read_text()
        d.state["alerted"].append("x")
        with mock.patch.object(watchdog.os, "replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                d.save()
        self.assertEqual(d.state_path.read_text(), before)


@unittest.skipIf(os.name == "nt", "pid liveness is not checked on Windows")
class SingleInstance(Base):
    def run_main(self, *args) -> tuple[int, str]:
        out = io.StringIO()
        with mock.patch.object(watchdog, "gh_json", return_value=None), redirect_stdout(out):
            code = watchdog.main(["--root", str(self.root), *args])
        return code, out.getvalue()

    def lock(self):
        return self.dog().state_path.with_name("watchdog.pid")

    def test_live_holder_blocks(self):
        self.lock().write_text(f"{os.getppid()}\n")
        code, out = self.run_main("--once")
        self.assertEqual(code, 1)
        self.assertEqual(out.count("\n"), 1)
        self.assertIn(f"another watchdog is running (pid {os.getppid()}", out)
        self.assertTrue(self.lock().exists())

    def test_stale_lock_taken_over_and_released(self):
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        self.lock().write_text(f"{dead.pid}\n")
        self.assertIsNone(watchdog.acquire_lock(self.lock()))
        self.assertEqual(self.lock().read_text().strip(), str(os.getpid()))
        self.lock().unlink()
        self.lock().write_text(f"{dead.pid}\n")
        self.assertEqual(self.run_main("--once")[0], 0)
        self.assertFalse(self.lock().exists())

    def test_released_on_ctrl_c(self):
        with mock.patch.object(watchdog.Watchdog, "tick", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_main()
        self.assertFalse(self.lock().exists())

    def test_stop_exits_0_and_says_why_every_time(self):
        (self.root / "STOP").write_text("")
        for _ in range(2):  # the second run has already alerted, but still says why it exits
            code, out = self.run_main()
            self.assertEqual(code, 0)
            self.assertIn("is present (delete it to run again)", out)

    def test_stop_alert_rearms_after_stop_is_removed(self):
        d = self.dog()
        (self.root / "STOP").write_text("")
        with redirect_stdout(io.StringIO()):
            d.check_stop()
            (self.root / "STOP").unlink()
            d.check_stop()
        self.assertNotIn("stop", d.state["alerted"])


class Gh(Base):
    def test_claim_actions_go_through_lib_gh(self):
        now = watchdog.datetime(2026, 10, 10, 12, 0, tzinfo=watchdog.timezone.utc)
        prs = [{"number": 1, "title": "feat(a): a", "updatedAt": "2026-10-10T10:30:00Z"},
               {"number": 2, "title": "feat(b): b", "updatedAt": "2026-10-10T11:10:00Z"}]
        with mock.patch.object(watchdog, "gh_json", return_value=prs), mock.patch.object(watchdog, "gh") as gh, \
                redirect_stdout(io.StringIO()):
            self.dog(dry=False).check_claims(now)
        self.assertEqual([c.args[1:3] for c in gh.call_args_list], [("pr", "close"), ("pr", "comment")])


if __name__ == "__main__":
    unittest.main()
