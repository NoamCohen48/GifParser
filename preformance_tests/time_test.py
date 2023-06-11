import time
import typing
from typing import List, Callable

import attrs
from attrs import define, field

from utils import chunker


@define
class Result:
    name: str = field(eq=False)
    runs: int = field(eq=False)
    total_time: float = field(eq=False)
    out: typing.Any = field(eq=True, repr=False)
    average: float = field(init=False, eq=False, on_setattr=attrs.setters.NO_OP)

    def __attrs_post_init__(self):
        self.average = self.total_time / self.runs


def time_function(n_runs: int, function: Callable, args, kwargs) -> Result:
    start = time.perf_counter()
    for i in range(n_runs):
        out = function(*args, **kwargs)
    end = time.perf_counter()
    return Result(function.__name__, n_runs, end - start, out)


def test_functions(n_runs: int, functions: List[Callable], *args, **kwargs):
    """
    the first function is treated as the truth, and every other function is
    """
    if not functions:
        return

    base = time_function(n_runs, functions[0], args, kwargs)
    print(base)

    for func in functions[1:]:
        result = time_function(n_runs, func, args, kwargs)
        print(result)
        if base != result:
            print(f"{result.name} not the same as base function")


def flip_data(compress_data):
    fliped_data = ''
    length = len(compress_data) / 8
    for i in range(int(length)):
        fliped_data += compress_data[-8:]
        compress_data = compress_data[:-8]

    bytes_object = fliped_data.encode("utf-8")

    return bytes_object


def flip_data2(compress_data):
    flipped_data = ''
    chunked = [x for x in chunker(8, compress_data)]
    for chunk in reversed(chunked):
        flipped_data += chunk

    bytes_object = flipped_data.encode("utf-8")

    return bytes_object


def flip_data3(compress_data):
    chunked = [x for x in chunker(8, compress_data)]
    fliped_data = ''.join(reversed(chunked))

    bytes_object = fliped_data.encode("utf-8")

    return bytes_object


def flip_data4(compress_data):
    fliped_data = ''.join(compress_data[i:i + 8][::-1] for i in range(0, len(compress_data), 8))
    bytes_object = fliped_data.encode("utf-8")
    return bytes_object


if __name__ == '__main__':
    s = "12345678" * 1000
    n = 100
    test_functions(n, [flip_data, flip_data2, flip_data3, flip_data4], s)