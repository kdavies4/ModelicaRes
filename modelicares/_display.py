#!/usr/bin/python
"""Contains *default_display_units*, loaded from display.ini.
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915
# pylint: disable=I0011, W0141, W0142

from natu.core import Exponents
from os import path

# Name of the directory containing this file
dname = path.dirname(__file__)

try:
    from configparser import RawConfigParser
except ImportError:
    # For Python 2:
    from ConfigParser import RawConfigParser

class DisplayUnits(dict):
    """Special dictionary of display units, indexed by dimension string
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for dimension_str, display_unit in self.items():
            dimension_str = dimension_str.replace('.', '*')
            self[dimension_str] = (Exponents.fromstr(dimension_str),
                                   display_unit)

    def find(self, dimension):
        """Return the display unit for a particular dimension.

        **Parameters:**

        - *dimension*: Dictionary of base dimensions and exponents

        **Returns:** The display unit as a string
        """
        return '.'.join([self[base][1] if exp == 1 else self[base][1] + str(exp)
                         for base, exp in dimension.items()])

# Load the default display units.
try:
    config = RawConfigParser(interpolation=None,
                             inline_comment_prefixes=[';'])
except TypeError:
    config = RawConfigParser()
config.optionxform = str  # Dimensions are case sensitive.
config.read(path.join(dname, 'display.ini'))
default_display_units = DisplayUnits(config.items('Default display units'))


if __name__ == '__main__':
    # Test the contents of this file.

    import doctest

    doctest.testmod()
