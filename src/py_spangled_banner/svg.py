"""
Manages the export to the SVG format.
"""

from collections.abc import Collection, Mapping
import dataclasses
from decimal import Decimal
import enum
from numbers import Real

from .geometry import _IntMeasurements, coordinates_from_layout, Measurements
from .stars import LayoutKind

__all__ = ("FlagColors", "get_svg_from_star_coordinates", "write_svg")

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
        height: Real|str|None = None,
        width: Real|str|None = None,
        colors: FlagColors = FlagPalette.DEFAULT,
        ) -> str:

    measurements = measurements.normalize()

    buffer = []

    _append_header(buffer, height, width, measurements)
    _append_stripes(buffer, measurements, colors)

    kind = LayoutKind.from_layout(layout)
    # TODO: implement the different layouts
    if kind in (LayoutKind.SHORT_SANDWICH,):
        _append_canton_from_layout(buffer, measurements, layout, colors)
    else:
        _append_canton_from_coordinates(buffer, measurements, set(coordinates_from_layout(layout)), colors)

    _append_footer(buffer)

    return "".join(buffer)

def get_svg_from_star_coordinates(
        measurements: Measurements,
        star_coordinates: Collection[tuple[Real, Real]],
        width: Real|str|None = None,
        height: Real|str|None = None,
        colors: FlagColors = FlagPalette.DEFAULT,
        ) -> str:

    measurements = measurements.normalize()

    buffer = []

    _append_header(buffer, height, width, measurements)
    _append_stripes(buffer, measurements, colors)
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

_append_stripes = _append_rect_stripes

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

    # TODO: use the real formulae to make up a 5-points star
    scale = Decimal(measurements.star_diameter) / Decimal(240)

    buffer.append(f'''
            <g id="star">
                <path
                    d="M {measurements.horizontal_stars_margin},{measurements.vertical_stars_margin}
                       m 0,{-scale*measurements.star_diameter/2}
                       l {scale*Decimal("70.534230")},{scale*Decimal("217.082039")}
                         {scale*Decimal("-184.661012")},{scale*Decimal("-134.164078")}
                       h {scale*Decimal("228.253564")}
                       l {scale*Decimal("-184.661012")},{scale*Decimal("134.164078")}
                       z"
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
        first_star_scale = Decimal(1)
        first_star, *other_stars = star_coordinates
    else:
        do_scaling = True
        first_star, *other_stars = star_coordinates
        first_star_scale = Decimal(star_coordinates[first_star]) / star_diameter
    first_star_x, first_star_y = first_star

    # TODO: use the real formulae to make up a 5-points star
    scale = Decimal(star_diameter) / Decimal(240)

    # TODO: avoid using float, somehow
    buffer.append(f'''
    <g id="star">
        <path
            d="M {float(first_star_x)*canton_width},{float(first_star_y)*canton_height}
               m 0,{-scale*first_star_scale*star_diameter/2}
               l {scale*Decimal("70.534230")},{scale*Decimal("217.082039")}
                 {scale*Decimal("-184.661012")},{scale*Decimal("-134.164078")}
               h {scale*Decimal("228.253564")}
               l {scale*Decimal("-184.661012")},{scale*Decimal("134.164078")}
               z"
            fill="{colors.stars}"/>
    </g>''')

    for (x, y) in other_stars:
        buffer.append(f'''
    <use href="#star" x="{float(x-first_star_x)*canton_width}" y="{float(y-first_star_y)*canton_height}"''') # type: ignore
        if do_scaling:
            star_size = star_coordinates[x, y] # type: ignore
            star_scale = Decimal(star_size) / (scale*first_star_scale * star_diameter)
            if star_scale != 1:
                buffer.append(f' transform="scale({star_scale})"')
        buffer.append('/>')

def _append_footer(buffer: list[str]) -> None:
    buffer.append('''
</svg>
''')

def write_svg_from_layout(file, *args, **kwargs):
    print(get_svg_from_layout(*args, **kwargs), file=file)

def write_svg(file, *args, **kwargs):
    print(get_svg_from_star_coordinates(*args, **kwargs), file=file)
