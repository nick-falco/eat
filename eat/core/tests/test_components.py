import unittest
from fractions import Fraction
import math
from eat.core.utilities import postfix_to_infix
from eat.core.components import TermOperation, Groupoid


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
        r_array = to.r_array([[0], [1], [0], [2]])
        self.assertAlmostEqual(r_array,
                               [[0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 2]])

    def test_r_of_l_array(self):
        grp = Groupoid(data=[2, 1, 2,
                             1, 0, 0,
                             0, 0, 1])
        to = TermOperation(grp)
        r_array = to.r_of_l_array([[0], [1], [0], [2]],
                                  [[0, 1], [0], [0, 1, 2], [0, 2]])
        self.assertEqual(r_array, [[1], [1, 2], [0, 1, 2], [0, 1]])

        r_array = to.r_of_l_array([[0], [1], [0], [2]],
                                  [[1], [0, 1, 2], [0, 1, 2], [0]])
        self.assertEqual(r_array, [[1], [0, 1, 2], [0, 1, 2], [0, 1]])

        r_array = to.r_of_l_array([[0], [1], [0], [2]],
                                  [[1, 2], [1], [1], [0]])
        self.assertEqual(r_array, [[0, 1, 2], [0], [1], [0, 1]])

    def test_is_solution(self):
        grp = Groupoid(data=[1, 1, 2,
                             0, 2, 0,
                             0, 2, 1])
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
            "zzxy**yy***zyy*zz*xz*xz**zyz**zy*yx***yz***zxz***xy*y***zz***zz*y"
            "**y*zy***x**")
        for i in range(0, len(to.target)):
            self.assertEqual(sol[i], to.target[i])
        self.assertNotEqual(to.compute("xy*z*yz**"), to.target)

    def test_solve(self):
        grp = Groupoid(data=[1, 1, 2,
                             0, 2, 0,
                             0, 2, 1])
        to = TermOperation(grp, term_variables=["x", "y", "z"])
        self.assertEqual(to.solve("000**"), 1)
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
            "yxy**xx**F*",
            [[0], [1], [2], [0], [0], [0], [0], [0], [0], [1], [1], [1], [0],
             [1], [2], [1], [1], [1], [2], [2], [2], [2], [2], [2], [0], [1],
             [2]])
        self.assertTrue(has_validity_array)
        self.assertEqual(
            validity_array,
            [[0], [2], [1], [0], [0], [0], [0], [0], [0], [0, 1], [0, 1],
             [0, 1], [0], [2], [1], [2], [2], [2], [1], [1], [1], [1], [1],
             [1], [0], [2], [1]])

    def test_target_length_validation(self):
        grp = Groupoid(data=[0, 1, 2,
                             1, 0, 2,
                             2, 2, 0])
        with self.assertRaises(ValueError) as ctx:
            TermOperation(grp, target=[[0]])
        self.assertIn("Target length does not match", str(ctx.exception))

    def test_target_value_validation(self):
        grp = Groupoid(data=[0, 1, 2,
                             1, 0, 2,
                             2, 2, 0])
        term_op = TermOperation(grp)
        invalid_target = [[3] for _ in range(len(term_op.input))]
        with self.assertRaises(ValueError) as ctx:
            term_op.target = invalid_target
        self.assertIn("not present in the groupoid", str(ctx.exception))

    def test_four_variable_random_target(self):
        grp = Groupoid(data=[0, 1,
                             1, 0])
        term_op = TermOperation(grp, term_variables=["a", "b", "c", "d"])
        target = term_op.get_random_target_array()

        self.assertEqual(len(term_op.input), 16)
        self.assertTrue(all(len(input_row) == 4 for input_row in term_op.input))
        self.assertEqual(len(target), 16)

        for input_row, target_value in zip(term_op.input, target):
            if len(set(input_row)) == 1:
                self.assertEqual(target_value, [input_row[0]])

    def test_ac_probability_rows_sum_to_one(self):
        grp = Groupoid(data=[2, 1, 2,
                             0, 0, 2,
                             1, 0, 0])
        table = grp.is_asymptotic_complete(
            [Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)],
            ["x", "y", "z"], limit=5)

        self.assertEqual(sum(table[0]), 1)
        for row in table[1:]:
            self.assertEqual(math.fsum(row), 1)


if __name__ == "__main__":
    unittest.main()
