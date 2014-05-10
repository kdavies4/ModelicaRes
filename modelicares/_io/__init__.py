#!/usr/bin/python
"""Packages to load data from various simulation and linearization formats

The format-dependent attributes and methods of
:class:`~modelicares.simres.SimRes` and :class:`~modelicares.linres.LinRes` are
placed here in order to support multiple formats.  However, this package
currently it only contains functions to load data from OpenModelica and Dymola
(omdy).
"""

if __name__ == '__main__':
    """Test the contents of this module.
    """
    import doctest
    from modelicares._io import *

    doctest.testmod()
    doctest.testmod(omdy)
