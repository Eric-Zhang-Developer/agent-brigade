import io
import unittest
from contextlib import redirect_stdout

import helpers
import ship
from check_ownership import lint_specs
from lib import load_config, load_milestones, load_shipped, load_specs, done_ids


def run(root, *args):
    out = io.StringIO()
    with redirect_stdout(out):
        rc = ship.main(["--root", str(root), *args])
    return rc, out.getvalue()


class Ship(helpers.RepoCase):
    files = {
        ".agents/config.toml": 'profile = "project"\n',
        "specs/milestones.toml": '[[milestone]]\nname = "v1"\nship = "2026-11-15"\nfeatures = ["store", "search", "tags"]\n',
        "specs/features/store/spec.md": helpers.spec(["jotter/store.py"], name="Store notes"),
        "specs/features/search/spec.md": helpers.spec(["jotter/search.py"], ["store"], name="Search"),
        "specs/features/tags/spec.md": helpers.spec(["jotter/tags.py"], name="Tags"),
        "changes/store.md": "# store\n## What shipped\nNotes in a JSON file.\n## Gaps\nNo locking.\n",
        "changes/search.md": "## What shipped\nCase-insensitive search.\n",
        "specs/decisions/search-case.md": "# Ignore case\n",
    }

    def test_moves_done_specs_and_writes_the_walkthrough(self):
        rc, out = run(self.root, "v1")
        self.assertEqual(rc, 0, out)
        self.assertIn("tags has no done note; it stays", out)
        self.assertIn("gh release create v1 --title v1 --notes-file specs/shipped/v1/README.md", out)
        self.assertTrue((self.root / "specs/shipped/v1/store/spec.md").exists())
        self.assertFalse((self.root / "specs/features/store").exists())
        self.assertTrue((self.root / "specs/features/tags/spec.md").exists())
        page = (self.root / "specs/shipped/v1/README.md").read_text()
        self.assertIn("## Store notes (`store`)", page)
        self.assertIn("#### What shipped\nNotes in a JSON file.", page)
        self.assertNotIn("# store\n", page)                           # the note's own title is dropped
        self.assertIn("Decisions: [search-case](../../decisions/search-case.md)", page)
        # the result is still a consistent repo: shipped specs count, and their paths are free again
        cfg = load_config(self.root)
        self.assertEqual(lint_specs(cfg, load_specs(self.root, cfg), load_shipped(self.root, cfg),
                                    done_ids(self.root, cfg), load_milestones(self.root, cfg)), [])

    def test_dry_run_changes_nothing(self):
        rc, out = run(self.root, "v1", "--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn("would move specs/features/store/", out)
        self.assertFalse((self.root / "specs/shipped").exists())

    def test_unknown_milestone(self):
        self.assertEqual(run(self.root, "v9")[0], 1)


if __name__ == "__main__":
    unittest.main()
