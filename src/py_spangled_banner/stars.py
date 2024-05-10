"""
Computes the layout of the stars on an American flag.
"""

from collections.abc import Container, Iterable
import enum
from fractions import Fraction
from functools import partial
from numbers import Rational, Real
from typing import NewType

__all__ = ("find_best_star_layout", "find_best_star_layouts", "generate_star_layouts")

Comparable = NewType('Comparable', Real)

def _optimize_layout(x: tuple[int, int, int, int], canton_factor: Rational) -> Comparable:
    a, b, c, d = x
    assert (c == 0) == (d == 0)
    return abs((a + c + 1) * canton_factor - (b + d + 1)) # type: ignore

_DEFAULT_LAYOUT = (5, 6, 4, 5)

class LayoutKind(enum.StrEnum):
    def __new__(cls, value, doc):
        self = str.__new__(cls, value)
        self._value_ = value
        self.__doc__ = doc
        return self

    GRID = enum.auto(), """
    The stars are arranged in a grid,
    like the 24-star "Old Glory" flag, or the 48-star flag.
    """

    SHORT_SANDWICH = enum.auto(), """
    Each shorter row of stars is between two longer rows, like the 50-star flag.
    It can be seen as two grids, one inside the other.
    """

    LONG_SANDWICH = enum.auto(), """
    Each longer row of stars is between two shorter rows.
    It looks like a rectangle with the corners cut off.
    """

    PAGODA = enum.auto(), """
    Each longer row of stars is followed by a shorter row, like the 45-star flag.
    It looks like a rectangle with two corners on the same long side cut off.
    (This module will always cut off the corners of the bottom side.)
    """

    SIDE_PAGODA = enum.auto(), """
    The rows are all of the same length and there is an odd number of them,
    like the short-lived 49-star flag.
    Each longer column of stars is followed by a shorter column,
    and it looks like a rectangle with two corners on the same short side cut off,
    making it similar to the pagoda layout but on the side.
    (This module will always cut off the corners of the right side.)
    """

    CUBE = enum.auto(), """
    The rows are all of the same length and there is an even number of them.
    It looks like a rectangle with two opposite corners cut off.
    (This module will always cut the top-right and bottom-left corners.)
    """

    @staticmethod
    def from_layout(layout: tuple[int, int, int, int]) -> "LayoutKind":
        a, b, c, d = layout
        if (a == 0) == (b == 0) and (c == 0) == (d == 0):
            if not c:
                return LayoutKind.GRID
            if d == b:
                if c == a-1:
                    return LayoutKind.SIDE_PAGODA
                if c == a:
                    return LayoutKind.CUBE
            elif d == b - 1:
                if c == a - 1:
                    return LayoutKind.SHORT_SANDWICH
                if c == a + 1:
                    return LayoutKind.LONG_SANDWICH
                if c == a:
                    return LayoutKind.PAGODA
        raise ValueError(f"Invalid layout: {layout}")

def generate_star_layouts(nstars: int,
        kinds: Container[LayoutKind|str]|None = None,
        ) -> Iterable[tuple[int, int, int, int]]:
    """
    The results represent that a rows of b stars are interspersed with c rows of d stars.

    Returns a, b and c such that :
    * a*b + c*(b-1) = nstars
    * b >= d
    * c is in (0, a-1, a, a+1)
    * if c = 0, then d = 0
    * elif c = a-1 (this condition may be optional), d is in (b-1, b)
    * else, d = b-1

    In any such case, the number of rows is a + c and the number of columns is b + d.

    If kinds is not None, only the layouts of those kinds are returned.
    """
    if kinds is None:
        kinds = set(map(str.casefold, LayoutKind))
    grid_in_kinds = LayoutKind.GRID.casefold() in kinds

    for a in range(1, nstars + 1):
        for b in range(1, nstars // a + 1):
            if a * b > nstars:
                break

            if a * b == nstars:
                if grid_in_kinds:
                    yield a, b, 0, 0
                break

            for c in (a - 1, a, a + 1):
                if not c:
                    continue

                d_options = [b - 1]
                if c in (a-1, a):
                    d_options.append(b)

                for d in d_options:
                    if (a * b + c * d) == nstars:
                        if LayoutKind.from_layout((a, b, c, d)).casefold() in kinds:
                            yield a, b, c, d

_DEFAULT_CANTON_FACTOR = Fraction(247, 175)
# TODO: import it from the geometry module ?

def find_best_star_layout(nstars: int,
        canton_factor: Rational = _DEFAULT_CANTON_FACTOR,
        kinds: Container[LayoutKind|str]|None = None,
        ) -> tuple[int, int, int, int]:
    """
    The optimization key makes the stars layout fit as best possible in a canton of that ratio (width over height)
    """
    return min(generate_star_layouts(nstars, kinds=kinds), key=partial(_optimize_layout, canton_factor=canton_factor))

def find_best_star_layouts(nstars: int,
        canton_factor: Rational = _DEFAULT_CANTON_FACTOR,
        kinds: Container[LayoutKind|str]|None = None,
        ) -> dict[tuple[int, int, int, int], Comparable]:
    """
    The keys are layout tuples, the values are arbitrary comparable values: the lower, the better it fits.
    """
    d = {t: _optimize_layout(t, canton_factor) for t in generate_star_layouts(nstars, kinds=kinds)}
    return {t: d[t] for t in sorted(d, key=d.__getitem__)}
