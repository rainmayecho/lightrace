from lighttrace.core.colors import Colors
from lighttrace.core.constants import HORIZON
from lighttrace.core.geometry import Plane, Sphere
from lighttrace.core.mesh import Mesh
from lighttrace.core.surface import Surface
from lighttrace.core.tracer import Tracer
from lighttrace.core.types import CoefficientSet, Color, Light, LightType, Point, Scene, Vector3, Viewport

from datetime import date, datetime


def run(filename: str, animate: bool = False) -> None:
    scene = Scene([], [], background=Colors.GREY_4)
    coefficients_1 = CoefficientSet(.005, .7, .0001, .1, .09)
    coefficients_2 = CoefficientSet(.005, .88, .0001, .1, .09)
    surface_1 = Surface(Colors.MATTE_RED, coefficients_1)
    surface_2 = Surface(Colors.MATTE_YELLOW, coefficients_2)
    mesh = Mesh(surface=surface_2)
    mesh.load(filename)
    scene.add(
        Light(LightType.AMBIENT, Colors.GREY_5),
        Light(LightType.POINT, Colors.MATTE_RED, Vector3(0, -200, 0)),
        Light(LightType.POINT, Colors.WHITE, Vector3(0, 100, 300)),
        Light(LightType.DIRECTIONAL, Colors.WHITE, Vector3(0, -1, 0)),
        Plane(Point(0, -400, 0), Vector3(0, 1, 0), surface=surface_1),
        Plane(Point(0, 0, HORIZON / 100000), Vector3(0, 0, -1), surface=surface_1),
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
        origin=Vector3(0, 10, -500),
        up=Vector3(0, 1, 0),
        focus=Vector3(),
        fov=120.0,
    )
    tracer = Tracer(viewport=viewport, scene=scene, filename=f"{filename}__{width}x{height}__{datetime.utcnow()}")
    tracer.render()

if __name__ == "__main__":
    run(input("Enter the filename in ../resources: "))