"""
Computes the sizes of different parts of the flag, mainly depending on the stars and other parameters.
"""

from collections.abc import Iterable
from fractions import Fraction
import math
from numbers import Rational
from typing import NamedTuple

from .stars import _DEFAULT_LAYOUT, LayoutKind

__all__ = ("Measurements", "coordinates_from_layout")

class Measurements(NamedTuple):
    # TODO: in 3.13, make the type parameterized and defaulted to Rational,
    # make the normalize method return a Measurements[int],
    # and make the fractionize and generate methods return Measurements[Fraction].
    height: Rational
    width: Rational
    canton_height: Rational
    canton_width: Rational
    vertical_stars_margin: Rational
    vertical_star_spacing: Rational
    horizontal_stars_margin: Rational
    horizontal_star_spacing: Rational
    star_diameter: Rational
    stripe_height: Rational

    def check(self) -> None:
        if self.canton_height % self.stripe_height:
            raise ValueError("The canton height should be a multiple of the stripe height.")

        if self.canton_width >= self.width:
            raise ValueError("The canton should not cover the whole width of the flag.")

        if self.canton_height > self.height/2: # type: ignore
            raise ValueError("The canton should not cover more than half of the height of the flag.")

    def normalize(self, *, more_precise=True, max_value=10**7) -> "_IntMeasurements":
        """
        Builds a version only using integers, chosen to be the smallest integers possible
        while keeping the same ratios between all values.
        The goal is to remove use of the Fraction type, while avoiding any use
        of floating point numbers which would expose the calculations to rounding errors.

        The star diameter value's precision will be reduced to make all returned values
        lower than max_value. Values may be higher than max_value if reducing the star
        diameter's precision is not enough, or if reducing it too much would nullify it.
        If more_precise is False, the star diameter will be directly rounded once,
        whereas if it is True, the star diameter will be rounded just enough
        to fit the constraints.
        """
        if isinstance(self, _IntMeasurements):
            return self

        max_lcm_value: int|Fraction = max_value/max(self) # type: ignore
        lcm = math.lcm(*(v.denominator for v in self))
        if lcm > max_lcm_value:
            # avoiding massive numbers
            lcm_without_star_diam = math.lcm(
                self.height.denominator, self.width.denominator,
                self.canton_height.denominator, self.canton_width.denominator,
                self.vertical_stars_margin.denominator, self.vertical_star_spacing.denominator,
                self.horizontal_stars_margin.denominator, self.horizontal_star_spacing.denominator,
                self.stripe_height.denominator,
            )

            if (not more_precise) or (lcm_without_star_diam > max_lcm_value) or not isinstance(self.star_diameter, Fraction):
                # all the roundings will be exact except for the star diameter
                return _IntMeasurements(*(round(v * lcm_without_star_diam) for v in self)) # type: ignore

            while lcm > max_lcm_value:
                new_star_diam = self.star_diameter.limit_denominator(self.star_diameter.denominator//10) # type: ignore
                if not new_star_diam:
                    new_star_diam = self.star_diameter.limit_denominator(int(self.star_diameter.denominator/self.star_diameter.numerator)) # type: ignore
                    if new_star_diam in (self.star_diameter, 0):
                        break
                self = self._replace(star_diameter=new_star_diam)
                lcm = math.lcm(*(v.denominator for v in self))

        return _IntMeasurements(*(int(v * lcm) for v in self)) # type: ignore

    def fractionize(self) -> "_FractionMeasurements":
        """
        Builds a version using fractions, to support safer calculations than ints do.
        """
        return _FractionMeasurements(*(map(Fraction, self)))

    @staticmethod
    def generate(*,
            star_layout: tuple[int, int, int, int] = _DEFAULT_LAYOUT,
            nstripes: int = 13,
            proportional_star_size: bool = True,
            ) -> "_FractionMeasurements":
        """
        Generates the government specifications for the flag.
        Parameters to be added one-by-one.
        """
        a, b, c, d = star_layout
        kind_is_grid = LayoutKind.from_layout(star_layout) == LayoutKind.GRID

        A = Fraction(1)
        B = A * Fraction(19, 10)
        C = A * Fraction(math.ceil(nstripes/2), nstripes)
        D = B * Fraction(2, 5)
        if kind_is_grid:
            # margin = .75*spacing
            # (ou spacing = 1.5*margin)
            H = Fraction(D, b+d+Fraction(1, 3))
            G = Fraction(2, 3) * H
            F = Fraction(C, a+c+Fraction(1, 3))
            E = Fraction(2, 3) * F
        else:
            E = F = C * Fraction(1, a+c+1)
            G = H = D * Fraction(1, b+d+1)

        L = A * Fraction(1, nstripes)
        if proportional_star_size:
            # take the closest distance between two stars
            # times a compat factor (so that the 50 remains the same)
            if kind_is_grid:
                dists = [
                    D / (b + 1),
                    C / (a + 1),
                    # the diagonal is always larger than the others
                ]
            else:
                dists = [
                    2 * D / (b + d + 1),
                    2 * C / (a + c + 1),
                    Fraction(math.sqrt((D/(b+d+1))**2 + (C/(a+c+1))**2)),
                ]
            K = Fraction(9007199254740992, 12167419471659595) * min(dists)
        else:
            K = L * Fraction(4, 5)

        return _FractionMeasurements(A, B, C, D, E, F, G, H, K, L)

class _FractionMeasurements(Measurements):
    __slots__ = ()
    height: Fraction
    width: Fraction
    canton_height: Fraction
    canton_width: Fraction
    vertical_stars_margin: Fraction
    vertical_star_spacing: Fraction
    horizontal_stars_margin: Fraction
    horizontal_star_spacing: Fraction
    star_diameter: Fraction
    stripe_height: Fraction

class _IntMeasurements(Measurements):
    __slots__ = ()
    height: int
    width: int
    canton_height: int
    canton_width: int
    vertical_stars_margin: int
    vertical_star_spacing: int
    horizontal_stars_margin: int
    horizontal_star_spacing: int
    star_diameter: int
    stripe_height: int

def coordinates_from_layout(layout: tuple[int, int, int, int]) -> Iterable[tuple[Rational, Rational]]:
    a, b, c, d = layout

    measurements = Measurements.generate(star_layout=layout)
    relative_xmargin = measurements.horizontal_stars_margin / measurements.canton_width
    relative_ymargin = measurements.vertical_stars_margin / measurements.canton_height
    relative_xspacing = measurements.horizontal_star_spacing / measurements.canton_width
    relative_yspacing = measurements.vertical_star_spacing / measurements.canton_height

    match LayoutKind.from_layout(layout):
        case LayoutKind.GRID:
            for x in range(b):
                for y in range(a):
                    yield relative_xmargin + x * relative_xspacing, relative_ymargin + y * relative_yspacing

        case LayoutKind.SHORT_SANDWICH|LayoutKind.PAGODA|LayoutKind.SIDE_PAGODA|LayoutKind.CUBE:
            # left-aligned rows
            for y in range(a):
                for x in range(b):
                    yield relative_xmargin + 2*x * relative_xspacing, relative_ymargin + 2*y * relative_yspacing
            # right-aligned rows
            for y in range(c):
                for x in range(d):
                    yield relative_xmargin + (2*x + 1) * relative_xspacing, relative_ymargin + (2*y + 1) * relative_yspacing

        case LayoutKind.LONG_SANDWICH:
            # long rows
            for y in range(a):
                for x in range(b):
                    yield relative_xmargin + 2*x * relative_xspacing, relative_ymargin + (2*y + 1) * relative_yspacing
            # short rows
            for y in range(c):
                for x in range(d):
                    yield relative_xmargin + (2*x + 1) * relative_xspacing, relative_ymargin + 2*y * relative_yspacing

        case _:
            raise ValueError(f"Invalid layout: {layout}")
