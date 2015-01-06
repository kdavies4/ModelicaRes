#!/usr/bin/python
"""Functions for the `design of experiments (DOE)`_

The functions below generate samples from the combination of multiple factors:

- :func:`aslisted` - Step through all the entries together.

- :func:`fullfact` - Full-factorial DOE_

- :func:`ofat` - `One-factor-at-a-time (OFAT)`_ method

Each of the functions can be called in three ways:

1. With one or more lists as positional arguments:
   The generator yields tuples with entries selected from each of the lists.

2. With one or more lists as keyword arguments:
   The generator yields dictionaries with the keywords as keys and values
   selected from the lists.

3. With a single positional argument that is a dictionary with lists as values:
   The generator yields dictionaries with the keys of the given dictionary and
   values selected its lists.

See :func:`aslisted` for examples of each of these cases.


.. _design of experiments (DOE): http://en.wikipedia.org/wiki/Design_of_experiments
.. _DOE: http://en.wikipedia.org/wiki/Design_of_experiments
.. _One-factor-at-a-time (OFAT): http://en.wikipedia.org/wiki/One-factor-at-a-time_method
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"

# TODO: Add functions for Monte Carlo, space-filling quasi-Monte Carlo, Latin
# hypercube, Morris method, etc.

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915
# pylint: disable=I0011, W0141, W0142

from itertools import product
from functools import wraps
from ..util import accept_dict


def _accept_kwargs(func):
    """Decorator to also accept keyword arguments
    """
    @wraps(func)
    def wrapped(*space, **kwargs):
        """Generator that accepts the following call signatures::

        - `wrapped`(*list1*, *list2*, ...): Returns the results of
          `func`(*list1*, *list2*, ...), which yields tuples of elements
          extracted from the lists

        - `wrapped`(*a*=*list1*, *b*=*list2*, ...):  Returns the results of
          `func`(*list1*, *list2*, ...) as values of dictionaries with keys
          'a', 'b', ..., respectively
        """
        assert not (space and kwargs), (
            "Positional and keyword arguments cannot be combined.")
        if space:
            return func(*space)
        else:
            keys = kwargs.keys()
            return (dict(zip(keys, vals)) for vals in func(*kwargs.values()))

    return wrapped


@accept_dict
@_accept_kwargs
def aslisted(*space):
    """Step through all the entries together (i.e., jointly or element-wise).

    The sequence of experiments terminates at end of the shortest list.

    **Example 1 (lists as positional arguments):**

    >>> for x in aslisted([0, 1], [0, 1], [0, 1, 2]):
    ...     print(x)
    (0, 0, 0)
    (1, 1, 1)

    **Example 2 (lists as keyword arguments):**

    .. code-block:: python

       >>> from modelicares import ParamDict

       >>> for x in aslisted(a=[0, 1], b=[0, 1], c=[0, 1, 2]):
       ...     print(ParamDict(x)) # ParamDict makes the output easier to read.
       (a=0, b=0, c=0)
       (a=1, b=1, c=1)

    **Example 3 (dictionary as a single positional argument):**

    .. code-block:: python

       >>> from modelicares import ParamDict

       >>> for x in aslisted(dict(a=[0, 1], b=[0, 1], c=[0, 1, 2])):
       ...     print(ParamDict(x)) # ParamDict makes the output easier to read.
       (a=0, b=0, c=0)
       (a=1, b=1, c=1)

     This is the same result as in example 2.  However, note that it is possible
     to represent a hierarchy using this approach in conjunction with
     :class:`~modelicares.exps.ParamDict`:

     >>> for x in aslisted({'a': [0, 1], 'b.c': [0, 1], 'b.d': [0, 1, 2]}):
     ...     print(ParamDict(x))
     (a=0, b(c=0, d=0))
     (a=1, b(c=1, d=1))
     """
    return zip(*space)


@accept_dict
@_accept_kwargs
def fullfact(*space):
    """Full-factorial DOE_

    **Example:**

    >>> for x in fullfact([0, 1], [0, 1], [0, 1, 2]):
    ...     print(x)
    (0, 0, 0)
    (0, 0, 1)
    (0, 0, 2)
    (0, 1, 0)
    (0, 1, 1)
    (0, 1, 2)
    (1, 0, 0)
    (1, 0, 1)
    (1, 0, 2)
    (1, 1, 0)
    (1, 1, 1)
    (1, 1, 2)

    It is also possible to call this function with keyword arguments or with a
    dictionary as a positional argument, like in examples 2 and 3 for
    :func:`aslisted`.
    """
    return product(*space)


@accept_dict
@_accept_kwargs
def ofat(*space):
    """`One-factor-at-a-time (OFAT)`_ method

    The first entry in each sublist is taken as the baseline value for that
    dimension.

    **Example:**

    >>> for x in ofat([0, 1], [0, 1], [0, 1, 2]):
    ...     print(x)
    (0, 0, 0)
    (1, 0, 0)
    (0, 1, 0)
    (0, 0, 1)
    (0, 0, 2)

    It is also possible to call this function with keyword arguments or with a
    dictionary as a positional argument, like in examples 2 and 3 for
    :func:`aslisted`.
    """
    baseline = [dimension[0] for dimension in space]
    yield tuple(baseline)
    for i, dimension in enumerate(space):
        for level in dimension[1:]:
            if i == 0:
                yield tuple([level] + baseline[i + 1:])
            elif i == len(space) - 1:
                yield tuple(baseline[:i] + [level])
            else:
                yield tuple(baseline[:i] + [level] + baseline[i + 1:])


if __name__ == '__main__':
    # Test the contents of this file.

    import doctest
    doctest.testmod()
