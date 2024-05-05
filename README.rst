Py-Spangled Banner
==================

Generator of customizable SVG displays of the US flag

See the official math specifications in `Executive Order 10834 <https://en.wikisource.org/wiki/Executive_Order_10834>`_.

Main module content
-------------------

(TBD)

Stars submodule content
-----------------------

(TBD)

Geometry submodule content
--------------------------

(TBD)

SVG submodule content
----------------------

(TBD)

Todos and future features
-------------------------

- [ ] Consider using etree in the SVG submodule, especially as part of handling
      the layouts
- [x] Add other builtin palettes
- [ ] Enable the layout generators to take a layout kind constraint, and only
      return layouts of that kind
- [x] Make the SVG builder take a sequence of relative coordinates inside the
      canton, or a dict whose values are the diameter of the stars
  - [x] Add, somewhere, a function generating the coordinates of the stars
        relative to the canton based on the layout
    - [ ] Add optional margin parameters ?
  - [ ] Put the builder taking a layout elsewhere ? Or in the main module, have
        a builder that takes just a number of stars (as well as other
        measurements data) ?
- In Measurements.generate:
  - [ ] Add xmargin and ymargin parameters, floats relative to the canton size
        which make up (or add to ?) the respective margins, and compute the
        stars spacing accordingly
  - [ ] Make the star size proportional to the canton size the layout
    - [ ] Add either a threshold system or a boolean parameter so that the 50
          flag remains the same
    - May cause issues with the no-layout builder version
