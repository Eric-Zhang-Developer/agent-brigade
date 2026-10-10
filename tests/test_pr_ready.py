import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import helpers

SCRIPT = helpers.SCRIPTS / "pr_ready.py"
# A fake `gh`: prints $FAKE_PR for `gh pr view`, $FAKE_THREADS for `gh api graphql`; exits 1 when it has nothing.
STUB = f"""#!{sys.executable}
import os, sys
out = os.environ.get("FAKE_PR" if sys.argv[1:3] == ["pr", "view"] else "FAKE_THREADS" if sys.argv[1:3] == ["api", "graphql"] else "")
if not out:
    sys.exit("gh: no fake for " + " ".join(sys.argv[1:]))
print(out)
"""
# Windows runs gh.exe, not a shebang script, so the stub can't answer there; the gh-missing test still runs.
NO_STUB = unittest.skipIf(os.name == "nt", "the fake gh is a shebang script, which Windows can't run as `gh`")
READY = {"number": 7, "url": "https://github.com/o/r/pull/7", "state": "OPEN", "isDraft": False,
         "mergeable": "MERGEABLE", "reviewDecision": "", "statusCheckRollup": [
             {"__typename": "CheckRun", "name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"},
             {"__typename": "StatusContext", "context": "deploy", "state": "SUCCESS"}]}


def threads(*resolved: bool) -> dict:
    nodes = [{"isResolved": r} for r in resolved]
    return {"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": nodes}}}}}


class PrReady(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.bin = Path(self._tmp.name)
        gh = self.bin / "gh"
        gh.write_text(STUB)
        gh.chmod(0o755)

    def tearDown(self):
        self._tmp.cleanup()

    def run_it(self, pr=None, thread_data=None, path=None, *args):
        env = {**os.environ, "PATH": path if path is not None else f"{self.bin}{os.pathsep}{os.environ['PATH']}",
               "FAKE_PR": json.dumps(pr) if pr is not None else "",
               "FAKE_THREADS": json.dumps(thread_data or threads())}
        r = subprocess.run([sys.executable, str(SCRIPT), "--root", self._tmp.name, *args],
                           capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr

    def assertVerdict(self, change, code, text, thread_data=None):
        rc, out = self.run_it({**READY, **change}, thread_data)
        self.assertEqual(rc, code, out)
        self.assertIn(text, out)

    @NO_STUB
    def test_ready(self):
        self.assertVerdict({}, 0, "ready to merge")

    @NO_STUB
    def test_each_blocker_has_its_own_exit_code(self):
        self.assertVerdict({"state": "MERGED"}, 3, "merged")
        self.assertVerdict({"state": "CLOSED"}, 3, "closed")
        self.assertVerdict({"isDraft": True}, 3, "expected while the work is in progress")
        self.assertVerdict({"mergeable": "CONFLICTING"}, 4, "rebase on origin/main")
        self.assertVerdict({"reviewDecision": "CHANGES_REQUESTED"}, 5, "changes requested")
        self.assertVerdict({}, 6, "2 unresolved review thread", threads(True, False, False))
        failing = [{"name": "lint", "status": "COMPLETED", "conclusion": "FAILURE"},
                   {"context": "ci/legacy", "state": "ERROR"}, READY["statusCheckRollup"][0]]
        self.assertVerdict({"statusCheckRollup": failing}, 7, "failing checks: lint, ci/legacy")
        self.assertVerdict({"statusCheckRollup": [{"name": "e2e", "status": "IN_PROGRESS", "conclusion": ""}]},
                           8, "pending checks: e2e")
        self.assertVerdict({"statusCheckRollup": [{"context": "deploy", "state": "EXPECTED"}]}, 8, "pending")
        self.assertVerdict({"mergeable": "UNKNOWN"}, 8, "still checking for conflicts")   # not "ready" after main moved

    @NO_STUB
    def test_skipped_and_neutral_checks_pass(self):
        rollup = [{"name": n, "status": "COMPLETED", "conclusion": c} for n, c in (("a", "SKIPPED"), ("b", "NEUTRAL"))]
        self.assertVerdict({"statusCheckRollup": rollup}, 0, "ready")

    @NO_STUB
    def test_first_blocker_wins(self):
        everything = {"isDraft": True, "mergeable": "CONFLICTING", "reviewDecision": "CHANGES_REQUESTED",
                      "statusCheckRollup": [{"name": "x", "status": "COMPLETED", "conclusion": "FAILURE"}]}
        self.assertVerdict(everything, 3, "draft", threads(False))
        self.assertVerdict({**everything, "isDraft": False}, 4, "conflicts", threads(False))
        self.assertVerdict({**everything, "isDraft": False, "mergeable": "MERGEABLE"}, 5, "changes", threads(False))
        self.assertVerdict({"statusCheckRollup": everything["statusCheckRollup"]}, 6, "unresolved", threads(False))
        pending_and_failing = [{"name": "a", "status": "QUEUED"}, *everything["statusCheckRollup"]]
        self.assertVerdict({"statusCheckRollup": pending_and_failing}, 7, "failing checks: x")

    def test_gh_missing_or_failing_is_one_line_exit_1(self):
        rc, out = self.run_it(READY, path=self._tmp.name + "/empty")
        self.assertEqual((rc, out.strip()), (1, "pr_ready: gh is not installed (https://cli.github.com)"))
        rc, out = self.run_it(None)  # gh pr view fails: not logged in, or no PR for this branch
        self.assertEqual(rc, 1, out)
        self.assertEqual(len(out.strip().splitlines()), 1, out)
        rc, out = self.run_it(READY, {"errors": ["bad credentials"]})
        self.assertEqual(rc, 1, out)

    def test_usage_error_is_exit_2(self):
        rc, _ = self.run_it(READY, None, None, "7", "8")
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
