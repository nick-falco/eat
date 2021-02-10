import string
from itertools import combinations


def subset_sums(array, target, length):
    return [c for c in combinations(array, length) if sum(c) == target]


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


def combine_postfix(term1, term2):
    return f"{term1}{term2}*"
