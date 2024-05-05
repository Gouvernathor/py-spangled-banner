"""
Computes the sizes of different parts of the flag, mainly depending on the stars and other parameters.
"""

from fractions import Fraction
import math
from numbers import Rational
from typing import NamedTuple

from .stars import _DEFAULT_LAYOUT

__all__ = ("Measurements",)

class Measurements(NamedTuple):
    # TODO: in 3.13, make the type parameterized and defaulted to Rational,
    # and make the normalize method return a Measurements[int]
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

    def normalize(self) -> "_IntMeasurements":
        """
        Builds a version only using integers, chosen to be the smallest integers possible
        while keeping the same ratios between all values.
        The goal is to remove use of the Fraction type, while avoiding any use
        of floating point numbers which would expose the calculations to rounding errors.
        """
        lcm = math.lcm(*(v.denominator for v in self))
        return Measurements(*(int(v * lcm) for v in self)) # type: ignore

    @staticmethod
    def generate(*,
            star_layout: tuple[int, int, int, int] = _DEFAULT_LAYOUT,
            nstripes: int = 13,
            ) -> "Measurements":
        """
        Generates the government specifications for the flag.
        Parameters to be added one-by-one.
        """
        a, b, c, d = star_layout

        A = Fraction(1)
        B = A * Fraction(19, 10)
        C = A * Fraction(math.ceil(nstripes/2), nstripes)
        D = B * Fraction(2, 5)
        E = F = C * Fraction(1, a+c+1)
        G = H = D * Fraction(1, b+d+1)

        L = A * Fraction(1, nstripes)
        K = L * Fraction(4, 5)

        return Measurements(A, B, C, D, E, F, G, H, K, L)

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