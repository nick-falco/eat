import unittest
from eat.core.utilities import split_male_term


class TestUtilities(unittest.TestCase):

    def test_split_male_term(self):
        self.assertEqual(split_male_term("yx*yzx***"), ("yx*", "yzx**"))
        self.assertEqual(split_male_term("xy*"), ("x", "y"))
        self.assertEqual(split_male_term("xy*zx**"), ("xy*", "zx*"))
