import unittest
import sys
from eat.runeat import parse_arguments


class TestRunEAT(unittest.TestCase):

    def test_parse_arguments(self):
        sys.argv = ['eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0', '0',
                    '0', '0', '1', '-rc', '3', '-tdt', '-tfc', '2', '-tv',
                    'x', 'y', 'z', '-mtgm', 'GRA', '-p', '0.5', '-v', '-ps',
                    '-bw', '5', '-sbw', '2', '-iva']
        args = parse_arguments()
        self.assertEqual(args.algorithm, 'MFBA')
        self.assertEqual(args.groupoid, [2, 1, 2, 1, 0, 0, 0, 0, 1])
        self.assertEqual(args.run_count, 3)
        self.assertTrue(args.target_ternary_descriminator)
        self.assertEqual(args.target_free_count, 2)
        self.assertEqual(args.term_variables, ['x', 'y', 'z'])
        self.assertEqual(args.male_term_generation_method, 'GRA')
        self.assertEqual(args.probability, 0.5)
        self.assertTrue(args.verbose)
        self.assertTrue(args.print_summary)
        self.assertEqual(args.beam_width, 5)
        self.assertEqual(args.sub_beam_width, 2)
        self.assertTrue(args.include_validity_array)
