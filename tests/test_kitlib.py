import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import helpers  # noqa: F401  (sets sys.path)
from lib import (find_root, front_matter, load_config, load_milestones, load_shipped, load_specs, parse_span,
                 parse_title, parse_when, pick_order, slug_error)

UTC = timezone.utc


class FrontMatter(unittest.TestCase):
    def test_inline_and_block_lists_comments_quotes_ints(self):
        fm = front_matter('---\nname: "A # not a comment"  # comment\nsize: 2\n'
                          'owns: [src/a/, tests/test_a]\ndepends_on:\n  - boot\n  - map\nbootstrap: true\n---\nbody')
        self.assertEqual(fm["name"], "A # not a comment")
        self.assertEqual(fm["size"], 2)
        self.assertEqual(fm["owns"], ["src/a/", "tests/test_a"])
        self.assertEqual(fm["depends_on"], ["boot", "map"])
        self.assertIs(fm["bootstrap"], True)

    def test_no_front_matter(self):
        self.assertEqual(front_matter("# just a doc"), {})


class Config(unittest.TestCase):
    def test_defaults_merge_and_find_root(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            helpers.write(root, {".agents/config.toml": 'profile = "project"\n[pr]\nwarn_lines = 50\n'})
            (root / "a" / "b").mkdir(parents=True)
            self.assertEqual(find_root(root / "a" / "b"), root.resolve())
            cfg = load_config(root)
            self.assertEqual(cfg["profile"], "project")
            self.assertEqual(cfg["pr"]["warn_lines"], 50)
            self.assertEqual(cfg["pr"]["exclude"], [])          # default kept alongside the override
            self.assertEqual(cfg["paths"]["specs"], "specs")


class Specs(unittest.TestCase):
    def test_folder_name_is_the_id_and_template_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            helpers.write(root, {
                "specs/features/_template/spec.md": helpers.spec([]),
                "specs/features/map-data/spec.md": helpers.spec(["a/"], name="Map data"),
                "specs/shipped/v0.1/boot/spec.md": helpers.spec([]),
                "specs/shipped/v0.1/README.md": "# v0.1",
            })
            cfg = load_config(root)
            specs = load_specs(root, cfg)
            self.assertEqual(list(specs), ["map-data"])
            self.assertEqual(specs["map-data"]["name"], "Map data")
            self.assertEqual(specs["map-data"]["_path"], "specs/features/map-data/spec.md")
            self.assertEqual(load_shipped(root, cfg)["boot"]["_milestone"], "v0.1")

    def test_slug_rules(self):
        self.assertIsNone(slug_error("map-data"))
        self.assertIsNone(slug_error("v2-export"))
        for bad in ("Map", "map_data", "-map", "map--data", "a" * 33, "F01 x"):
            self.assertIsNotNone(slug_error(bad), bad)
        self.assertIn("reserved", slug_error("plan"))


class Milestones(unittest.TestCase):
    def test_spans_and_times(self):
        self.assertEqual(parse_span("2d"), timedelta(days=2))
        self.assertEqual(parse_span("36h"), timedelta(hours=36))
        self.assertEqual(parse_span("5:30"), timedelta(hours=5, minutes=30))
        self.assertEqual(parse_span(""), timedelta(0))
        with self.assertRaises(ValueError):
            parse_span("soon")
        start = datetime(2026, 10, 10, 9, tzinfo=UTC)
        self.assertEqual(parse_when("+35:30", start), datetime(2026, 10, 11, 20, 30, tzinfo=UTC))
        self.assertIsNone(parse_when("+1:00", None))                  # an offset with no start: no deadline
        self.assertEqual(parse_when("2026-11-15", None), datetime(2026, 11, 16, tzinfo=UTC))  # through the 15th
        self.assertIsNone(parse_when("", start))
        with self.assertRaises(ValueError):
            parse_when("2026-11-15T09:00:00", None)                   # needs an offset

    def test_load_and_pick_order(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            helpers.write(root, {"specs/milestones.toml": (
                'start = "2026-10-10T09:00:00+00:00"\n'
                '[[milestone]]\nname = "early"\nship = "+2:00"\nfeatures = ["boot"]\n'
                '[[milestone]]\nname = "late"\nship = "+30:00"\nfreeze = "4:00"\nfeatures = ["b", "a"]\ncut = ["a"]\n'
                '[[milestone]]\nname = "end"\nship = "+36:00"\nfreeze = "6:00"\nfinal = true\nreport_before = "1:30"\n'
                'features = ["c"]\n'
                '[[milestone]]\nname = "someday"\nfeatures = ["d"]\n')})
            ms = load_milestones(root, load_config(root))
            late, end = ms["milestones"][1], ms["milestones"][2]
            self.assertEqual(late["freeze_start"], datetime(2026, 10, 11, 11, tzinfo=UTC))
            self.assertIsNone(late["report_start"])
            self.assertEqual(end["report_start"], datetime(2026, 10, 11, 19, 30, tzinfo=UTC))
            self.assertEqual(pick_order(ms, datetime(2026, 10, 10, 10, tzinfo=UTC)), ["boot", "b", "a", "c", "d"])
            self.assertEqual(pick_order(ms, datetime(2026, 10, 10, 12, tzinfo=UTC)), ["b", "a", "c", "d"])


class Titles(unittest.TestCase):
    def test_conventional_commits(self):
        self.assertEqual(parse_title("feat(map-data): nodes per map"),
                         {"kind": "feature", "type": "feat", "scope": "map-data"})
        self.assertEqual(parse_title("fix(bots): difficulty")["kind"], "fix")
        self.assertEqual(parse_title("refactor(bots): split ai")["kind"], "fix")
        self.assertEqual(parse_title("fix: shared typo")["scope"], None)
        self.assertEqual(parse_title("feat(ui)!: breaking")["scope"], "ui")
        self.assertEqual(parse_title("docs: NOW.md")["kind"], "docs")
        self.assertEqual(parse_title("contract: add a field")["kind"], "contract")
        self.assertEqual(parse_title("plan: batch of 9")["kind"], "plan")
        self.assertEqual(parse_title("revert: undo map")["kind"], "revert")
        self.assertEqual(parse_title('Revert "feat(map): x"')["kind"], "revert")   # GitHub's revert button

    def test_rejected(self):
        for bad in ("feat: no scope", "Map feature", "[F01] old style", "wip(x): y", "fix(x):", "feature(x): y"):
            self.assertIsNone(parse_title(bad), bad)


if __name__ == "__main__":
    unittest.main()
