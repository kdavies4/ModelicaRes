#!/usr/bin/python
"""Packages to load data from various simulation and linearization formats

TODO doc

The format-dependent attributes and methods of
:class:`~modelicares.simres.SimRes` and :class:`~modelicares.linres.LinRes` are
placed here in order to support multiple formats.  However, this package
currently only contains functions to load data from OpenModelica and Dymola
(omdy).
"""

# List of file-loading functions for SimRes:
from modelicares._io.dymola import loadsim as dymola_sim
simloaders = [('dymola', dymola_sim)] # SimRes tries these in order.

# List of file-loading functions for LinRes:
from modelicares._io.dymola import loadlin as dymola_lin
linloaders = [('dymola', dymola_lin)] # LinRes tries these in order.


if __name__ == '__main__':
    """Test the contents of this module.
    """
    import doctest
    from modelicares._io import *

    doctest.testmod()
    doctest.testmod(dymola)
