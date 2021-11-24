from .constants import INFINITY
from .ray import Ray
from .types import AbstractSurface, Bounds, BoundsType, Parameterized, Point, RGBAPixel, Scene, SceneObject, Vector3
from .volume import Volume

from typing import List, Tuple

class Plane(SceneObject, Parameterized):
    _type = BoundsType.INFINITE
    parameters = (
        "center",
        "normal",
    )
    def __init__(self, center: Point, normal: Vector3, surface: AbstractSurface) -> None:
        self.__center = center
        self.normal = normal.normalized
        self.surface = surface

    def intersect(self, ray: Ray) -> bool:
        cos = ray.direction.dot(self.normal)
        if not cos:
            return False

        t = (self.center - ray.anchor).dot(self.normal) / cos

        if t > ray.t or t < 0:
            return False

        if t > 0:
            ray.t = t
            ray.object = self
            return True
        return False

    def shade(self, ray: Ray, scene: Scene) -> RGBAPixel:
        p = ray.anchor + (ray.direction * ray.t)
        v = -1 * ray.direction
        return self.surface.shade(p, v.normalized, self.normal, scene)

    @property
    def center(self) -> Point:
        return self.__center

    @property
    def bounds(self) -> Volume:
        bounds = [Bounds(-INFINITY, INFINITY) for _ in range(3)]
        for idx, normal_component in enumerate(self.normal):
            if not normal_component:
                v = self.normal[idx]
                bounds[idx] = Bounds(v, v)
        return Volume(*bounds)



class Sphere(SceneObject, Parameterized):
    _type = BoundsType.FINITE
    attrs = (
        "radius",
        "center",
    )
    def __init__(self, radius: float = 1, center: Point = None, surface: AbstractSurface = None) -> None:
        self.radius = radius
        self.__center = center
        self.surface = surface

    def intersect(self, ray: Ray) -> bool:
        r = self.radius
        center_to_anchor = Vector3(*(self.center - ray.anchor))
        v = center_to_anchor.dot(ray.direction)
        d = center_to_anchor.size

        if (v - r) > ray.t:
            return False

        t = (r * r) + (v * v) - (d * d)
        if t < 0:
            return False

        t = (v - t**.5)
        if t > ray.t:
            return False

        if t < 0:
            return False

        ray.t = t
        ray.object = self
        return True

    def shade(self, ray: Ray, scene: Scene) -> RGBAPixel:
        p = ray.anchor + (ray.direction * ray.t)
        v = ray.direction.normalized * -1
        n = (p - self.center).normalized
        return self.surface.shade(p, v, n, scene)

    @property
    def center(self) -> Point:
        return self.__center


    @property
    def bounds(self) -> Tuple[Bounds]:
        c = self.center
        r = self.radius
        return Volume(
            i=Bounds(min=c.i - r, max=c.i + r),
            j=Bounds(min=c.j - r, max=c.j + r),
            k=Bounds(min=c.k - r, max=c.k + r),
        )


class Polygon(SceneObject):
    _type = BoundsType.FINITE

    attrs = (
        "center",
        "normal",
    )

    def __init__(self, vertices: List[Vector3], surface: AbstractSurface) -> None:
        self.__vertices = vertices
        self.surface = surface
        self.__normal = None

    def __iter__(self):
        return iter(self.__vertices)

    def __next__(self):
        for v in self.__vertices:
            next(v)

    @property
    def normal(self):
        if self.__normal is None:
            a, b, c = self.__vertices[:3]
            v1 = b - a
            v2 = c - a
            self.__normal = v1.cross(v2).normalized
        return self.__normal

    @property
    def vertices(self):
        return self.__vertices

    def intersect(self, ray: Ray) -> bool:
        normal = self.normal
        cos = ray.direction.dot(normal)
        if not cos:
            return False

        t = -(ray.anchor - self.vertices[0]).dot(normal) / cos

        if t >= ray.t:
            return False

        if t < 0:
            return False

        r = ray.direction.normalized * t
        vertices = self.vertices
        n = len(vertices)
        x = ray.anchor + r
        for i in range(n):
            a = vertices[i % n]
            b = vertices[(i + 1) % n]
            ab = b - a
            ax = x - a

            if (ab.cross(ax).dot(normal) >= 0):
                continue
            else:
                return False
        ray.t = t
        ray.object = self
        return True

    def shade(self, ray: Ray, scene: Scene) -> RGBAPixel:
        p = ray.anchor + ray.direction * ray.t
        v = ray.direction.normalized * -1
        return self.surface.shade(p, v, self.normal, scene)

    @property
    def center(self) -> Point:
        p = Point()
        for v in self.vertices:
            p += v
        return (p * (1 / len(self.vertices)))

    @property
    def bounds(self) -> Tuple[Bounds]:
        min_i, max_i = INFINITY, -INFINITY
        min_j, max_j = INFINITY, -INFINITY
        min_k, max_k = INFINITY, -INFINITY
        for vertex in self.vertices:
            min_i = min(vertex.i, min_i)
            min_j = min(vertex.j, min_j)
            min_k = min(vertex.k, min_k)

            max_i = max(vertex.i, max_i)
            max_j = max(vertex.j, max_j)
            max_k = max(vertex.k, max_k)
        return Volume(
            i=Bounds(min_i, max_i),
            j=Bounds(min_j, max_j),
            k=Bounds(min_k, max_k),
        )
