from .constants import DELTA_SMALL
from .ray import Ray
from .types import AbstractSurface, CoefficientSet, Color, LightType, Point, RGBAPixel, Scene, Vector3

class Surface(AbstractSurface):
    def __init__(self, color: Color = None, coefficients: CoefficientSet = None) -> None:
        self.color = color
        self.coefficients = coefficients

    def shade(self, p: Point, v: Vector3, n: Vector3, scene: Scene) -> RGBAPixel:
        color = Color()
        alpha = 1.0
        k = self.coefficients
        for light in scene.lights:
            if light.type == LightType.AMBIENT:
                color += self.color.mix(light.color * k.ambient)
            else:
                intensity = 1.0
                dsqr = float("inf")
                if light.type == LightType.POINT:
                    l = (light.direction - p)
                    dsqr = l.dot(l)
                    intensity = light.color.dot(light.color) / dsqr
                    l = l.normalized
                else:
                    l = (light.direction * -1).normalized

                shadowpoint = (p + l * DELTA_SMALL)
                shadowray = Ray(shadowpoint, l)
                shadowray.t = dsqr**.5

                if (shadowray.trace(scene)):
                    continue

                cos = n.dot(l)
                if cos > 0:
                    diffuse = k.diffuse * cos
                    color += light.color * diffuse * intensity

                if k.specular > 0:
                    u = (2 * cos * n) - l
                    specular = v.dot(u)
                    if specular > 0:
                        specular = k.specular * abs(specular)**2.2
                        color += light.color * specular * intensity
        if k.reflect > 0:
            t = v.dot(n)
            if t > 0:
                t *= 2
                reflect = (n * t) - v
                shadowpos = p + (reflect * DELTA_SMALL)
                reflected_ray = Ray(shadowpos, reflect)

                rcolor = scene.background
                if reflected_ray.trace(scene):
                    rcolor = Color(*reflected_ray.shade(scene))
                color += k.reflect * rcolor

        color.truncate()
        return RGBAPixel(*color, alpha)



