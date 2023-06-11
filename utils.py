from itertools import zip_longest
from typing import Literal


def grouper(iterable, n, *, incomplete=Literal['fill', 'strict', 'ignore'], fillvalue=None):
    """
    Collect data into non-overlapping fixed-length chunks or blocks
        grouper('ABCDEFG', 3, fillvalue='x') --> (A,B,C) (D,E,F) (G,x,x)
        grouper('ABCDEFG', 3, incomplete='strict') --> (A,B,C) (D,E,F) ValueError
        grouper('ABCDEFG', 3, incomplete='ignore') --> (A,B,C) (D,E,F)
    """
    args = [iter(iterable)] * n
    if incomplete == 'fill':
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == 'strict':
        return zip(*args, strict=True)
    if incomplete == 'ignore':
        return zip(*args)
    else:
        raise ValueError('Expected fill, strict, or ignore')


def chunker(size, seq):
    """
    chunker(3, "ABCDEFG") -> "ABC" "DEF" "G"
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def reverse_chunker(size, seq):
    """
    reverse_chunker(3, "ABCDEFG") -> "EFG" "BCD" "A"
    reverse_chunker(4, "ABCDEFG") -> "DEFG" "ABC"
    """
    n = len(seq)
    return (seq[n - pos - size: n - pos] for pos in range(0, n, size))


def string_comp(s1: str, s2: str):
    for i, (c1, c2) in enumerate(zip_longest(s1, s2)):
        if c1 != c2:
            print(f"diff in index {i}\n1:{s1[i - 30:i + 30]}\n2:{s2[i - 30:i + 8]}")
            return
