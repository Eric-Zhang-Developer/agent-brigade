import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from unittest import mock

import helpers
import sync_issues

URL, BRANCH = "https://github.com/o/r", "main"
MS = {"start": None, "milestones": [
    {"name": "v1", "ship": datetime(2026, 11, 16, tzinfo=timezone.utc), "features": ["tokenize", "rank"]},
    {"name": "v2", "ship": None, "features": ["export"]},
]}


def specs(*items):
    return {slug: {"name": name, "_path": f"specs/features/{slug}/spec.md", "depends_on": deps}
            for slug, name, deps in items}


def issue(n, slug, state="OPEN", milestone=None, title="anything"):
    return {"number": n, "title": title, "state": state, "body": f"Spec: ...\n\n<!-- spec: {slug} -->",
            "milestone": {"title": milestone} if milestone else None}


class Plan(unittest.TestCase):
    def test_creates_missing_in_its_milestone_and_skips_done_ones(self):
        acts = sync_issues.plan(specs(("tokenize", "Tokenize", []), ("rank", "Rank", ["tokenize"]),
                                      ("idea", "Someday", [])), {"tokenize"}, MS, [], URL, BRANCH)
        self.assertEqual([(a[0], a[1], a[2], a[4]) for a in acts],
                         [("create", "rank", "Rank", "v1"), ("create", "idea", "Someday", None)])
        body = acts[0][3]
        self.assertIn(f"{URL}/blob/main/specs/features/rank/spec.md", body)
        self.assertIn("Depends on: tokenize", body)
        self.assertIn("<!-- spec: rank -->", body)

    def test_closes_done_moves_milestone_and_ignores_titles(self):
        issues = [issue(3, "tokenize", milestone="v1", title="Renamed by a human"),
                  issue(4, "rank", milestone="v2"), issue(5, "export", milestone="v2")]
        acts = sync_issues.plan(specs(("tokenize", "Tokenize", []), ("rank", "Rank", []), ("export", "Export", [])),
                                {"tokenize"}, MS, issues, URL, BRANCH)
        self.assertEqual(acts, [("close", 3, "tokenize"), ("move", 4, "v1")])

    def test_backlog_issue_leaves_its_milestone(self):
        acts = sync_issues.plan(specs(("idea", "Someday", [])), set(), MS, [issue(6, "idea", milestone="v1")], URL, BRANCH)
        self.assertEqual(acts, [("move", 6, None)])

    def test_never_reopens_or_touches_closed(self):
        acts = sync_issues.plan(specs(("rank", "Rank", [])), set(), MS, [issue(7, "rank", state="CLOSED")], URL, BRANCH)
        self.assertEqual(acts, [])

    def test_milestones_created_and_due_dates_kept_in_step(self):
        have = [{"number": 1, "title": "v1", "due_on": "2026-11-10T07:00:00Z"}]
        self.assertEqual(sync_issues.milestone_plan(MS, have),
                         [("due", 1, "v1", "2026-11-15T23:59:59Z"), ("create", "v2", None)])
        have = [{"number": 1, "title": "v1", "due_on": "2026-11-15T08:00:00Z"}, {"number": 2, "title": "v2"}]
        self.assertEqual(sync_issues.milestone_plan(MS, have), [])   # same day: GitHub normalizes the time


class Main(helpers.RepoCase):
    files = {".agents/config.toml": 'profile = "project"\n',
             "specs/milestones.toml": '[[milestone]]\nname = "v1"\nship = "2026-11-15"\nfeatures = ["alpha"]\n',
             "specs/features/alpha/spec.md": helpers.spec(["a/"], name="Alpha")}

    def test_creates_milestone_issue_and_missing_labels(self):
        calls = []
        ok = mock.Mock(returncode=0, stdout="", stderr="")

        def fake_json(root, *args):
            if args[:2] == ("repo", "view"):
                return {"url": URL, "defaultBranchRef": {"name": "main"}}
            if args[:2] == ("label", "list"):
                return [{"name": n} for n in sync_issues.LABELS if n != "needs-human"]
            return []

        with mock.patch.object(sync_issues, "gh_json", side_effect=fake_json), \
             mock.patch.object(sync_issues, "gh", side_effect=lambda root, *a: calls.append(a) or ok), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(sync_issues.main(["--root", str(self.root)]), 0)
        self.assertEqual(calls[0][:3], ("label", "create", "needs-human"))
        self.assertEqual(calls[1], ("api", "-X", "POST", "repos/{owner}/{repo}/milestones", "-f", "title=v1",
                                    "-f", "due_on=2026-11-15T23:59:59Z"))
        self.assertEqual(calls[2][:4], ("issue", "create", "--title", "Alpha"))
        self.assertEqual(calls[2][-2:], ("--milestone", "v1"))

    def test_without_gh_says_so(self):
        out = io.StringIO()
        with mock.patch.object(sync_issues, "gh_json", return_value=None), redirect_stdout(out):
            self.assertEqual(sync_issues.main(["--root", str(self.root)]), 1)
        self.assertIn("nothing synced", out.getvalue())


if __name__ == "__main__":
    unittest.main()
