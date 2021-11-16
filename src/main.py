from lighttrace.core.colors import Colors
from lighttrace.core.constants import HORIZON
from lighttrace.core.geometry import Plane, Sphere
from lighttrace.core.mesh import Mesh
from lighttrace.core.surface import Surface
from lighttrace.core.tracer import Tracer
from lighttrace.core.types import CoefficientSet, Color, Light, LightType, Point, Scene, Vector3, Viewport
from lighttrace.core.utils import flatten

from functools import reduce
from operator import add

def run():
    scene = Scene([], [], background=Colors.GREY_4)
    coefficients_1 = CoefficientSet(.005, .7, .0001, .1, .09)
    coefficients_2 = CoefficientSet(.005, .88, .0001, .1, .09)
    surface_1 = Surface(Colors.WHITE, coefficients_1)
    surface_2 = Surface(Colors.GREY_6, coefficients_2)
    mesh = Mesh(surface=surface_2, offset=Vector3(0, 0, 10))
    mesh.load("cornellbox.obj")
    scene.add(
        Light(LightType.AMBIENT, Colors.GREY_5),
        # Light(LightType.POINT, Colors.BLUE, Vector3(0, 20, -4)),
        # Light(LightType.POINT, Colors.WHITE, Vector3(0, 50, 10)),
        Light(LightType.DIRECTIONAL, Colors.WHITE, Vector3(0, 1, -1)),
        # Plane(Point(0, -400, 0), Vector3(0, 1, 0), surface=surface_1),
        # Plane(Point(0, 0, HORIZON / 1000), Vector3(0, 0, -1), surface=surface_1),
        # Sphere(radius=300, center=Point(0, 0, 100), surface=surface_2),
        # Sphere(radius=25, center=Point(350, 50, 100), surface=surface_1),
        # # Sphere(radius=5, center=Point(0, 25, 10), surface=surface_1),
        # Sphere(radius=7, center=Point(10, 10, 10), surface=surface_1),
        *mesh.generate_polygons()
    )

    width = int(input("Width: "))
    height = int(input("Height: "))

    viewport = Viewport(
        width=width,
        height=height,
        origin=Vector3(0, -1, 5),
        up=Vector3(0, 1, 0),
        focus=Vector3(),
        fov=120.0,
    )
    tracer = Tracer(viewport=viewport, scene=scene, filename=f"box{width}x{height}")
    tracer.render()

if __name__ == "__main__":
    run()