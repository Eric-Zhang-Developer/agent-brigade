import io
import unittest
from contextlib import redirect_stdout

import helpers
from check_ownership import lint_specs, main
from lib import load_config, load_milestones, load_shipped, load_specs

CONFIG = 'profile = "hackathon"\n[ownership]\nfrozen = ["core/", "AGENTS.md"]\nopen = ["NOW.md"]\n'


def run(root, *args) -> tuple[int, str]:
    out = io.StringIO()
    with redirect_stdout(out):
        rc = main(["--root", str(root), *args])
    return rc, out.getvalue()


class Lint(helpers.RepoCase):
    files = {
        ".agents/config.toml": CONFIG,
        "specs/features/boot/spec.md": helpers.spec([], extra="bootstrap: true\n"),
        "specs/features/alpha/spec.md": helpers.spec(["src/a/"], ["boot"]),
        "specs/features/beta/spec.md": helpers.spec(["src/a/x"], ["ghost"]),
        "specs/features/gamma/spec.md": helpers.spec(["core/thing"]),
        "specs/features/Bad_Name/spec.md": helpers.spec([]),
        "specs/shipped/v0.1/old/spec.md": helpers.spec(["src/old/"]),
        "specs/milestones.toml": ('[[milestone]]\nname = "m1"\nfeatures = ["alpha", "nope"]\ncut = ["beta"]\n'
                                  '[[milestone]]\nname = "m2"\nfeatures = ["alpha", "old"]\n'),
    }

    def lint(self):
        cfg = load_config(self.root)
        return "\n".join(lint_specs(cfg, load_specs(self.root, cfg), load_shipped(self.root, cfg), set(),
                                    load_milestones(self.root, cfg)))

    def test_overlaps_missing_deps_frozen_and_slugs(self):
        errs = self.lint()
        self.assertIn("alpha owns 'src/a/', which overlaps beta's 'src/a/x'", errs)
        self.assertIn("beta: depends_on ghost does not exist", errs)
        self.assertIn("gamma owns 'core/thing', which overlaps frozen path 'core/'", errs)
        self.assertIn("specs/features/Bad_Name: 'Bad_Name' is not a slug", errs)

    def test_milestones(self):
        errs = self.lint()
        self.assertIn("milestone m1: feature nope does not exist", errs)
        self.assertIn("milestone m1: cut beta is not one of its features", errs)
        self.assertIn("alpha is in milestones m1 and m2", errs)
        self.assertNotIn("feature old does not exist", errs)       # shipped specs count

    def test_done_features_release_their_paths(self):
        cfg = load_config(self.root)
        errs = lint_specs(cfg, load_specs(self.root, cfg), {}, {"beta"}, None)
        self.assertFalse([e for e in errs if "overlaps beta" in e], errs)


class Titles(helpers.RepoCase):
    files = {
        ".agents/config.toml": CONFIG,
        "specs/features/boot/spec.md": helpers.spec([], extra="bootstrap: true\n"),
        "specs/features/alpha/spec.md": helpers.spec(["src/a/"]),
        "specs/features/beta/spec.md": helpers.spec(["src/b/"]),
        "specs/shipped/v0.1/old/spec.md": helpers.spec(["src/old/"]),
        "changes/beta.md": "## What shipped\nb\n",
    }

    def check(self, title, files):
        self.branch("work")
        self.commit("work", files)
        return run(self.root, "--title", title, "--base", "main")

    def test_feature_in_owns_plus_extras_and_open(self):
        rc, out = self.check("feat(alpha): a", {"src/a/x.py": "x", "changes/alpha.md": "done", "NOW.md": "now",
                                                "specs/decisions/alpha-why.md": "d", "specs/features/alpha/notes.md": "n"})
        self.assertEqual(rc, 0, out)

    def test_feature_outside_owns_fails(self):
        rc, out = self.check("feat(alpha): a", {"src/b/x.py": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("src/b/x.py is outside", out)

    def test_feat_on_a_done_feature_points_to_fix(self):
        rc, out = self.check("feat(beta): more", {"src/b/x.py": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("use fix(beta)", out)

    def test_scoped_fix_for_done_and_shipped_features(self):
        self.assertEqual(self.check("fix(beta): y", {"src/b/y.py": "y", "changes/beta.md": "more"})[0], 0)

    def test_fix_on_shipped_feature(self):
        rc, out = self.check("perf(old): faster", {"src/old/z.py": "z"})
        self.assertEqual(rc, 0, out)

    def test_unscoped_fix_avoids_in_flight_frozen_and_specs(self):
        self.assertEqual(self.check("fix: shared helper", {"src/shared/u.py": "u", "src/b/y.py": "y"})[0], 0)

    def test_unscoped_fix_may_not_touch_in_flight_owns(self):
        rc, out = self.check("chore: tidy", {"src/a/x.py": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("src/a/x.py is outside", out)

    def test_unscoped_fix_may_not_touch_frozen_or_specs(self):
        self.assertEqual(self.check("fix: x", {"core/x.py": "x"})[0], 1)

    def test_docs(self):
        self.assertEqual(self.check("docs: status", {"NOW.md": "n", "docs/guide.md": "g"})[0], 0)

    def test_docs_may_not_touch_code_or_specs(self):
        self.assertEqual(self.check("docs: x", {"src/shared/u.py": "u"})[0], 1)

    def test_contract_may_touch_frozen_and_specs_only(self):
        self.assertEqual(self.check("contract: add", {"core/x.py": "x", "specs/mission.md": "m"})[0], 0)

    def test_contract_outside_fails(self):
        self.assertEqual(self.check("contract: add", {"src/a/x.py": "x"})[0], 1)

    def test_plan_may_add_specs_and_ship(self):
        rc, out = self.check("plan: batch", {"specs/features/new-one/spec.md": "s", "specs/roadmap.md": "r",
                                             "specs/milestones.toml": "", "specs/shipped/v0.2/README.md": "w"})
        self.assertEqual(rc, 0, out)

    def test_plan_may_not_touch_code(self):
        self.assertEqual(self.check("plan: batch", {"src/a/x.py": "x"})[0], 1)

    def test_bootstrap_anything(self):
        self.assertEqual(self.check("feat(boot): skeleton", {"anything/at/all": "x"})[0], 0)

    def test_unknown_title(self):
        rc, out = self.check("[F01] old style", {"x": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("isn't one of", out)

    def test_unknown_feature(self):
        rc, out = self.check("feat(ghost): boo", {"x": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("unknown feature 'ghost'", out)

    def test_revert_exact_files(self):
        self.commit("bad", {"src/a/x.py": "bad"})               # lands on main
        sha = helpers.sh(self.root, "git", "rev-parse", "HEAD").strip()
        self.branch("undo")
        helpers.sh(self.root, "git", "-c", "core.hooksPath=/dev/null", "revert", "--no-edit", sha)
        self.assertEqual(run(self.root, "--title", 'Revert "bad"', "--base", "main")[0], 0)
        self.commit("sneak", {"src/b/extra.py": "x"})
        self.assertEqual(run(self.root, "--title", "revert: bad", "--base", "main")[0], 1)

    def test_revert_without_a_revert_commit(self):
        rc, out = self.check("revert: hand-made", {"src/a/x.py": "x"})
        self.assertEqual(rc, 1)
        self.assertIn("git revert", out)

    def test_no_args_is_usage_error(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root)]), 2)


if __name__ == "__main__":
    unittest.main()
