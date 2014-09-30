# Make all possible combinations using cartesian product
import itertools


def permutation_with_replacement(n, seq):
    """
    Returns a list of all possible combinations of elements in seq, with length n.
    (Like permutation with replacement)
    """
    options = list()
    for p in itertools.product(seq, repeat=n):
        options.append(p)
    return options
