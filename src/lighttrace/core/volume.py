
from dataclasses import dataclass
from .constants import INFINITY
from .ray import Ray
from .types import BoundingVolumeHierarchy, Bounds, IntersectionResult, Point, Scene, SceneObject, Vector3
from .utils import step

from collections import defaultdict
from typing import Generator, List, NamedTuple, Set, TypeVar

T = TypeVar("T")
Volume = NamedTuple("Volume", [("i", Bounds), ("j", Bounds), ("k", Bounds)])
STEPS = [0.5, -0.5]

counter = 0

@dataclass
class Volume:
    i: Bounds
    j: Bounds
    k: Bounds

    def contains_point(self, p: Point) -> bool:
        return (
            self.i.min <= p.i <= self.i.max and
            self.j.min <= p.j <= self.j.max and
            self.k.min <= p.k <= self.k.max
        )

    def intersects_volume(self, v: Volume) -> bool:
        c0, c1 = centroid_of_bounds(self), centroid_of_bounds(v)
        d_sep = Vector3(*(c1 - c0)).size
        d0, d1 = self.halfdiagonal.size, v.halfdiagonal.size
        return (d0 + d1) >= d_sep


    @property
    def halfdiagonal(self):
        c = centroid_of_bounds(self)
        v = Point(i=self.i.max, j=self.j.max, k=self.k.max)
        return Vector3(*(v - c))


    @property
    def size(self):
        return (self.i.max - self.i.min) * (self.j.max - self.j.min) * (self.k.max - self.k.min)


    def __iter__(self):
        yield self.i
        yield self.j
        yield self.k
    

def centroid_of_bounds(bounds: List[Bounds]) -> Point:
    return Point(*[(b.min + b.max) / 2 for b in bounds])


def get_bounds_extremes(bounds: List[List[Bounds]]) -> Volume:
    minx, maxx = INFINITY, -INFINITY
    miny, maxy = INFINITY, -INFINITY
    minz, maxz = INFINITY, -INFINITY

    for bx, by, bz in bounds:
        minx = min(bx.min, minx)
        miny = min(by.min, miny)
        minz = min(bz.min, minz)
        maxx = max(bx.max, maxx)
        maxy = max(by.max, maxy)
        maxz = max(bz.max, maxz)

    
    return [
        Bounds(min=minx, max=maxx),
        Bounds(min=miny, max=maxy),
        Bounds(min=minz, max=maxz),
    ]


def get_bounding_cube(bounds: List[List[Bounds]]) -> Volume:
    _min, _max = INFINITY, -INFINITY
    for bx, by, bz in bounds:
        _min = min([bx.min, by.min, bz.min, _min])
        _max = max([bx.max, by.max, bz.max, _max])

    return Volume(
        i=Bounds(min=_min, max=_max),
        j=Bounds(min=_min, max=_max),
        k=Bounds(min=_min, max=_max),
    )

def centroid_of_centroids(centroids: List[Point]) -> Point:
    n = len(centroids)
    p = Point()
    for c in centroids:
        p += c
    return p * (1 / n)


def iteroctants(p: Point, d: T) -> Generator[Point, None, None]:
    for k in STEPS:
        for j in STEPS:
            for i in STEPS:
                yield Point(
                    i=p.i + (i * d / 2),
                    j=p.j + (j * d / 2),
                    k=p.k + (k * d / 2),
                )

class OctreeNode:
    INDEX_LOOKUP = {
        (True, True, True): 0,
        (False, True, True): 1,
        (True, False, True): 2,
        (False, False, True): 3,
        (True, True, False): 4,
        (False, True, False): 5,
        (True, False, False): 6,
        (False, False, False): 7
    }

    def __init__(self, volume: Volume, objects: List[SceneObject] = None) -> None:
        self.objects = objects or []
        self.volume = volume
        self.octants = []
        self.split()

    def construct_octants(self) -> List[Volume]:
        c = centroid_of_bounds(self.volume)
        d = self.volume.i.max - self.volume.i.min
        hd = d / 2 / 2
        return [
            Volume(
                i=Bounds(min=p.i - hd, max=p.i + hd),
                j=Bounds(min=p.j - hd, max=p.j + hd),
                k=Bounds(min=p.k - hd, max=p.k + hd),
            )
            for p in iteroctants(c, d)
        ]

    def intersect(self, ray: Ray) -> IntersectionResult:
        v = self.volume

        pi, pj, pk = ray.anchor
        ri, rj, rk = ray.direction
        ti_0 = (v.i.min - pi) * ri
        ti_1 = (v.i.max - pi) * ri

        tmin, tmax = max(ti_0, ti_1), max(ti_0, ti_1)

        tj_0 = (v.j.min - pj) * rj
        tj_1 = (v.j.max - pj) * rj

        tmin, tmax = max(tmin, min(tj_0, tj_1)), max(tmax, max(tj_0, tj_1))

        tk_0 = (v.k.min - pk) * rk
        tk_1 = (v.k.max - pk) * rk

        tmin, tmax = max(tmin, min(tk_0, tk_1)), max(tmax, max(tk_0, tk_1))

        return IntersectionResult(tmax >= max(0, tmin), tmin=tmin, tmax=tmax, r=ray)

    def split(self) -> None:
        if len(self.objects) > 1 and self.volume.size > 10:
            octants = self.construct_octants()
            octant_members = defaultdict(list)
            for o in self.objects:
                for i, octant in enumerate(octants):
                    if octant.intersects_volume(Volume(*o.bounds)):
                        octant_members[i].append(o)
            for i, octant in enumerate(octants):
                self.octants.append(OctreeNode(octant, objects=octant_members[i]))
        else:
            global counter
            counter += 1
            print(f"Constructing octree: {counter}      ", end="\r")


    @property
    def size(self) -> int:
        if not self.octants:
            return 1
        return sum(n.size for n in self.octants)


    @property
    def centroid(self) -> Point:
        return centroid_of_bounds(self.volume)

    @classmethod
    def get_key(cls, p: Point, c: Point) -> int:
        return (p.i > c.i, p.j > c.j, p.k > c.k)

    def find(self, p: Point) -> "OctreeNode":
        if not self.octants:
            return self
        idx = self.INDEX_LOOKUP[self.get_key(p, self.centroid)]
        return self.octants[idx].find(p)



class Octree(BoundingVolumeHierarchy):
    def __init__(self, objects: List[SceneObject]) -> None:
        global counter
        print(f"Constructing octree: {counter}     ", end="\r")
        self.__root = OctreeNode(get_bounding_cube([o.bounds for o in objects]), objects=objects)
        print("\ndone!")
        counter = 0

    @property
    def size(self) -> int:
        return self.__root.size

    @property
    def bounds(self) -> Volume:
        return self.__root.volume

    def intersect(self, ray: Ray) -> IntersectionResult:
        return self.__root.intersect(ray)

    def find(self, point: Point) -> OctreeNode:
        return self.__root.find(point)
    
    def get_candidates(self, ray: Ray) -> Set[SceneObject]:
        ir = self.intersect(ray)
        c = set()
        for t in step(ir.tmin, ir.tmax, (ir.tmax - ir.tmin) / 100):
            p = ray.anchor + (ray.direction * t)
            c = {*c, *self.find(p).objects}
        return c   


