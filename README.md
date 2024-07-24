# Py-Spangled Banner

Generator of customizable SVG displays of the US flag

See the official math specifications in [Executive Order 10834](https://en.wikisource.org/wiki/Executive_Order_10834).

## Main module content

These are found in the `py_spangled_banner` module.

`write_svg(file: str|io.TextIOBase, /, nstars: int, *, canton_factor: Rational = Fraction(247, 175), kinds: Iterable[stars.LayoutKind|str]|None = None, nstripes: int = 13, proportional_star_size: bool = True, width: float|str|None = None, height: float|str|None = None, colors: svg.FlagColors = FlagPalette.DEFAULT)`

This function writes an SVG file representing a stars-and-stripes flag. The parameters are as follows:

- `file: str|io.TextIOBase`: a file-like object open in text mode, or the path to the file to write on. If a path is provided, the file will be written ti in UTF-8 encoding, and it will be created if it doesn't exist or overwritten if it does.

- `nstars: int`: the number of stars to display in the canton.

- The other keyword parameters are passed to functions from the submodules used by this function:

  - `stars.find_best_star_layout`: `canton_factor` and `kinds`
  - `geometry.Measurements.generate`: `nstripes` and `proportional_star_size`
  - `svg.get_svg_from_layout`: `width`, `height` and `colors`

`get_svg(nstars: int, *, canton_factor: Rational = Fraction(247, 175), kinds: Iterable[stars.LayoutKind|str]|None = None, nstripes: int = 13, proportional_star_size: bool = True, width: float|str|None = None, height: float|str|None = None, colors: svg.FlagColors = FlagPalette.DEFAULT) -> str`

Instead of writing it to a file, this function returns the SVG content as a string. The parameters are otherwise the same.

## Stars submodule content

These are found in the `py_spangled_banner.stars` module. This submodule generates layouts for the stars in the canton.

`LayoutKind`

  This is an enumeration of the possible kinds of layouts for the stars in the canton.

  `GRID`

    The stars are arranged in a grid, like the 24-star "Old Glory" flag, or the 48-star flag.

  `SHORT_SANDWICH`

    Each shorter row of stars is between two longer rows, like the 50-star flag. It can be seen as two grids, one inside the other.

  `LONG_SANDWICH`

    Each longer row of stars is between two shorter rows. It looks like a rectangle with the corners cut off.

  `PAGODA`

    Each longer row of stars is followed by a shorter row, like the 45-star flag. It looks like a rectangle with two corners on the same long side cut off. (This module will always cut off the corners of the bottom side.)

  `SIDE_PAGODA`

    The rows are all of the same length and there is an odd number of them, like the short-lived 49-star flag. Each longer column of stars is followed by a shorter column, and it looks like a rectangle with two corners on the same short side cut off, making it similar to the pagoda layout but on the side. (This module will always cut off the corners of the right side.)

  `CUBE`

    The rows are all of the same length and there is an even number of them. It looks like a rectangle with two opposite corners cut off. (This module will always cut the top-right and bottom-left corners.)

  `from_layout(layout: tuple[int, int, int, int], /) -> LayoutKind`

    This static method computes the layout kind from a given 4-tuple layout. More about what those tuple layouts mean in the following function.

`generate_star_layouts(nstars: int, *, kinds: Iterable[LayoutKind|str]|None = None) -> Iterable[tuple[int, int, int, int]]`

  This is a generator for all the possible layouts, in arbitrary order, for the given number of stars, optionally filtered by a set of layout kinds.

  The `(a, b, c, d)` layouts represent that `a` rows of `b` stars are interspersed with `c` rows of `d` stars.

`find_best_star_layout(nstars: int, *, canton_factor: Rational = Fraction(247, 175), kinds: Iterable[LayoutKind|str]|None = None) -> tuple[int, int, int, int]`

  This returns the best possible layout for the given number of stars and canton size ratio (width over height) defaulting to the official US canton ratio.

`find_best_star_layouts(nstars: int, *, canton_factor: Rational = Fraction(247, 175), kinds: Iterable[LayoutKind|str]|None = None) -> dict[tuple[int, int, int, int], Comparable]`

  The keys of the dict are the same layouts generated by `generate_star_layouts`, but sorted by how well it fits the given canton size ratio, the first the better. The values are arbitrary comparable values : the lower, the better it fits.

## Geometry submodule content

(TBD)

## SVG submodule content

(TBD)

## Todos and future features

- [ ] Consider using etree in the SVG submodule, especially as part of handling
  the layouts
- [x] Add other builtin palettes
- [x] Enable the layout generators to take a layout kind constraint, and only
  return layouts of that kind
  - [ ] Enable that constraint to be passed through from the main function in init
- [x] Make the SVG builder take a sequence of relative coordinates inside the
  canton, or a dict whose values are the diameter of the stars
  - [x] Add, somewhere, a function generating the coordinates of the stars
    relative to the canton based on the layout
    - [ ] Add optional margin parameters ?
  - [ ] Put the builder taking a layout elsewhere ?
  - [x] Or in the main module, have a builder that takes just a number of stars
    (as well as other measurements data) ?
- In Measurements.generate:
  - [ ] Add xmargin and ymargin parameters, floats relative to the canton size
    which make up (or add to ?) the respective margins, and compute the stars
    spacing accordingly
  - [x] Make the star size proportional to the canton size and the layout
    - [x] Add either a threshold system or a boolean parameter so that the 50
      flag remains the same
    - May cause issues with the no-layout builder version - but generate
      requires a layout anyway so it's a bigger issue
- In the SVG writer, fix:
  - [ ] Sizing the stars arbitrarily using a dict
  - [ ] The layout method for all layout kinds
- [ ] Add a CLI
- [x] Make the normalize function reduce the denominator of the star size when
  the lcm is too high, rather than doing that preventively
