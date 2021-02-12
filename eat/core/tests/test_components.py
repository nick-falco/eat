import unittest
from eat.core.components import TermOperation, Groupoid


class TestTermOperation(unittest.TestCase):

    def test_l_array(self):
        grp = Groupoid(3)
        grp.data = grp.list_to_groupoid_data([2, 1, 2,
                                              1, 0, 0,
                                              0, 0, 1])
        to = TermOperation(grp, random_target=True)
        l_array = to.l_array([[0], [1], [0], [2]])
        self.assertEqual(l_array, [[1, 2], [0, 1, 2], [1, 2], [0]])


if __name__ == "__main__":
    unittest.main()
