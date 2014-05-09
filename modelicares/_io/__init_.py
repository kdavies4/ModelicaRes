#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Packages to load data from various simulation and linearization formats

The format-dependent functions and methods of
:class:`~modelicares.simres.SimRes` and :class:`~modelicares.linres.LinRes` are
placed here in order to support multiple formats.  However, this package
currently it only contains functions to load data from OpenModelica and Dymola
(omdy).
"""

from . import omdy

if __name__ == '__main__':
    """Test the contents of this module.
    """
    import doctest
    import modelicares._io # TODO: Use relative import?

    doctest.testmod(_io.omdy) # TODO: Use relative import?
    exit()
