"""
Support code used to generate code suffixes in ``codes`` module.

Not for runtime use.

"""
import itertools



def dissimilar_strings(num, lengths, alphabet,
                       min_distance=2, filter_func=None):
    """
    Return up to ``num`` dissimilar strings of ``lengths`` from ``alphabet``.

    "Dissimilar" is defined in this case by minimum Damerau-Levenshtein
    distance, which can be provided as the ``min_distance`` argument (defaults
    to 2).

    ``lengths`` is an iterable of allowable lengths.

    If ``num`` dissimilar strings cannot be found, return all that were found.

    If a ``filter_func`` callable is given, it should accept a single string
    and return False for strings which should not be considered.

    This function is extremely inefficient - O(num^2 * max(lengths)^2) in
    time. It is intended only for generating additions to the static lookup
    list; it should never be used at runtime.

    """
    ret = set()
    for length in lengths:
        for s in (''.join(p) for p in itertools.permutations(alphabet, length)):
            if filter_func and not filter_func(s):
                continue
            if all(dameraulevenshtein(s, tmp) >= min_distance for tmp in ret):
                ret.add(s)
            if len(ret) >= num:
                return ret
    return ret



# From http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
def dameraulevenshtein(seq1, seq2):
    """Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.

    >>> dameraulevenshtein('ba', 'abc')
    2
    >>> dameraulevenshtein('fee', 'deed')
    2

    It works with arbitrary sequences too:
    >>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
    2
    """
    # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
    # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
    # However, only the current and two previous rows are needed at once,
    # so we only store those.
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1]
