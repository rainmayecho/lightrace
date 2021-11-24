from cProfile import Profile
from typing import Generator, List, TypeVar
from copy import deepcopy

T = TypeVar("T")

def flatten(l: List[List[T]]) -> List[T]:
    return [item for sublist in l for item in l]


def step(t0: T, t1: T, step: T = 1.0) -> Generator[T, None, None]:
    t = deepcopy(t0)
    while t < t1:
        yield t
        t += step

class SectionProfiler:
    def __init__(self, sort_by="cumulative"):
        self.__sort_by = sort_by
        self.profiler = Profile()

    def __enter__(self):
        self.profiler.enable()
        return self

    def __exit__(self, *args):
        self.profiler.print_stats(sort=self.__sort_by)