from .constants import TWO_PI
from .types import Parameter

from functools import partial
from math import cos, sin
from typing import Callable, TypeVar

T = TypeVar("T")

class ParamterizedFunction(Parameter):
    def __init__(self, f: Callable[[], Parameter]) -> None:
        self.__function = f

    def __call__(self, *args, **kwargs):
        return self.__function(*args, **kwargs)

    def __add__(self, f: Callable[[], Parameter]):
        def __composition(*args, **kwargs):
            return self.__function(*args, **kwargs) + f(*args, **kwargs)
        return ParamterizedFunction(f=__composition)

def parameter(a: T, b: T, steps: int = 1, function = None) -> T:
    return Parameter(a, b, steps=steps, function=function)

def sine(r: T, steps: int = 1) -> Callable[[], Parameter]:
    return partial(parameter, 0, TWO_PI, steps=steps, function=lambda t: r * sin(t))

def cosine(r: T, steps: int = 1) -> Callable[[], Parameter]:
    return partial(parameter, 0, TWO_PI, steps=steps, function=lambda t: r * cos(t))

def linear(steps: int = 1) -> Callable[[T, T], Parameter]:
    return partial(parameter, steps=steps)

def quadratic(steps: int = 1) -> Callable[[T, T], Parameter]:
    return partial(parameter, steps=steps, function=lambda t: t * t)