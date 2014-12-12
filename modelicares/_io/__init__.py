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
from functools import wraps
from scipy.interpolate import interp1d
from ..util import CallList, get_indices


def select(meth):
    """Decorate a method to use time-based indexing to select values.
    """
    @wraps(meth, assigned=('__module__', '__name__')) # without __doc__
    def wrapped(self, t=None):
        """
        **Parameters:**

        - *t*: Time index

             - Default or *None*: All samples are included.

             - *float*: Interpolate to a single time.

             - *list*: Interpolate to a list of times.

             - *tuple*: Extract samples from a range of times.  The structure is
               signature to the arguments of Python's slice_ function, except
               that the start and stop values can be floating point numbers.
               The samples within and up to the limits are included.
               Interpolation is not used.

                  - (*stop*,): All samples up to *stop* are included.

                       Be sure to include the comma to establish this as a
                       tuple.

                  - (*start*, *stop*): All samples between *start* and *stop*
                    are included.

                  - (*start*, *stop*, *skip*): Every *skip*th sample between
                    *start* and *stop* is included.
        """
        def get_slice(t):
            """Return a slice that indexes the variable.

            Argument *t* is a tuple with one of the following forms:

              - (*stop*,): All samples up to *stop* are included.

                   Be sure to include the comma to establish this as a tuple.

              - (*start*, *stop*): All samples between *start* and *stop* are
                included.

              - (*start*, *stop*, *skip*): Every *skip*th sample between *start*
                and *stop* is included.
            """
            # Retrieve the start time, stop time, and number of samples to
            # skip.
            try:
                t1, t2, skip = t
            except ValueError:
                skip = None
                try:
                    t1, t2 = t
                except ValueError:
                    t1 = None
                    t2, = t
            assert t1 is None or t2 is None or t1 <= t2, (
                "The lower time limit must be less than or equal to the upper "
                "time limit.")

            # Determine the corresponding indices and return them in a tuple.
            times = self.times()
            i1 = None if t1 is None else get_indices(times, t1)[1]
            i2 = None if t2 is None else get_indices(times, t2)[0] + 1
            return slice(i1, i2, skip)

        if t is None:
            # Return all values.
            return meth(self)
        elif isinstance(t, tuple):
            # Apply a slice with optional start time, stop time, and number
            # of samples to skip.
            return meth(self)[get_slice(t)]
        else:
            # Interpolate at single time or list of times.
            meth_at_ = interp1d(self.times(), meth(self))
            # For some reason, this wraps single values as arrays, so need to
            # cast back to float.
            try:
                # Assume t is a list of times.
                return [float(meth_at_(time)) for time in t]
            except TypeError:
                # t is a single time.
                return float(meth_at_(t)) # Cast the singleton array as a float.

    wrapped.__doc__ = meth.__doc__ + wrapped.__doc__
    return wrapped


class VarDict(dict):

    """Special dictionary for simulation variables (instances of
    :class:`~modelicares.simres.Variable`)
    """

    def __getattr__(self, attr):
        """Look up a property for each of the variables (e.g., n_constants).
        """
        return CallList([getattr(variable, attr) for variable in self.values()])

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
