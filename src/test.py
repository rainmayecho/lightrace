from lighttrace.core.types import Point, Vector3
from lighttrace.core.geometry import Sphere
from lighttrace.core.ray import Ray
from lighttrace.core.volume import Octree

from pprint import pprint
from random import randint


def random_point(n = 10) -> Point:
    return Point(randint(-n, n), randint(-n, n), randint(-n, n))

def test_octree() -> None:
    spheres = [Sphere(radius=randint(1, 3), center=random_point()) for _ in range(30)]
    # spheres = [Sphere(radius=5, center=Point(0, 0, 10))]
    octree = Octree(spheres)
    pprint(spheres)
    print(octree.bounds)
    ray = Ray(Point(0, 0, -50), Vector3(0, 0, 1))
    # ir = octree.intersect(Ray(Point(0, 0, -50), Vector3(0, 0, 1)))
    print(octree.get_candidates(ray))



if __name__ == "__main__":
    test_octree()