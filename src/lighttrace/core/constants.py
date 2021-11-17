from pathlib import Path

INFINITY = float("inf")
HORIZON = 1e20
DELTA_SMALL = .000001

ROOT_DIRECTORY = Path(__file__).parents[3]
RESOURCE_DIRECTORY = f"{ROOT_DIRECTORY}/resources"
OUTPUT_DIRECTORY = f"{ROOT_DIRECTORY}/rendered"
