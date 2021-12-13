from lighttrace.core.colors import Colors
from lighttrace.core.constants import HORIZON
from lighttrace.core.functions import sine, cosine, linear, quadratic
from lighttrace.core.geometry import Plane, Sphere
from lighttrace.core.mesh import Mesh
from lighttrace.core.surface import Surface
from lighttrace.core.tracer import Tracer
from lighttrace.core.types import Animation, CoefficientSet, Light, LightType, Point, Scene, Vector3, Viewport
from lighttrace.core.volume import Octree
from lighttrace.core.utils import SectionProfiler



def run(filename: str, animate: bool = False) -> None:
    scene = Scene([], [], background=Colors.GREY_4)
    coefficients_1 = CoefficientSet(.005, .7, .0001, .1, .09)
    coefficients_2 = CoefficientSet(.005, .88, .0001, .1, .09)
    surface_1 = Surface(Colors.MATTE_BLUE, coefficients_1)
    surface_2 = Surface(Colors.GREY_6, coefficients_2)
    mesh = Mesh(surface=surface_2)
    # mesh.load(filename)

    width = 300
    height = 300
    name = "orbit_5"
    # width = int(input("Width: "))
    # height = int(input("Height: "))
    # name = input("Output name: ")
    bvh_factory = lambda objects: Octree([o for o in objects if o.is_finite])
    scene = Scene([], [], background=Colors.BLACK, bvh_factory=bvh_factory)

    FRAMES = 30
    R = 600
    Linear = linear(FRAMES)
    Quadratic = quadratic(FRAMES)
    Sine = sine(R, FRAMES)
    Cosine = cosine(R, FRAMES)

    E = 1000

    scene.add(
        Light(LightType.AMBIENT, Colors.GREY_5),
        Light(LightType.POINT, Colors.MATTE_RED, Vector3(0, Linear(30, 30), -10)),
        Light(LightType.POINT, Colors.WHITE, Vector3(Cosine(), 700, Sine())),
        Light(LightType.DIRECTIONAL, Colors.WHITE, Vector3(-1, -1, -1)),
        Plane(Point(0, -400, 0), Vector3(0, 1, 0), surface=surface_1),
        # Plane(Point(0, 0, HORIZON / 100000), Vector3(0, 0, -1), surface=surface_1),
        Sphere(radius=300, center=Point(0, 0, 0), surface=surface_1),
        Sphere(radius=70, center=Point(Cosine(), 0, Sine()), surface=surface_2),
        # # Sphere(radius=5, center=Point(0, 25, 10), surface=surface_1),
        # Sphere(radius=7, center=Point(10, 10, 10), surface=surface_1),
        # *mesh.generate_polygons()
    )
    O = Vector3(sine(E / 2, FRAMES)(), 200, cosine(E, FRAMES)())
    with Animation(scene, frames=FRAMES) as animation:
        for i, _scene in animation:
            viewport = Viewport(
                width=width,
                height=height,
                origin=O,
                up=Vector3(0, 1, 0),
                focus=Vector3(0, 0, 0),
                fov=120.0,
            )
            print(i)
            tracer = Tracer(viewport=viewport, scene=_scene, directory=name, filename=f"{name}__{width}x{height}__{i + 1}")
            tracer.render()
            print("")

if __name__ == "__main__":
    # run(input("Enter the filename in ../resources: "))

    run("Ethereum")
