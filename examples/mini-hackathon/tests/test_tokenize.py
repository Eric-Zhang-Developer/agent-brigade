import unittest

from wordfreq.tokenize import words


class Tokenize(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(words("Don't STOP 2day, café!"), ["don", "t", "stop", "day", "caf"])
        self.assertEqual(words(""), [])
