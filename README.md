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

(TBD)

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
