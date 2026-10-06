import unittest

from wordfreq.rank import ranked


class Rank(unittest.TestCase):
    def test_ties_alphabetical_and_limit(self):
        self.assertEqual(ranked({"b": 2, "a": 2, "c": 5}, 2), [("c", 5), ("a", 2)])
        self.assertEqual(ranked({"a": 1}, 0), [])
