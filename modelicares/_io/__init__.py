#!/usr/bin/python
"""Packages to load data from various simulation and linearization formats

TODO doc

The format-dependent attributes and methods of
:class:`~modelicares.simres.SimRes` and :class:`~modelicares.linres.LinRes` are
placed here in order to support multiple formats.  However, this package
currently only contains functions to load data from OpenModelica and Dymola
(omdy).
"""

import numpy as np

from collections import namedtuple
from scipy.integrate import trapz as integral
from scipy.interpolate import interp1d

from modelicares import util


class DataEntry(namedtuple('DataEntry', ['times', 'samples', 'description',
                                         'unit', 'displayUnit'])):
    """Specialized named tuple that contains attributes and methods to
    represent a variable in a simulation

    TODO doc
    """

    def array(self, i=None, ft=None, fv=None):
        """Return an array with function *ft* of the times of the variable as
        the first column and function *fv* of the values of the variable as the
        second column.

        The times and values are taken at index or slice *i*.  If *i* is *None*,
        then all times and values are returned.
        """
        return np.array([self.times(i, ft), self.values(i, fv)]).T

    def array_wi_times(self, t1=None, t2=None, ft=None, fv=None):
        """Return an array with function *ft* of the times of the variable as
        the first column and function *fv* of the values of the variable as the
        second column, all within time range [*t1*, *t2*].
        """
        return self.array(self._slice(t1, t2), ft, fv)

    def FV(self, f=None):
        """Return function *f* of the final value of the variable.
        """
        return self.values(-1, f)

    def is_constant(self):
        """Return the *true* if the variable does not change over time.
        """
        return not np.any((np.diff(self.values()) <> 0))

    def IV(self, f=None):
        """Return function *f* of the initial value of the variable.
        """
        return self.values(0, f)

    def max(self, f=None):
        """Return the maximum value of function *f* of the variable.
        """
        return np.max(self.values(f=f))

    def mean(self, f=None):
        """Return the time-averaged mean of function *f* of the variable.
        """
        t = self.times
        return integral(self.values(f=f), t)/(t[-1] - t[0])

    def min(self, f=None):
        """Return the minimum value of function *f* of the variable.
        """
        return np.min(self.values(f=f))

    def values(self, i=None, f=None):
        """Return function *f* of the values of the variable at index or slice
        *i*.

        If *i* is *None*, then all values are returned.
        """
        return self.samples

    def values_at_times(self, times, f=None):
        """Return function *f* of the values of the variable at *times*.
        """
        return interp1d(self.times, self.values(f=f), bounds_error=False)(times)

    def values_wi_times(self, t1=None, t2=None, f=None):
        """Return function *f* of the values of the variable in the time range
        [*t1*, *t2*].
        """
        return self.values(self._slice(t1, t2), f)

    def _slice(self, t1=None, t2=None):
        """Return a slice that indexes the variable within time range
        [*t1*, *t2*].
        """
        assert t1 is None or t2 is None or t1 <= t2, (
            "The lower time limit must be less than or equal to the upper time "
            "limit.")

        times = self.times
        i1 = None if t1 is None else util.get_indices(times, t1)[1]
        i2 = None if t2 is None else util.get_indices(times, t2)[0] + 1
        return slice(i1, i2)


module_names = ['dymola']
# TODO fix:
#modules = [__import__('modelicares._io.' + name) for name in module_names]

# List of file-loading functions for SimRes:
#simloaders = [module.loadsim for module in modules]
from modelicares._io.dymola import loadsim
simloaders = [loadsim]

# List of file-loading functions for LinRes:
#linloaders = [module.loadlin for module in modules]
from modelicares._io.dymola import loadlin
linloaders = [loadlin]


if __name__ == '__main__':
    """Test the contents of this module.
    """
    import doctest
    from modelicares._io import *

    doctest.testmod()
    doctest.testmod(omdy)
