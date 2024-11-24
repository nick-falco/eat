import unittest
from eat.deep_drilling_algorithm.dda import DeepDrillingAlgorithm
from eat.core.components import TermOperation, Groupoid


class TestDeepDrillingAlgorithm(unittest.TestCase):

    def test_generate_test_terms(self):
        grp = Groupoid([2, 1, 2, 1, 0, 0, 0, 0, 1])
        to = TermOperation(grp)
        dda = DeepDrillingAlgorithm(grp, to)
        assert len(dda.generate_test_terms(m=1)) == 3
        assert len(dda.generate_test_terms(m=2)) == 12
        assert len(dda.generate_test_terms(m=3)) == 147
        assert len(dda.generate_test_terms(m=4)) == 21612
