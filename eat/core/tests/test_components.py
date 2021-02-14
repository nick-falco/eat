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

    def test_solve(self):
        grp = Groupoid(data=[1, 1, 2,
                             0, 2, 0,
                             0, 2, 1])
        to = TermOperation(grp,
                           term_variables=["x", "y", "z"])
        to.target = to.get_ternary_descriminator_target_array()
        sol = to.compute("xxz*xz***zyx*yxzyzxxy*z****zxxzxzz**yyx*xyz***zz****"
                       "**********zzz*yzz*xy*xyxxyxyxxx*x*zz***xyxzxxz*z*****"
                       "****zzx*xz*******xzxxyyx*zx*****zxz********zxzxxyy*z*"
                       "**zzx*x*****yzyyxx****zxyzz*yxyzx*yyxyy****yxzxz***yy"
                       "yxzxyx***zzxyy*********zzz**x*yxyyz****xy*xyyxyz*yz*y"
                       "zz*y*********************************zyz*zyx*xzzy****"
                       "***zyxxyxx*x***zz*zy*zyyzz*yyyyx****xxz**xy*zzy******"
                       "********yzxyzxxyzyyyzzzzxzyzyxyxzyzzzxzyzzxxyzyxzzyyz"
                       "y*zyyyy**********************************************"
                       "***zzx**xyxx*yxzy*****xzyyy*yx****zzy*zzy*yyzy**xxxz*"
                       "x**yyyzxxxyzyxzzzx*xy***************xzy*zyzyyxx*****z"
                       "xyzyyy*xy********************************")
        self.assertEqual(sol, to.target)
        self.assertNotEqual(to.compute("xy*z*yz**"), to.target)

    def test_postfix_to_infix(self):
        self.assertEqual(postfix_to_infix("xy*z*"), "((x*y)*z)")


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
