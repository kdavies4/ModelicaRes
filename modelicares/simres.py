# !/usr/bin/python # pylint: disable=I0011, C0301, C0302
# -*- coding: utf-8 -*-
"""This submodule contains the following classes:

- :class:`SimRes` - Class to load, analyze, and plot results from a Modelica_
  simulation

- :class:`SimResSequence` - Class to load, analyze, and plot results from a
  sequence of continued Modelica_ simulations

- :class:`SimResList` - Special list of simulation results (:class:`SimRes` or
  :class:`SimResSequence` instances)

- :class:`Variable` - Special namedtuple_ to represent a variable in a
  simulation, with methods to retrieve and perform calculations on its values

- :class:`VarList` - Special list of simulation variables (instances of
  :class:`Variable`), with attributes to access information from all of the
  variables at once


.. _Modelica: http://www.modelica.org/
.. _namedtuple: https://docs.python.org/2/library/collections.html#collections.namedtuple

.. testsetup::
   >>> decimals = 4
   >>> import numpy as np
   >>> np.set_printoptions(precision=decimals)
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=I0011, C0103, E0611, E1101, R0801, R0921, W0102

import os

from collections import namedtuple
from difflib import get_close_matches
from functools import wraps
from itertools import cycle
from matplotlib import rcParams
from matplotlib.cbook import iterable
from matplotlib.pyplot import figlegend
from natu import core as nc
from natu import numpy as np
from natu import units as U
from natu.core import Quantity
from natu.util import flatten_list, multiglob
from pandas import DataFrame
from scipy.integrate import trapz
from scipy.interpolate import interp1d
from six import string_types

from . import util
from ._res import Res, ResList
from .texunit import unit2tex, number_label # TODO Use natu.

# Use Modelica formatting for dimensions and units.
from natu import config

config.default_format = 'M'


def _integral(y, x):
    """Quantity-aware integration
    """
    integral = trapz(nc.value(y), nc.value(x))
    if U._use_quantities:
        return Quantity.quicknew(integral,
                                 nc.dimension(x) + nc.dimension(y),
                                 nc.display_unit(x) + nc.display_unit(y))
    return integral


def _interp1d(x, y, *args, **kwargs):
    """1D interpolation for quantities
    """
    interp = interp1d(nc.value(x), y, *args, **kwargs)
    # x_dimension = nc.dimension(x)

    def new_interpolator(xnew):
        #assert nc.dimension(xnew) == x_dimension, (
        #    "The abscissa doesn't have the correct dimension.")
        return nc.merge(interp(nc.value(xnew)), y)

    return new_interpolator


def _select(meth):
    """Decorate a method to use time-based indexing to select values.
    """

    @wraps(meth, assigned=('__module__', '__name__')) # without __doc__
    def wrapped(self, t=None):
        """
        **Parameters:**

        - *t*: Time index

             - Default or *None*: All samples are included.

             - :class:`float`: Interpolate to a single time.

             - :class:`list` or :class:`numpy.array`: Interpolate to a sequence
               of times (returned as a :class:`list` or :class:`numpy.array`,
               respectively).

             - *tuple*: Extract samples from a range of times.  The structure is
               similar to the arguments of Python's slice_ function, except that
               the start and stop values can be floating point numbers.  The
               samples within and up to the limits are included.  There is no
               interpolation.

                  - (*stop*,): All samples up to *stop* are included.

                       Be sure to include the comma to establish this as a
                       tuple.

                  - (*start*, *stop*): All samples between *start* and *stop*
                    are included.

                  - (*start*, *stop*, *skip*): Every *skip*th sample between
                    *start* and *stop* is included.

             If a unit of time is not used to define the time(s), then the
             time(s) are interpreted using the unit system used by :mod:`natu`
             (SI by default).
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
            i1 = None if t1 is None else util.get_indices(times, t1)[1]
            i2 = None if t2 is None else util.get_indices(times, t2)[0] + 1
            return slice(i1, i2, skip)

        if t is None:
            # Return all values.
            return meth(self)
        elif isinstance(t, tuple):
            # Apply a slice with optional start time, stop time, and number
            # of samples to skip.
            return meth(self)[get_slice(t)]
        else:
            # Interpolate at a single time or list of times.
            meth_at_ = _interp1d(self.times(), meth(self))
            # For some reason, this wraps single values as arrays, so need to
            # cast back to float.
            try:
                # Assume t is a list of times.
                return type(t)(map(meth_at_, t))
            except (AttributeError, TypeError):
                # t is a single time.
                return meth_at_(t)

    wrapped.__doc__ = meth.__doc__ + wrapped.__doc__
    return wrapped


# Default class to store time and value information of a variable (for samples
# field of Variable below).
Samples = namedtuple('Samples', ['times', 'values'])


class Variable(object):
    """Class to represent a variable in a simulation, with methods to retrieve
    and perform calculations on its values

    This class is usually not instantiated directly by the user, but instances
    are returned when indexing a variable name from a simulation result
    (:class:`SimRes` instance).

    **Properties:**

    - *dimension* - The physical dimensionality of the variable

         The factors and exponents are formatted as for Modelica_ unit strings.
         This property is read-only.

    - *display_unit* - Display unit for the variable's values

         This property is settable using a Modelica_-formatted unit string
         (e.g., 'm/s2').  SI units and prefixes are recognized, as well
         `other units defined in natu
         <http://kdavies4.github.io/natu/definitions.html>`_.  An error is
         raised if the physical dimension of the display unit does not match
         *dimension*

    - *description* - String describing the variable

         This property is settable.

    If *dimension* and *display_unit* are unknown, use *None*.

    **Examples:**

    Load a simulation and retrieve a variable (instance of this class):

    >>> sim = SimRes('examples/ChuaCircuit.mat')
    >>> T = sim['G.T_heatPort']

    Get the variable's description:

    >>> T.description # doctest: +SKIP
    'Temperature of HeatPort'

    Determine if the variable is constant:

    >>> T.is_constant
    True

    .. testcleanup::

       >>> assert T.description == 'Temperature of HeatPort'

    Besides the properties above, there are methods to retrieve times, values,
    and functions of the times and values (:meth:`array`, :meth:`FV`,
    :meth:`IV`, :meth:`max`, :meth:`mean`, :meth:`mean_rectified`, :meth:`min`,
    :meth:`RMS`, :meth:`RMS_AC`, :meth:`times`, :meth:`value`, :meth:`values`).
    Please see the summary in :meth:`SimRes.__getitem__` or the full
    descriptions of those methods below.


    .. _SI: https://en.wikipedia.org/wiki/SI
    """

    __slots__ = ['_samples', '_dimension', '_display_unit', 'description']

    def __init__(self, samples, dimension, display_unit, description=""):
        self._samples = samples
        self._dimension = dimension

        try:
            self._display_unit = nc.UnitExponents.fromstr(display_unit.replace('.',
                                                                               '*'))
        except AttributeError:
            self._display_unit = display_unit

        self.description = description

    @property
    def dimension(self):
        """Physical dimension of the variable"""
        return self._dimension

    @property
    def display_unit(self):
        """Display unit"""
        return self._display_unit

    @display_unit.setter
    def display_unit(self, unit):
        """Set the display unit"""
        display_unit = nc.UnitExponents.fromstr(unit.replace('.', '*'))
        dimension = nc.dimension(U._units(**display_unit))
        assert dimension == self._dimension, (
            "The dimensionality of the display unit is %s but must be %s."
            % (dimension, self._dimension))
        self._display_unit = nc.unitspace.simplify(display_unit)

    @property
    def FV(self):
        """Return the final value of the variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the final value:

        >>> C1_v.FV()
        2.4209836
        """
        return self.values()[-1]

    @property
    def is_constant(self):
        """*True* if the variable does not change over time

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Determine if the variable is constant:

        >>> C1_v.is_constant
        False
        """
        values = self.values()
        return np.array_equal(values[:-1], values[1:])

    @property
    def IV(self):
        """Return the initial value of the variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the initial value:

        >>> C1_v.IV()
        4.0
        """
        return self.values()[0]

    @property
    def max(self):
        """Return the maximum value of the variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the maximum value:

        >>> C1_v.max()
        4.5046349
        """
        return np.max(self.values())

    @property
    def mean(self):
        """Return the time-averaged arithmetic mean value of the variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the mean value:

        >>> C1_v.mean()
        0.76859528
        """
        t = self.times()
        return _integral(self.values(), t) / (t[-1] - t[0])

    @property
    def mean_rectified(self):
        """Return the time-averaged rectified arithmetic mean value of the
        variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the rectified mean value:

        >>> C1_v.mean_rectified()
        2.2870927
        """
        t = self.times()
        return _integral(np.abs(self.values()), t) / (t[-1] - t[0])

    @property
    def min(self):
        """Return the minimum value of the variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the minimum value:

        >>> C1_v.min()
        -3.8189442
        """
        return np.min(self.values())

    @property
    def RMS(self):
        """Return the time-averaged root mean square value of the variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the root mean square value:

        >>> C1_v.RMS()
        2.4569478
        """
        t = self.times()
        return np.sqrt(_integral(self.values() ** 2, t) / (t[-1] - t[0]))

    @property
    def RMS_AC(self):
        """Return the time-averaged AC-coupled root mean square value of the
        variable.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the AC-coupled root mean square value:

        >>> C1_v.RMS_AC()
        3.1022301
        """
        t = self.times()
        mean = self.mean
        return mean + np.sqrt(_integral((self.values() - mean) ** 2, t)
                              / (t[-1] - t[0]))

    @_select
    def times(self):
        """Return the recorded times of the variable.

        **Parameters:**

        - *t*: Time index

             This may have any of the forms listed in :meth:`values`, but the
             useful ones are:

             - Default or *None*: All times are included.

             - *tuple*: Extract recorded times from a range of times.  The
               structure is similar to the arguments of Python's slice_
               function, except that the start and stop values can be floating
               point numbers.  The times within and up to the limits are
               included.  Interpolation is not used.

                  - (*stop*,): All times up to *stop* are included.

                       Be sure to include the comma to distinguish this tuple
                       from a float.

                  - (*start*, *stop*): All recorded times between *start* and
                    *stop* are included.

                  - (*start*, *stop*, *skip*): Every *skip*th recorded time is
                    included between *start* and *stop*.

        **Example:**

        Load a simulation and retrieve a variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the recorded times between 0 and 20 s:

        >>> C1_v.times(t=(0, 20))
        array([  0.,   5.,  10.,  15.,  20.], dtype=float32)
        """
        if U._use_quantities:
            return Quantity(self._samples.times, nc.dimension(U.s), 's')
        return self._samples.times

    @property
    def value(self):
        """Return the value of a constant variable.

        This method raises a :class:`ValueError` if the variable is
        time-varying.

        **Example:**

        Load a simulation and retrieve a constant variable:

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> Ro_R = sim['Ro.R']

        Get the value of the variable:

        >>> Ro_R.value()
        0.0125
        """
        values = self.values()
        if np.array_equal(values[:-1], values[1:]):
            return values[0]
        raise ValueError("The value varies.  Use values() instead of value().")

    @_select
    def values(self):
        r"""Return the values of the variable.

        **Parameters:**

        - *t*: Time index

             - Default or *None*: All samples are included.

             - *float*: Interpolate (linearly) to a single time.

             - *list*: Interpolate (linearly) to a list of times.

             - *tuple*: Extract samples from a range of times.  The structure is
               similar to the arguments of Python's slice_ function, except that
               the start and stop values can be floating point numbers.  The
               samples within and up to the limits are included.  Interpolation
               is not used.

                  - (*stop*,): All samples up to *stop* are included.

                       Be sure to include the comma to distinguish this tuple
                       from a float.

                  - (*start*, *stop*): All samples between *start* and *stop*
                    are included.

                  - (*start*, *stop*, *skip*): Every *skip*\ th sample is
                    included between *start* and *stop*.

        **Examples:**

        Load a simulation and retrieve a variable.

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> C1_v = sim['C1.v']

        Get the recorded values between 0 and 20 s:

        >>> C1_v.values(t=(0, 20)) # doctest: +NORMALIZE_WHITESPACE
        array([ 4.    ,  3.8827,  3.8029,  3.756 ,  3.7374], dtype=float32)

        Get the interpolated values at 2.5 and 17.5 s:

        >>> C1_v.values(t=[2.5, 17.5])
        [3.941368936561048, 3.7467045785160735]
        """
        if U._use_quantities:
            return Quantity.quicknew(self._samples.values, self._dimension,
                                     self._display_unit)
        return self._samples.values

# List of file-loading functions for SimRes
from ._io.dymola import readsim as dymola

READERS = [('dymola', dymola)] # SimRes tries these in order.
# All of the keys should be in lowercase.
# This must be below the definition of Variable because that class is required
# by the loading functions.
# TODO: Avoid this cyclic import--readsim requires Variable, which is defined
# here so that it's included in the documentation.


def _get_sims(fnames):
    """Return a list of :class:`SimRes` instances from a list of filenames.

    No errors are given unless no files could be loaded.
    """
    sims = []
    for fname in fnames:
        try:
            sims.append(SimRes(fname))
        except (AssertionError, IndexError, IOError, KeyError, TypeError,
                ValueError):
            continue
    assert len(sims) > 0, "No simulations were loaded."
    return sims


class VarList(list):
    """Special list of simulation variables (instances of :class:`Variable`),
    allowing access to information from all of the variables at once

    The properties and methods of this class are the same as :class:`Variable`,
    except that they return lists.  Each entry in the list is the result of
    accessing or calling the corresponding property or method of each simulation
    result.

    This class is typically not instantiated directly by the user, but instances
    are returned when indexing multiple variables from a simulation result
    (:meth:`~SimRes.__call__` method of a :class:`SimRes` instance) or a single
    variable from multiple simulations (:meth:`~SimResList.__getitem__` method
    of a :class:`SimResList`).  In the case of indexing multiple variables from
    a simulation result, this list may be nested.

    **Examples:**

    .. testsetup::

       >>> from modelicares import SimRes, SimResList

    Multiple variables from a simulation:

    >>> sim = SimRes('examples/ChuaCircuit.mat')
    >>> voltages = sim(['C1.v', 'L.v'])
    >>> voltages.FV()
    [2.4209836, -0.25352862]

    Single variable from multiple simulations:

    >>> sims = SimResList('examples/ChuaCircuit/*/')
    >>> sims['C1.v'].mean() # doctest: +SKIP
    [-1.6083468, 0.84736514]

    .. testcleanup:

       >>> sims.sort()
       >>> sims['C1.v'].mean()
       [-1.6083468, 0.84736514]
    """
    # pylint: disable=I0011, E0213

    def _listmethod(meth):
        """Return a method that operates on all of the variables in the list of
        variables, given a function that operates on a single variable.
        """

        @wraps(meth)
        def wrapped(self, attr):
            """Traverse the list recursively until the argument is a single
            variable, then pass it to the method and return the result upwards.
            """
            # pylint: disable=I0011, E1102
            return util.CallList([meth(variable, attr)
                                  if isinstance(variable, Variable) else
                                  wrapped(variable, attr)
                                  for variable in self])

        return wrapped

    @_listmethod
    def __getattr__(variable, attr):
        """Return a list of containing an attribute of each of the variables
        (e.g., values or unit).

        The list is callable if the attribute is a method.
        """
        return getattr(variable, attr)


class SimRes(Res, dict):
    """Class to load, analyze, and plot results from a Modelica_ simulation

    **Initialization parameters:**

    - *fname*: Name of the file (including the directory if necessary)

         '/' can be used as a path separator in both Windows and Unix/Linux.

    - *constants_only*: *True* (default) to load only the variables from the
      first data table

         The first data table typically contains all of the constants,
         parameters, and variables that don't vary.  If only that
         information is needed, it may save resources to set
         *constants_only* to *True*.

    - *tool*: String indicating the simulation tool that created the file
      and thus the function to be used to load it

         By default (*None), the available functions are tried in order until
         one works (or none do).

    **Methods:**

    A :class:`SimRes` instance is a special dictionary with variable names as
    keys and corresponding :class:`Variable` instances as values.  The following
    built-in dictionary methods may be used:

    - :meth:`__contains__` (invoked as ``name in sim``, where ``name`` is a
      string containing the name of a variable) - Return *True* if a variable is
      present in the simulation results.

         **Example:**

         .. code-block:: python

            >>> sim = SimRes('examples/ChuaCircuit.mat')

            >>> # 'L.v' is a valid variable name:
            >>> 'L.v' in sim
            True
            >>> # but 'x' is not:
            >>> 'x' in sim
            False

    - :meth:`__getitem__` (invoked as ``sim[name]``, where ``name`` is a string
      containing the name of a variable) - Access a :class:`Variable` by name.

         This method returns a :class:`Variable` instance, which has the
         following properties:

         - :attr:`~Variable.description` - The Modelica_ variable's description
           string

         - :attr:`~Variable.display_unit` - The Modelica_ variable's
           *displayUnit* attribute as an :class:`natu.exponents.Exponents`
           instance

               The Modelica_ variable's *unit* attribute is used if
               *displayUnit* is not specified.

         - :meth:`~Variable.FV` - Return the final value of the variable.

         - :meth:`~Variable.IV` - Return the initial value of the variable.

         - :attr:`~Variable.is_constant` - *True*, if the variable does not
           change over time

         - :meth:`~Variable.max` - Return the maximum value of the variable.

         - :meth:`~Variable.mean` - Return the time-averaged value of the
           variable.

         - :meth:`~Variable.mean_rectified` - Return the time-averaged absolute
           value of the variable.

         - :meth:`~Variable.min` - Return the minimum value of the variable.

         - :meth:`~Variable.RMS` - Return the time-averaged root mean square
           value of the variable.

         - :meth:`~Variable.RMS_AC` - Return the time-averaged AC-coupled root
           mean square value of the variable.

         - :attr:`~Variable.unit` - The Modelica_ variable's *unit* attribute

         - :meth:`~Variable.value` - Return the value of the variable if it is
           a constant (otherwise, error).

         The following methods are also available:

         - :meth:`~Variable.times` - Return the sample times of the variable.

         - :meth:`~Variable.values` - Return the values of the variable.

         **Examples:**

         .. code-block:: python

            >>> sim = SimRes('examples/ChuaCircuit.mat')

            >>> sim['L.v'].unit
            'V'

            >>> sim['L.v'].values(t=(10, 25)) # doctest: +NORMALIZE_WHITESPACE
            array([ 0.2108,  0.3046,  0.3904,  0.468 ], dtype=float32)

    - :meth:`__iter__` (used via ``list(sim)``, ``sorted(sim)``,
      ``for name in sim``, etc.) - Return an iterable of the names of the
      variables loaded from the simulation.

    - :meth:`__len__` (invoked as ``len(sim)``) - Return the number of variables
      loaded from the simulation.

         This includes the time variable.

         **Example:**

         >>> sim = SimRes('examples/ChuaCircuit.mat')
         >>> print("There are %i variables in the %s simulation." %
         ...       (len(sim), sim.fbase))
         There are 62 variables in the ChuaCircuit simulation.

    - :meth:`items` (invoked as ``sim.items()`): Return a list (Python 2.x) or
      iterable view (Python 3.x) of tuples of variable names and corresponding
      :class:`Variable` instances.

    - :meth:`keys` (invoked as ``sim.keys()`): Return a list (Python 2.x) or
      iterable view (Python 3.x) of variable names.

    - :meth:`values` (invoked as ``sim.values()`): Return a list (Python 2.x) or
      iterable view (Python 3.x) of :class:`Variable` instances corresponding to
      the keys.

    These methods may also be used:

    - :meth:`__call__` (invoked as ``sim(names)``, where ``names`` is a list of
      variable names) - Access a list of variables by their names.

         Like :meth:`__getitem__` above, the return value has attributes and
         methods to retrieve information
         about all of the variables in the list at once (values, times, IV,
         etc.).

    - :meth:`__getattr__` (invoked as ``sim.attribute``, where ``attribute`` is
      the literal name of an attribute) - Return a dictionary containing the
      variable names as keys and the requested attribute of the variables as the
      values.

         If the attribute is a method, it is possible to call the dictionary.
         The result of the call is a new dictionary containing the variable
         names as keys and the return values as the values.

    **Other methods:**

    - :meth:`browse` - Launch a variable browser.

    - :meth:`find` - Find variable names that match a pattern.

    - :meth:`plot` - Plot data as points and/or curves in 2D Cartesian
      coordinates.

    - :meth:`sankey` - Create a figure with one or more Sankey diagrams.

    - :meth:`to_pandas` - Return a `pandas DataFrame`_ with selected variables.

    **Properties:**

    - :attr:`dirname` - Directory from which the variables were loaded

    - :attr:`fbase` - Base filename from which the results were loaded, without
      the directory or file extension.

    - :attr:`fname` - Filename from which the variables were loaded, with
      absolute path

    - :attr:`n_constants` - Number of variables that do not change over time

    - :attr:`names` - List of all the variable names

    - :attr:`tool` - String indicating the function used to load the results
      (named after the corresponding Modelica_ tool)

    **Examples:**

    .. code-block:: python

       >>> # Loading a simulation:
       >>> sim = SimRes('examples/ChuaCircuit.mat')
       >>> print(sim) # doctest: +ELLIPSIS
       Modelica simulation results from .../examples/ChuaCircuit.mat

       >>> # Looking up a property across all variables:
       >>> sim.IV # doctest: +SKIP +ELLIPSIS
       {...
        'C1.v': 4.0,
       ...
        'C2.v': 0.0,
       ...
        'L.L': 18.0,
       ...}

       >>> # Calling a method across all variables and simulations:
       >>> sim.values(t=10) # doctest: +SKIP +ELLIPSIS
       {...
        'C1.v': 3.8029...,
       ...
        'C2.v': 0.2115...,
       ...
        'L.L': 18.0,
       ...}

    .. testcleanup::

       >>> IVs = sim.IV
       >>> IVs['C1.v']
       4.0
       >>> IVs['C2.v']
       0.0
       >>> IVs['L.L']
       18.0

       >>> values = sim.values(t=10)
       >>> IVs['C1.v'] # doctest: +ELLIPSIS
       3.8029...
       >>> IVs['C2.v'] # doctest: +ELLIPSIS
       0.2115...
       >>> IVs['L.L']
       18.0


    .. _Python: http://www.python.org/
    .. _pandas DataFrame:
       http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html?highlight=dataframe#pandas.DataFrame
    """

    def __init__(self, fname='dsres.mat', constants_only=False, tool=None):
        """Upon initialization, read Modelica_ simulation results from a file.

        See the top-level class documentation.
        """

        # Read the file.
        fname = util.cleanpath(fname)
        if tool is None:
            # Read the file and store the variables.
            for tool, read in READERS[:-1]:
                try:
                    variables = read(fname, constants_only)
                except IOError:
                    raise
                except Exception as exception:
                    print("The %s reader gave the following error message:\n%s"
                          % (tool, exception.args[0]))
                    continue
                else:
                    break
            tool, read = READERS[-1]
        else:
            readerdict = dict(READERS)
            try:
                read = readerdict[tool.lower()]
            except KeyError:
                raise LookupError("%s isn't one of the available tools (%s)."
                                  % (tool, ', '.join(list(readerdict))))
        variables = read(fname, constants_only)
        self.update(variables)

        # Remember the tool and filename.
        self.tool = tool
        super(SimRes, self).__init__(fname)

    # TODO: Remove the "_" prefix and add this to the list once it's finished.
    def _bar(self, names, times=[0], width=0.6, n_rows=1,
             title=None, subtitles=[], label="bar",
             xlabel=None, xticklabels=None, ylabel=None,
             left=rcParams['figure.subplot.left'],
             right=1 - rcParams['figure.subplot.right'],
             bottom=rcParams['figure.subplot.bottom'],
             top=1 - rcParams['figure.subplot.top'],
             hspace=0.1, vspace=0.25,
             leg_kwargs=None, **kwargs):
        r"""Create a sequence of bar plots at times.

        **Parameters:**

        - *names*: List of names of the variables to be plotted

             The names should be fully qualified (i.e., relative to the root of
             the simulation results).

        - *times*: List of times at which the variables should be sampled

             If multiple times are given, then subfigures will be generated.

        - *width*: Width of the bars

            At ``width = 1``, there is no overlap.

        - *n_rows*: Number of rows of (sub)plots

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be the base
             filename of the source.  Use '' for no title.

        - *subtitles*: List of subtitles (i.e., titles for each subplot)

             If not provided, "t = *xx* s" will be used, where *xx* is the time
             of each entry.  "(initial)" or "(final)" is appended if
             appropriate.

        - *label*: Label for the figure

             This is used as the base filename if the figure is saved using
             :func:`~modelicares.util.save` or
             :func:`~modelicares.util.saveall`.

        - *xlabel*: Label for the x-axes (only shown for the subplots on the
          bottom row)

        - *xticklabels*: Labels for the x-axis ticks (only shown for the
          subplots on the bottom row)

        - *ylabel*: Label for the y-axis (only shown for the subplots on the
          left column)

        - *left*: Left margin

        - *right*: Right margin

        - *bottom*: Bottom margin

        - *top*: Top margin

        - *hspace*: Horizontal space between columns of subplots

        - *vspace*: Vertical space between rows of subplots

        - *leg_kwargs*: Dictionary of keyword arguments for
          :func:`matplotlib.pyplot.legend`

             If *leg_kwargs* is *None*, then no legend will be shown.

        - *\*\*kwargs*: Additional arguments for  :func:`matplotlib.pyplot.bar`

        **Returns:**

        1. List of the axes within the figure
        """
        raise NotImplementedError
        # Base this on sankey().

        # Indices for the bars (1, 2, ...)
        ind = np.arange(len(names)) + 1

        # Create a title if necessary.
        if title is None:
            title = self.fbase

        # Set up the subplots.
        n_plots = len(times) # Number of plots
        ax = util.setup_subplots(n_plots=n_plots, n_rows=n_rows,
                                 title=title, subtitles=subtitles, label=label,
                                 xlabel=xlabel, xticks=ind,
                                 xticklabels=xticklabels,
                                 ylabel=ylabel,
                                 left=left, right=right, bottom=bottom, top=top,
                                 hspace=hspace, vspace=vspace)[0]

        # Create the bar plots.
        for axis, time in zip(ax, times):
            axis.bar(ind - width / 2., self(names).values(time),
                     width, **kwargs)
            a = axis.axis()
            axis.axis([0, ind[-1] + 1, a[2], a[3]])

        # Decorate and finish.
        if leg_kwargs is not None:
            loc = leg_kwargs.pop('loc', 'best')
            if len(ax) == 1:
                ax[0].legend(loc=loc, **leg_kwargs)
            else:
                figlegend(ax[0].lines, **leg_kwargs)
        return ax

    def browse(self):
        """Launch a variable browser.

        When a variable is selected, the right panel shows its attributes and
        a simple plot of the variable over time.  Variable names can be dragged
        and dropped into a text editor.

        There are no arguments or return values.

        **Example:**

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> sim.browse() # doctest: +SKIP

        .. image:: _static/browse.png
           :scale: 80 %
           :alt: variable browser
        """
        try:
            import wx
        except ImportError:
            raise ImportError("wx (aka wxPython) must be installed to used the "
                              "variable browser.  It is available at "
                              "http://www.wxpython.org/")

        from ._gui import Browser

        def do_work():
            """Launch the broswer."""
            # pylint: disable=E1101
            app = wx.GetApp()
            if app is None:
                app = wx.App()
            frame = Browser(None, -1, self)
            frame.Show(True)
            app.SetTopWindow(frame)
            app.MainLoop()

        # TODO: Fix multithreading so that the browser runs in the background.
        # import threading
        # thread = threading.Thread(target=_do_work)
        # thread.setDaemon(True)
        # thread.start()

        do_work()

    @property
    def names(self):
        """List of all of the variable names

        The names are sorted alphabetically.

        **Example:**

        .. code-block:: python

           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> # Names for voltages across all of the components:
           >>> sim.names # doctest: +SKIP
           ['C1.v', 'C2.v', 'G.v', 'L.v', 'Nr.v', 'Ro.v']

        .. testcleanup::

           >>> sorted(sim.names) # doctest: +ELLIPSIS
           ['C1.C', 'C1.der(v)', 'C1.i', 'C1.n.i', ..., 'Time']
        """
        return sorted(self)

    def find(self, pattern=None, re=False, constants_only=False):
        r"""Find variable names that match a pattern.

        By default, all names are returned.  The names are sorted
        alphabetically.

        **Parameters:**

        - *pattern*: Case-sensitive string used for matching

          - If *re* is *False* (next argument), then the pattern follows the
            Unix shell style:

            ============   ============================
            Character(s)   Role
            ============   ============================
            \*             Matches everything
            ?              Matches any single character
            [seq]          Matches any character in seq
            [!seq]         Matches any char not in seq
            ============   ============================

            Wildcard characters ('\*') are not automatically added at the
            beginning or the end of the pattern.  For example, '\*x\*' matches
            all variables that contain "x", but 'x\*' matches only the variables
            that begin with "x".

          - If *re* is *True*, the regular expressions are used a la `Python's
            re module <http://docs.python.org/2/library/re.html>`_.  See also
            http://docs.python.org/2/howto/regex.html#regex-howto.

            Since :func:`re.search` is used to produce the matches, it is as if
            wildcards ('.*') are automatically added at the beginning and the
            end.  For example, 'x' matches all variables that contain "x".  Use
            '^x$' to match only the variables that begin with "x" and 'x$' to
            match only the variables that end with "x".

            Note that '.' is a subclass separator in Modelica_ but a wildcard in
            regular expressions.  Escape subclass separators as '\\.'.

        - *re*: *True* to use regular expressions (*False* to use shell style)

        - *constants_only*: *True* to include only the variables that do not
          change over time

        **Example:**

        .. code-block:: python

           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> # Names for voltages across all of the components:
           >>> sim.find('^[^.]*.v$', re=True) # doctest: +SKIP
           ['C1.v', 'C2.v', 'G.v', 'L.v', 'Nr.v', 'Ro.v']

        .. testcleanup::

           >>> sorted(sim.find('^[^.]*.v$', re=True))
           ['C1.v', 'C2.v', 'G.v', 'L.v', 'Nr.v', 'Ro.v']
        """
        # Get a list of all the variables or just the constants.
        names = self.names
        if constants_only:
            names = [name for name in names if self[name].is_constant]

        # Return the filtered list.
        return util.match(names, pattern, re)

    @property
    def n_constants(self):
        """Number of variables that do not change over time.

        Note that this number may be greater than the number of declared
        constants in the Modelica_ model, since a variable may have a constant
        value even if it is not declared as a constant.

        **Example:**

        .. code-block:: python

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> print("There are %i constants in the %s simulation." %
           ...       (sim.n_constants, sim.fbase))
           There are 23 constants in the ChuaCircuit simulation.
        """
        return sum(self.is_constant)

    def plot(self, y1=[], ylabel1=None, f1={}, legends1=[],
             leg1_kwargs={'loc': 'best'}, ax1=None,
             y2=[], ylabel2=None, f2={}, legends2=[],
             leg2_kwargs={'loc': 'best'}, ax2=None,
             x='Time', xlabel=None,
             title=None, label="xy", incl_prefix=False, suffix=None,
             use_paren=True, **kwargs):
        r"""Plot variables as points and/or curves in 2D Cartesian coordinates.

        The abscissa may be time or any other variable (i.e., scatterplots are
        possible).

        **Parameters:**

        - *y1*: Name or list of names of variables for the primary y axis

             If any names are invalid, then they will be skipped.

        - *ylabel1*: Label for the primary y axis

             If *ylabel1* is *None* (default) and all of the variables have the
             same Modelica_ description string, then it will be used as the
             label.  Use '' for no label.  The units will be automatically
             noted, so they should not be included here.

        - *f1*: Dictionary of labels and functions for additional traces to be
          plotted on the primary y axis

             The functions take as the input a list of the vectors of values of
             the variables in *y1*, sampled at the values of the 'Time'
             variable.

        - *legends1*: List of legend entries for variables assigned to the
          primary y axis

             If *legends1* is an empty list ([]), y1 will be used along with the
             keys from the *f1* dictionary.  If *legends1* is *None* and all of
             the variables on the primary axis have the same unit, then no
             legend will be shown.

        - *leg1_kwargs*: Dictionary of keyword arguments for the primary legend

        - *ax1*: Primary y axes

             If *ax1* is not provided, then axes will be created in a new
             figure.

        - *y2*, *ylabel2*, *f2*, *legends2*, *leg2_kwargs*, and *ax2*: Similar
          to *y1*, *ylabel1*, *f1*, *legends1*, *leg1_kwargs*, and *ax1* but for
          the secondary y axis

        - *x*: Name of the x-axis variable

        - *xlabel*: Label for the x axis

             If *xlabel* is *None* (default), the variable's Modelica_
             description string will be applied.  Use '' for no label.

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be the base
             filename.  Use '' for no title.

        - *label*: Label for the figure (ignored if *ax* is provided)

             This is used as the base filename if the figure is saved using
             :func:`~modelicares.util.save` or
             :func:`~modelicares.util.saveall`.

        - *incl_prefix*: If *True*, prefix the legend strings with the base
          filename of the class.

        - *suffix*: String that will be added at the end of the legend entries

        - *use_paren*: Add parentheses around the suffix

        - *\*\*kwargs*: Propagated to :func:`modelicares.util.plot` and then to
          :func:`matplotlib.pyplot.plot`.

             If both y axes are used (primary and secondary), then the *dashes*
             argument is ignored.  The curves on the primary axis will be solid
             and the curves on the secondary axis will be dotted.

        **Returns:**

        1. *ax1*: Primary y axes

        2. *ax2*: Secondary y axes

        **Example:**

        .. plot:: examples/ChuaCircuit.py
           :alt: plot of Chua circuit
        """
        # Note:  y1 is the first argument (besides self) so that plot() can be
        # called with simply a variable name.

        def ystrings(ynames, ylabel, legends, funcs):
            """Generate a y-axis label and set of legend entries.
            """
            if ynames:
                if ylabel is None: # Try to create a suitable axis label.
                    descriptions = self(ynames).description
                    # If the descriptions are the same, label the y axis with
                    # the 1st one.
                    ylabel = descriptions[0]
                    if len(set(descriptions)) != 1:
                        print("The y-axis variable descriptions are different. "
                              " The first has been used as the axis label. "
                              " Please check it and provide ylabel1 or ylabel2"
                              " to override it if necessary.")
                if legends == []:
                    legends = ynames + list(funcs)
                if incl_prefix:
                    legends = [self.fbase + ': ' + leg for leg in legends]
                if suffix:
                    legends = ([leg + ' (%s)' % suffix for leg in legends]
                               if use_paren else
                               [leg + suffix for leg in legends])
                variables = self(ynames)
                dimensions = variables.dimension
                if len(ynames) == 1 or dimensions[1:] == dimensions[:-1]:
                    # The variables have the same dimension; use the first
                    # variable's display unit.
                    display_unit = variables[0]._display_unit
                    if ylabel != "":
                        ylabel = number_label(ylabel, display_unit)
                    display_units = [U._units(**display_unit)] * len(variables)
                else:
                    # Show the units in the legend.
                    if legends:
                        for i, unit in enumerate(variables._display_unit):
                            legends[i] = number_label(legends[i], unit)
                    else:
                        legends = [number_label(name, unit) for name, unit in
                                   zip(ynames, variables._display_unit)]
                        legends += list(funcs)
                    display_units = [U._units(**unit)
                                     for unit in variables._display_unit]
            else:
                display_units = []

            return ylabel, legends, display_units

        # Process the inputs.
        y1 = flatten_list(y1)
        y2 = flatten_list(y2)
        assert y1 or y2, "No signals were provided."
        if title is None:
            title = self.fbase

        # Create primary and secondary axes if necessary.
        if not ax1:
            fig = util.figure(label)
            ax1 = fig.add_subplot(111)
        if y2 and not ax2:
            ax2 = ax1.twinx()

        # Generate the x-axis label.
        if xlabel is None:
            xlabel = 'Time' if x == 'Time' else self[x].description
            # With Dymola 7.4, the description of the time variable will be
            # "Time in", which isn't good.
        if xlabel != "":
            xlabel = number_label(xlabel, self[x].display_unit)

        # Generate the y-axis labels and sets of legend entries.
        ylabel1, legends1, units1 = ystrings(y1, ylabel1, legends1, f1)
        ylabel2, legends2, units2 = ystrings(y2, ylabel2, legends2, f2)

        # Retrieve the data.
        time = self['Time']
        all_times = time.values()
        time_unit = U._units(**time._display_unit)
        yvars1 = self(y1)
        yvars2 = self(y2)
        if x == 'Time':
            y1 = [value / unit for value, unit in zip(yvars1.values(), units1)]
            if f1:
                y1_all = yvars1.values(all_times)
                y1 += [f(y1_all) for f in f1.values()]
            y2 = [value / unit for value, unit in zip(yvars2.values(), units2)]
            if f2:
                y2_all = yvars2.values(all_times)
                y2 += [f(y2_all) for f in f2.values()]
        else:
            x = self[x].values()
            times = self[x].times()
            y1 = yvars1.values(times)
            y1 += [f(y1) for f in f1.values()]
            y2 = yvars2.values(times)
            y2 += [f(y2) for f in f2.values()]

        # Plot the data.
        if y2:
            y2times = ([time / time_unit for time in yvars2.times()]
                       + [all_times] * len(f2) if x == 'Time' else x)
        if y1:
            y1times = ([time / time_unit for time in yvars1.times()]
                       + [all_times] * len(f1) if x == 'Time' else x)
            if y2:
                # Use solid lines for the primary axis and dotted lines for the
                # secondary.
                kwargs['dashes'] = [(None, None)]
                util.plot(y1, y1times, ax1, label=legends1, **kwargs)
                kwargs['dashes'] = [(3, 3)]
                util.plot(y2, y2times, ax2, label=legends2, **kwargs)
            else:
                util.plot(y1, y1times, ax1, label=legends1, **kwargs)
        elif y2:
            util.plot(y2, y2times, ax2, label=legends2, **kwargs)

        # Decorate the figure.
        ax1.set_title(title)
        ax1.set_xlabel(xlabel)
        if ylabel1:
            ax1.set_ylabel(ylabel1)
        if ylabel2:
            ax2.set_ylabel(ylabel2)
        if legends1:
            if legends2:
                # Put the primary legend in the upper left and secondary in
                # upper right.
                leg1_kwargs['loc'] = 2
                leg2_kwargs['loc'] = 1
                ax1.legend(**leg1_kwargs)
                ax2.legend(**leg2_kwargs)
            else:
                ax1.legend(**leg1_kwargs)
        elif legends2:
            ax2.legend(**leg2_kwargs)

        return ax1, ax2

    def sankey(self, names=[], times=[0], n_rows=1, title=None, subtitles=[],
               label="sankey",
               left=0.05, right=0.05, bottom=0.05, top=0.1,
               hspace=0.1, vspace=0.25, **kwargs):
        r"""Create a figure with one or more Sankey diagrams.

        **Parameters:**

        - *names*: List of names of the flow variables

        - *times*: List of times at which the variables should be sampled

             If multiple times are given, then subfigures will be generated,
             each with a Sankey diagram.

        - *n_rows*: Number of rows of subplots

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be "Sankey
             Diagram of *fbase*", where *fbase* is the base filename of the
             data.  Use '' for no title.

        - *subtitles*: List of titles for each subplot

             If not provided, "t = x s" will be used, where x is the time of
             each entry.  "(initial)" or "(final)" is appended if applicable.

        - *label*: Label for the figure

             This is used as the base filename if the figure is saved using
             :func:`~modelicares.util.save` or
             :func:`~modelicares.util.saveall`.

        - *left*: Left margin

        - *right*: Right margin

        - *bottom*: Bottom margin

        - *top*: Top margin

        - *hspace*: Horizontal space between columns of subplots

        - *vspace*: Vertical space between rows of subplots

        - *\*\*kwargs*: Additional arguments for
          :class:`matplotlib.sankey.Sankey`

        **Returns:**

        1. List of :class:`matplotlib.sankey.Sankey` instances of the subplots

        **Example:**

        .. plot:: examples/ThreeTanks.py
           :alt: Sankey diagram of three tanks
        """
        from matplotlib.sankey import Sankey

        # Retrieve the data.
        n_plots = len(times)
        Qdots = self(names).values(times)
        start_time = self['Time'].IV()
        stop_time = self['Time'].FV()

        # Create a title if necessary.
        if title is None:
            title = "Sankey diagram of " + self.fbase

        # Determine the units of the data.
        flow_unit = self(names).unit
        assert len(set(flow_unit)) == 1, (
            "The variables have inconsistent units.")
        flow_unit = flow_unit[0]

        # Set up the subplots.
        if not subtitles:
            unit = unit2tex(self('Time').unit) # TODO: Use natu for time.
            subtitles = ["t = %s %s" % (time, unit) for time in times]
            for i, time in enumerate(times):
                if time == start_time:
                    subtitles[i] += " (initial)"
                elif time == stop_time:
                    subtitles[i] += " (final)"
        axes = util.setup_subplots(n_plots=n_plots, n_rows=n_rows, title=title,
                                   subtitles=subtitles, label=label,
                                   left=left, right=right, bottom=bottom,
                                   top=top,
                                   hspace=hspace, vspace=vspace)[0]

        # Create the plots.
        sankeys = []
        for i, ax in enumerate(axes):
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            sankeys.append(Sankey(ax, flows=[Qdot[i] for Qdot in Qdots],
                                  unit=flow_unit, **kwargs).finish())
        return sankeys

    def to_pandas(self, names=None, aliases={}):
        """Return a `pandas DataFrame`_ with values from selected variables.

        The index is time.  The column headings indicate the variable names and
        units.

        The data frame has methods for further manipulation and exporting (e.g.,
        :meth:`~pandas.DataFrame.to_clipboard`,
        :meth:`~pandas.DataFrame.to_csv`, :meth:`~pandas.DataFrame.to_excel`,
        :meth:`~pandas.DataFrame.to_hdf`, and
        :meth:`~pandas.DataFrame.to_html`).

        **Parameters:**

        - *names*: String or list of strings of the variable names

             If *names* is *None* (default), then all variables are included.

        - *aliases*: Dictionary of aliases for the variable names

             The keys are the "official" variable names from the Modelica_ model
             and the values are the names as they should be included in the
             column headings.  Any variables not in this list will not be
             aliased.  Any unmatched aliases will not be used.

        **Examples:**

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> voltages = sim.find('^[^.]*.v$', re=True)
        >>> sim.to_pandas(voltages) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
                  C1.v / V  C2.v / V   G.v / V   L.v / V  Nr.v / V  Ro.v / V
        Time / s
        0         4.000000  0.000000 -4.000000  0.000000  4.000000  0.000000
        5         3.882738  0.109426 -3.773312  0.109235  3.882738  0.000191
        ...
        [514 rows x 6 columns]

        We can relabel columns using the *aliases* argument:

        >>> sim = SimRes('examples/ThreeTanks.mat')
        >>> aliases = {'tank1.level': "Tank 1 level",
        ...            'tank2.level': "Tank 2 level",
        ...            'tank3.level': "Tank 3 level"}
        >>> sim.to_pandas(list(aliases), aliases) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
                   Tank 1 level / m  Tank 2 level / m  Tank 3 level / m
        Time / s
        0.000000           8.000000          3.000000          3.000000
        0.400000           7.974962          2.990460          3.034578
        0.800000           7.950003          2.981036          3.068961
        1.200000           7.925121          2.971729          3.103150
        1.600000           7.900317          2.962539          3.137144
        ...
        [502 rows x 3 columns]
        """
        # Note: The frst doctest above requires pandas >= 0.14.0.  Otherwise,
        # more decimal places are shown in the Time column.

        # Create the list of variable names.
        if names:
            names = set(flatten_list(names))
            names.add('Time')
        else:
            names = self.names

        # Create a dictionary of names and values.
        times = self['Time'].values()
        data = {}
        for name in names:

            # Get the values.
            if np.array_equal(self[name].times(), times):
                values = self[name].values() # Save computation.
            else:
                values = self[name].values(t=times) # Resample.

            unit = self[name].unit

            # Apply an alias if available.
            try:
                name = aliases[name]
            except KeyError:
                pass

            if unit:
                data.update({name + ' / ' + unit: values})
            else:
                data.update({name: values})

        # Create the pandas data frame.
        return DataFrame(data).set_index('Time / s')

    def __call__(self, names):
        """Access a list of variables by their names.

        This method returns :class:`VarList`, give access to retrieve properties
        and call methods on all of the variables at once.  Please see
        :class:`Variable` or :meth:`__getitem__` for more information about the
        the accessible attributes.

        **Arguments**:

        - *names*: List of variable names

             The list can be nested, and the results will retain the hierarchy.
             If *names* is a single variable name, then the result is the same
             as from :meth:`__getitem__`.

        **Example**:

        .. testsetup::

           >>> from modelicares import SimRes

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> sim(['L.v', 'L.i']).unit
        ['V', 'A']
        """

        def entries(names):
            """Create a (possibly nested) list of data entries given a (possibly
            nested) list of variable names.
            """
            if isinstance(names, string_types):
                return self[names]
            return [entries(name) for name in names] # Recursion

        assert not isinstance(names, string_types), (
            "Use square brackets (__getitem__ method) to retrieve a single "
            "variable.")
        return VarList(entries(names))

    def __getitem__(self, key):
        """Include suggestions in the error message if a variable is missing.
        """
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            msg = key + " isn't a valid variable name."
            close_matches = get_close_matches(key, self.keys())
            if close_matches:
                msg += "\n       ".join(["\n\nDid you mean one of these?"]
                                        + close_matches)
            raise LookupError(msg)

    def __getattr__(self, attr):
        """Return a dictionary containing the variable names as keys and the
        requested attribute of the variables as the values.

        If the attribute is a method, it is possible to call the dictionary.
        The result of the call is a new dictionary containing the variable names
        as keys and the return values as the values.
        """
        values = (getattr(value, attr) for value in self.values())
        try:
            return util.CallDict(zip(self.keys(), values))
        except ValueError:
            if attr == 'value' and len(self) <> self.n_constants:
                raise ValueError("The variables aren't all constants.  "
                                 "Use values() instead of value.")
            raise

    def __str__(self):
        """Return an informal description of the :class:`SimRes` instance.

        **Example:**

        >>> sim = SimRes('examples/ChuaCircuit.mat')
        >>> print(sim) # doctest: +ELLIPSIS
        Modelica simulation results from ...ChuaCircuit.mat
        """
        return "Modelica simulation results from " + self.fname

    def get_dimension(self, names):
        """Return the dimension(s) of trajectory variable(s).

        **Parameters:**

        - *names*: Name(s) of the variable(s) from which to get the
          dimension(s)

             This may be a single string or (possibly nested) list of strings
             representing the names of the variables.

        If *names* is a string, then the output will be a single unit.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of units.

        **Example:**

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/SaturationPressure.mat')
           >>> sim.get_dimension('environment.p')
           'm/(l.T2)'
           >>> sim.get_dimension([[['environment.p', 'environment.T']]])
           [[['m/(l.T2)', 'l2.m/(N.T2)']]]
        """
        return self._get(names, lambda name: self._traj[name].unit)


class SimResList(ResList):
    r"""Special list of simulation results (:class:`SimRes` instances)

    **Initialization signatures:**

    - :class:`SimResList`\(): Returns an empty simulation list

    - :class:`SimResList`\(*sims*), where sims is a list of :class:`SimRes`
      instances:  Casts the list into a :class:`SimResList`

    - :class:`SimResList`\(*filespec*), where *filespec* is a filename or
      directory, possibly with wildcards a la `glob
      <https://docs.python.org/2/library/glob.html>`_:  Returns a
      :class:`SimResList` of :class:`SimRes` instances loaded from the
      matching or contained files

         The filename or directory must include the absolute path or be
         resolved to the current directory.

         An error is only raised if no files can be loaded.

    - :class:`SimResList`\(*filespec1*, *filespec2*, ...): Loads all files
      matching or contained by *filespec1*, *filespec2*, etc. as above.

         Each file will be opened once at most; duplicate filename matches are
         ignored.

    **Built-in methods**

    The list has all of the methods of a standard Python_ list (e.g., + or
    `__add__
    <https://docs.python.org/2/reference/datamodel.html#object.__add__>`_/`__radd__
    <https://docs.python.org/2/reference/datamodel.html#object.__radd__>`_,
    :meth:`clear`,
    **del** or `__delitem__
    <https://docs.python.org/2/reference/datamodel.html#object.__delitem__>`_,
    += or `__iadd__
    <https://docs.python.org/2/reference/datamodel.html#object.__iadd__>`_,
    \*= or `__imul__
    <https://docs.python.org/2/reference/datamodel.html#object.__imul__>`_,
    :meth:`iter` or `__iter__
    <https://docs.python.org/2/reference/datamodel.html#object.__iter__>`_,
    :meth:`copy`,
    :meth:`extend`,
    :meth:`index`,
    :meth:`insert`,
    :meth:`len` or `__len__
    <https://docs.python.org/2/library/functions.html#len>`_,
    \* or `__mul__
    <https://docs.python.org/2/reference/datamodel.html#object.__mul__>`_/`__rmul__
    <https://docs.python.org/2/reference/datamodel.html#object.__rmul__>`_,
    :meth:`pop`,
    :meth:`remove`,
    :meth:`reverse`,
    :meth:`reversed` or `__reversed__
    <https://docs.python.org/2/reference/datamodel.html#object.__reversed__>`_,
    = or `__setitem__
    <https://docs.python.org/2/reference/datamodel.html#object.__setitem__>`_,
    :meth:`__sizeof__`, and :meth:`sort`).  By default, the :meth:`sort` method
    orders the list of simulations by the full path of the result files.  Note
    that :meth:`len` returns the number of simulations, not the number of
    variables like it does for :class:`SimRes`.

    **Overloaded standard methods:**

    - :meth:`append` - Add simulation(s) to the end of the list of simulations
      (accepts a :class:`SimRes` instance, directory, or filename).

    - :meth:`__getitem__` - Retrieve a simulation using an index, simulations
      using a slice, or a :class:`Variable` across the list of simulations using
      a variable name.

    - :meth:`__contains__` - Return *True* if:

         - a simulation is in the list of simulations or
         - a variable name is present in all of the simulations in the list.

    **Methods using built-in Python operators and syntax:**

    - :meth:`__getattr__` (invoked as ``sims.<attribute>``) - Return a
      dictionary containing the common variable names as keys.  The values are
      lists of the requested attribute of the common variables across the
      simulations in the list of simulations.

         If the attribute is a method, it is possible to call the dictionary.
         The result of the call is a new dictionary containing the common
         variable names as keys.  The values are lists of the return values
         across the simulations in the list of simulations.

    **Additional methods:**

    - :meth:`find` - Find the names of variables that are present in all of the
      simulations and that match a pattern.

    - :meth:`plot` - Plot data from the simulations in 2D Cartesian coordinates.

    - :meth:`get_unique_IVs` - Return a dictionary of initial values that are
      different among the variables that the simulations share.

    **Properties:**

    - :attr:`dirname` - Highest common directory that the result files share

    - :attr:`unique_names` - Return a dictionary of variable names that are not
      in all of the simulations.

    - :attr:`names` - List of names of variables that are present in all of the
      simulations

    - Also, the properties of :class:`SimRes` (:attr:`~SimRes.dirname`,
      :attr:`~SimRes.fbase`, :attr:`~SimRes.fname`, :attr:`~SimRes.n_constants`,
      and :attr:`~SimRes.tool`) can be retrieved as a list across all of the
      simulations; see the example below.

    **Examples:**

    .. code-block:: python

       >>> # Loading simulations:
       >>> sims = SimResList('examples/ChuaCircuit/*/')
       >>> sims.dirname # doctest: +SKIP
       ['.../examples/ChuaCircuit/1', '.../examples/ChuaCircuit/2']

       >>> # Looking up a property across all variables and simulations:
       >>> sims.IV # doctest: +SKIP +ELLIPSIS
       {...
        'C1.v': [4.0, 4.0],
       ...
        'C2.v': [0.0, 0.0],
       ...
        'L.L': [15.0, 21.0],
       ...}

       >>> # Calling a method across all variables and simulations:
       >>> sims.values(t=10) # doctest: +SKIP +ELLIPSIS
       {...
        'C1.v': [3.8028..., 3.8029...]
       ...
        'C2.v': [0.2111..., 0.2118...]
       ...
        'L.L': [15.0, 21.0],
       ...}

    .. testcleanup::

       >>> sims.sort()
       >>> sims.dirname # doctest: +ELLIPSIS
       ['.../examples/ChuaCircuit/1', '.../examples/ChuaCircuit/2']

       >>> IVs = sims.IV
       >>> IVs['C1.v']
       [4.0, 4.0]
       >>> IVs['C2.v']
       [0.0, 0.0]
       >>> IVs['L.L']
       [15.0, 21.0]

       >>> values = sims.values(t=10)
       >>> IVs['C1.v'] # doctest: +ELLIPSIS
       [3.8028..., 3.8029...]
       >>> IVs['C2.v'] # doctest: +ELLIPSIS
       [0.2111..., 0.2118...]
       >>> IVs['L.L']
       [15.0, 21.0]
    """

    def __init__(self, *args):
        """Initialize as a list of :class:`SimRes` instances, loading files as
        necessary.

        See the top-level class documentation.
        """
        if not args: # Empty list
            super(SimResList, self).__init__([])

        elif isinstance(args[0], string_types): # Filenames or directories
            try:
                fnames = multiglob(args)
            except TypeError:
                raise TypeError(
                    "The simulation list can only be initialized by "
                    "providing a list of SimRes instances or a series of "
                    "arguments, each of which is a filename or directory.")
            list.__init__(self, _get_sims(fnames))

        elif len(args) == 1: # List or iterable of SimRes instances
            sims = list(args[0])
            for sim in sims:
                assert isinstance(sim, SimRes), ("All entries in the list must "
                                                 "be SimRes instances.")
            list.__init__(self, sims)

        else:
            raise TypeError(
                "The simulation list can only be initialized by "
                "providing a list of SimRes instances or a series of "
                "arguments, each of which is a filename or directory.")

    def append(self, item):
        """Add simulation(s) to the end of the list of simulations.

        **Parameters:**

        - *item*: :class:`SimRes` instance or a file specification

             The file specification may be a filename or directory, possibly
             with wildcards a la `glob
             <https://docs.python.org/2/library/glob.html>`_, where simulation
             results can be loaded by :class:`SimRes`.  The filename or
             directory must include the absolute path or be resolved to the
             current directory.  An error is only raised if no files can be
             loaded.

         Unlike the `append
         <https://docs.python.org/2/tutorial/datastructures.html>`_ method of a
         standard Python_ list, this method may add more than one item.  If
         *item* is a directory or a wildcarded filename, it may match multiple
         valid files.

         Simulation results will be appended to the list even if they are
         already included.

        **Example:**

        >>> sims = SimResList('examples/ChuaCircuit/*/')
        >>> sims.append('examples/ThreeTanks.mat')
        >>> print(sims) # doctest: +SKIP
        List of simulation results (SimRes instances) from the following files
        in the .../examples directory:
           ChuaCircuit/1/dsres.mat
           ChuaCircuit/2/dsres.mat
           ThreeTanks.mat

        .. testcleanup::

           >>> sims.sort()
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../examples directory:
              ChuaCircuit/1/dsres.mat
              ChuaCircuit/2/dsres.mat
              ThreeTanks.mat
        """
        if isinstance(item, SimRes):
            list.append(self, item)
        else:
            assert isinstance(item, string_types), (
                "The simulation list can ony be appended by providing a SimRes "
                "instance, filename, or directory.")
            fnames = multiglob(item)
            self.extend(SimResList(_get_sims(fnames)))

    def find(self, pattern=None, re=False, constants_only=False):
        r"""Find the names of variables that are present in all of the
        simulations and that match a pattern.

        By default, all of the common variables are returned.  The names are
        sorted alphabetically.

        **Parameters:**

        - *pattern*: Case-sensitive string used for matching

          - If *re* is *False* (next argument), then the pattern follows the
            Unix shell style:

            ============   ============================
            Character(s)   Role
            ============   ============================
            \*             Matches everything
            ?              Matches any single character
            [seq]          Matches any character in seq
            [!seq]         Matches any char not in seq
            ============   ============================

            Wildcard characters ('\*') are not automatically added at the
            beginning or the end of the pattern.  For example, '\*x\*' matches
            all variables that contain "x", but 'x\*' matches only the variables
            that begin with "x".

          - If *re* is *True*, regular expressions are used a la `Python's re
            module <http://docs.python.org/2/library/re.html>`_.  See also
            http://docs.python.org/2/howto/regex.html#regex-howto.

            Since :func:`re.search` is used to produce the matches, it is as if
            wildcards ('.*') are automatically added at the beginning and the
            end.  For example, 'x' matches all variables that contain "x".  Use
            '^x$' to match only the variables that begin with "x" and 'x$' to
            match only the variables that end with "x".

            Note that '.' is a subclass separator in Modelica_ but a wildcard in
            regular expressions.  Escape subclass separators as '\\.'.

        - *re*: *True* to use regular expressions (*False* to use shell style)

        - *constants_only*: *True* to include only the variables that do not
          change over time

        **Example:**

        .. code-block:: python

           >>> sims = SimResList('examples/ChuaCircuit/*/')

           >>> # Names for voltages across all of the components:
           >>> sorted(sims.find('^[^.]*.v$', re=True))
           ['C1.v', 'C2.v', 'G.v', 'L.v', 'Nr.v', 'Ro.v']
        """
        # Get a set of all the variables or just the constants.
        names = set.intersection(*[set(sim.find(pattern, re, constants_only))
                                   for sim in self])

        # Return the set as a sorted list.
        return sorted(names)

    def get_unique_IVs(self, constants_only=False, tolerance=1e-10):
        """Return a dictionary of initial values that are different among the
        variables that the simulations share.  Each key is a variable name and
        each value is a list of initial values across the simulations.

        **Parameters:**

        - *constants_only*: *True* to include only the variables that do not
          change over time

        - *tolerance*: Maximum variation allowed for values to still be
          considered the same

        **Example:**

        .. testsetup::

           >>> from modelicares import SimResList

        >>> sims = SimResList('examples/ChuaCircuit/*/')
        >>> print(sims) # doctest: +SKIP
        List of simulation results (SimRes instances) from the following files
        in the .../examples/ChuaCircuit directory:
           1/dsres.mat
           2/dsres.mat
        >>> sims.get_unique_IVs()['L.L'] # doctest: +SKIP
        [15.0, 21.0]

        .. testcleanup::

           >>> sims.sort()
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../examples/ChuaCircuit directory:
              1/dsres.mat
              2/dsres.mat
           >>> sims.get_unique_IVs()['L.L']
           [15.0, 21.0]
        """
        unique_IVs = {}
        for name in self.find(constants_only=constants_only):
            IVs = self[name].IV
            if max(IVs) - min(IVs) > tolerance:
                unique_IVs[name] = IVs
        return unique_IVs

    @property
    def names(self):
        """List of all of the names of variables that are present in all of the
        simulations

        The names are sorted alphabetically.

        **Example:**

        >>> sims = SimResList('examples/ChuaCircuit/*/')
        >>> sims.names # doctest: +ELLIPSIS
        ['C1.C', 'C1.der(v)', 'C1.i', 'C1.n.i', ..., 'Time']
        """
        names = set.intersection(*[set(sim) for sim in self])
        return sorted(names)

    def __contains__(self, item):
        """Return *True* if a variable is present in all of the simulation
        results or a simulation is present in the list of simulations.

        This method is overloaded---*item* can be a string representing a
        variable name or a :class:`SimRes` instance.

        **Example:**

        First, load some simulations:

        >>> sims = SimResList('examples/ChuaCircuit/*/')

        Now check if a variable is in all of the simulations:

        >>> 'L.L' in sims
        True

        or if a simulation in the list:

        >>> sims[0] in sims
        True
        """
        if isinstance(item, string_types):
            return all(item in sim for sim in self)
        return list.__contains__(self, item)

    def __getattr__(self, attr):
        """Return a dictionary containing the common variable names as keys.
        The values are lists of the requested attribute of the common variables
        across the simulations in the list of simulations.

        If the attribute is a method, it is possible to call the dictionary.
        The result of the call is a new dictionary containing the common
        variable names as keys.  The values are lists of the return values
        across the simulations in the list of simulations.
        """
        names = self.names
        values = (util.CallList([getattr(sim[name], attr) for sim in self])
                  for name in names)
        try:
            return util.CallDict(zip(names, values))
        except ValueError:
            if attr == 'value':
                raise ValueError("The variables aren't all constants.  "
                                 "Use values() instead of value.")
            raise

    def __getitem__(self, i):
        """Return a list of results of a variable across all of the simulations
        or a simulation from the list of simulations.

        This method is overloaded beyond the standard indexing and slicing.  If
        the index (*i*) is a variable name (string), then a :class:`VarList` is
        returned with references to the corresponding variable in each of the
        simulations.  That list can be used to access the attributes listed in
        :meth:`SimRes.__getitem__` and described further in :class:`Variable`.

        **Example:**

        .. testsetup::

           >>> from modelicares import SimResList

        >>> sims = SimResList('examples/ChuaCircuit/*/')
        >>> sims['L.v'].mean() # doctest: +SKIP
        [0.0013353984, 0.023054097]

        .. testcleanup::

            >>> sims.sort()
            >>> sims['L.v'].mean()
            [0.0013353984, 0.023054097]
        """
        if isinstance(i, slice):
            # Slice the simulation list and cast it as a SimResList.
            return self.__class__(list.__getitem__(self, i))
        elif isinstance(i, string_types):
            # Return a list containing the variable from each simulation.
            return VarList([sim[i] for sim in self])
        # Return a single simulation (SimRes instance).
        return list.__getitem__(self, i)

    def __str__(self):
        """Return str(self).

        This provides a readable description of the :class:`SimResList`.

        **Example:**

        >>> sims = SimResList('examples/ChuaCircuit/*/')
        >>> print(sims) # doctest: +SKIP
        List of simulation results (SimRes instances) from the following files
        in the .../examples/ChuaCircuit directory:
           1/dsres.mat
           2/dsres.mat

        .. testcleanup::

           >>> sims.sort()
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../examples/ChuaCircuit directory:
              1/dsres.mat
              2/dsres.mat
        """
        if len(self) == 0:
            return "Empty list of simulation results"
        elif len(self) == 1:
            return ("List of simulation results (SimRes instance) from\n"
                    + self[0].fname)
        dirname = self.dirname
        string = ("List of simulation results (SimRes instances) from the "
                  "following files")
        string += ("\nin the %s directory:\n   "
                   % dirname if dirname else ":\n   ")
        string += "\n   ".join(self.fnames)
        return string

    def plot(self, *args, **kwargs):
        r"""Plot data from selected variables over all of the simulations in 2D
        Cartesian coordinates.

        This method calls :meth:`~SimRes.plot` from the included instances of
        :class:`SimRes`.

        A new figure is created if necessary.

        **Parameters:**

        *\*args* and *\*\*kwargs* are propagated to :meth:`SimRes.plot`
        (then to :func:`modelicares.util.plot` and finally to
        :func:`matplotlib.pyplot.plot`), except for the following keyword
        arguments:

        - *suffixes*: Suffix or list of suffixes for the legends (see
          :meth:`SimRes.plot`)

             Use '' for no suffix.  If *suffixes* is *None*, the *label*
             property of the simulations will be used.  If the simulations do
             not have *label* properties, then the base filenames will be used
             with enough of the path to distinguish the files.

        - *color*: Single entry, list, or :func:`itertools.cycle` of colors to
          be used sequentially

             Each entry may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *dashes*: Single entry, list, or :func:`itertools.cycle` of dash
          styles to be used sequentially

             Each style is a tuple of on/off lengths representing dashes.  Use
             (0, 1) for no line and (None ,None) for a solid line.

             .. Seealso:: http://matplotlib.sourceforge.net/api/collections_api.html

        **Returns:**

        1. *ax1*: Primary y axes

        2. *ax2*: Secondary y axes

        **Example:**

        .. plot:: examples/ChuaCircuits.py
           :alt: plot of a Chua circuit with different inductances
        """
        # Get the local arguments.
        suffixes = kwargs.pop('suffixes', None)
        color = kwargs.pop('color', ['b', 'g', 'r', 'c', 'm', 'y', 'k'])
        dashes = kwargs.pop('dashes', [(None, None), (3, 3), (1, 1),
                                       (3, 2, 1, 2)])

        # Set up the color(s) and dash style(s).
        cyc = type(cycle([]))
        if not isinstance(color, cyc):
            if not iterable(color):
                color = [color]
            color = cycle(color)
        kwargs['color'] = color
        if not isinstance(dashes, cyc):
            if not iterable(dashes[0]):
                dashes = [dashes]
            dashes = cycle(dashes)
        kwargs['dashes'] = dashes

        # Process the suffixes input.
        if suffixes is None:
            try:
                suffixes = self.label
            except AttributeError:
                suffixes = self.fnames
        elif suffixes == '':
            suffixes = [''] * len(self)

        # Generate the plots.
        for i, (sim, suffix) in enumerate(zip(self, suffixes)):
            ax1, ax2 = sim.plot(*args, suffix=suffix, **kwargs)
            if i == 0:
                kwargs.update({'ax1': ax1, 'ax2': ax2})
        return ax1, ax2

    @property
    def unique_names(self):
        """Dictionary of variable names that are not in all of the simulations

        Each key is a variable name and each value is a Boolean list indicating
        if the associated variable appears in each of the simulations.

        **Example:**

        >>> sims = SimResList('examples/*')
        >>> print(sims) # doctest: +SKIP
        List of simulation results (SimRes instances) from the following files
        in the .../examples directory:
           ThreeTanks.mat
           ChuaCircuit.mat
        >>> sims.unique_names['L.L'] # doctest: +SKIP
        [False, True]

        .. testcleanup::

           >>> sims.sort()
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../examples directory:
              ChuaCircuit.mat
              ThreeTanks.mat
           >>> sims.unique_names['L.L']
           [True, False]
        """
        sets = [set(sim.names) for sim in self]
        all_names = set.union(*sets)
        unique_names = all_names
        return {name: [name in sim for sim in self] for name in unique_names}


class SimResSequence(SimRes):
    """Class to load, analyze, and plot results from a sequence of continued
    Modelica simulations of the same model

    **Initialization signatures:**

    - :class:`SimResList`\(*sims*), where sims is a list of :class:`SimRes`
      instances:  Casts the list into a :class:`SimResSequence`

    - :class:`SimResSequence`\(*filespec*), where *filespec* is a filename or
      directory, possibly with wildcards a la `glob
      <https://docs.python.org/2/library/glob.html>`_:  Returns a
      :class:`SimResSequence` loaded from the matching or contained files

         The filename or directory must include the absolute path or be
         resolved to the current directory.

         An error is only raised if no files can be loaded.

    - :class:`SimResSequence`\(*filespec1*, *filespec2*, ...): Loads all files
      matching or contained by *filespec1*, *filespec2*, etc. as above.

         Each file will be opened once at most; duplicate filename matches are
         ignored.

    The simulations are sorted by the initial time.

    This class has all of the methods and properties of :class:`SimRes`.
    However, :attr:`fname`, :attr:`fbase`, and :attr:`dirname` are only those of
    the first simulation in the sequence.  Use :attr:`fname` to get a list of
    all of the filenames relative to the highest directory that the simulations
    share.

    The :attr:`description` and :attr:`display_unit` of each variable is taken
    from the first simulation.  It is assumed but not checked that these are the
    same for all of the simulations.
    """

    def __init__(self, *args):
        """Initialize the sequence of continued simulations.

        See the top-level class documentation.
        """
        # Load and sort the simulations by start time.
        sims = SimResList(*args)
        sims.sort(key=lambda sim: sim['Time'].IV)

        # Check for overlap.
        times = sims['Time']
        if np.any(times.FV[0:-1] > times.IV[1:]):
            raise ValueError("The simulations overlap.")

        # Retrieve the times and values of each variable from the simulations.
        # Take the description, unit, and display unit of each variable from the
        # first simulation.
        def get_variable(name):
            entries = sims[name]
            first = entries[0]

            return Variable(Samples(np.concatenate(entries.times()),
                                    np.concatenate(entries.values())),
                            first.dimension,
                            first.display_unit,
                            first.description)

        self.update({name: get_variable(name) for name in sims.names})

        # Set the other attributes.
        sim0 = sims[0]
        self.tool = sim0.tool if len(set(sims.tool)) == 1 else "multiple tools"
        self.fname = sim0.fname
        self.fnames = sims.fnames


if __name__ == '__main__':
    # Test the contents of this file.

    import doctest

    if os.path.isdir('examples'):
        doctest.testmod()
    else:
        # Create a link to the examples folder.
        EXAMPLE_DIR = '../examples'
        if not os.path.isdir(EXAMPLE_DIR):
            raise IOError("Could not find the examples folder.")
        try:
            os.symlink(EXAMPLE_DIR, 'examples')
        except AttributeError:
            raise AttributeError("This method of testing isn't supported in "
                                 "Windows.  Use runtests.py in the base "
                                 "folder.")

        # Test the docstrings in this file.
        doctest.testmod()

        # Remove the link.
        os.remove('examples')
