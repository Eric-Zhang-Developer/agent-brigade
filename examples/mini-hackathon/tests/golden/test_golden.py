"""The worked example from specs/context/worked-example.md. Frozen: if this fails, the math changed."""

import unittest

from wordfreq import count, top


class Golden(unittest.TestCase):
    def test_worked_example(self):
        self.assertEqual(top(count("The cat and the hat. The CAT sat!"), 3), [("the", 3), ("cat", 2), ("and", 1)])
