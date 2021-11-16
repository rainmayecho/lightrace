from typing import List, TypeVar

T = TypeVar("T")

def flatten(l: List[List[T]]) -> List[T]:
    return [item for sublist in l for item in l]