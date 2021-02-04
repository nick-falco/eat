from itertools import combinations


def subset_sums(array, target, length):
    return [c for c in combinations(array, length) if sum(c) == target]
