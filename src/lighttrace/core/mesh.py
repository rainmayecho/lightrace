from .geometry import Polygon
from .types import AbstractSurface, Vector3


from typing import Generator, List
import re

VERTEX_REGEX = re.compile(r"")
FACE_REGEX = re.compile(r"")

class Mesh:
    def __init__(self, surface: AbstractSurface, offset: Vector3 = None) -> None:
        self.__vertices = []
        self.__faces = []
        self.__offset = Vector3(0, 0, 0)
        self.__locus = Vector3(0, 0, 0)
        self.surface = surface

    def load(self, filename: str) -> None:
        with open(filename, "r") as f:
            for line in f:
                tokens = line.split(" ")
                if tokens[0] == 'v':
                    self.__vertices.append(Vector3(*[float(c) for c in tokens[1:]]))
                elif tokens[0] == 'f':
                    self.__faces.append(
                        [[int(i) if len(i) else 0 for i in c.split('/')] for c in tokens[1:]]
                    )

    def generate_polygons(self) -> Generator[Polygon, None, None]:
        verts = self.__vertices
        for face in self.__faces:
            yield Polygon(
                vertices=[verts[idx[0] - 1] - self.__locus for idx in face],
                surface=self.surface
            )


