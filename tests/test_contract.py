"""The 1.x contract: docs/stability.md and the code must agree, so a break fails CI instead of an installed project.

Every expected value is parsed from the tables in docs/stability.md, not copied into this file: the page is the
contract, so changing the surface means changing that page, in the same PR, where a reviewer sees it. Each check runs
both ways (documented == implemented), so an undocumented addition fails too.
"""

import os
import re
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

import helpers
import lib
import sync_issues

DOC = (helpers.KIT / "docs/stability.md").read_text()
SCRIPTS = {p.name: p for d in (helpers.SCRIPTS, helpers.HACKATHON_SCRIPTS) for p in d.glob("*.py") if p.name != "lib.py"}
SCRIPTS["install.py"] = helpers.KIT / "install.py"
ENV = {**os.environ, "PYTHONPATH": str(helpers.SCRIPTS)}  # installed, the hackathon scripts sit next to lib.py


def table(heading: str) -> list[list[str]]:
    """Body rows (cells stripped) of the first table under `### heading` / `## heading` in docs/stability.md."""
    section = re.search(rf"^#+ {re.escape(heading)}\n(.*?)(?=^#+ |\Z)", DOC, re.M | re.S)
    assert section, f"docs/stability.md has no '{heading}' section"
    rows = [line.strip().strip("|").split(" | ") for line in section[1].splitlines() if line.startswith("|")]
    return [[c.strip() for c in r] for r in rows[2:]]  # skip the header and the |---| line


def code(cell: str) -> str:
    """The first `backticked` text in a cell."""
    return re.search(r"`([^`]+)`", cell)[1]


def flatten(d: dict, prefix="") -> dict:
    out = {}
    for k, v in d.items():
        out.update(flatten(v, f"{prefix}{k}.") if isinstance(v, dict) else {f"{prefix}{k}": v})
    return out


def usage_flags(path: Path) -> set[str]:
    """Long flags in the script's argparse usage line (the text before the first blank line of --help)."""
    r = subprocess.run([sys.executable, str(path), "--help"], capture_output=True, text=True, env=ENV)
    assert r.returncode == 0, r.stdout + r.stderr
    return set(re.findall(r"--[a-z][a-z-]*", r.stdout.split("\n\n")[0])) - {"--help"}


class Contract(unittest.TestCase):
    def test_every_documented_flag_parses_and_none_is_undocumented(self):
        rows = table("Command line: the installer") + table("Installed scripts")
        documented = {code(r[0]): set(re.findall(r"`(--[a-z-]+)`", r[1])) for r in rows}
        self.assertEqual(set(documented), set(SCRIPTS), "every installed script (and install.py) has a row")
        for name, flags in documented.items():
            with self.subTest(script=name):
                self.assertEqual(usage_flags(SCRIPTS[name]), flags)
                bad = subprocess.run([sys.executable, str(SCRIPTS[name]), "--no-such-flag"], capture_output=True, env=ENV)
                self.assertEqual(bad.returncode, 2, "usage errors exit 2")

    def test_config_keys_and_defaults_match_lib_defaults(self):
        documented = {code(r[0]): tomllib.loads(f"v = {code(r[1])}")["v"] for r in table("`.agents/config.toml`")}
        self.assertEqual(documented, flatten(lib.DEFAULTS))

    def test_installed_config_shows_the_documented_defaults(self):
        installed = tomllib.loads((helpers.KIT / "template/common/.agents/config.toml").read_text()
                                  .replace("__SCHEMA__", "3").replace("__OPEN__", "")
                                  .replace("__PARALLEL__", "3"))
        self.assertEqual({k: v for k, v in flatten(installed).items() if k not in ("profile", "size")},
                         {k: v for k, v in flatten(lib.DEFAULTS).items() if k not in ("profile", "size")})

    def test_pr_title_types(self):
        self.assertEqual({code(r[0]) for r in table("PR titles")}, set(lib.KINDS))

    def test_label_names(self):
        self.assertEqual({code(r[0]) for r in table("Issues and labels")}, set(sync_issues.LABELS))

    def test_spec_marker(self):
        self.assertIn("`<!-- spec: <slug> -->`", DOC)
        self.assertEqual(sync_issues.MARKER.findall("x <!-- spec: map-data --> y"), ["map-data"])

    def test_slug_rules(self):
        self.assertEqual(lib.SLUG.pattern, "^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertIn(f"`{lib.SLUG.pattern}`", DOC)
        self.assertEqual(lib.RESERVED, {"shipped", "contract", "plan", "docs", "revert"})
        self.assertIsNone(lib.slug_error("a" * 32))
        self.assertIsNotNone(lib.slug_error("a" * 33))

    def test_front_matter_keys_are_the_template_keys(self):
        documented = {code(r[0]) for r in table("Slugs and spec front matter") if r[0].startswith("`")}
        tpl = lib.front_matter((helpers.KIT / "template/common/specs/features/_template/spec.md").read_text())
        self.assertEqual(documented - {"bootstrap"}, set(tpl))  # bootstrap is opt-in, named in the template comment

    def test_milestone_fields_and_formats(self):
        documented = {code(r[0]) for r in table("`specs/milestones.toml`")}
        self.assertEqual(documented, {"start", "name", "ship", "freeze", "final", "report_before", "features", "cut",
                                      "allow"})
        from datetime import datetime, timedelta
        start = datetime.fromisoformat("2026-10-10T09:00:00-04:00")
        for v in ("+1:30", "+36h", "+2d", "2026-10-12", "2026-10-12T09:00:00-04:00"):
            self.assertIsNotNone(lib.parse_when(v, start), v)
        self.assertIsNone(lib.parse_when("", start))
        self.assertEqual([lib.parse_span(v) for v in ("1:30", "36h", "2d")],
                         [timedelta(minutes=90), timedelta(hours=36), timedelta(days=2)])

    def test_done_note_headings(self):
        documented = re.findall(r"^- `## ([^`]+)`$", DOC, re.M)
        agents = (helpers.KIT / "template/parts/agents-common.md").read_text()
        self.assertEqual(documented, ["What shipped", "Where it lives", "How to check it", "Gaps"])
        self.assertEqual(re.findall(r"`## ([^`]+)`", agents), documented)


# The `verify:` line formats in docs/stability.md, as one regex.
VERIFY_LINE = re.compile(r"^verify: (?:`.*` (?:pass|FAIL \(exit \d+\)|FAIL \(timed out after [\d.]+s\)) at \S+"
                         r"(?: \(uncommitted changes\))?(?: \(evidence: .+\))?"
                         r"|not set up \(\[verify\]\.command is empty\); the done note says `not verified`)$")


class VerifyLine(helpers.RepoCase):
    def run_verify(self, command: str) -> str:
        cfg = 'profile = "project"\n' + (f"[verify]\ncommand = '{command}'\ntimeout = 5\n" if command else "")
        (self.root / ".agents/config.toml").write_text(cfg)
        self.commit("config")
        r = subprocess.run([sys.executable, str(SCRIPTS["verify.py"]), "--root", str(self.root), "--slug", "x"],
                           capture_output=True, text=True)
        return r.stdout.strip().splitlines()[-1]

    def test_every_result_line_matches_the_documented_format(self):
        for command in ("", "true", "exit 3", "echo {out} > /dev/null"):
            with self.subTest(command=command):
                self.assertRegex(self.run_verify(command), VERIFY_LINE)
        self.assertIn("FAIL (exit 3)", self.run_verify("exit 3"))
        for line in re.findall(r"^verify: .*$", DOC, re.M):
            sample = (line.replace("`<command>`", "`true`").replace("<sha>", "abc1234").replace("<N>", "1")
                      .replace("<seconds>", "300").replace("<dir>", "/tmp/e"))
            for variant in (re.sub(r"\[( \([^]]*\))\]", "", sample), re.sub(r"\[( \([^]]*\))\]", r"\1", sample)):
                self.assertRegex(variant, VERIFY_LINE)


if __name__ == "__main__":
    unittest.main()
