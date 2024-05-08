from .stars import find_best_star_layout
from .geometry import Measurements
from .svg import get_svg_from_layout

def get_svg(nstars: int) -> str:
    layout = find_best_star_layout(nstars)
    measurements = Measurements.generate(star_layout=layout)
    return get_svg_from_layout(measurements, layout)

def write_svg(file, nstars: int) -> None:
    if isinstance(file, str):
        with open(file, "w") as f:
            return write_svg(f, nstars)
    print(get_svg(nstars), file=file)
