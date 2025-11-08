import unittest
from unittest.mock import patch
import sys
from eat.runeat import parse_arguments, main
from io import StringIO


class TestRunEAT(unittest.TestCase):

    def test_parse_arguments(self):
        """
        Tests parsing arguments for the runeat module.
        """
        sys.argv = ['eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0', '0',
                    '0', '0', '1', '-rc', '3', '-tdt', '-tfc', '2', '-tv',
                    'x', 'y', 'z', '-mtgm', 'GRA', '-p', '0.5',
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
        self.assertFalse(args.quiet)  # verbose is now inverted as quiet
        self.assertFalse(args.no_print_summary)  # print_summary is inverted
        self.assertEqual(args.beam_width, 5)
        self.assertEqual(args.sub_beam_width, 2)
        self.assertTrue(args.include_validity_array)

    def test_main(self):
        """
        Test the main function of the runeat module. Runs each algorithm.
        """
        output = StringIO()
        with patch('sys.stdout', new=output):
            sys.argv = ['eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0',
                        '0', '0', '0', '1', '-rc', '1', '-trt', '-tfc', '2',
                        '-tv', 'x', 'y', 'z', '-p', '0.1', '-bw', '5', '-sbw',
                        '2']
            main()
            sys.argv = ['eat', '-a', 'FBA', '-g', '2', '1', '2', '1', '0', '0',
                        '0', '0', '1', '-rc', '1', '-tdt', '-tfc', '2', '-tv',
                        'a', 'b', 'c', '-p', '0.1', '-bw', '5']
            main()
            sys.argv = ['eat', '-a', 'SBA', '-g', '2', '1', '2', '1', '0', '0',
                        '0', '0', '1', '-rc', '1', '-tdt', '-tfc', '2', '-tv',
                        'x', 'y', 'z', '-p', '0.1']
            main()
            sys.argv = ['eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                        '0', '0', '1', '-rc', '1', '-tdt', '-tfc', '2', '-tv',
                        'x', 'y', 'z', '-mtgm', 'random-term-generation']
            main()
            sys.argv = ['eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                        '0', '0', '1', '-rc', '1', '-tdt', '-tfc', '2', '-tv',
                        'x', 'y', 'z', '-mtgm', 'random-term-generation']
            main()
            sys.argv = ['eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                        '0', '0', '-rc', '1', '-tdt', '-tfc', '2', '-tv',
                        'x', 'y', 'z', '-mtgm', 'random-term-generation']
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(str(context.exception),
                             "Groupoid data must be a perfect square.")
            sys.argv = ['eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                        '0', '0', '1', '-rc', '1', '-tdt', '-tfc', '2', '-tv',
                        'x', 'y', 'z', '-mtgm', 'GRA', '-iva']
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(str(context.exception),
                             "The --include-validity-array (-iva) option only "
                             "applies to the beam algorithms.")
            sys.argv = ['eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                        '0', '0', '1', '-rc', '1', '-tdt', '-tfc', '2', '-tv',
                        'x', 'y', 'z', '-mtgm', 'GRA', '-bw', '10']
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(str(context.exception),
                             "The --beam-width (-bw) option only "
                             "applies to the beam algorithms.")
            sys.argv = ['eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0',
                        '0', '0', '0', '1', '-rc', '1', '-tdt', '-tfc', '2',
                        '-mtgm', 'GRA', '-bw', '3', '-iva', '-q']
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(str(context.exception),
                             "Verbose output must be enabled for the "
                             "--include-validity-array (-iva) option "
                             "to apply. (Use -q or --quiet to disable "
                             "verbose\noutput.)")
