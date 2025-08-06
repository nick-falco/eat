import argparse
import platform
import sys
import os
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
from eat.deep_drilling_algorithm.dda import DeepDrillingAlgorithm
from eat.core.components import Groupoid, TermOperation
from eat.core.utilities import log_execution_results_summary, \
    log_ac_table, get_logger
from eat.utilities.argparse_types import non_negative_integer, \
    positive_integer, restricted_float


LOG = get_logger('runeat_logger')


def supports_color():
    """Check if terminal supports color output"""
    return (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
            os.environ.get('TERM') != 'dumb' and
            os.environ.get('NO_COLOR') is None)


def colorize(text, color_code):
    """Add ANSI color codes to text if terminal supports it"""
    if supports_color():
        return f"\033[{color_code}m{text}\033[0m"
    return text


# Color definitions
BLUE = "34"      # For headers and sections
GREEN = "32"     # For successful/positive elements
YELLOW = "33"    # For warnings/important info
CYAN = "36"      # For examples and commands
MAGENTA = "35"   # For algorithm names
BOLD = "1"       # For emphasis

# Combined color codes (avoiding backslashes in f-strings)
BOLD_BLUE = BOLD + ";" + BLUE
BOLD_GREEN = BOLD + ";" + GREEN
BOLD_YELLOW = BOLD + ";" + YELLOW

# Newline character for f-strings
NL = "\n"


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
        usage='eat [-h] [--version] -g GROUPOID [GROUPOID ...] '
              '[(-tdt | -trt | -t TARGET [TARGET ...]) | -ac] [options...]',
        description=(
            colorize('🧮 Evolution of Algebraic Terms (EAT', BOLD_BLUE) + " "
            + colorize(VERSION, BOLD_GREEN) + colorize(') 🧮', BOLD_BLUE) +
            "\n\n" +
            colorize('Python implementation of algorithms from', CYAN) + " " +
            colorize('"Evolution of Algebraic Terms 4: Biological Beam '
            'Algorithms."', BOLD) + " " +
            "Given an arbitrary performance specification, systematically "
            "designs "
            "digital circuits using binary logic on groupoids of size 3 "
            "or larger. Consistently finds designs from an incredibly "
            "vast search space in fractions of a second.\n\n" +
            colorize('💡 Quick start:', BOLD_YELLOW) + " " +
            colorize('eat -g 2 1 2 1 0 0 0 0 1 -tdt', CYAN) + "\n" +
            "   " + colorize('(-tdt = ternary discriminator target '
            'operation)', MAGENTA) + "\n" +
            "   Verbose output and summaries enabled by default."
        ),
        epilog=(
            colorize('📚 EXAMPLES:', BOLD_BLUE) + "\n" +
            "  " + colorize('eat -g 2 1 2 1 0 0 0 0 1 -tdt', CYAN) + "\n" +
            "    Basic evolution using " + colorize('MFBA', MAGENTA) +
            " with ternary discriminator\n" +
            "    target\n\n" +
            "  " + colorize('eat -g 2 1 2 1 0 0 0 0 1 -tdt -a DDA', CYAN) +
            "\n" +
            "    " + colorize('Deep drilling algorithm', MAGENTA) +
            " for systematic search\n\n" +
            "  " + colorize('eat -g 2 1 2 1 0 0 0 0 1 -trt -rc 10', CYAN) +
            "\n" +
            "    Statistical analysis with " + colorize('10 runs', YELLOW) +
            " using random target\n\n" +
            "  " + colorize('eat -g 2 1 2 1 0 0 0 0 1 -tdt -q', CYAN) + "\n" +
            "    " + colorize('Quiet mode', YELLOW) +
            " showing only final results\n\n" +
            "  " + colorize('eat -g 2 1 2 1 0 0 0 0 1 -ac', CYAN) + "\n" +
            "    " + colorize('Asymptotic completeness analysis', MAGENTA) +
            " of the groupoid\n\n" +
            colorize('🌟 DEFAULTS:', BOLD_GREEN) +
            " Verbose output and result summaries enabled. " +
            colorize('MFBA (Male-Female Beam Algorithm)', MAGENTA) +
            " is selected by default.\n\n" +
            colorize('🔧 CUSTOMIZATION:', BOLD_YELLOW) + " Use " +
            colorize('-q', CYAN) + " for quiet mode, " +
            colorize('--no-print-summary', CYAN) + " to disable summaries, " +
            colorize('-a', CYAN) + " to change algorithms, " +
            "or " + colorize('-ac', CYAN) + " for asymptotic completeness " +
            "analysis."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--version',
                        action='version',
                        version=VERSION)

    # ========== REQUIRED ARGUMENTS (grouped together) ==========
    required_group = parser.add_argument_group(
        '🔥 ' + colorize('REQUIRED ARGUMENTS', BOLD_YELLOW) + 
        ' (groupoid always required, target required unless using -ac)')
    
    required_group.add_argument('-g', '--groupoid',
                                help=(
                                    colorize('⊞ Groupoid operation matrix',
                                             BLUE) +
                                    ". Binary operation table for " +
                                    "algebraic " +
                                    "structure. " +
                                    "Example: " +
                                    colorize('-g 2 1 2 1 0 0 0 0 1', CYAN)),
                                nargs='+',
                                type=non_negative_integer,
                                required=True)
    
    target_mutex = required_group.add_mutually_exclusive_group(required=False)
    target_mutex.add_argument('-tdt', '--target-ternary-descriminator',
                              help=(
                                  "🎯 " + colorize('Ternary discriminator ' +
                                                  'target', CYAN) + " output"),
                              action='store_true')
    target_mutex.add_argument('-trt', '--target-random',
                              help=(
                                  "🎲 " + colorize('Random target', CYAN) +
                                  " output"),
                              action='store_true')
    target_mutex.add_argument('-t', '--target',
                              help=(
                                  "🎨 " + colorize('Custom target', CYAN) +
                                  " output (space delimited)"),
                              nargs='+', type=str)

    # ========== OPTIONAL ARGUMENTS ==========
    optional_group = parser.add_argument_group(
        '⚙️  ' + colorize('Optional Configuration', BLUE))
    
    optional_group.add_argument('-a', '--algorithm',
                                help=(
                                    colorize('🔍 Evolutionary search algorithm', BLUE) +
                                    " " +
                                    "(default: " + colorize('MFBA', BOLD) + "). " +
                                    colorize('DDA', MAGENTA) +
                                    " = Deep Drilling Algorithm, " +
                                    colorize('MFBA', MAGENTA) +
                                    " = Male-Female Beam " +
                                    "Algorithm, " + colorize('FBA', MAGENTA) +
                                    " = Female Beam Algorithm, " +
                                    colorize('SBA', MAGENTA) +
                                    " = Sample Beam Algorithm"),
                                type=str, default="MFBA",
                                choices=["DDA", "MFBA", "FBA", "SBA"])
    optional_group.add_argument('-rc', '--run-count',
                                help=(
                                    "🔄 Number of evolutionary runs (default: 1). "
                                    "Multiple runs provide statistical data about "
                                    "algorithm performance"),
                                type=non_negative_integer,
                                default=1)
    optional_group.add_argument('-tfc', '--target_free_count',
                                help=("Number of target values to force to accept any "
                                      "input value (default=0)."),
                                type=non_negative_integer,
                                default=0)
    optional_group.add_argument('-tv', '--term-variables',
                                help="Term variables to use. (default=['x','y',z'])",
                                nargs='+', type=str, default=["x", "y", "z"])
    vtg_group = parser.add_argument_group(
        '🔧 ' + colorize('Valid term generator options', MAGENTA))
    vtg_group.add_argument('-mtgm', '--male-term-generation-method',
                           choices=["GRA", "random-term-generation"],
                           help=("Male term generation method (default: "
                                 "random-term-generation). "
                                 "GRA = Gambler's Ruin Algorithm for "
                                 "stochastic term construction, "
                                 "random-term-generation = Modified GRA "
                                 "with adaptive term tree selection (1-4 "
                                 "variables)"),
                           default="random-term-generation")
    vtg_group.add_argument('-p', '--probability',
                           help=("For random term generation specify the "
                                 "probability of growing the random term. "
                                 "Must be a number between 0 and 1. "
                                 "(default = 0.1 = 10%%)"),
                           type=restricted_float, default=0.1)
    log_group = parser.add_argument_group(
        '📋 ' + colorize('Output Control', GREEN) + 
        ' (verbose & summaries ON by default)')
    log_group.add_argument('-q', '--quiet', 
                           help=(
                               "🔇 Disable verbose output (ON by default). "
                               "Minimal output showing only final results"),
                           action='store_true', default=False)
    log_group.add_argument('--no-print-summary',
                           help=(
                               "📊 Disable result summary (ON by default). "
                               "Disables statistical summary of "
                               "performance metrics, execution time, and "
                               "solution quality"),
                           action='store_true', default=False)
    dda_group = parser.add_argument_group(
        '⛏️  ' + colorize('Deep Drilling Algorithm only options', CYAN))
    dda_group.add_argument('-m',
                           help=("The value of m to use for the "
                                 "Deep Drilling Algorithm. This determines "
                                 "the tree height of the test terms. "
                                 "(default=2)"),
                           type=positive_integer, default=2)
    beam_group = parser.add_argument_group(
        '🌟 ' + colorize('Beam algorithm only options', MAGENTA))
    beam_group.add_argument('-bw', '--beam-width',
                            type=non_negative_integer,
                            help=("Width of the beam (default: 3)"),
                            default=None)
    beam_group.add_argument('-sbw', '--sub-beam-width',
                            type=non_negative_integer,
                            help=("Width of all sub beams (defaults to the "
                                  "same as the --beam-width). Only applies "
                                  "the MFBA, FBA, and SBA BEAM algorithms."),
                            default=None)
    beam_group.add_argument('-iva', '--include-validity-array',
                            help=("Whether to include validity array in "
                                  "verbose log output (default=False)"),
                            action='store_true')
    ac_group = parser.add_argument_group(
        '🔬 ' + colorize('Advanced Analysis Options', BLUE))
    ac_group.add_argument('-ac', '--asymptotic-complete',
                          help=(
                              "🧪 Test if the groupoid is asymptotically "
                              "complete. Mathematical property analysis"),
                          action='store_true')
    ac_group.add_argument('-acp', '--ac-probabilities',
                          help=(
                              "📈 Probability values for asymptotic "
                              "analysis (required when using -ac)"),
                          nargs='+', type=restricted_float)
    ac_group.add_argument('-th', '--table-height',
                          help=(
                              "📏 Height of analysis table (default: 700). "
                              "Higher values give more detailed analysis"),
                          type=positive_integer, default=700)

    import sys
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    return parser.parse_args()



def main():
    args = parse_arguments()
    
    # Validate that either a target is specified OR -ac is used
    if not args.asymptotic_complete and not (args.target or 
                                            args.target_random or 
                                            args.target_ternary_descriminator):
        print("Error: A target must be specified (use -tdt, -trt, or -t) " +
              "unless using -ac for asymptotic completeness analysis.")
        sys.exit(1)
    
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

    # Run AC check and return table
    if args.asymptotic_complete is True:
        try:
            ac_table = grp.is_asymptotic_complete(args.ac_probabilities,
                                                  args.term_variables,
                                                  limit=args.table_height)
            log_ac_table(ac_table, LOG)
            return
        except ValueError as e:
            if "probability values" in str(e):
                print("Error: Asymptotic completeness analysis requires " +
                      "probability values. Use -acp to specify them.")
            else:
                print(f"Error: {e}")
            sys.exit(1)

    mtgm = args.male_term_generation_method

    # verbose is True by default, False when --quiet is specified
    verbose = not args.quiet
    # print_summary is True by default, False when --no-print-summary
    # is specified
    print_summary = not args.no_print_summary
    run_count = args.run_count

    # MFBA specific arguments
    include_validity_array = args.include_validity_array
    beam_width = args.beam_width
    sub_beam_width = args.sub_beam_width

    prob = args.probability
    algorithm = args.algorithm
    if algorithm == "DDA":
        if include_validity_array:
            raise ValueError("The --include-validity-array (-iva) option "
                             "only applies to the beam algorithms.")
        elif beam_width:
            raise ValueError("The --beam-width (-bw) option only applies to "
                             "the beam algorithms.")
    elif (algorithm == "MFBA" or algorithm == "FBA" or
          algorithm == "SBA"):
        if include_validity_array and not verbose:
            raise ValueError("Verbose output must be enabled for the "
                             "--include-validity-array (-iva) option "
                             "to apply. (Use --quiet to disable verbose\n"
                             "output.)")
        if beam_width is None:
            beam_width = 3
        if sub_beam_width is None:
            sub_beam_width = beam_width
    execution_results = []
    total_time = 0
    total_term_length = 0
    for i in range(run_count):
        if (algorithm == "MFBA" or algorithm == "FBA" or algorithm == "SBA"):
            beam = BeamEnumerationAlgorithm(
                                grp,
                                to,
                                algorithm,
                                male_term_generation_method=mtgm,
                                term_expansion_probability=prob,
                                beam_width=beam_width,
                                sub_beam_width=sub_beam_width)
            node, search_time = beam.run(
                verbose=verbose, print_summary=print_summary,
                include_validity_array=include_validity_array)
        elif algorithm == "DDA":
            dda = DeepDrillingAlgorithm(grp, to, m=args.m)
            node, search_time = \
                dda.run(verbose=verbose, print_summary=print_summary)

        # calculate execution times
        term_length = len(node.term)
        # calculate totals for final averages
        total_time += search_time
        total_term_length += term_length

        execution_results.append({
            "search_time": round(search_time, 2),
            "term_length": term_length
        })
        if not (print_summary or verbose):
            if run_count > 1:
                LOG.info(f"Run {i+1} of {run_count}")
            LOG.info(node.term if (i == 0 or run_count > 1)
                     else "\n" + node.term)
    if run_count > 1:
        log_execution_results_summary(execution_results, run_count,
                                      total_time, total_term_length, LOG)


if __name__ == '__main__':
    main()
