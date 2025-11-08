import unittest
from eat.core.components import Groupoid, TermOperation
from eat.core.utilities import split_male_term, \
    get_target_indexes_not_preserving_idempotents


class TestUtilities(unittest.TestCase):

    def test_split_male_term(self):
        self.assertEqual(split_male_term("yx*yzx***"), ("yx*", "yzx**"))
        self.assertEqual(split_male_term("xy*"), ("x", "y"))
        self.assertEqual(split_male_term("xy*zx**"), ("xy*", "zx*"))

    def test_get_target_indexes_not_preserving_idempotents(self):
        grp = Groupoid(data=[2, 1, 2,
                             0, 0, 0,
                             0, 2, 1])
        to = TermOperation(grp)
        # The ternary descriminator gives d(v,v,v) = v for all v
        target = to.get_ternary_descriminator_target_array()
        # This groupoid has no idempotents (0*0=2, 1*1=0, 2*2=1)
        # so no diagonal positions need to be checked for idempotent
        # preservation
        self.assertEqual(
            get_target_indexes_not_preserving_idempotents(grp, target), [])

        # Now test with a groupoid that HAS idempotents
        grp = Groupoid(data=[0, 1, 2,
                             0, 1, 0,
                             0, 2, 2])
        # This groupoid: 0*0=0 (idempotent), 1*1=1 (idempotent),
        # 2*2=2 (idempotent)
        to = TermOperation(grp)
        target = to.get_ternary_descriminator_target_array()
        # Ternary discriminator preserves all idempotents since
        # d(v,v,v) = v
        self.assertEqual(
            get_target_indexes_not_preserving_idempotents(grp, target), [])

        # Change target at idempotent positions
        # target(0,0,0) = 1, but 0*0=0 so should be 0
        bad_target_0 = [[1]] + target[1:]
        self.assertEqual(
            get_target_indexes_not_preserving_idempotents(
                grp, bad_target_0),
            [0])

        # target(1,1,1) = 0, but 1*1=1
        bad_target_1 = target[:13] + [[0]] + target[14:]
        self.assertEqual(
            get_target_indexes_not_preserving_idempotents(
                grp, bad_target_1),
            [13])

        # target(2,2,2) = 0, but 2*2=2
        bad_target_2 = target[:26] + [[0]]
        self.assertEqual(
            get_target_indexes_not_preserving_idempotents(
                grp, bad_target_2),
            [26])

        bad_target_0_and_2 = [[1]] + target[1:26] + [[0]]
        self.assertEqual(
            get_target_indexes_not_preserving_idempotents(
                grp, bad_target_0_and_2),
            [0, 26])


if __name__ == "__main__":
    unittest.main()
