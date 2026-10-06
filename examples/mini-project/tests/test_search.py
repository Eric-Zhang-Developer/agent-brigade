import unittest

from jotter.search import search


class Search(unittest.TestCase):
    def test_case_insensitive_newest_first(self):
        notes = [{"text": "Old Idea", "created": "2026-01-01T00:00:00+00:00"},
                 {"text": "new idea", "created": "2026-02-01T00:00:00+00:00"},
                 {"text": "other", "created": "2026-03-01T00:00:00+00:00"}]
        self.assertEqual([n["text"] for n in search(notes, "IDEA")], ["new idea", "Old Idea"])
