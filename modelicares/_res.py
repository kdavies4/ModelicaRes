#!/usr/bin/python
"""TODO

"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
from functools import wraps


def cast_sametype(f):
    """Return a method that casts its output as a :class:`SimResList`, given one
    that doesn't (*f*).
    """
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        """Function that casts its output as a :class:`SimResList`
        """
        return type(self)(f(self, *args, **kwargs))

    return wrapped

def assert_sametype(f):
    """TODO
    """
    @wraps(f)
    def wrapped(self, other):
        """TODO
        """
        t = self.__class__
        assert isinstance(other, t), ("A {obj} can only be combined with "
                                      "another {obj}.".format(obj=t.__name__))
        return f(self, other)

    return wrapped

class ResList(list):
    """TODO
    """

    @cast_sametype
    def __add__(self, *args, **kwargs):
        """TODO add doc from list"""
        return list.__add__(self, *args, **kwargs)

    def __getitem__(self, i):
        """TODO add doc from list"""
        if isinstance(i, slice):
            return type(self)(list.__getitem__(self, i))
        else:
            return list.__getitem__(self, i)

    # TODO is this needed in Python2.7?
    #@cast_sametype
    #def __getslice__(self, *args, **kwargs):
    #    """TODO add doc from list"""
    #    return list.__getslice__(self, *args, **kwargs)

    @cast_sametype
    def __mul__(self, *args, **kwargs):
        """TODO add doc from list"""
        return list.__mul__(self, *args, **kwargs)

    @cast_sametype
    @assert_sametype
    def __radd__(self, other):
        """TODO add doc from list"""
        return other + self

    @cast_sametype
    def __rmul__(self, *args, **kwargs):
        """TODO add doc from list"""
        return list.__rmul__(self, *args, **kwargs)

    def fnames(self):
        """TODO doc, example
        """
        return [sim.fname for sim in self]

    def basedir(self):
        """TODO doc, example
        """
        basedir = os.path.commonprefix([os.path.dirname(fname)
                                        for fname in self.fnames()])
        return basedir.rstrip(os.sep)

    @assert_sametype
    def extend(self, other):
        """TODO add doc from list"""
        list.extend(self, other)
        return self

    @assert_sametype
    def __add__(self, other):
        """TODO add doc from list"""
        list.__add__(self, other)
        return self

    @assert_sametype
    def __iadd__(self, other):
        """TODO add doc from list"""
        list.__iadd__(self, other)
        return self

    def __imul__(self, n):
        """TODO add doc from list"""
        list.__imul__(self, n)
        return self

    # Remove support for some list methods that are no longer applicable.
    def sort(self, other):
        raise AttributeError("'%s' object has no attribute 'sort'" % self.__class__.name)
    def __ge__(self, other):
        raise AttributeError("'%s' object has no attribute '__ge__'" % self.__class__.name)
    def __gt__(self, other):
        raise AttributeError("'%s' object has no attribute '__gt__'" % self.__class__.name)
    def __le__(self, other):
        raise AttributeError("'%s' object has no attribute '__le__'" % self.__class__.name)
    def __lt__(self, other):
        raise AttributeError("'%s' object has no attribute '__lt__'" % self.__class__.name)


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
