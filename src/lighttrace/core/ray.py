from .constants import HORIZON
from .types import Point, RGBAPixel, Scene, SceneObject, Vector3

class Ray:
    def __init__(self, p: Point, v: Vector3) -> None:
        self.anchor = Vector3(*p)
        self.direction = v.normalized
        self.t = HORIZON
        self.object = None

    def trace(self, scene: Scene) -> RGBAPixel:
        for obj in scene.objects:
            if obj.intersect(self):
                continue
        return self.object is not None

    def shade(self, scene: Scene) -> RGBAPixel:
        return self.object.shade(self, scene)