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
from functools import wraps
from scipy.integrate import trapz as integral
from scipy.interpolate import interp1d
from difflib import get_close_matches

from modelicares import util


class VarDict(dict):
    """Dictionary of variables (instances of the Variable class below)
    """
    def __getitem__(self, key):
       """Include suggestions in the error message if a variable is missing.
       """
       try:
           return dict.__getitem__(self, key)
       except KeyError:
            msg = '%s is not a valid variable name.' % key
            close_matches = get_close_matches(key, self.keys())
            if close_matches:
                msg += "\n       ".join(["\n\nDid you mean one of these?"]
                                        + close_matches)
            raise LookupError(msg)


class Variable(namedtuple('Variable', ['samples', 'description', 'unit',
                                       'displayUnit'])):
    """Specialized named tuple that contains attributes and methods to
    represent a variable in a simulation

    TODO doc
    """

    # TODO: go back to times as a method (so that units can be applied)


    def select_times(f):
        """Return a function that uses time-based indexing to return values,
        given a function that returns all values (*f*).

        If *t* is *None*, then all values are returned (pass through).
        """
        @wraps(f)
        def wrapped(self, t=None, *args, **kwargs):
            if t is None:
                # Return all values.
                return f(self, *args, **kwargs)
            elif isinstance(t, tuple):
                # Apply a slice with optional start time, stop time, and number
                # of samples to skip.
                return f(self, *args, **kwargs)[self._slice(t)]
            else:
                # Interpolate at single time or list of times.
                function_at_ = interp1d(self.times(), f(self, *args, **kwargs))
                try:
                    # Assume t is a list of times.
                    return map(function_at_, t)
                except TypeError:
                    # t is a single time.
                    return float(function_at_(t))

    @select_times
    def array(self, ft=None, fv=None):
        """Return an array with function *ft* of the times of the variable as
        the first column and function *fv* of the values of the variable as the
        second column.

        The times and values are taken at index or slice *i*.  If *i* is *None*,
        then all times and values are returned.
        """
        return np.array([self.times(ft), self.values(fv)]).T

    def FV(self, f=None):
        """Return function *f* of the final value of the variable.
        """
        return f(self.values()[-1]) if f else self.values()[-1]

    def is_constant(self):
        """Return the *true* if the variable does not change over time.
        """
        return not np.any((np.diff(self.values()) <> 0))

    def IV(self, f=None):
        """Return function *f* of the initial value of the variable.
        """
        return f(self.values()[0]) if f else self.values()[0]

    def max(self, f=None):
        """Return the maximum value of function *f* of the variable.
        """
        return np.max(self.values(f=f))

    def mean(self, f=None):
        """Return the time-averaged mean of function *f* of the variable.
        """
        t = self.times()
        return integral(self.values(f=f), t)/(t[-1] - t[0])

    def min(self, f=None):
        """Return the minimum value of function *f* of the variable.
        """
        return np.min(self.values(f=f))

    def RMS(self, f=None):
        """Return the time-averaged root mean square of function *f* of the
        variable.
        """
        t = self.times()
        return np.sqrt(integral(self.values(f=f)**2, t)/(t[-1] - t[0]))

    def times(self):
        """Return function *f* of the times of the variable.
        """
        raise NotImplementedError("This method must be redefined for specific "
                                  "file formats.")

    def values(self):
        """Return function *f* of the values of the variable.
        """
        raise NotImplementedError("This method must be redefined for specific "
                                  "file formats.")

    def _slice(self, t):
        """Return a slice that indexes the variable, given a slice-like tuple
        of times.
        """

        # Retrieve the start time, stop time, and the number of samples to skip.
        try:
            (t1, t2, skip) = t
        except ValueError:
            skip = None
            try:
                (t1, t2) = t
            except ValueError:
                t1 = None
                (t2,) = t
        assert t1 is None or t2 is None or t1 <= t2, (
            "The lower time limit must be less than or equal to the upper time "
            "limit.")

        # Determine the corresponding indices and return them in a tuple.
        times = self.times()
        i1 = None if t1 is None else util.get_indices(times, t1)[1]
        i2 = None if t2 is None else util.get_indices(times, t2)[0] + 1
        return slice(i1, i2, skip)


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
