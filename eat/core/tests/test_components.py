import unittest
from eat.core.components import TermOperation, Groupoid


class TestTermOperation(unittest.TestCase):

    def test_l_array(self):
        grp = Groupoid(3)
        grp.data = grp.list_to_groupoid_data([2, 1, 2,
                                              1, 0, 0,
                                              0, 0, 1])
        to = TermOperation(grp)
        l_array = to.l_array([[0], [1], [0], [2]])
        self.assertEqual(l_array, [[1, 2], [0, 1, 2], [1, 2], [0]])

    def test_r_array(self):
        grp = Groupoid(3)
        grp.data = grp.list_to_groupoid_data([2, 1, 2,
                                              1, 0, 0,
                                              0, 0, 1])
        to = TermOperation(grp)
        r_array = to.r_array([[0], [1], [0], [2]],
                             [[0, 1], [0], [0, 1, 2], [0, 2]])
        self.assertEqual(r_array, [[1], [1, 2], [0, 1, 2], [0, 1]])

        r_array = to.r_array([[0], [1], [0], [2]],
                             [[1], [0, 1, 2], [0, 1, 2], [0]])
        self.assertEqual(r_array, [[1], [0, 1, 2], [0, 1, 2], [0, 1]])

        r_array = to.r_array([[0], [1], [0], [2]],
                             [[1, 2], [1], [1], [0]])
        self.assertEqual(r_array, [[0, 1, 2], [0], [1], [0, 1]])

    def test_is_solution(self):
        grp = Groupoid(3)
        to = TermOperation(grp)
        self.assertTrue(to.is_solution([[0], [1], [0], [2]],
                                       [[0], [1], [0], [2]]))
        self.assertTrue(to.is_solution([[0], [1], [0], [2]],
                                       [[0, 1, 2], [0, 1], [0, 1], [0, 2]]))


if __name__ == "__main__":
    unittest.main()
