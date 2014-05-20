#!/usr/bin/python
"""This submodule contains a class and an associated wrapper to handle groups of
Modelica_ results.

.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
from functools import wraps
from modelicares.util import cast_sametype


def check_sametype(f):
    """Decorator that checks that an argument to a method is also an instance of
    the containing class
    """
    @wraps(f)
    def wrapped(self, other):
        """Method that can only operate on an instance of the containing class
        """
        if not isinstance(other, self.__class__):
           raise TypeError("A {obj} can only be combined with another "
                           "{obj}.".format(obj=self.__class__.__name__))
        return f(self, other)

    return wrapped

class ResList(list):
    """Base class for a list of Modelica_ results
    """

    @cast_sametype
    def __add__(self, value):
        """Return self+value.
        """
        return list.__add__(self, value)

    def __getitem__(self, i):
        """x.__getitem__(y) <==> x[y]
        """
        if isinstance(i, slice):
            return self.__class__(list.__getitem__(self, i)) # Cast as same type.
        else:
            return list.__getitem__(self, i)

    @cast_sametype
    def __mul__(self, n):
        """Return self*n.
        """
        return list.__mul__(self, n)

    @cast_sametype
    @check_sametype
    def __radd__(self, value):
        """Return value+self.
        """
        return other + self

    @cast_sametype
    def __rmul__(self, n):
        """Return n*self.
        """
        return list.__rmul__(self, n)

    def fnames(self):
        """Return a list of filenames from which the results were loaded.

        There are no arguments.
        """
        return [sim.fname for sim in self]

    def basedir(self):
        """Return the highest common directory that the result files share.

        There are no arguments.
        """
        basedir = os.path.commonprefix([os.path.dirname(fname)
                                        for fname in self.fnames()])
        return basedir.rstrip(os.sep)

    @check_sametype
    def extend(self, other):
        """Extend the list by appending elements from an iterable of Modelica_
        results (:class:`SimRes` or :class:`LinRes` instances, as applicable).
        """
        list.extend(self, other)
        return self

    @check_sametype
    def __iadd__(self, value):
        """Implement self+=value.
        """
        list.__iadd__(self, value)
        return self

    def __imul__(self, n):
        """Implement self*=n.
        """
        list.__imul__(self, n)
        return self

if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
