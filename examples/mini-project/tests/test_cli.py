import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from jotter.__main__ import main


class Cli(unittest.TestCase):
    def test_add_then_list_and_search(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"JOTTER_FILE": str(Path(d) / "n.jsonl")}):
            main(["add", "Buy milk"])
            main(["add", "call mom"])
            out = io.StringIO()
            with redirect_stdout(out):
                main(["search", "MILK"])
            self.assertIn("Buy milk", out.getvalue())
            self.assertNotIn("call mom", out.getvalue())
            out = io.StringIO()
            with redirect_stdout(out):
                main(["list"])
            self.assertEqual(len(out.getvalue().splitlines()), 2)
