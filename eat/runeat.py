import os
import argparse
import platform
import time
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
from eat.deep_drilling_algorithm.dda import DeepDrillingAlgorithm
from eat.core.components import Groupoid, TermOperation
from eat.utilities.argparse_types import non_negative_integer, restricted_float


def parse_arguments():
    version_path = 'VERSION'
    VERSION = open(os.path.join(os.path.dirname(__file__),
                                version_path)).read()
    VERSION = VERSION.replace("\n", "")

    if platform.python_version() < "3.0.0":
        raise RuntimeError("Python 3 is required. You ran this script with "
                           "python version {}"
                           .format(platform.python_version()))

    parser = argparse.ArgumentParser(
        description=("Implementation of Evolution of Algebraic Terms (EAT {})"
                     .format(VERSION))
    )
    parser.add_argument('--version',
                        action='version',
                        version=VERSION)
    parser.add_argument('-a', '--algorithm',
                        help="EAT algorithm to run. (default='MFBA')",
                        type=str, default="MFBA",
                        choices=["DDA", "MFBA", "FBA", "SBA"])
    parser.add_argument('-g', '--groupoid',
                        help="Gropoid operation matrix",
                        nargs='+',
                        type=non_negative_integer,
                        default=[2, 1, 2, 1, 0, 0, 0, 0, 1])
    parser.add_argument('-rc', '--run-count',
                        help="Run the algorithm rc times.",
                        type=non_negative_integer,
                        default=1)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-tdt', '--target-ternary-descriminator',
                       help="Ternary descriminator target output (default)",
                       action='store_true')
    group.add_argument('-trt', '--target-random',
                       help="Random target output",
                       action='store_true')
    group.add_argument('-t', '--target', help="Custom target output",
                       nargs='+', type=str)
    parser.add_argument('-tfc', '--target_free_count',
                        help=("Number of target values to force to accept any "
                              "input value (default=0)"),
                        type=non_negative_integer,
                        default=0)
    parser.add_argument('-tv', '--term-variables',
                        help="Term variables to use. (default=['x','y',z'])",
                        nargs='+', type=str, default=["x", "y", "z"])
    vtg_group = parser.add_argument_group('Valid term generator options')
    vtg_group.add_argument('-mtgm', '--male-term-generation-method',
                           choices=["GRA", "random-term-generation"],
                           help=("Method to use for generating male terms. "
                                 "Choose from 'GRA' and "
                                 "'random-term-generation'. "
                                 "The 'GRA' option randomly creates a male "
                                 "term using the Gamblers Ruin Algorithm. The "
                                 "'random-term-generation' RTG (default) "
                                 "method randomly is a modified version of "
                                 "the GRA that randomly selects a 1 to 4 "
                                 "variable occurance term tree, and then "
                                 "runs the GRA with the selected term tree "
                                 "as the starting point if the randomly "
                                 "selected tree has 4 variable occurances. "
                                 "Otherwise, if the term tree has less than "
                                 "4 variable occurances it is used as is."),
                           default="random-term-generation")
    vtg_group.add_argument('-p', '--probability',
                           help=("For random term generation specify the "
                                 "probability of growing the random term. "
                                 "Must be a number between 0 and 1. "
                                 "(default = 0.1 = 10%%)"),
                           type=restricted_float, default=0.1)
    log_group = parser.add_argument_group('Logging verbosity options')
    log_group.add_argument('-v', '--verbose', help="Print verbose output",
                           action='store_true')
    log_group.add_argument('-ps', '--print-summary',
                           help=("Print a summary of the algorithms result. "
                                 "(default=False)"),
                           action='store_true')
    beam_group = parser.add_argument_group('Beam algorithm only options')
    beam_group.add_argument('-bw', '--beam-width',
                            type=non_negative_integer,
                            help=("Width of the beam (default=3)"),
                            default=None)
    beam_group.add_argument('-sbw', '--sub-beam-width',
                            type=non_negative_integer,
                            help=("Width of all sub beams (defaults to the "
                                  "same as the --beam-width). Only applies "
                                  "the MFBA algorithm."),
                            default=None)
    beam_group.add_argument('-iva', '--include-validity-array',
                            help=("Whether to include validity array in "
                                  "verbose log output (default=False)"),
                            action='store_true')

    return parser.parse_args()


def main():
    args = parse_arguments()
    # create groupoid table
    grp = Groupoid(args.groupoid)

    # setup term operation
    to_options = {}
    if args.term_variables:
        to_options["term_variables"] = args.term_variables
    to = TermOperation(grp,
                       **to_options)
    if args.target:
        to.target = \
            [[int(v) for v in t.split(",")] for t in args.target]
    elif args.target_random:
        to.target = to.get_random_target_array()
    elif args.target_ternary_descriminator:
        to.target = to.get_ternary_descriminator_target_array()

    if args.target_free_count > 0:
        to.target = to.get_filled_target_array(to.target,
                                               args.target_free_count)

    mtgm = args.male_term_generation_method

    verbose = args.verbose
    print_summary = args.print_summary
    run_count = args.run_count

    # MFBA specific arguments
    include_validity_array = args.include_validity_array
    beam_width = args.beam_width
    sub_beam_width = args.sub_beam_width

    prob = args.probability
    algorithm = args.algorithm
    if algorithm == "DDA":
        if run_count > 1:
            raise ValueError("The --run-count (-rc) option "
                             "only applies to the beam algorithms.")
        if include_validity_array:
            raise ValueError("The --include-validity-array (-iva) option "
                             "only applies to the beam algorithms.")
        elif beam_width:
            raise ValueError("The --beam-width (-bw) option only applies to "
                             "the beam algorithms.")
        # run the deep drilling algorithm
        dda = DeepDrillingAlgorithm(grp, to,
                                    male_term_generation_method=mtgm,
                                    term_expansion_probability=prob)
        dda.run(verbose=verbose, print_summary=print_summary)
    elif (algorithm == "MFBA" or algorithm == "FBA" or
          algorithm == "SBA"):
        if include_validity_array and not verbose:
            raise ValueError("The --verbose (-v) option must be set for the "
                             "--include-validity-array (-iva) option "
                             "to apply.")
        if beam_width is None:
            beam_width = 3
        if sub_beam_width is None:
            sub_beam_width = beam_width

        # run the beam algorithm
        beam = BeamEnumerationAlgorithm(
                                grp,
                                to,
                                algorithm,
                                male_term_generation_method=mtgm,
                                term_expansion_probability=prob,
                                beam_width=beam_width,
                                sub_beam_width=sub_beam_width)
        execution_results = []
        total_time = 0
        total_term_length = 0
        for i in range(run_count):
            start = time.time()
            node = beam.run(verbose=verbose, print_summary=print_summary,
                            include_validity_array=include_validity_array)
            end = time.time()

            # calculate execution times
            search_time = round(end - start, 2)
            term_length = len(node.term)
            # calculate totals for final averages
            total_time += search_time
            total_term_length += term_length

            execution_results.append({
                "search_time": search_time,
                "term_length": term_length
            })
            if not (print_summary or verbose):
                print(node.term if i == 0 else "\n" + node.term)


if __name__ == '__main__':
    main()
