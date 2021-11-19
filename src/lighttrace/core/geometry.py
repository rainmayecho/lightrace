from .ray import Ray
from .types import AbstractSurface, Parameter, Parameterized, Point, RGBAPixel, Scene, SceneObject, Vector3

from typing import List

class Plane(SceneObject, Parameterized):
    parameters = (
        "center",
        "normal",
    )
    def __init__(self, center: Point, normal: Vector3, surface: AbstractSurface) -> None:
        self.center = center
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

class Sphere(SceneObject, Parameterized):
    parameters = (
        "center",
    )
    def __init__(self, radius: float = 1, center: Point = None, surface: AbstractSurface = None) -> None:
        self.radius = radius
        self.center = center
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


class Polygon(SceneObject):
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

