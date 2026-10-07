import tempfile
import unittest
from pathlib import Path

import helpers  # noqa: F401  (sets sys.path)
from kitlib import find_root, front_matter, load_config, load_specs, parse_title


class FrontMatter(unittest.TestCase):
    def test_inline_and_block_lists_comments_quotes_ints(self):
        fm = front_matter('---\nid: F01  # comment\nname: "A # not a comment"\nphase: 2\n'
                          'owns: [src/a/, tests/test_a]\ndepends_on:\n  - F00\n  - F02\nbootstrap: true\n---\nbody')
        self.assertEqual(fm["id"], "F01")
        self.assertEqual(fm["name"], "A # not a comment")
        self.assertEqual(fm["phase"], 2)
        self.assertEqual(fm["owns"], ["src/a/", "tests/test_a"])
        self.assertEqual(fm["depends_on"], ["F00", "F02"])
        self.assertIs(fm["bootstrap"], True)

    def test_no_front_matter(self):
        self.assertEqual(front_matter("# just a doc"), {})


class Config(unittest.TestCase):
    def test_defaults_merge_and_find_root(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "kit.toml").write_text('profile = "project"\n[pr]\nmax_lines = 50\n')
            (root / "a" / "b").mkdir(parents=True)
            self.assertEqual(find_root(root / "a" / "b"), root.resolve())
            cfg = load_config(root)
            self.assertEqual(cfg["profile"], "project")
            self.assertEqual(cfg["pr"]["max_lines"], 50)
            self.assertEqual(cfg["pr"]["exclude"], [])          # default kept alongside the override
            self.assertEqual(cfg["paths"]["specs"], "specs")

    def test_load_specs_skips_template_and_keeps_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            helpers.write(root, {
                "specs/features/_template/spec.md": helpers.spec("F00", []),
                "specs/features/F01-a/spec.md": helpers.spec("F01", ["a/"]),
                "specs/features/F01-b/spec.md": helpers.spec("F01", ["b/"]),
            })
            specs = load_specs(root, load_config(root))
            self.assertEqual(list(specs), ["F01"])
            self.assertEqual(len(specs["F01"]), 2)


class Titles(unittest.TestCase):
    def test_prefixes(self):
        self.assertEqual(parse_title("[F12] Map")["kind"], "feature")
        self.assertEqual(parse_title("[FIX-F3] typo"), {"kind": "fix", "id": "F3", "sha": None})
        self.assertEqual(parse_title("[C4] add field")["id"], "C4")
        self.assertEqual(parse_title("[PLAN] week 3")["kind"], "plan")
        self.assertEqual(parse_title("[REVERT-abc1234] oops")["sha"], "abc1234")
        self.assertIsNone(parse_title("Map feature"))
        self.assertIsNone(parse_title("[REVERT-xyz] nope"))


if __name__ == "__main__":
    unittest.main()
