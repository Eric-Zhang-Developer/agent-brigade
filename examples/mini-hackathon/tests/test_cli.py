import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from wordfreq.__main__ import main


class Cli(unittest.TestCase):
    def test_prints_top_words(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.txt"
            p.write_text("b a b")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([str(p), "--top", "1"]), 0)
            self.assertEqual(out.getvalue(), "b\t2\n")

    def test_missing_file_is_a_message_not_a_traceback(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(main(["/nonexistent/file.txt"]), 1)
        self.assertIn("can't read", err.getvalue())
