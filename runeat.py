import argparse
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
from eat.deep_drilling_agorithm.dda import DeepDrillingAlgorithm
from eat.core.components import Groupoid, TermOperation


def restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError(
                "%r not a floating-point literal" % (x,))

    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("{} not in range [0.0, 1.0]"
                                         .format(x))
    return x


def parse_argments():
    parser = argparse.ArgumentParser(
        description=('Implementation of Evolution of Algebraic Terms (EAT)')
    )
    parser.add_argument('-a', '--algorithm',
                        help="EAT algorithm to run. (default='DDA')",
                        type=str, default="DDA", choices=["DDA", "BEAM"])
    parser.add_argument('-g', '--groupoid',
                        help="Gropoid operation matrix",
                        nargs='+', type=int,
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
                              "input value (default=0)"), type=int, default=0)
    parser.add_argument('-tv', '--term-variables',
                        help="Term variables to use. (default=['x','y',z'])",
                        nargs='+', type=str, default=["x", "y", "z"])
    vtg_group = parser.add_argument_group('Valid term generator options')
    vtg_group.add_argument('-mtgm', '--male-term-generation-method',
                           choices=["random", "random-12-terms"],
                           help=("Method to use for generating male terms. "
                                 "Choose from 'random' and 'random-12-terms'. "
                                 "The 'random' option randomly creates a male "
                                 "term using the Gamblers Ruin Algorithm. The "
                                 "'random-12-terms' method randomly selects a "
                                 "term from the set of 12 one and two variable "
                                 "terms. (default='random')"),
                           default="random")
    vtg_group.add_argument('-mmtl', '--max-male-term-length',
                           help=("Maximum length of a randomly generated "
                                 "term. (default=None)"),
                           type=int, default=None),
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
    beam_group.add_argument('-bw', '--beam-width', type=int,
                            help=("Width of the beam (default=1)"),
                            default=None)
    beam_group.add_argument('-bto', '--beam-timeout', type=float,
                            help=("The maximum amount of time (sec) to spend "
                                  "searching for all nodes at a specific "
                                  "beam height. After this time, the program "
                                  "will continue to search until it has at "
                                  "least one valid female term at the current "
                                  "beam height. (default=None)"),
                            default=None)
    beam_group.add_argument('-iva', '--include-validity-array',
                            help=("Whether to include validity array in "
                                 "verbose log output (default=False)"),
                           action='store_true')
    

    return parser.parse_args()


def main():
    args = parse_argments()
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
    mmtl = args.max_male_term_length

    verbose = args.verbose
    print_summary = args.print_summary

    # BEAM specific arguments
    include_validity_array = args.include_validity_array
    beam_width = args.beam_width
    beam_timeout = args.beam_timeout

    prob = args.probability
    algorithm = args.algorithm
    if algorithm == "DDA":
        if include_validity_array:
            raise ValueError("The --include-validity-array (-iva) option "
                             "only applies to the BEAM algorithm.")
        elif beam_width:
            raise ValueError("The --beam-width (-bw) option only applies to "
                             "the BEAM algorithm.")
        elif beam_timeout:
            raise ValueError("The --beam-timeout (-bto) option only applies to "
                             "the BEAM algorithm.")
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
            beam_width = 1
        # run the beam algorithm
        beam = BeamEnumerationAlgorithm(grp, to,
                                        male_term_generation_method=mtgm,
                                        max_male_term_length=mmtl,
                                        term_expansion_probability=prob,
                                        beam_width=beam_width,
                                        beam_timeout=beam_timeout)
        beam.run(verbose=verbose, print_summary=print_summary,
                 include_validity_array=include_validity_array)


if __name__ == '__main__':
    main()
