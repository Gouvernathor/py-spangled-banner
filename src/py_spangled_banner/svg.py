"""
Manages the export to the SVG format.
"""

from collections.abc import Collection, Mapping
import dataclasses
import enum
from fractions import Fraction
from math import cos, pi, sin
from numbers import Real

from ._util import write_from_get
from .geometry import _IntMeasurements, coordinates_from_layout, Measurements

__all__ = (
    "FlagColors",
    "get_svg_from_layout",
    "get_svg_from_star_coordinates",
    "write_svg_from_layout",
    "write_svg_from_star_coordinates",
)

@dataclasses.dataclass
class FlagColors:
    """
    The colors of the flag.
    Takes strings, which can be standard CSS color names, hexadecimal RGB values, rgb() calls...
    """
    outer_stripes: str
    inner_stripes: str
    canton: str
    stars: str

class FlagPalette(FlagColors, enum.Enum):
    DEFAULT = ("#B22234", "#FFFFFF", "#3C3B6E", "#FFFFFF")
    SATURATED = ("#FF0000", "#FFFFFF", "#0000FF", "#FFFFFF")
    BLACK_AND_GREY = ("#000000", "#888888", "#000000", "#888888")

def get_svg_from_layout(
        measurements: Measurements,
        layout: tuple[int, int, int, int],
        *,
        width: Real|str|None = None,
        height: Real|str|None = None,
        colors: FlagColors = FlagPalette.DEFAULT,
        ) -> str:

    measurements = measurements.normalize()

    buffer = []

    _append_header(buffer, height, width, measurements)
    _append_rect_stripes(buffer, measurements, colors)
    # use of _append_canton_from_layout possible here
    _append_canton_from_coordinates(buffer, measurements, set(coordinates_from_layout(layout)), colors)
    _append_footer(buffer)

    return "".join(buffer)

def get_svg_from_star_coordinates(
        measurements: Measurements,
        star_coordinates: Collection[tuple[Real, Real]],
        *,
        width: Real|str|None = None,
        height: Real|str|None = None,
        colors: FlagColors = FlagPalette.DEFAULT,
        ) -> str:

    measurements = measurements.normalize()

    buffer = []

    _append_header(buffer, height, width, measurements)
    _append_rect_stripes(buffer, measurements, colors)
    _append_canton_from_coordinates(buffer, measurements, star_coordinates, colors)
    _append_footer(buffer)

    return "".join(buffer)

def _append_header(
        buffer: list[str],
        height: Real|str|None,
        width: Real|str|None,
        measurements: _IntMeasurements,
        ) -> None:
    buffer.append('''\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"''')

    if width is height is None:
        buffer.append('''
     height="100%"''')
    elif width is not None:
        buffer.append(f'''
     width="{width}"''')
    else:
        buffer.append(f'''
     height="{height}"''')

    buffer.append(f'''
     viewBox="0 0 {measurements.width} {measurements.height}">''')
    buffer.append('''
    <!-- Created with py-spangled-banner (https://github.com/Gouvernathor/py-spangled-banner) -->''')

def _append_rect_stripes(
        buffer: list[str],
        measurements: _IntMeasurements,
        colors: FlagColors,
        ) -> None:
    nb_white_stripes = (measurements.height // measurements.stripe_height) // 2
    nb_short_white_stripes = (measurements.canton_height // measurements.stripe_height) // 2
    white_id = "white_stripe" if colors is FlagPalette.DEFAULT else "inner_stripe"

    # TODO: what if there is only short white stripes ? or no white stripes ?
    buffer.append(f'''
    <rect width="{measurements.width}" height="{measurements.height}" fill="{colors.outer_stripes}"/>''')

    if nb_white_stripes:
        if not (nb_white_stripes - nb_short_white_stripes):
            raise NotImplementedError("Versions of the flag where there is no long inner (white) stripe are not supported.")
        buffer.append(f'''
    <rect id="large_{white_id}" width="{measurements.width}" y="{measurements.stripe_height*(nb_short_white_stripes*2+1)}" height="{measurements.stripe_height}" fill="{colors.inner_stripes}"/>''')

    if nb_short_white_stripes:
        buffer.append(f'''
    <use href="#large_{white_id}" id="short_{white_id}" x="{measurements.canton_width}" width="{measurements.width-measurements.canton_width}" y="{measurements.stripe_height*(-nb_short_white_stripes*2)}"/>''')

    for ismall in range(1, nb_short_white_stripes):
        buffer.append(f'''
    <use href="#short_{white_id}" y="{measurements.stripe_height*(ismall*2)}"/>''')

    for ilarge in range(1, nb_white_stripes - nb_short_white_stripes):
        buffer.append(f'''
    <use href="#large_{white_id}" y="{measurements.stripe_height*(ilarge*2)}"/>''')

def _append_path_stripes(buffer: list[str], measurements: _IntMeasurements, colors: FlagColors) -> None:
    raise NotImplementedError

def _append_canton_from_layout(
        buffer: list[str],
        measurements: _IntMeasurements,
        layout: tuple[int, int, int, int],
        colors: FlagColors,
        ) -> None:

    nb_lg_rows, ln_lg_rows, nb_sh_rows, ln_sh_rows = layout

    buffer.append(f'''
    <rect width="{measurements.canton_width}" height="{measurements.canton_height}" fill="{colors.canton}"/>''')

    if not (nb_lg_rows and ln_lg_rows):
        return

    lg_row_id = f"{ln_lg_rows}-row"
    sh_row_id = f"{ln_sh_rows}-row"

    if nb_lg_rows>1:
        buffer.append(f'''
    <g id="{lg_row_id}">''')

    if nb_sh_rows>1:
        buffer.append(f'''
        <g id="{sh_row_id}">''')

    starpath = _get_star_path((measurements.horizontal_stars_margin, measurements.vertical_stars_margin), measurements.star_diameter/2, 23*' ')

    buffer.append(f'''
            <g id="star">
                <path
                    d="{starpath}"
                    fill="{colors.stars}"/>
            </g>''')

    if nb_sh_rows>1:
        for i in range(1, ln_sh_rows):
            buffer.append(f'''
            <use href="#star" x="{measurements.horizontal_star_spacing*2*i}"/>''')

        buffer.append('''
        </g>''')
    else:
        i = 0

    if nb_lg_rows>1:
        for j in range(ln_lg_rows-ln_sh_rows):
            buffer.append(f'''
        <use href="#star" x="{measurements.horizontal_star_spacing*2*(i+j+1)}"/>''')

        buffer.append('''
    </g>''')

    # TODO: find a way to intermingle the rows
    for k in range(nb_sh_rows):
        buffer.append(f'''
    <use href="#{sh_row_id}" y="{measurements.vertical_star_spacing*(2*k+1)}" x="{measurements.horizontal_star_spacing}"/>''')

    for k in range(1, nb_lg_rows):
        buffer.append(f'''
    <use href="#{lg_row_id}" y="{measurements.vertical_star_spacing*(2*k)}"/>''')

def _append_canton_from_coordinates(
        buffer: list[str],
        measurements: _IntMeasurements,
        star_coordinates: Collection[tuple[Real, Real]],
        colors: FlagColors,
        ) -> None:

    buffer.append(f'''
    <rect width="{measurements.canton_width}" height="{measurements.canton_height}" fill="{colors.canton}"/>''')

    if not star_coordinates:
        return

    star_diameter = measurements.star_diameter
    canton_width = measurements.canton_width
    canton_height = measurements.canton_height

    if not isinstance(star_coordinates, Mapping):
        do_scaling = False
        first_star_scale = 1
        first_star, *other_stars = star_coordinates
    else:
        do_scaling = True
        first_star, *other_stars = star_coordinates
        first_star_scale = Fraction(star_coordinates[first_star]) / star_diameter
    first_star_x, first_star_y = first_star

    star_path = _get_star_path((Fraction(first_star_x)*canton_width, Fraction(first_star_y)*canton_height), star_diameter*first_star_scale/2, 15*' ') # type: ignore
    buffer.append(f'''
    <g id="star">
        <path
            d="{star_path}"
            fill="{colors.stars}"/>
    </g>''')

    for (x, y) in other_stars:
        buffer.append(f'''
    <use href="#star" x="{float(x-first_star_x)*canton_width}" y="{float(y-first_star_y)*canton_height}"''') # type: ignore
        if do_scaling:
            star_size = star_coordinates[x, y] # type: ignore
            star_scale = Fraction(star_size) / (first_star_scale * star_diameter)
            if star_scale != 1:
                buffer.append(f' transform="scale({star_scale})"')
        buffer.append('/>')

def _append_footer(buffer: list[str]) -> None:
    buffer.append('''
</svg>
''')

def _get_star_path(
        start: tuple[Fraction|int, Fraction|int],
        radius: Fraction|int|float,
        indent: str,
        ) -> str:

    def fraccos(x):
        return Fraction(cos(x))
    def fracsin(x):
        return Fraction(sin(x))
    fracpi = Fraction(pi)

    top, topright, bottomright, bottomleft, topleft = [(fraccos(3*fracpi/2 + k*2*fracpi/5), fracsin(3*fracpi/2 + k*2*fracpi/5)) for k in range(5)]

    def c(x):
        return float(radius*x)

    initial_y = c(top[1])
    first_move_x = c(bottomright[0]-top[0])
    first_move_y = c(bottomright[1]-top[1])
    second_move_x = c(topleft[0]-bottomright[0])
    second_move_y = c(topleft[1]-bottomright[1])
    third_move_x = c(topright[0]-topleft[0])
    fourth_move_x = c(bottomleft[0]-topright[0])
    fourth_move_y = c(bottomleft[1]-topright[1])

    return indent + ('\n'+indent).join((
        f'M {float(start[0])},{float(start[1])}',
        f'm 0,{initial_y}',
        f'l {first_move_x},{first_move_y}',
        f'  {second_move_x},{second_move_y}',
        f'h {third_move_x}',
        f'l {fourth_move_x},{fourth_move_y}',
        'z',
    ))

write_svg_from_layout = write_from_get(get_svg_from_layout)
write_svg_from_star_coordinates = write_from_get(get_svg_from_star_coordinates)
