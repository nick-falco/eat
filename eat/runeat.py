import csv
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
                        help="EAT algorithm to run. (default='BEAM')",
                        type=str, default="BEAM",
                        choices=["DDA", "BEAM", "LITTLEBEAM"])
    parser.add_argument('-g', '--groupoid',
                        help="Gropoid operation matrix",
                        nargs='+',
                        type=non_negative_integer)
    parser.add_argument('-rc', '--run-count',
                        help="Run the algorithm rc times. Write the run "
                             "times and term length for each execution to a "
                             "file named "
                             "beam_algorithm_execution_times.csv",
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
    vtg_group.add_argument('-mintl', '--min-term-length',
                           help=("Minimum length of a randomly generated "
                                 "term. (default=None) (GRA only)"),
                           type=non_negative_integer, default=None),
    vtg_group.add_argument('-maxtl', '--max-term-length',
                           help=("Maximum length of a randomly generated "
                                 "term. (default=None) (GRA only)"),
                           type=non_negative_integer, default=None),
    vtg_group.add_argument('-p', '--probability',
                           help=("For random term generation specify the "
                                 "probability of growing the random term. "
                                 "Must be a number between 0 and 1. "
                                 "(default = 0.025 = 2.5%%)"),
                           type=restricted_float, default=0.025)
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
                                  "the BEAM algorithm."),
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
    mintl = args.min_term_length
    maxtl = args.max_term_length

    verbose = args.verbose
    print_summary = args.print_summary
    run_count = args.run_count

    # BEAM specific arguments
    include_validity_array = args.include_validity_array
    beam_width = args.beam_width
    sub_beam_width = args.sub_beam_width

    prob = args.probability
    algorithm = args.algorithm
    if algorithm == "DDA":
        if run_count > 1:
            raise ValueError("The --run-count (-rc) option "
                             "only applies to the BEAM algorithm.")
        if include_validity_array:
            raise ValueError("The --include-validity-array (-iva) option "
                             "only applies to the BEAM algorithm.")
        elif beam_width:
            raise ValueError("The --beam-width (-bw) option only applies to "
                             "the BEAM algorithm.")
        # run the deep drilling algorithm
        dda = DeepDrillingAlgorithm(grp, to,
                                    male_term_generation_method=mtgm,
                                    term_expansion_probability=prob)
        dda.run(verbose=verbose, print_summary=print_summary)
    elif algorithm == "BEAM" or algorithm == "LITTLEBEAM":
        if include_validity_array and not verbose:
            raise ValueError("The --verbose (-v) option must be set for the "
                             "--include-validity-array (-iva) option "
                             "to apply.")
        if beam_width is None:
            beam_width = 3
        if sub_beam_width is None:
            sub_beam_width = beam_width

        if mtgm == 'random-term-generation' and (mintl or maxtl):
            raise ValueError(
                "The --min-term-length (-mintl) and --max-term-length "
                "options only apply when the --male-term-generation-method "
                "is set to 'GRA'.")

        # run the beam algorithm
        beam = BeamEnumerationAlgorithm(
                                grp,
                                to,
                                male_term_generation_method=mtgm,
                                min_term_length=mintl,
                                max_term_length=maxtl,
                                term_expansion_probability=prob,
                                beam_width=beam_width,
                                sub_beam_width=sub_beam_width,
                                is_subbeam=(algorithm == "LITTLEBEAM"))
        execution_results = []
        total_time = 0
        total_term_length = 0
        for _ in range(run_count):
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

        if print_summary and run_count > 1:
            result_file_name = "beam_algorithm_execution_times.csv"
            with open(result_file_name, "w") as results_file:
                keys = execution_results[0].keys()
                dict_writer = csv.DictWriter(results_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(execution_results)
            average_search_time = round(total_time / run_count, 2)
            average_term_length = round(total_term_length / run_count, 2)
            print(f"Average serach time = {average_search_time}")
            print(f"Average term length = {average_term_length}")
            print("----")


if __name__ == '__main__':
    main()
