import string
import itertools


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


def combine_postfix(term1, term2):
    return "{}{}*".format(term1, term2)
