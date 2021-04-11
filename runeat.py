import os
import argparse
import platform
import logging
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
from eat.deep_drilling_agorithm.dda import DeepDrillingAlgorithm
from eat.core.components import Groupoid, TermOperation
from eat.utilities.argparse_types import non_negative_integer, restricted_float


def parse_arguments():
    version_path = 'eat/VERSION'
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
                        help="EAT algorithm to run. (default='DDA')",
                        type=str, default="DDA", choices=["DDA", "BEAM"])
    parser.add_argument('-g', '--groupoid',
                        help="Gropoid operation matrix",
                        nargs='+',
                        type=non_negative_integer,
                        default=[1, 1, 2, 0, 2, 0, 0, 2, 1])
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
                           choices=["GRA", "random-12-terms"],
                           help=("Method to use for generating male terms. "
                                 "Choose from 'GRA' and 'random-12-terms'. "
                                 "The 'GRA' option randomly creates a male "
                                 "term using the Gamblers Ruin Algorithm. The "
                                 "'random-12-terms' method randomly selects a "
                                 "term from the set of 12 one and two "
                                 "variable terms. (default='GRA')"),
                           default="GRA")
    vtg_group.add_argument('-mintl', '--min-term-length',
                           help=("Minimum length of a randomly generated "
                                 "term. (default=None)"),
                           type=non_negative_integer, default=1),
    vtg_group.add_argument('-maxtl', '--max-term-length',
                           help=("Maximum length of a randomly generated "
                                 "term. (default=None)"),
                           type=non_negative_integer, default=None),
    vtg_group.add_argument('-p', '--probability',
                           help=("For random term generation specify the "
                                 "probability of growing the random term. "
                                 "Must be a number between 0 and 1. "
                                 "(default = 0.3)"),
                           type=restricted_float, default=0.3)
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
    beam_group.add_argument('-iva', '--include-validity-array',
                            help=("Whether to include validity array in "
                                  "verbose log output (default=False)"),
                            action='store_true')
    beam_group.add_argument('-pcc', '--promotion-child-count',
                            help=("The number of child terms required to "
                                  "promote a proccess before a higher beam "
                                  "level is full (default=2)"),
                            type=non_negative_integer, default=None)
    beam_group.add_argument('-lrlc', '--lr-level-count',
                            help=("The number of beam levels to take the left "
                                  "and/or right array of. Whether the left or "
                                  "right array is taken is choosen at random. "
                                  "(default=15)"),
                            type=non_negative_integer, default=15)

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

    # BEAM specific arguments
    include_validity_array = args.include_validity_array
    beam_width = args.beam_width
    promotion_child_count = args.promotion_child_count
    lr_level_count = args.lr_level_count

    prob = args.probability
    algorithm = args.algorithm
    if algorithm == "DDA":
        if include_validity_array:
            raise ValueError("The --include-validity-array (-iva) option "
                             "only applies to the BEAM algorithm.")
        elif beam_width:
            raise ValueError("The --beam-width (-bw) option only applies to "
                             "the BEAM algorithm.")
        elif promotion_child_count:
            raise ValueError("The --promotion_child_count (-pcc) option only "
                             "applies to the BEAM algorithm.")
        # run the deep drilling algorithm
        dda = DeepDrillingAlgorithm(grp, to,
                                    male_term_generation_method=mtgm,
                                    term_expansion_probability=prob)
        dda.run(verbose=verbose, print_summary=print_summary)
    elif algorithm == "BEAM":
        if include_validity_array and not verbose:
            raise ValueError("The --verbose (-v) option must be set for the "
                             "--include-validity-array (-iva) option "
                             "to apply.")
        if beam_width is None:
            beam_width = 3
        if promotion_child_count is None:
            promotion_child_count = 2
        if promotion_child_count > beam_width:
            logging.warning("The --promotion_child_count (-pcc) value must "
                            "less than or equal to the beam width. The "
                            "--beam-width={} and -pcc={}. Setting "
                            "-pcc={}".format(beam_width, promotion_child_count,
                                             promotion_child_count))
            promotion_child_count = beam_width

        # run the beam algorithm
        beam = BeamEnumerationAlgorithm(
                                grp,
                                to,
                                male_term_generation_method=mtgm,
                                min_term_length=mintl,
                                max_term_length=maxtl,
                                term_expansion_probability=prob,
                                beam_width=beam_width,
                                promotion_child_count=promotion_child_count,
                                lr_level_count=lr_level_count)
        beam.run(verbose=verbose, print_summary=print_summary,
                 include_validity_array=include_validity_array)


if __name__ == '__main__':
    main()
