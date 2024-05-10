from ._util import write_from_get
from .stars import find_best_star_layout
from .geometry import Measurements
from .svg import get_svg_from_layout

__all__ = ("get_svg", "write_svg")

def get_svg(nstars: int) -> str:
    layout = find_best_star_layout(nstars)
    measurements = Measurements.generate(star_layout=layout)
    return get_svg_from_layout(measurements, layout)

write_svg = write_from_get(get_svg)
