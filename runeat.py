import argparse
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
from eat.deep_drilling_agorithm.dda import DeepDrillingAlgorithm
from eat.core.components import Groupoid, TermOperation


def parse_argments():
    parser = argparse.ArgumentParser(
        description=('Implementation of Evolution of Algebraic Terms (EAT)'))
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
                       help="Random target output (default)", action='store_true')
    group.add_argument('-t', '--target', help="Custom target output",
                       nargs='+', type=int)
    parser.add_argument('-tv', '--term-variables',
                        help="Term variables to use. (default=['x','y',z'])",
                        nargs='+', type=str, default=["x", "y", "z"])
    parser.add_argument('-mtgm', "--male-term-generation-method",
                        choices=["random", "random-12-terms"],
                        help=("Method to use for generating male terms. "
                              "Choose from 'random' and 'random-12-terms'. "
                              "The 'random' option randomly creates a male "
                              "term using the Gamblers Ruin Algorithm. The "
                              "'random-12-terms' method randomly selects a "
                              "term from the set of 12 one and two variable "
                              "terms. (default='random')"),
                        default="random")
    parser.add_argument('-v', '--verbose', help="Print verbose output",
                        action='store_true')
    parser.add_argument('-ps', '--print-summary',
                        help="Print a summary of the algorithms result",
                        action='store_true')
    return parser.parse_args()


def main():
    args = parse_argments()
    # create groupoid table
    grp = Groupoid(args.groupoid)

    # setup term operation
    to_options = {}
    if args.target:
        to_options["target"] = [[t] for t in args.target]
    if args.term_variables:
        to_options["term_variables"] = args.term_variables
    to = TermOperation(grp,
                       **to_options)
    if args.target_random:
        to.target = to.get_random_target_array()
    elif args.target_ternary_descriminator:
        to.target = to.get_ternary_descriminator_target_array()

    mtgm = args.male_term_generation_method

    verbose = args.verbose
    print_summary = args.print_summary
    algorithm = args.algorithm
    if algorithm == "DDA":
        # run the deep drilling algorithm
        dda = DeepDrillingAlgorithm(grp, to)
        dda.run(male_term_generation_method=mtgm, verbose=verbose,
                print_summary=print_summary)
    elif algorithm == "BEAM":
        # run the beam algorithm
        beam = BeamEnumerationAlgorithm(grp, to)
        beam.run()


if __name__ == '__main__':
    main()
