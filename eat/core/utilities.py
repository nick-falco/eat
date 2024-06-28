import string
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


def get_all_one_and_two_variable_terms(term_variables):
    combinations = []
    for i in range(len(term_variables)+1):
        for combination in \
                itertools.product(term_variables, repeat=i):
            combination = "".join(combination)
            if len(combination) == 1:
                combinations.append(combination)
            elif len(combination) == 2:
                combinations.append("{}*".format(combination))
    return combinations


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
    history = ["Level, Term, Term Length, Time Since Parent Creation, "
               "Time Since Start, Fitness"]
    while node is not None:
        node = deepcopy(node)
        history.append(
            f"{node.level}, "
            f"{node.term}, "
            f"{len(node.term)}, "
            f"{round(node.time_since_parent_creation(), 2)} sec, "
            f"{round(node.elapsed_time(algorithm_start_time), 2)} sec, "
            f"{Decimal(node.fitness):.2e}")
        node = deepcopy(node.parent_node)
    return history


def print_search_summary(node, last_node, term_operation, groupoid,
                         algorithm_start_time, algorithm_end_time,
                         show_creation_history=False):
    print("--------")
    print("Summary")
    print("--------")
    print("Groupoid used:")
    print(groupoid)
    print("Computed term:")
    print(node.term)
    print("Term length  = {}".format(len(node.term)))
    print("Search time  = {} sec".format(
        round(algorithm_end_time - algorithm_start_time, 2)))
    print("Term array   = {}".format(
          condensed_array(term_operation.compute(node.term), groupoid.size)))
    print("Target array = {}".format(
          condensed_array(term_operation.target, groupoid.size)))
    if show_creation_history:
        print("-----------------")
        print("Creation History")
        print("-----------------")
        for info in get_creation_history(last_node, algorithm_start_time):
            print(info)
