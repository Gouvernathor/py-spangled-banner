"""
Computes the layout of the stars on an American flag.
"""

from collections.abc import Iterable
from fractions import Fraction
from functools import partial
from numbers import Real

__all__ = ("find_best_star_layout", "find_best_star_layouts", "generate_star_layouts")

def _optimize_layout(x: tuple[int, int, int, int], canton_factor: Real) -> Real:
    a, b, c, d = x
    if c == 0:
        d = 0
    return abs((a + c + 1) * canton_factor - (b + d + 1)) # type: ignore

def generate_star_layouts(nstars: int, _allow_extended_quincunx=False) -> Iterable[tuple[int, int, int, int]]:
    """
    The results represent that a rows of b stars are interspersed with c rows of d stars.

    Returns a, b and c such that :
    * a*b + c*(b-1) = nstars
    * c is in (0, a-1, a, a+1)
    * if c = 0, then d = 0
    * elif c = a-1 (this condition may be optional), d is in (b-1, b)
    * else, d = b-1

    When c is 0, the stars are arranged in a grid, like the 24-star "Old Glory" flag, or the 48-star flag.
    When d is b, the stars are arranged in a quincunx, like the 49-star flag.
    When c is a-1, each shorter row of stars is between two longer rows, like the 50-star flag.
    When c is a+1, each longer row of stars is between two shorter rows.
    When c is a, each longer row of stars is followed by a shorter row, like the 45-star flag.
    """
    # TODO: pass the extended quincunx option through the other functions
    for a in range(1, nstars + 1):
        for b in range(1, nstars // a + 1):
            if a * b > nstars:
                break

            if a * b == nstars:
                yield a, b, 0, 0
                break

            for c in (a - 1, a, a + 1):
                if not c:
                    continue

                d_options = [b - 1]
                if (c == a-1) or _allow_extended_quincunx:
                    d_options.append(b)

                for d in d_options:
                    if (a * b + c * d) == nstars:
                        yield a, b, c, d

_DEFAULT_CANTON_FACTOR = Fraction(247, 175)
# TODO: import it from the geometry module ?

def find_best_star_layout(nstars: int, canton_factor: Real = _DEFAULT_CANTON_FACTOR) -> tuple[int, int, int, int]:
    """
    The optimization key makes the stars layout fit as best possible in a canton of that ratio (width over height)
    """
    return min(generate_star_layouts(nstars), key=partial(_optimize_layout, canton_factor=canton_factor))

def find_best_star_layouts(nstars: int, canton_factor: Real = _DEFAULT_CANTON_FACTOR) -> dict[tuple[int, int, int, int], Real]:
    """
    The keys are layout tuples, the values are arbitrary comparable values: the lower, the better it fits.
    """
    d = {t: _optimize_layout(t, canton_factor) for t in generate_star_layouts(nstars)}
    return {t: d[t] for t in sorted(d, key=d.__getitem__)}
