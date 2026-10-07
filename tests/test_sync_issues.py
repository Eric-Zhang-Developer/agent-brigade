import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import helpers
import sync_issues

URL, BRANCH = "https://github.com/o/r", "main"


def specs(*items):
    return {fid: {"name": name, "_path": f"specs/features/{fid}-x/spec.md", "depends_on": deps}
            for fid, name, deps in items}


class Plan(unittest.TestCase):
    def test_creates_missing_skips_done_ones_never_opened(self):
        acts = sync_issues.plan(specs(("F01", "Tokenize", []), ("F02", "Rank", ["F01"])), {"F01"}, [], URL, BRANCH)
        self.assertEqual([(a[0], a[1], a[2]) for a in acts], [("create", "F02", "[F02] Rank")])
        body = acts[0][3]
        self.assertIn(f"{URL}/blob/main/specs/features/F02-x/spec.md", body)
        self.assertIn("Depends on: F01", body)

    def test_closes_done_and_retitles_renamed(self):
        issues = [{"number": 3, "title": "[F01] Tokenize", "state": "OPEN"},
                  {"number": 4, "title": "[F02] Old name", "state": "OPEN"}]
        acts = sync_issues.plan(specs(("F01", "Tokenize", []), ("F02", "Rank", [])), {"F01"}, issues, URL, BRANCH)
        self.assertEqual(acts, [("close", 3, "F01"), ("retitle", 4, "[F02] Rank")])

    def test_never_reopens_and_matches_ids_exactly(self):
        issues = [{"number": 7, "title": "[F1] Cut by a human", "state": "CLOSED"},
                  {"number": 8, "title": "[F10] Ten", "state": "OPEN"}]
        acts = sync_issues.plan(specs(("F1", "Cut by a human", []), ("F10", "Ten", [])), set(), issues, URL, BRANCH)
        self.assertEqual(acts, [])


class Main(helpers.RepoCase):
    files = {".agents/config.toml": 'profile = "project"\n',
             "specs/features/F01-a/spec.md": helpers.spec("F01", ["a/"])}

    def test_creates_issue_and_missing_labels(self):
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
        self.assertEqual(calls[1][:4], ("issue", "create", "--title", "[F01] Feature F01"))

    def test_without_gh_says_so(self):
        out = io.StringIO()
        with mock.patch.object(sync_issues, "gh_json", return_value=None), redirect_stdout(out):
            self.assertEqual(sync_issues.main(["--root", str(self.root)]), 1)
        self.assertIn("nothing synced", out.getvalue())


if __name__ == "__main__":
    unittest.main()
