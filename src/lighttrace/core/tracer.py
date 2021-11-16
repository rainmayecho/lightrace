from PIL import Image, ImageDraw

from .ray import Ray
from .types import Color, Scene, Vector3, Viewport

from typing import List


class Tracer:
    def __init__(self, viewport: Viewport = None, scene: Scene = None, filename: str = "output") -> None:
        self.viewport = viewport or Viewport()
        self.scene = scene or Scene()
        self.image = Image.new("RGB", (self.viewport.width, self.viewport.height))
        self.draw = ImageDraw.Draw(self.image)
        self.__filename = f"{filename}.png"

    @staticmethod
    def print_progress(percent: float) -> None:
        percent = int(percent)
        if not int(percent) % 2 and percent > 0:
            bar = f'[{">" * (percent // 2)}>{" " * ((100 - percent) // 2)}]'
            print(bar, end="\r")

    @staticmethod
    def compute_ray_directions(i: int, j: int, du: Vector3, dv: Vector3, vp: Vector3, antialiasing: bool = True):
        d = []
        d.append(
            Vector3(
                i=(i * du.i + j * dv.i + vp.i),
                j=(i * du.j + j * dv.j + vp.j),
                k=(i * du.k + j * dv.k + vp.k),
            )
        )
        if antialiasing:
            i1, i2 = i - .5, i + .5
            j1, j2 = j - .5, j + .5
            for ix, jx in [(i1, j1), (i1, j2), (i2, j1), (i2, j2)]:
                d.append(
                    Vector3(
                        i=(ix * du.i + jx * dv.i + vp.i),
                        j=(ix * du.j + jx * dv.j + vp.j),
                        k=(ix * du.k + jx * dv.k + vp.k),
                    )
                )
        return d

    @staticmethod
    def average_colors(colors: List[Color]) -> Color:
        res = Color()
        for c in colors:
            res += c
        res = res * (1./len(colors))
        res.truncate()
        return res

    def render(self) -> None:
        width, height, du, dv, vp = self.viewport
        scene = self.scene
        for j in range(height):
            for i in range(width):
                colors = []
                for d in self.compute_ray_directions(i, j, du, dv, vp):
                    ray = Ray(self.viewport.origin, d)
                    if ray.trace(scene):
                        colors.append(Color(*ray.shade(scene)))
                    else:
                        colors.append(scene.background)
                self.draw.line([i,j, i, j], tuple(self.average_colors(colors)))
            percent = (float(j) / height) * 100
            self.print_progress(percent)
        self.image.save(self.__filename, "PNG")