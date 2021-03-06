import unittest
from eat.core.utilities import postfix_to_infix
from eat.core.components import TermOperation, Groupoid, ValidTermGenerator


class TestTermOperation(unittest.TestCase):

    def test_l_array(self):
        grp = Groupoid(data=[2, 1, 2,
                             1, 0, 0,
                             0, 0, 1])
        to = TermOperation(grp)
        l_array = to.l_array([[0], [1], [0], [2]])
        self.assertEqual(l_array, [[1, 2], [0, 1, 2], [1, 2], [0]])

    def test_r_array(self):
        grp = Groupoid(data=[2, 1, 2,
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
        grp = Groupoid()
        to = TermOperation(grp)
        self.assertTrue(to.is_solution([[0], [1], [0], [2]],
                                       [[0], [1], [0], [2]]))
        self.assertTrue(to.is_solution([[0], [1], [0], [2]],
                                       [[0, 1, 2], [0, 1], [0, 1], [0, 2]]))

    def test_compute(self):
        grp = Groupoid(data=[1, 1, 2,
                             0, 2, 0,
                             0, 2, 1])
        to = TermOperation(grp,
                           term_variables=["x", "y", "z"])
        to.target = to.get_ternary_descriminator_target_array()
        sol = to.compute(
            "yzz**yy**zyy**yxz*xzzy**zyy*yyy********yz*xz*z*xxzz**xzzxzx*y**x*"
            "*x**xy***z****x**zx***y***xxz**y*yz**x**")
        self.assertEqual(sol, to.target)
        self.assertNotEqual(to.compute("xy*z*yz**"), to.target)

    def test_solve(self):
        grp = Groupoid(data=[2, 1, 2,
                             1, 0, 0,
                             0, 0, 1])
        to = TermOperation(grp, term_variables=["x", "y", "z"])
        self.assertEqual(to.solve("0011***"), 2)

    def test_postfix_to_infix(self):
        self.assertEqual(postfix_to_infix("xy*z*"), "((x*y)*z)")

    def test_compute_validity_array(self):
        grp = Groupoid(data=[1, 1, 2,
                             0, 2, 0,
                             0, 2, 1])
        to = TermOperation(grp, term_variables=["x", "y", "z"])
        has_validity_array, validity_array = to.compute_validity_array(
            "zz*yy**F*",
            [[0], [1], [2], [0], [0], [0], [0], [0], [0], [1], [1], [1], [0],
             [1], [2], [1], [1], [1], [2], [2], [2], [2], [2], [2], [0], [1],
             [2]])
        self.assertTrue(has_validity_array)
        self.assertEqual(
            validity_array,
            [[0, 2], [0, 1], [1], [0], [0], [0], [0], [0], [0], [2], [2], [2],
             [0], [2], [1], [2], [2], [2], [2], [1], [2], [2], [2], [1],
             [0, 2], [0, 1], [1]])


class TestValidTermGenerator(unittest.TestCase):

    def test_random_12_terms(self):
        vtg = ValidTermGenerator(["x", "y", "z"])
        rand_term = vtg.random_12_terms()
        self.assertIn(rand_term,
                      ['x', 'y', 'z', 'xx*', 'xy*', 'xz*', 'yx*', 'yy*',
                       'yz*', 'zx*', 'zy*', 'zz*'])

        vtg = ValidTermGenerator(["x", "y", "z", "a"])
        with self.assertRaises(RuntimeError):
            vtg.random_12_terms()


if __name__ == "__main__":
    unittest.main()
