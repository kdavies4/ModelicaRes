#!/usr/bin/python
"""Submodules to read data from various simulation and linearization formats

Each submodule contains the following functions for a specific results format:

- :func:`readsim` - Read simulation results.

- :func:`readlin` - Read linearization results.

The first argument of each function is *fname*, the name of the results file
(including the path).  :func:`readsim` takes a second argument,
*constants_only*.  If it is `True` and the format supports it, :func:`readsim`
will only read constants.

:func:`readsim` returns a dictionary of variables.  The keys are variable names
and the values are instances of :class:`~modelicares.simres.Variable` or a
derived class.  :func:`readlin` returns an instance of
:class:`control.StateSpace`.

Errors are raised under the following conditions:

- :class:`IOError`: The file cannot be accessed.

- :class:`TypeError`: The file does not appear to be from the supported tool.

- :class:`AssertionError`: Meta information in the file is incorrect or unrecognized.

- :class:`KeyError`: An expected variable is missing.

- :class:`IndexError`: A variable has the wrong shape.

The last three errors occur when the file does appear to be from the supported
tool but something else is wrong.
"""

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915
# pylint: disable=I0011, W0141, W0142

if __name__ == '__main__':
    # Test the contents of this file.

    import doctest
    doctest.testmod()
