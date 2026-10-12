import unittest
from fractions import Fraction
from unittest.mock import patch
from types import SimpleNamespace
import sys
from eat.runeat import parse_arguments, main
from io import StringIO


class TestRunEAT(unittest.TestCase):

    def test_parse_arguments(self):
        """
        Tests parsing arguments for the runeat module.
        """
        sys.argv = [
            'eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0', '0',
            '0', '0', '1', '-rc', '3', '-ttd', '-tfc', '2', '-tv',
            'x', 'y', 'z', '-mtgm', 'gamblers-ruin-algorithm', '-p',
            '0.5', '-bw', '5', '-sbw', '2', '-iva'
        ]
        args = parse_arguments()
        self.assertEqual(args.algorithm, 'MFBA')
        self.assertEqual(args.groupoid, [2, 1, 2, 1, 0, 0, 0, 0, 1])
        self.assertEqual(args.run_count, 3)
        self.assertTrue(args.target_ternary_discriminator)
        self.assertEqual(args.target_free_count, 2)
        self.assertEqual(args.term_variables, ['x', 'y', 'z'])
        self.assertEqual(
            args.male_term_generation_method,
            'gamblers-ruin-algorithm')
        self.assertEqual(args.probability, 0.5)
        self.assertFalse(args.quiet)  # verbose is now inverted as quiet
        self.assertFalse(args.no_print_summary)  # print_summary is inverted
        self.assertEqual(args.beam_width, 5)
        self.assertEqual(args.sub_beam_width, 2)
        self.assertTrue(args.include_validity_array)

    def test_aca_requires_starting_tuple(self):
        sys.argv = [
            'eat', '-a', 'ACA', '-g', '2', '1', '2', '1', '0', '0',
            '0', '0', '1'
        ]
        args = parse_arguments()
        self.assertEqual(args.algorithm, 'ACA')

        output = StringIO()
        with patch('sys.stdout', new=output):
            with self.assertRaises(SystemExit) as context:
                main()
        self.assertEqual(context.exception.code, 1)
        self.assertIn('requires a starting tuple', output.getvalue())

    def test_aca_derives_probabilities_from_starting_tuple(self):
        sys.argv = [
            'eat', '-a', 'ACA', '-g', '2', '1', '2', '1', '0', '0',
            '0', '0', '1', '-d', '0', '0', '2'
        ]
        with patch('eat.runeat.Groupoid.is_asymptotic_complete',
                   autospec=True, return_value=[]) as ac_check:
            with patch('eat.runeat.log_ac_table'):
                main()

        self.assertEqual(ac_check.call_args.args[1], [
            Fraction(2, 3), Fraction(0, 1), Fraction(1, 3)
        ])
        self.assertEqual(sum(ac_check.call_args.args[1]), 1)
        self.assertEqual(ac_check.call_args.args[2], ['x', 'y', 'z'])
        self.assertEqual(ac_check.call_args.kwargs, {'limit': 700})

    def test_aca_supports_starting_tuple_option(self):
        sys.argv = [
            'eat', '-a', 'ACA', '-g', '2', '1', '2', '1', '0', '0',
            '0', '0', '1', '-d', '0', '0', '2'
        ]
        args = parse_arguments()
        self.assertEqual(args.tuple, [0, 0, 2])

    def test_aca_validates_starting_tuple(self):
        output = StringIO()
        with patch('sys.stdout', new=output):
            sys.argv = [
                'eat', '-a', 'ACA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-d', '0', '1'
            ]
            with self.assertRaises(SystemExit) as context:
                main()
        self.assertEqual(context.exception.code, 1)
        self.assertIn('one value for each term variable', output.getvalue())

        output = StringIO()
        with patch('sys.stdout', new=output):
            sys.argv = [
                'eat', '-a', 'ACA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-d', '0', '1', '3'
            ]
            with self.assertRaises(SystemExit) as context:
                main()
        self.assertEqual(context.exception.code, 1)
        self.assertIn('must be present in the groupoid', output.getvalue())

    def test_random_target_supports_four_term_variables(self):
        sys.argv = [
            'eat', '-tv', 'a', 'b', 'c', 'd', '-g', '2', '1', '2', '1',
            '0', '0', '0', '0', '1', '-trg'
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            with patch('eat.runeat.BeamEnumerationAlgorithm') as beam:
                beam.return_value.run.return_value = (
                    SimpleNamespace(term='a'), 0.0)
                main()

        term_operation = beam.call_args.args[1]
        self.assertEqual(len(term_operation.input), 81)
        self.assertTrue(all(
            len(input_row) == 4 for input_row in term_operation.input))
        self.assertEqual(len(term_operation.target), 81)

    def test_ternary_target_requires_three_term_variables(self):
        sys.argv = [
            'eat', '-tv', 'a', 'b', 'c', 'd', '-g', '2', '1', '2', '1',
            '0', '0', '0', '0', '1', '-ttd'
        ]
        output = StringIO()
        with patch('sys.stdout', new=output):
            with self.assertRaises(SystemExit) as context:
                main()

        self.assertEqual(context.exception.code, 1)
        self.assertIn('requires exactly 3 term variables', output.getvalue())

    def test_main(self):
        """
        Test the main function of the runeat module. Runs each algorithm.
        """
        output = StringIO()
        with patch('sys.stdout', new=output):
            sys.argv = [
                'eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-trg', '-tfc', '2', '-tv',
                'x', 'y', 'z', '-p', '0.1', '-bw', '5', '-sbw', '2'
            ]
            main()
            sys.argv = [
                'eat', '-a', 'FBA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-ttd', '-tfc', '2', '-tv',
                'a', 'b', 'c', '-p', '0.1', '-bw', '5'
            ]
            main()
            sys.argv = [
                'eat', '-a', 'SBA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-ttd', '-tfc', '2', '-tv',
                'x', 'y', 'z', '-p', '0.1'
            ]
            main()
            sys.argv = [
                'eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-ttd', '-tfc', '2', '-tv',
                'x', 'y', 'z', '-mtgm', 'random-term-generation'
            ]
            main()
            sys.argv = [
                'eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-ttd', '-tfc', '2', '-tv',
                'x', 'y', 'z', '-mtgm', 'random-term-generation'
            ]
            main()
            sys.argv = [
                'eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '-rc', '1', '-ttd', '-tfc', '2', '-tv', 'x',
                'y', 'z', '-mtgm', 'random-term-generation'
            ]
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(str(context.exception),
                             "Groupoid data must be a perfect square.")
            sys.argv = [
                'eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-ttd', '-tfc', '2', '-tv',
                'x', 'y', 'z', '-mtgm', 'gamblers-ruin-algorithm', '-iva'
            ]
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(
                str(context.exception),
                "The --include-validity-array (-iva) option only "
                "applies to the beam algorithms.")
            sys.argv = [
                'eat', '-a', 'DDA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-ttd', '-tfc', '2', '-tv',
                'x', 'y', 'z', '-mtgm', 'gamblers-ruin-algorithm',
                '-bw', '10'
            ]
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(
                str(context.exception),
                "The --beam-width (-bw) option only applies to the beam "
                "algorithms.")
            sys.argv = [
                'eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-ttd', '-tfc', '2', '-mtgm',
                'gamblers-ruin-algorithm', '-bw', '3', '-iva', '-q'
            ]
            with self.assertRaises(ValueError) as context:
                main()
            self.assertEqual(
                str(context.exception),
                "Verbose output must be enabled for the "
                "--include-validity-array (-iva) option to apply. (Use -q "
                "or --quiet to disable verbose\noutput.)")

    def test_target_length_mismatch(self):
        output = StringIO()
        with patch('sys.stdout', new=output):
            sys.argv = [
                'eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-t', '0', '1'
            ]
            with self.assertRaises(SystemExit) as context:
                main()
            self.assertEqual(context.exception.code, 1)
        self.assertIn('Target length does not match', output.getvalue())

    def test_target_value_out_of_range(self):
        output = StringIO()
        with patch('sys.stdout', new=output):
            target_values = ['0'] * 26 + ['0,3']
            sys.argv = [
                'eat', '-a', 'MFBA', '-g', '2', '1', '2', '1', '0', '0',
                '0', '0', '1', '-rc', '1', '-t', *target_values
            ]
            with self.assertRaises(SystemExit) as context:
                main()
            self.assertEqual(context.exception.code, 1)
        self.assertIn('not present in the groupoid', output.getvalue())
