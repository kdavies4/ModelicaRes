#!/usr/bin/python
"""Submodules to read data from various simulation and linearization formats

Each submodule contains the following functions for a specific results format:

- :func:`readsim` - Read simulation results.

- :func:`readlin` - Read linearization results.

The first argument of each function is *fname*, the name of the results file
(including the path).  :func:`readsim` takes a second argument,
*constants_only*.  If it is *True* and the format supports it, :func:`readsim`
will only read constants.

:func:`readsim` returns an instance of :class:`~modelicares.simres._VarDict`, a
specialized dictionary of variables.  The keys are variable names and the values
are instances of :class:`~modelicares.simres.Variable` or a derived class.
:func:`readlin` returns an instance of :class:`control.StateSpace`.

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

from difflib import get_close_matches
from ..util import CallList


class VarDict(dict):

    """Special dictionary for simulation variables (instances of
    :class:`~modelicares.simres.Variable`)
    """

    def __getattr__(self, attr):
        """Look up a property across all of the variables (e.g., is_constant).
        """
        return getattr(CallList(self.values()), attr)

    def __getitem__(self, key):
        """Include suggestions in the error message if a variable is missing.
        """
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            msg = key + ' is not a valid variable name.'
            close_matches = get_close_matches(key, self.keys())
            if close_matches:
                msg += "\n       ".join(["\n\nDid you mean one of these?"]
                                        + close_matches)
            raise LookupError(msg)


if __name__ == '__main__':
    # Test the contents of this file.

    import doctest
    doctest.testmod()
