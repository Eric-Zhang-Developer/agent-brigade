import io
import unittest
from contextlib import redirect_stdout

import helpers
from check_ownership import lint_specs, main
from kitlib import load_config, load_specs

KIT = 'profile = "hackathon"\n[ownership]\nfrozen = ["core/", "kit.toml"]\nopen = ["NOW.md"]\n'


class Lint(helpers.RepoCase):
    files = {
        "kit.toml": KIT,
        "specs/features/F00-boot/spec.md": helpers.spec("F00", [], extra="bootstrap: true\n"),
        "specs/features/F01-a/spec.md": helpers.spec("F01", ["src/a/"], ["F00"]),
        "specs/features/F02-b/spec.md": helpers.spec("F02", ["src/a/x"], ["F09"]),
        "specs/features/F03-c/spec.md": helpers.spec("F03", ["core/thing"]),
    }

    def test_overlaps_missing_deps_and_frozen(self):
        cfg = load_config(self.root)
        errs = "\n".join(lint_specs(cfg, load_specs(self.root, cfg)))
        self.assertIn("F01 owns 'src/a/', which overlaps F02's 'src/a/x'", errs)
        self.assertIn("F02: depends_on F09 does not exist", errs)
        self.assertIn("F03 owns 'core/thing', which overlaps frozen path 'core/'", errs)


class Titles(helpers.RepoCase):
    files = {
        "kit.toml": KIT,
        "specs/features/F00-boot/spec.md": helpers.spec("F00", [], extra="bootstrap: true\n"),
        "specs/features/F01-a/spec.md": helpers.spec("F01", ["src/a/"]),
    }

    def check(self, title, files):
        self.branch("work")
        self.commit("work", files)
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.root), "--title", title, "--base", "main"])
        return rc, out.getvalue()

    def test_feature_in_owns_plus_extras_and_open(self):
        rc, out = self.check("[F01] a", {"src/a/x.py": "x", "changes/F01.md": "done", "NOW.md": "now",
                                         "specs/decisions/F01-why.md": "d", "specs/inbox/F01-q.md": "q"})
        self.assertEqual(rc, 0, out)

    def test_feature_outside_owns_fails(self):
        rc, out = self.check("[F01] a", {"src/b/x.py": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("src/b/x.py is outside", out)

    def test_fix_same_as_feature(self):
        self.assertEqual(self.check("[FIX-F01] a", {"src/a/y.py": "y"})[0], 0)

    def test_contract_may_touch_frozen_and_specs_only(self):
        self.assertEqual(self.check("[C1] add", {"core/x.py": "x", "specs/mission.md": "m"})[0], 0)

    def test_contract_outside_fails(self):
        self.assertEqual(self.check("[C1] add", {"src/a/x.py": "x"})[0], 1)

    def test_plan_may_add_specs(self):
        self.assertEqual(self.check("[PLAN] batch", {"specs/features/F02-new/spec.md": "s", "specs/roadmap.md": "r"})[0], 0)

    def test_plan_may_not_touch_code(self):
        self.assertEqual(self.check("[PLAN] batch", {"src/a/x.py": "x"})[0], 1)

    def test_bootstrap_anything(self):
        self.assertEqual(self.check("[F00] boot", {"anything/at/all": "x"})[0], 0)

    def test_unknown_prefix(self):
        self.assertEqual(self.check("Add stuff", {"x": "x"})[0], 1)

    def test_unknown_feature(self):
        rc, out = self.check("[F42] ghost", {"x": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("unknown feature F42", out)

    def test_revert_exact_files(self):
        self.branch("work")
        self.commit("bad", {"src/a/x.py": "bad"})
        sha = helpers.sh(self.root, "git", "rev-parse", "HEAD").strip()
        helpers.sh(self.root, "git", "revert", "--no-edit", sha)
        with redirect_stdout(io.StringIO()):
            rc = main(["--root", str(self.root), "--title", f"[REVERT-{sha[:7]}] undo", "--base", "main"])
        self.assertEqual(rc, 0)

    def test_no_args_is_usage_error(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root)]), 2)


if __name__ == "__main__":
    unittest.main()
