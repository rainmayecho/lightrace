from pathlib import Path
from math import pi


INFINITY = float("inf")
HORIZON = 1e10
DELTA_SMALL = .0001
TWO_PI = 2 * pi


ROOT_DIRECTORY = Path(__file__).parents[3]
RESOURCE_DIRECTORY = f"{ROOT_DIRECTORY}/resources"
OUTPUT_DIRECTORY = f"{ROOT_DIRECTORY}/rendered"
