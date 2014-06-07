#!/usr/bin/python
"""This submodule contains a class and an associated wrapper to handle groups of
Modelica_ results.

.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
from functools import wraps
from modelicares.util import cast_sametype, basename

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915,
# pylint: disable=I0011, W0141, W0142


def assert_sametype(func):
    """Decorator that checks that an argument to a method is also an instance of
    the containing class
    """
    @wraps(func)
    def wrapped(self, other):
        """Method that can only operate on an instance of the containing class
        """
        if not isinstance(other, self.__class__):
            raise TypeError("A {obj} can only be combined with another "
                            "{obj}.".format(obj=self.__class__.__name__))
        return func(self, other)

    return wrapped


def compare_fnames(func):
    """Decorator that sends filenames to a comparison function
    """
    @wraps(func)
    def wrapped(self, other):
        """Method that compares filenames of *self* and *other*
        """
        try:
            return func(self.fname, other.fname)
        except AttributeError:
            raise TypeError("A {obj} instance can only be compared with "
                            "another {obj} "
                            "instance.".format(obj=self.__class__.__name__))

    return wrapped


class Res(object):
    """Base class for a Modelica_ result
    """
    # pylint: disable=E0213

    def __init__(self, fname):
        self.fname = os.path.abspath(fname)

    @compare_fnames
    def __eq__(fname1, fname2):
        """Return self == other.
        """
        return fname1 == fname2

    @compare_fnames
    def _ne__(fname1, fname2):
        """Return self != other.
        """
        return fname1 != fname2

    @compare_fnames
    def __ge__(fname1, fname2):
        """Return self >= other.
        """
        return fname1 < fname2

    @compare_fnames
    def __gt__(fname1, fname2):
        """Return self > other.
        """
        return fname1 > fname2

    @compare_fnames
    def __le__(fname1, fname2):
        """Return self <= other.
        """
        return fname1 <= fname2

    @compare_fnames
    def __lt__(fname1, fname2):
        """Return self < other.
        """
        return fname1 < fname2

    def __repr__(self):
        """Return a formal description of an instance of this class.
        """
        return "{Class}('{fname}')".format(Class=self.__class__.__name__,
                                           fname=self.fname)
        # Note:  The class name is inquired so that this method will still be
        # correct if the class is extended.

    @property
    def dirname(self):
        """Directory from which the variables were loaded
        """
        return os.path.dirname(self.fname)

    @property
    def fbase(self):
        """Base filename from which the variables were loaded, without the
        directory or file extension
        """
        return basename(self.fname)

class ResList(list):
    """Base class for a list of Modelica_ results
    """

    @cast_sametype
    def __add__(self, value):
        """Return self + value.
        """
        return list.__add__(self, value)

    @cast_sametype
    def __getslice__(self, i, j):
        """x.__getslice__(i, j) <==> x[i:j]

        Use of negative indices is not supported.
        """
        return super(ResList, self).__getslice__(i, j)

    def __getattr__(self, attr):
        """If this class does not have attribute *attr*, return a list of
        that attribute from the entries in an instance of this class.
        """
        return [getattr(res, attr) for res in self]

    def __getitem__(self, i):
        """x.__getitem__(y) <==> x[y]
        """
        if isinstance(i, slice):
            # Cast as the same type.
            return self.__class__(super(ResList, self).__getitem__(i))
        else:
            return list.__getitem__(self, i)

    @cast_sametype
    def __mul__(self, n):
        """Return self * n.
        """
        return list.__mul__(self, n)

    @cast_sametype
    @assert_sametype
    def __radd__(self, value):
        """Return value + self.
        """
        return value + self

    @cast_sametype
    def __rmul__(self, n):
        """Return n * self.
        """
        return list.__rmul__(self, n)

    @property
    def basedir(self):
        """Highest common directory that the result files share
        """
        fnames = [fname.rpartition(os.sep)[0] for fname in self.fname]
        return os.path.commonprefix(fnames).rstrip(os.sep)

    @property
    def fnames(self):
        """Filenames of the result files, resolved to *basedir*

        The get the absolute paths of the result files, use *fname* (singular).
        """
        start = len(self.basedir) + 1
        return [res.fname[start:] for res in self]

    @assert_sametype
    def extend(self, other):
        """Extend the list by appending elements from an iterable of Modelica_
        results (:class:`SimRes` or :class:`LinRes` instances, as applicable).
        """
        list.extend(self, other)
        return self

    @assert_sametype
    def __iadd__(self, value):
        """Implement self += value.
        """
        list.__iadd__(self, value)
        return self

    def __imul__(self, n):
        """Implement self *= n.
        """
        list.__imul__(self, n)
        return self

if __name__ == '__main__':
    # Test the contents of this file.

    import doctest
    doctest.testmod()
