from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from functools import partial
from math import tan, pi
from typing import Generator, Generic, List, NamedTuple, Optional, Tuple, TypeVar, Union

from .constants import DELTA_SMALL

RGBAPixel = NamedTuple("RGBAPixel", [("r", int), ("g", int), ("b", int), ("alpha", int)])
CoefficientSet = NamedTuple(
    "CoefficientSet",
    [
        ("ambient", float),
        ("specular", float),
        ("diffuse", float),
        ("refract", float),
        ("reflect", float),
    ]
)

L = TypeVar("L")
S = TypeVar("S")
T = TypeVar("T")

class Scalar(float):
    def __init__(self, v: float) -> None:
        self.__value = v

    def __call__(self):
        return self.__value


PARAMETER_REGISTRY = {}
class Parameter:
    def __init__(self, start: float, stop: float = 0, steps: int = 1):
        self.__start = start
        self.__stop = stop
        self.__value = start
        self.__delta = (stop - start) / steps
        PARAMETER_REGISTRY[hash(self)] = self

    def rewind(self) -> None:
        self.__value = self.__start

    def __next__(self) -> float:
        if abs(self.__value - self.__stop) > DELTA_SMALL:
            self.__value += self.__delta
        return self.__value

    def __call__(self) -> float:
        return self.__value

    def __hash__(self) -> int:
        return hash((self.__start, self.__stop, self.__delta))

StaticParameter = lambda v: Parameter(v, v)

class Parameterized:
    parameters: List[str]
    def __next__(self):
        for p in self.parameters:
            if hasattr(self, p):
                parameter = getattr(self, p)
                if hasattr(parameter, "__next__"):
                    next(parameter)


class ThreeSpace(Generic[T]):
    def __init__(self, i: Optional[T] = 0, j: Optional[T] = 0, k: Optional[T] = 0, scalar: Optional[Scalar] = 0) -> None:
        if not isinstance(i, Parameter):
            i = StaticParameter(i)
        if not isinstance(j, Parameter):
            j = StaticParameter(j)
        if not isinstance(k, Parameter):
            k = StaticParameter(k)

        self.__i = i
        self.__j = j
        self.__k = k

        next(self)
        self.mag = self.dot(self)**.5
        self._normalized = None

    def __next__(self):
        self.i: T = next(self.__i)
        self.j: T = next(self.__j)
        self.k: T = next(self.__k)
        return self

    def __add__(self, other: Generic[T]) -> Generic[T]:
        return self.__class__(self.i + other.i, self.j + other.j, self.k + other.k)

    def __radd__(self, other: Generic[T]) -> Generic[T]:
        return self.__add__(other)

    def __iadd__(self, other: Generic[T]) -> Generic[T]:
        self.i += other.i
        self.j += other.j
        self.k += other.k
        return self

    def __sub__(self, other: Generic[T]) -> Generic[T]:
        return self.__class__(self.i - other.i, self.j - other.j, self.k - other.k)

    def __rsub__(self, other: Generic[T]) -> Generic[T]:
        return self.__sub__(other)

    def __isub__(self, other: Generic[T]) -> Generic[T]:
        self.i -= other.i
        self.j -= other.j
        self.k -= other.k
        return self

    def __mul__(self, s: float) -> Generic[T]:
        return self.__class__(self.i * s, self.j * s, self.k * s)

    def __rmul__(self, s: float) -> Generic[T]:
        return self.__mul__(s)

    def __imul__(self, s: float) -> Generic[T]:
        self.i *= s
        self.j *= s
        self.k *= s
        return self

    def __len__(self):
        return self.mag

    def __iter__(self):
        yield self.i
        yield self.j
        yield self.k

    def dot(self, other: Generic[T]) -> T:
        return (
            self.i * other.i + self.j * other.j + self.k * other.k
        )


class Point(ThreeSpace):
    def __repr__(self) -> str:
        return f"<Point i={self.i}, j={self.j}, k={self.k}>"

    def __str__(self) -> str:
        return repr(self)


class Color(ThreeSpace):
    def mix(self, other: ThreeSpace) -> ThreeSpace:
        return Color(self.i * other.i, self.j * other.j, self.k * other.k)

    @property
    def red(self) -> int:
        return self.i

    @property
    def green(self) -> int:
        return self.j

    @property
    def blue(self) -> int:
        return self.k

    @property
    def r(self) -> int:
        return self.i

    @property
    def g(self) -> int:
        return self.j

    @property
    def b(self) -> int:
        return self.k

    @property
    def normalized(self) -> Generic[T]:
        if self.mag > 0:
            return self * (1.0 / self.mag)
        return self

    def truncate(self):
        self.i = int(min(self.i, 255))
        self.j = int(min(self.j, 255))
        self.k = int(min(self.k, 255))

    def __repr__(self) -> str:
        return f"Color({self.i}, {self.j}, {self.k})"

    def __str__(self) -> str:
        return repr(self)


class Vector3(ThreeSpace):
    # def __init__(self, i: Optional[T] = 0, j: Optional[T] = 0, k: Optional[T] = 0, scalar: Optional[Scalar] = 0) -> None:
    #     print(self)
    #     super().__init__(i, j, k, scalar)

    def __repr__(self) -> str:
        return f"<Vector i={self.i}, j={self.j}, k={self.k}>"

    def __str__(self) -> str:
        return repr(self)

    def cross(self, other: Generic[T]) -> Generic[T]:
        return Vector3(
            i=(self.j * other.k - other.j * self.k),
            j=-(self.i * other.k - other.i * self.k),
            k=(self.i * other.j - other.i * self.j)
        )

    def scale(self, v: float) -> None:
        self.i *= v
        self.j *= v
        self.k *= v

    @property
    def size(self):
        return self.mag

    @property
    def normalized(self) -> Generic[T]:
        if self._normalized is None:
            if self.mag:
                self._normalized = Vector3(self.i / self.mag, self.j / self.mag, self.k / self.mag)
            else:
                self._normalized = self
        return self._normalized

Vector = Vector3

class LightType(IntEnum):
    AMBIENT = 0
    DIRECTIONAL = 1
    POINT = 2

class Light(Parameterized):
    parameters = ("direction", )

    def __init__(self, kind: LightType = LightType.AMBIENT, color: Color = None, direction: Vector3 = None) -> None:
        self.type = kind
        self.color = color
        self.direction = direction
        if self.type == LightType.DIRECTIONAL:
            self.direction = self.direction.normalized


class SceneObject(ABC):
    @abstractmethod
    def intersect(self, ray: Vector3) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def shade(self, scene: Generic[L, S]) -> RGBAPixel:
        raise NotImplementedError()


@dataclass
class Scene(Generic[L, S]):
    lights: List[Light]
    objects: List[SceneObject]
    background: Color = Color(0, 0, 0)

    def add(self, *items: Union[Light, SceneObject]) -> None:
        for item in items:
            if isinstance(item, Light):
                self.lights.append(item)
            elif isinstance(item, SceneObject):
                self.objects.append(item)
            else:
                raise TypeError(
                    "cannot add item that is neither an instance of a subclass of Light nor SceneObject"
                )

    def __next__(self):
        global PARAMETER_REGISTRY
        for p in PARAMETER_REGISTRY.values():
            next(p)


class Animation:
    def __init__(self, scene: Scene, frames: int = 1) -> None:
        self.scene = scene
        self.frames = frames

    def __iter__(self) -> "Animation":
        for i in range(self.frames):
            yield i, self.scene
            next(self.scene)

    def __enter__(self) -> "Animation":
        return self

    def __exit__(self, *args):
        return True


class AbstractSurface(ABC):
    @abstractmethod
    def shade(self, p: Point, v: Vector3, n: Vector3, scene: Scene) -> RGBAPixel:
        raise NotImplementedError()


OrthonormalBasis = NamedTuple("OrthonormalBasis", [("du", Vector3), ("dv", Vector3)])

class Viewport:
    def __init__(
        self,
        width: int = 128,
        height: int = 128,
        origin: Vector3 = None,
        up: Vector3 = None,
        focus: Vector3 = None,
        fov: float = 90.0
    ) -> None:
        self.width = width
        self.height = height
        if origin is None:
            origin = Vector3()
        if up is None:
            up = Vector3(0, 1, 0)

        if focus is None:
            focus = Vector3(0, 0, 1)

        self.origin = origin
        self.up = up
        self.focus = focus
        self.fov = width / (2 * (tan(0.5 * fov * pi / 180)))

        self.__look: Vector3 = None
        self.__basis: OrthonormalBasis = None
        self.__viewpoint: Point = None

    @property
    def look(self) -> Vector3:
        if self.__look is None:
            self.__look = (self.focus - self.origin).normalized
        return self.__look

    @property
    def basis(self) -> OrthonormalBasis:
        if self.__basis is None:
            du = self.look.cross(self.up).normalized
            dv = self.look.cross(du).normalized
            self.__basis = OrthonormalBasis(du=du, dv=dv)
        return self.__basis

    @property
    def viewpoint(self) -> Point:
        if self.__viewpoint is None:
            l = self.look
            w = self.width
            h = self.height
            fov = self.fov
            du, dv = self.basis
            self.__viewpoint = Point(
                i=(l.i * fov - 0.5 * (w * du.i + h * dv.i)),
                j=(l.j * fov - 0.5 * (w * du.j + h * dv.j)),
                k=(l.k * fov - 0.5 * (w * du.k + h * dv.k))
            )
        return self.__viewpoint

    def __iter__(self):
        yield self.width
        yield self.height
        du, dv = self.basis
        yield du
        yield dv
        yield self.viewpoint

if __name__ == "__main__":
    print(Vector3(1, 2, 3))