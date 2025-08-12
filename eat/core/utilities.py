import logging
import string
import sys
import itertools
from copy import deepcopy
from decimal import Decimal


def subset_sums(array, target, length):
    return [c for c in
            itertools.combinations(array, length) if sum(c) == target]


def get_term_variables(size):
    """
    Returns a list of term variables matching the specified size.
    Term elments are selected from [a-z].

    :type size: int
    :param size: number of possible term elements

    :rtype: list
    :return: list of term elements
    """
    if size < 1:
        raise ValueError("Row size must be a valid positive integer.")
    return list(string.ascii_lowercase)[0:size]


def postfix_to_infix(exp):

    def is_operand(x):
        return ((x >= 'a' and x <= 'z') or
                (x >= 'A' and x <= 'Z'))

    stack = []
    for j in range(len(exp)):
        if is_operand(exp[j]):
            stack.append(exp[j])
        else:
            operator1 = stack.pop()
            operator2 = stack.pop()
            stack.append("(" + operator2 + exp[j] + operator1 + ")")
    return stack.pop()


def split_male_term(term):
    count = 0
    term_len = len(term)
    for i in range(term_len-1, 0, -1):
        c = term[i]
        if c == "*":
            count += 1
        else:
            count -= 1
        if count == 0:
            return term[0:i], term[i:term_len-1]


def combine_postfix(term1, term2):
    return term1 + term2 + "*"


def condensed_array(array, groupoid_size):
    return [v if len(v) != groupoid_size else "~" for v in array]


def get_creation_history(node, algorithm_start_time):
    history = ["Level, Term, Term Length, Time Since Previous (sec), "
               "Time Since Start (sec), Fitness"]
    while node is not None:
        node = deepcopy(node)
        history.append(
            f"{node.level}, "
            f"{node.term}, "
            f"{len(node.term)}, "
            f"{round(node.time_since_parent_creation(), 2)}, "
            f"{round(node.elapsed_time(algorithm_start_time), 2)}, "
            f"{Decimal(node.fitness):.2e}")
        node = deepcopy(node.parent_node)
    return history


def get_logger(name):
    """
    Setup logger for DDA and Beam Algorithm
    """
    log = logging.getLogger(name)
    if not log.hasHandlers():
        log.setLevel(logging.INFO)  # Set the default logging level
        # Configure logging to mimic print function
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        # Set formatter to mimic print
        formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(formatter)
        log.addHandler(console_handler)
    return log


def log_search_summary(node, last_node, term_operation, groupoid,
                       algorithm_start_time, algorithm_end_time,
                       log, show_creation_history=False):
    log.info("--------")
    log.info("Summary")
    log.info("--------")
    log.info("Groupoid used:")
    log.info(groupoid)
    log.info("Computed term:")
    log.info(node.term)
    log.info("Term length  = {}".format(len(node.term)))
    log.info("Search time  = {} sec".format(
        round(algorithm_end_time - algorithm_start_time, 3)))
    log.info("Term array   = {}".format(
          condensed_array(term_operation.compute(node.term), groupoid.size)))
    log.info("Target array = {}".format(
          condensed_array(term_operation.target, groupoid.size)))
    if show_creation_history:
        log.info("-----------------")
        log.info("Creation History")
        log.info("-----------------")
        for info in get_creation_history(last_node, algorithm_start_time):
            log.info(info)


def log_execution_results_summary(execution_results, run_count,
                                  total_time, total_term_length, log):
    avg_time = round(total_time / run_count, 2)
    avg_term_length = round(total_term_length / run_count, 2)
    log.info("-----------------------------")
    log.info(f"Execution results for {run_count} runs")
    log.info("-----------------------------")
    log.info("Run, Search Time (sec), Term Length")
    for i, result in enumerate(execution_results):
        log.info(f"{i+1}, {result['search_time']}, "
                 f"{result['term_length']}")
    log.info(f"Average search time: {avg_time} sec")
    log.info(f"Average term length: {int(avg_term_length)}")


def log_ac_table(table_output, log):
    # Calculate the maximum width for each column
    col_widths = [max(len(f"{v:.6f}") for v in col)
                  for col in zip(*table_output)]
    header_widths = [max(len(f"B{i}"), col_width)
                     for i, col_width in enumerate(col_widths)]

    # Calculate the width needed for the row index column
    index_width = max(len(str(len(table_output))), len("H"))

    # Log the header
    header = "H".ljust(index_width) + " " + " ".join(
        [f"B{i}".ljust(header_width)
         for i, header_width in enumerate(header_widths)])
    log.info(header)

    # Log each row
    for i, row in enumerate(table_output):
        row_str = f"{i+1}".ljust(index_width) + " " + " ".join([
            f"{v:.6f}".ljust(header_width)
            for v, header_width in zip(row, header_widths)])
        log.info(row_str)
