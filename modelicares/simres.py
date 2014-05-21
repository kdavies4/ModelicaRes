#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This submodule contains the following classes:

- :class:`SimRes` - Class to load, analyze, and plot results from a Modelica_
  simulation

- :class:`SimResList` - Specialized list of simulation results (:class:`SimRes`
  instances)

- :class:`Variable` - Specialized namedtuple_ to represent a variable in a
  simulation, with methods to retrieve and perform calculations on its values


.. _Modelica: http://www.modelica.org/
.. _namedtuple: https://docs.python.org/2/library/collections.html#collections.namedtuple

.. testsetup::
   >>> import numpy as np
   >>> np.set_printoptions(precision=4)
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
import numpy as np

from abc import abstractmethod
from collections import namedtuple
from difflib import get_close_matches
from functools import wraps
from glob import glob
from itertools import cycle
from matplotlib import rcParams
from matplotlib.cbook import iterable
from matplotlib.pyplot import figlegend
from pandas import DataFrame
from scipy.integrate import trapz as integral
from scipy.interpolate import interp1d
from six import string_types

from modelicares import util
from modelicares._res import ResList
from modelicares.texunit import unit2tex, number_label


def _apply_function(g):
    """Return a method that applies a function to its output, given a
    method that doesn't (*g*).

    I.e., a decorator to apply a function to the return value
    """
    @wraps(g)
    def wrapped(self, f=None, *args, **kwargs):
        """Function that applies a function *f* to its output

        If *f* is *None* (default), no function is applied (i.e., pass
        through or identity).
        """
        return (g(self, *args, **kwargs) if f is None else
                f(g(self, *args, **kwargs)))

    return wrapped

def _get_sims(fnames):
    """Return a list of :class:`SimRes` instances from a list of filenames.

    No errors are given unless no files could be loaded.
    """
    sims = []
    for fname in fnames:
        try:
            sims.append(SimRes(fname))
        except:
            continue
    assert len(sims) > 0, "No simulations were loaded."
    return sims

def _select(f):
    """Return a method that uses time-based indexing to return values,
    given a method that returns all values (*f*).

    I.e., a decorator to use time-based indexing to select values
    """
    @wraps(f)
    def wrapped(cls, t=None, *args, **kwargs):
        """Function that uses time-based indexing to return values

        If *t* is *None* (default), then all values are returned (i.e., pass
        through or identity).
        """
        if t is None:
            # Return all values.
            return f(cls, *args, **kwargs)
        elif isinstance(t, tuple):
            # Apply a slice with optional start time, stop time, and number
            # of samples to skip.
            return f(cls, *args, **kwargs)[cls._slice(t)]
        else:
            # Interpolate at single time or list of times.
            function_at_ = interp1d(cls.times(), f(cls, *args, **kwargs))
            # For some reason, this wraps single values as arrays, so need to
            # cast back to float.
            try:
                # Assume t is a list of times.
                return [float(function_at_(time)) for time in t]
            except TypeError:
                # t is a single time.
                return float(function_at_(t))

    return wrapped

def _swap(g):
    """Decorator that swaps the first two arguments of a method and gives them
    each a default of *None*.

    This is useful because for computational efficiency it's best to apply the
    time selection (_select decorator below) before the applying the fuction
    (_apply_function decorator), but we want time to be the first
    argument and the function to be the second.
    """
    @wraps(g)
    def wrapped(self, t=None, f=None):
        """Look up the variable and pass it to the original function."""
        return g(self, f, t)

    return wrapped


class Variable(namedtuple('VariableBase', ['samples', 'description', 'unit',
                                           'displayUnit'])):
    """Specialized namedtuple_ to represent a variable in a simulation, with
    methods to retrieve and perform calculations on its values

    Instances of this class are returned when indexing a variable name from a
    simulation result (:class:`SimRes` instance).  Lists of instances are
    returned when indexing multiple variables from a simulation result or a
    single variable from multiple simulations (in a :class:`SimResList`).
    """

    def array(self, t=None, ft=None, fv=None):
        """Return an array with function *ft* of the times of the variable as
        the first column and function *fv* of the values of the variable as the
        second column.

        The times and values are taken at index or slice *i*.  If *i* is *None*,
        then all times and values are returned.

        **Arguments:**

        - *t*: Time index

             - Default or *None*: All samples are included.

             - *float*: Interpolate to a single time.

             - *list*: Interpolate to a list of times.

             - *tuple*: Extract samples from a range of times.  The structure is
               similar to the arguments of Python's slice_ function, except that
               the start and stop values can be floating point numbers.  The
               samples within and up to the limits are included.  Interpolation
               is not used.

                  - (*stop*,): All samples up to *stop* are included.

                       Be sure to include the comma to distinguish this from a
                       float.

                  - (*start*, *stop*): All samples between *start* and *stop*
                    are included.

                  - (*start*, *stop*, *skip*): Every *skip*th sample is included
                    between *start* and *stop*.

        - *ft*: Function that operates on the vector of times (default or
          *None* is identity)

        - *fv*: Function that operates on the vector of values (default or
          *None* is identity)


        .. _slice: https://docs.python.org/2/library/functions.html#slice
        """
        return np.array([self.times(t=t, f=ft), self.values(t=t, f=fv)]).T

    def FV(self, f=None):
        """Return function *f* of the final value of the variable.
        """
        return self.values()[-1] if f is None else f(self.values()[-1])

    def is_constant(self):
        """Return *True* if the variable does not change over time.
        """
        values = self.values()
        return np.array_equal(values[:-1], values[1:])

    def IV(self, f=None):
        """Return function *f* of the initial value of the variable.
        """
        return self.values()[0] if f is None else f(self.values()[0])

    def max(self, f=None):
        """Return the maximum value of function *f* of the variable.
        """
        return np.max(self.values(f=f))

    def mean(self, f=None):
        """Return the time-averaged mean value of function *f* of the variable.
        """
        t = self.times()
        return integral(self.values(f=f), t)/(t[-1] - t[0])

    def mean_rectified(self, f=None):
        """Return the time-averaged rectified mean value of function *f* of the
        variable.
        """
        t = self.times()
        return integral(np.abs(self.values(f=f)), t)/(t[-1] - t[0])

    def min(self, f=None):
        """Return the minimum value of function *f* of the variable.
        """
        return np.min(self.values(f=f))

    def RMS(self, f=None):
        """Return the time-averaged root mean square value of function *f* of
        the variable.
        """
        t = self.times()
        return np.sqrt(integral(self.values(f=f)**2, t)/(t[-1] - t[0]))

    def RMS_AC(self, f=None):
        """Return the time-averaged AC-coupled root mean square value of
        function *f* of the variable.
        """
        t = self.times()
        mean = self.mean(f=f)
        return mean + np.sqrt(integral((self.values(f=f) - mean)**2, t)/(t[-1] - t[0]))

    @abstractmethod
    def times(self, t=None, f=None):
        """Return function *f* of the recorded times of the variable.

        **Arguments:**

        - *t*: Time index

             This may have any of the forms list in :meth:`values`, but the
             useful ones are:

             - Default or *None*: All times are included.

             - *tuple*: Extract recorded times from a range of times.  The
               structure is similar to the arguments of Python's slice_
               function, except that the start and stop values can be floating
               point numbers.  The times within and up to the limits are
               included.  Interpolation is not used.

                  - (*stop*,): All times up to *stop* are included.

                       Be sure to include the comma to distinguish this from a
                       float.

                  - (*start*, *stop*): All recorded times between *start* and
                    *stop* are included.

                  - (*start*, *stop*, *skip*): Every *skip*th recorded time is
                    included between *start* and *stop*.

        - *f*: Function that operates on the vector of recorded times (default
          or *None* is identity)
        """
        pass

    def value(self, f=None):
        """Return function *f* of the value of the constant variable.

        This method raises a **ValueError** if the variable is time-varying.

        **Arguments:**

        - *f*: Function that operates on the value (default or *None* is
          identity)
        """
        values = self.values()
        if np.array_equal(values[:-1], values[1:]):
            return values[0] if f is None else f(values[0])
        else:
            raise ValueError("The variable is not a constant.  Use values() "
                             "instead of value().")

    @abstractmethod
    def values(self, t=None, f=None):
        """Return function *f* of the values of the variable.

        **Arguments:**

        - *t*: Time index

             - Default or *None*: All samples are included.

             - *float*: Interpolate to a single time.

             - *list*: Interpolate to a list of times.

             - *tuple*: Extract samples from a range of times.  The structure is
               similar to the arguments of Python's slice_ function, except that
               the start and stop values can be floating point numbers.  The
               samples within and up to the limits are included.  Interpolation
               is not used.

                  - (*stop*,): All samples up to *stop* are included.

                       Be sure to include the comma to distinguish this from a
                       float.

                  - (*start*, *stop*): All samples between *start* and *stop*
                    are included.

                  - (*start*, *stop*, *skip*): Every *skip*th sample is included
                    between *start* and *stop*.

        - *f*: Function that operates on the vector of values (default or *None*
          is identity)
        """
        pass

    def _slice(self, t):
        """Return a slice that indexes the variable.

        Argument *t* is a tuple with one of the following forms:

          - (*stop*,): All samples up to *stop* are included.

               Be sure to include the comma to distinguish this from a
               float.

          - (*start*, *stop*): All samples between *start* and *stop* are
            included.

          - (*start*, *stop*, *skip*): Every *skip*th sample between *start* and
            *stop* is included.
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


class _VarDict(dict):
    """Specialized dictionary for simulation variables (instances of
    :class:`Variable`)
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


class _VarList(list):
    """Specialized list of simulation variables (instances of
    :class:`Variable`), with attributes to access information from all of the
    variables at once

    The list may be nested.
    """

    def _method(f):
        """Return a method that operates on all of the variables in the list of
        variables, given a function that operates on a single variable.
        """
        @wraps(f)
        def wrapped(cls, *args, **kwargs):
            """Traverse the list recursively until the argument is a single
            variable, then pass it to the function and return the result
            upwards.
            """
            return [f(variable, *args, **kwargs)
                    if isinstance(variable, Variable) else
                    wrapped(variable, *args, **kwargs)
                    for variable in cls]

        return wrapped

    @_method
    def __getattr__(variable, attr):
        """Look up a field in each of the variables (e.g., description, unit, or
        displayUnit).
        """
        return variable.__getattribute__(attr)

    # The methods below are straightforward calls to the methods of the
    # Variable class (above).

    @_method
    def arrays(variable, *args, **kwargs):
        """Return a list containing an array of times and values for each
        variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.array`, so this method has the same call signature.
        """
        return variable.array(*args, **kwargs)

    @_method
    def FV(variable, *args, **kwargs):
        """Return a list containing the final of each variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.FV`, so this method has the same call signature.
        """
        return variable.FV(*args, **kwargs)

    @_method
    def is_constant(variable):
        """Return a list containing *True* or *False* depending on whether each
        variable is constant or not.

        There are no arguments.
        """
        return variable.is_constant()

    @_method
    def IV(variable, *args, **kwargs):
        """Return a list containing the initial value of each variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.IV`, so this method has the same call signature.
        """
        return variable.IV(*args, **kwargs)

    @_method
    def max(variable, *args, **kwargs):
        """Return a list containing the maximum value of each variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.max`, so this method has the same call signature.
        """
        return variable.max(*args, **kwargs)

    @_method
    def mean(variable, *args, **kwargs):
        """Return a list containing the time-averaged mean value of each
        variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.mean`, so this method has the same call signature.
        """
        return variable.mean(*args, **kwargs)

    @_method
    def mean_rectified(variable, *args, **kwargs):
        """Return a list containing the time-averaged rectified mean of each
        variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.mean_rectified`, so this method has the same call
        signature.
        """
        return variable.mean_rectified(*args, **kwargs)

    @_method
    def min(variable, *args, **kwargs):
        """Return a list containing the minimum value of each variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.min`, so this method has the same call signature.
        """
        return variable.min(*args, **kwargs)

    @_method
    def RMS(variable, *args, **kwargs):
        """Return a list containing the time-averaged root mean square of each
        variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.RMS`, so this method has the same call signature.
        """
        return variable.RMS(*args, **kwargs)

    @_method
    def RMS_AC(variable, *args, **kwargs):
        """Return a list containing the time-averaged AC-coupled root mean
        square of each variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.RMS_AC`, so this method has the same call signature.
        """
        return variable.RMS_AC(*args, **kwargs)

    @_method
    def times(variable, *args, **kwargs):
        """Return a list containing the sampling times of each variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.times`, so this method has the same call signature.
        """
        return variable.times(*args, **kwargs)

    @_method
    def value(variable, *args, **kwargs):
        """Return a list containing the value of each constant variable.

        This method raises a **ValueError** if any of the variables are
        time-varying.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.value`, so this method has the same call signature.
        """
        return variable.value(*args, **kwargs)

    @_method
    def values(variable, *args, **kwargs):
        """Return a list containing the values of each variable.

        Arguments *\*args* and *\*\*kwargs* are passed directly to
        :meth:`Variable.values`, so this method has the same call signature.
        """
        return variable.values(*args, **kwargs)


# List of file-loading functions for SimRes
from modelicares._io.dymola import loadsim as dymola
simloaders = [('dymola', dymola)] # SimRes tries these in order.
# All of the keys should be in lowercase.
# This must be below the definition of Variable and _VarDict because those
# classes are required by the loading functions.

class SimRes(object):
    """Class to load, analyze, and plot results from a Modelica_ simulation

    Methods:

    - :meth:`browse` - Launch a variable browser.

    - :meth:`fbase` - Return the base filename from which the results were
      loaded, without the directory or file extension.

    - :meth:`names` - Return a list of variable names, optionally filtered by
      pattern matching.

    - :meth:`nametree` - Return a tree of variable names that reflects the
      Modelica_ model hierarchy.

    - :meth:`n_constants` - Return the number of variables that do not change
      over time.

    - :meth:`plot` - Plot data as points and/or curves in 2D Cartesian
      coordinates.

    - :meth:`sankey` - Create a figure with Sankey diagram(s).

    - :meth:`to_pandas` - Return a `pandas DataFrame`_ with selected variables.

    Methods invoked using built-in Python_ operators and syntax:

    - :meth:`__call__` - Access a list of variables by their names (invoked as
      ``sim(<list of variable names>)``).

         The return value has attributes to retrieve information about all of
         the variables in the list at once (values, units, etc.).

    - :meth:`__contains__` - Return *True* if a variable is present in the
      simulation results (invoked as ``<variable name> in sim``).

    - :meth:`__getitem__` - Access a variable by name (invoked as
      ``sim[<variable name>]``).

         The return value has attributes to retrieve information about the
         variable (values, unit, etc.).

    - :meth:`__len__` - Return the number of variables in the simulation
      (invoked as ``len(sim)``).

    Other attributes:

    - *fname* - Filename from which the variables were loaded, with absolute
      path

    - *tool* - String indicating the function used to load the results (named
      after the corresponding simulation tool)


    .. _Python: http://www.python.org
    .. _pandas DataFrame: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html?highlight=dataframe#pandas.DataFrame
    """

    def __init__(self, fname='dsres.mat', constants_only=False, tool=None):
        """Upon initialization, load Modelica_ simulation results from a file.

        **Arguments:**

        - *fname*: Name of the file (including the directory if necessary)

        - *constants_only*: *True* to load only the variables from the first
          data table

             The first data table typically contains all of the constants,
             parameters, and variables that don't vary.  If only that
             information is needed, it may save resources to set
             *constants_only* to *True*.

        - *tool*: String indicating the simulation tool that created the file
          and thus the function to be used to load it

             By default, the available functions are tried in order until one
             works (or none do).

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
        """

        # Load the file.
        if tool is None:
            # Load the file and store the variables.
            for (tool, load) in simloaders[:-1]:
                try:
                    self._variables = load(fname, constants_only)
                except IOError:
                    raise
                except Exception as exception:
                    print("The %s loader gave the following error message:\n%s"
                          % (tool, exception.args[0]))
                    continue
                else:
                    break
            (tool, load) = simloaders[-1]
        else:
            loaderdict = dict(simloaders)
            try:
                load = loaderdict[tool.lower()]
            except:
                raise LookupError('"%s" is not one of the available tools ("%s").'
                                  % (tool, '", "'.join(list(loaderdict))))
        self._variables = load(fname, constants_only)

        # Remember the tool and filename.
        self.tool = tool
        self.fname = os.path.abspath(fname)

    def _acceptlists(f):
        """Return a function that accepts an optionally nested list of variable
        names, given a function that accepts a single variable name.
        """
        @wraps(f)
        def wrapped(self, names, *args, **kwargs):
            """Traverse lists recursively until the argument is a single
            variable name, then pass it to the original function and return the
            result upwards.
            """
            if isinstance(names, string_types):
                return f(self, names, *args, **kwargs)
            else:
                return [wrapped(self, name, *args, **kwargs) for name in names]

        return wrapped

    def _fromname(f):
        """Return a function that accepts the name of variable, given a function
        that accepts the variable itself.
        """
        @wraps(f)
        def wrapped(self, name, *args, **kwargs):
            """Look up the variable and pass it to the original function."""
            try:
                return f(self._variables[name], *args, **kwargs)
            except TypeError:
                if isinstance(name, list):
                    raise TypeError("To access a list of variables, use the "
                               "call method (parentheses instead of brackets).")
                else:
                    raise

        return wrapped

    # TODO: Remove the "_" prefix and add this to the list once it's finished.
    def _bar(self, names, times=[0], width=0.6, n_rows=1,
             title=None, subtitles=[], label="bar",
             xlabel=None, xticklabels=None, ylabel=None,
             margin_left=rcParams['figure.subplot.left'],
             margin_right=1-rcParams['figure.subplot.right'],
             margin_bottom=rcParams['figure.subplot.bottom'],
             margin_top=1-rcParams['figure.subplot.top'],
             wspace=0.1, hspace=0.25,
             leg_kwargs=None, **kwargs):
        """Create a sequence of bar plots at times.

        **Arguments:**

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

             This will be used as a base filename if the figure is saved.

        - *xlabel*: Label for the x-axes (only shown for the subplots on the
          bottom row)

        - *xticklabels*: Labels for the x-axis ticks (only shown for the
          subplots on the bottom row)

        - *ylabel*: Label for the y-axis (only shown for the subplots on the
          left column)

        - *margin_left*: Left margin

        - *margin_right*: Right margin

        - *margin_bottom*: Bottom margin

        - *margin_top*: Top margin

        - *wspace*: The amount of width reserved for blank space between
          subplots

        - *hspace*: The amount of height reserved for white space between
          subplots

        - *leg_kwargs*: Dictionary of keyword arguments for
          :meth:`matplotlib.pyplot.legend`

             If *leg_kwargs* is *None*, then no legend will be shown.

        - *\*\*kwargs*: Additional arguments for  :meth:`matplotlib.pyplot.bar`

        **Returns:**

        1. List of the axes within the figure
        """
        raise NotImplementedError
        # Base this on sankey().

        # Indices for the bars (1, 2, ...)
        ind = np.arange(len(names)) + 1

        # Create a title if necessary.
        if title is None:
            title = self.fbase()

        # Set up the subplots.
        n_plots = len(times) # Number of plots
        ax = util.setup_subplots(n_plots=n_plots, n_rows=n_rows,
                            title=title, subtitles=subtitles, label=label,
                            xlabel=xlabel, xticks=ind, xticklabels=xticklabels,
                            ylabel=ylabel,
                            margin_left=margin_left, margin_right=margin_right,
                            margin_bottom=margin_bottom, margin_top=margin_top,
                            wspace=wspace, hspace=hspace)[0]

        # Create the bar plots.
        for axis, time in zip(ax, times):
            axis.bar(ind-width/2., self(names).values(time),
                     width, **kwargs)
            a = axis.axis()
            axis.axis([0, ind[-1]+1, a[2], a[3]])

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

        .. code-block:: python

           >>> from modelicares import SimRes
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

        from modelicares._gui import Browser

        def do_work():
            """Launch the broswer."""
            app = wx.GetApp()
            if app is None:
                app = wx.App()
            frame = Browser(None, -1, self)
            frame.Show(True)
            app.SetTopWindow(frame)
            app.MainLoop()

        # TODO: Fix multithreading so that the browser can run in the background.
        #import threading
        #thread = threading.Thread(target=_do_work)
        #thread.setDaemon(True)
        #thread.start()

        do_work()

    def fbase(self):
        """Return the base filename from which the variables were loaded,
        without the directory or file extension.
        """
        return os.path.splitext(os.path.split(self.fname)[1])[0]

    def names(self, pattern=None, re=False, constants_only=False):
        r"""Return a list of variable names that match a pattern.

        By default, all names are returned.

        **Arguments:**

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
            beginning or the end of the pattern.  For example, 'x\*' matches
            variables that begin with "x", whereas '\*x\*' matches all variables
            that contain "x".

          - If *re* is *True*, regular expressions are used a la `Python's re
            module <http://docs.python.org/2/library/re.html>`_.  See also
            http://docs.python.org/2/howto/regex.html#regex-howto.

            Since :mod:`re.search` is used to produce the matches, it is as if
            wildcards ('.*') are automatically added at the beginning and the
            end.  For example, 'x' matches all variables that contain "x".  Use
            '^x$' to match only the variables that begin with "x" and 'x$' to
            match only the variables that end with "x".

            Note that '.' is a subclass separator in Modelica_ but a wildcard in
            regular expressions.  Escape the subclass separator as '\\.'.

        - *re*: *True* to use regular expressions (*False* to use shell style)

        - *constants_only*: *True* to include only the variables that do not
          change over time

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> # Names for voltages across all of the components:
           >>> sim.names('^[^.]*.v$', re=True)
           ['G.v', 'L.v', 'C2.v', 'Nr.v', 'Ro.v', 'C1.v']
        """
        # Get a list of all the variables or just the constants.
        if constants_only:
            names = (name for (name, variable) in self._variables.items()
                     if variable.is_constant())
        else:
            names = self._variables.keys()

        # Filter the list and return it.
        return util.match(names, pattern, re)

    def n_constants(self):
        """Return the number of variables that do not change over time.

        There are no arguments.  Note that this number may be greater than the
        number of declared parameters and constants in the Modelica_ model,
        since a variable may be fixed in value even though it is not declared as
        a constant or parameter.
        """
        return sum([variable.is_constant()
                    for variable in self._variables.values()])

    def nametree(self, pattern=None, re=False, constants_only=False):
        """Return a tree of variable names based on the Modelica_ model
        hierarchy.

        The tree is returned as a nested dictionary.  The keys are the Modelica_
        class instances (including the index if there are arrays) and the values
        are are subclasses.  The value at the end of each branch is the full
        variable name.

        All names are included by default, but the names can be filtered using
        *pattern*, *re*, and *constants_only*.  See :mod:`names` for a
        description of those arguments.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.nametree('L*v') # doctest: +ELLIPSIS
           {'L': {'p': {'v': 'L.p.v'}, 'n': {'v': 'L.n.v'}, 'v': 'L.v'}}
        """
        return util.tree(self.names(pattern, re, constants_only))

    def plot(self, ynames1=[], ylabel1=None, f1={}, legends1=[],
             leg1_kwargs={'loc': 'best'}, ax1=None,
             ynames2=[], ylabel2=None, f2={}, legends2=[],
             leg2_kwargs={'loc': 'best'}, ax2=None,
             xname='Time', xlabel=None,
             title=None, label="xy", incl_prefix=False, suffix=None,
             use_paren=True, **kwargs):
        """Plot variables as points and/or curves in 2D Cartesian coordinates.

        The abscissa may be time or any other variable (i.e., scatterplot).

        **Arguments:**

        - *ynames1*: Names of variables for the primary y axis

             If any names are invalid, then they will be skipped.

        - *ylabel1*: Label for the primary y axis

             If *ylabel1* is *None* (default) and all of the variables have the
             same Modelica_ description string, then the common description
             will be used.  Use '' for no label.

        - *f1*: Dictionary of labels and functions for additional traces to be
          plotted on the primary y axis

             The functions take as an input a list of the vectors of values of
             the variables in *ynames1*, sampled at the values of the 'Time'
             variable.

        - *legends1*: List of legend entries for variables assigned to the
          primary y axis

             If *legends1* is an empty list ([]), ynames1 will be used along
             with the keys from the *f1* dictionary.  If *legends1* is *None*
             and all of the variables on the primary axis have the same unit,
             then no legend will be shown.

        - *leg1_kwargs*: Dictionary of keyword arguments for the primary legend

        - *ax1*: Primary y axes

             If *ax1* is not provided, then axes will be created in a new
             figure.

        - *ynames2*, *ylabel2*, *f2*, *legends2*, *leg2_kwargs*, and *ax2*:
          Similar to *ynames1*, *ylabel1*, *f1*, *legends1*, *leg1_kwargs*, and
          *ax1* but for the secondary y axis

        - *xname*: Name of the x-axis variable

        - *xlabel*: Label for the x axis

             If *xlabel* is *None* (default), the variable's Modelica_
             description string will be applied.  Use '' for no label.

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be the base
             filename.  Use '' for no title.

        - *label*: Label for the figure (ignored if ax is provided)

             This will be used as a base filename if the figure is saved.

        - *incl_prefix*: If *True*, prefix the legend strings with the base
          filename of the class.

        - *suffix*: String that will be added at the end of the legend entries

        - *use_paren*: Add parentheses around the suffix

        - *\*\*kwargs*: Propagated to :meth:`util.plot` (and thus to
          :meth:`matplotlib.pyplot.plot`)

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
        # Note:  ynames1 is the first argument (besides self) so that plot()
        # can be called with simply a variable name.

        def ystrings(ynames, ylabel, legends, f):
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
                              " if necessary.")
                if legends == []:
                    legends = ynames + list(f)
                if incl_prefix:
                    legends = [self.fbase() + ': ' + leg for leg in legends]
                if suffix:
                    legends = ([leg + ' (%s)' % suffix for leg in legends]
                               if use_paren else
                               [leg + suffix for leg in legends])
                units = self(ynames).unit
                if len(set(units)) == 1:
                    # The  units are the same, so show the 1st one on the axis.
                    if ylabel != "":
                        ylabel = number_label(ylabel, units[0])
                else:
                    # Show the units in the legend.
                    if legends:
                        for i, unit in enumerate(units):
                            legends[i] = number_label(legends[i], unit)
                    else:
                        legends = [number_label(entry, unit) for entry, unit in
                                   zip(ynames, units)] + list(f)

            return ylabel, legends

        # Process the inputs.
        ynames1 = util.flatten_list(ynames1)
        ynames2 = util.flatten_list(ynames2)
        assert ynames1 or ynames2, "No signals were provided."
        if title is None:
            title = self.fbase()

        # Create primary and secondary axes if necessary.
        if not ax1:
            fig = util.figure(label)
            ax1 = fig.add_subplot(111)
        if ynames2 and not ax2:
            ax2 = ax1.twinx()

        # Generate the x-axis label.
        if xlabel is None:
            xlabel = 'Time' if xname == 'Time' else self[xname].description
            # With Dymola 7.4, the description of the time variable will be
            # "Time in", which isn't good.
        if xlabel != "":
            xlabel = number_label(xlabel, self[xname].unit)

        # Generate the y-axis labels and sets of legend entries.
        ylabel1, legends1 = ystrings(ynames1, ylabel1, legends1, f1)
        ylabel2, legends2 = ystrings(ynames2, ylabel2, legends2, f2)

        # Retrieve the data.
        all_times = self['Time'].values()
        yvars1 = self(ynames1)
        yvars2 = self(ynames2)
        if xname == 'Time':
            y1 = yvars1.values()
            if f1:
                y1_all = yvars1.values(all_times)
                y1 += [f(y1_all) for f in f1.values()]
            y2 = yvars2.values()
            if f2:
                y2_all = yvars2.values(all_times)
                y2 += [f(y2_all) for f in f2.values()]
        else:
            x = self[xname].values()
            times = self[xname].times()
            y1 = yvars1.values(times)
            y1 += [f(y1) for f in f1.values()]
            y2 = yvars2.values(times)
            y2 += [f(y2) for f in f2.values()]

        # Plot the data.
        if ynames2:
            y2times = (yvars2.times() + [all_times]*len(f2)
                       if xname == 'Time' else x)
        if ynames1:
            y1times = (yvars1.times() + [all_times]*len(f1)
                       if xname == 'Time' else x)
            if ynames2:
                # Use solid lines for primary axis and dotted lines for
                # secondary.
                kwargs['dashes'] = [(None, None)]
                util.plot(y1, y1times, ax1, label=legends1, **kwargs)
                kwargs['dashes'] = [(3, 3)]
                util.plot(y2, y2times, ax2, label=legends2, **kwargs)
            else:

                util.plot(y1, y1times, ax1, label=legends1, **kwargs)
        elif ynames2:
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
               margin_left=0.05, margin_right=0.05,
               margin_bottom=0.05, margin_top=0.1,
               wspace=0.1, hspace=0.25, **kwargs):
        """Create a figure with Sankey diagram(s).

        **Arguments:**

        - *names*: List of names of the flow variables

        - *times*: List of times at which the variables should be sampled

             If multiple times are given, then subfigures will be generated,
             each with a Sankey diagram.

        - *n_rows*: Number of rows of (sub)plots

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be "Sankey
             Diagram of *fbase*", where *fbase* is the base filename of the
             data.  Use '' for no title.

        - *subtitles*: List of subtitles (i.e., titles for each subplot)

             If not provided, "t = xx s" will be used, where *xx* is the time
             of each entry.  "(initial)" or "(final)" is appended if
             appropriate.

        - *label*: Label for the figure

             This will be used as the base filename if the figure is saved.

        - *margin_left*: Left margin

        - *margin_right*: Right margin

        - *margin_bottom*: Bottom margin

        - *margin_top*: Top margin

        - *wspace*: The amount of width reserved for blank space between
          subplots

        - *hspace*: The amount of height reserved for white space between
          subplots

        - *\*\*kwargs*: Additional arguments for :class:`matplotlib.sankey.Sankey`

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
            title = "Sankey diagram of " + self.fbase()

        # Determine the units of the data.
        flow_unit = self(names).unit
        assert len(set(flow_unit)) == 1, (
            "The variables have inconsistent units.")
        flow_unit = flow_unit[0]

        # Set up the subplots.
        if not subtitles:
            unit = unit2tex(self('Time').unit)
            subtitles = ["t = %s %s" % (time, unit) for time in times]
            for i, time in enumerate(times):
                if time == start_time:
                    subtitles[i] += " (initial)"
                elif time == stop_time:
                    subtitles[i] += " (final)"
        axes = util.setup_subplots(n_plots=n_plots, n_rows=n_rows,
            title=title, subtitles=subtitles, label=label,
            margin_left=margin_left, margin_right=margin_right,
            margin_bottom=margin_bottom, margin_top=margin_top,
            wspace=wspace, hspace=hspace)[0]

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

        The index is time.  The column headings indicate the units.

        The data frame has methods for further manipulation and exporting (e.g.,
        :meth:`~pandas.DataFrame.to_clipboard`,
        :meth:`~pandas.DataFrame.to_csv`, :meth:`~pandas.DataFrame.to_excel`,
        :meth:`~pandas.DataFrame.to_hdf`, and
        :meth:`~pandas.DataFrame.to_html`).

        **Arguments:**

        - *names*: String or list of strings of the variable names

             If *names* is *None* (default), then all variables are included.

        - *aliases*: Dictionary of aliases for the variable names

             The keys are the "official" variable names from the simulation and
             the values are the names as they will be included in the column
             headings.  Any variables not in this list will not be aliased.  Any
             unmatched alias will not be used.

        **Examples:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> voltages = sim.names('^[^.]*.v$', re=True)
           >>> sim.to_pandas(voltages) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
                       C1.v / V  C2.v / V   G.v / V   L.v / V  Nr.v / V  Ro.v / V
           Time / s
           0.000000    4.000000  0.000000 -4.000000  0.000000  4.000000  0.000000
           5.000000    3.882738  0.109426 -3.773312  0.109235  3.882738  0.000191
           ...
           [514 rows x 6 columns]

        We can relabel columns using the *aliases* argument:

        .. code-block:: python

           >>> sim = SimRes('examples/ThreeTanks.mat')
           >>> aliases = {'tank1.level': "Tank 1 level",
           ...            'tank2.level': "Tank 2 level",
           ...            'tank3.level': "Tank 3 level"}
           >>> sim.to_pandas(aliases.keys(), aliases) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
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
        # Simple function to label a variable with its unit:
        label = lambda name, unit: name + ' / ' + unit

        # Create the list of variable names.
        if names is None:
            names = self.names()
        else:
            names = set(util.flatten_list(names))
            names.add('Time')

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

            data.update({label(name, unit): values})

        # Create the pandas data frame.
        return DataFrame(data).set_index('Time / s')

    def __call__(self, names):
        """Access a list of variables by their names.

        See :meth:`__getitem__` for the attributes that can be accessed via the
        return value.  The result of the corresponding attribute in this class
        is a list of the results of the attribute of each variable.  The
        attributes in this class accept the same call signature.
        :meth:`arrays` in this class correponds to :meth:`Variable.array`.

        **Arguments**:

        - *names*: List of variable names

             The list can be nested, and the results will retain the hierarchy.
             If *names* is a single variable name, then the result is the same
             as from :meth:`__getitem__`.

        **Example**:

        .. code-block:: python

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
                return self._variables[names]
            else:
                return [entries(name) for name in names] # Recursion

        if isinstance(names, string_types):
            return self._variables[names]
        else:
            return _VarList(entries(names))

    def __contains__(self, name):
        """Return *True* if a variable is present in the simulation results.

        **Arguments**:

        - *name*: Name of variable

        **Example**:

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> # 'L.v' is a valid variable name:
           >>> 'L.v' in sim
           True
           >>> # but 'x' is not:
           >>> 'x' not in sim
           True
        """
        return name in self._variables

    @_fromname
    def __getitem__(variable):
        """Access a variable by name.

        The return value can be used to retrieve information about the variable.
        It has the following methods:

        - :meth:`Variable.array` - Return an array of times and values for the
          variable.

        - :meth:`Variable.FV` - Return the final value of the variable.

        - :meth:`Variable.is_constant` - Return *True* if the variable does not
          change over time.

        - :meth:`Variable.IV` - Return the final value of the variable.

        - :meth:`Variable.max` - Return the maximum value of the variable.

        - :meth:`Variable.mean` - Return the time-averaged value of the
          variable.

        - :meth:`Variable.mean_rectified` - Return the time-averaged absolute
          value of the variable.

        - :meth:`Variable.min` - Return the minimum value of the variable.

        - :meth:`Variable.RMS` - Return the time-averaged root mean square value
          of the variable.

        - :meth:`Variable.RMS_AC` - Return the time-averaged AC-coupled root
          mean square value of the variable.

        - :meth:`Variable.times` - Return the sample times of the variable.

        - :meth:`Variable.value` - Return the value of the variable if it is
          a constant (otherwise, error).

        - :meth:`Variable.values` - Return the values of the variable.

        and other attributes:

        - *description* - The Modelica_ variable's description string

        - *unit* - The Modelica_ variable's *unit* attribute

        - *displayUnit* - The Modelica_ variable's *displayUnit* attribute

        **Examples:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> sim['L.v'].unit
           'V'

           >>> sim['L.v'].values(t=(10,25)) # doctest: +NORMALIZE_WHITESPACE
           array([ 0.2108,  0.3046,  0.3904,  0.468 ], dtype=float32)
        """
        return variable

    def __len__(self):
        """Return the number of variables in the simulation.

        This includes the time variable.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> print("There are %i variables in the %s simulation." %
           ...       (len(sim), sim.fbase()))
           There are 62 variables in the ChuaCircuit simulation.
        """
        return len(self._variables)

    def __repr__(self):
        """Return a formal description of the :class:`SimRes` instance.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim # doctest: +ELLIPSIS
           SimRes('...ChuaCircuit.mat')
        """
        return "{Class}('{fname}')".format(Class=self.__class__.__name__,
                                           fname=self.fname)
        # Note:  The class name is inquired so that this method will still be
        # correct if the class is extended.

    def __str__(self):
        """Return an informal description of the :class:`SimRes` instance.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> print(sim) # doctest: +ELLIPSIS
           Modelica simulation results from ...ChuaCircuit.mat
        """
        return "Modelica simulation results from {f}".format(f=self.fname)


class SimResList(ResList):
    """Specialized list of simulation results

    The entries are :class:`SimRes` instances, but simulations can be specified
    via filename when initializing or appending the list.  The list has all
    of the methods of a standard Python_ list (e.g.,
    + or `__add__
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
    and :meth:`__sizeof__`).  Note that :meth:`len` returns the number of
    simulations, not the number of variables like it does for :class:`SimRes`.

    The comparison methods
    (`< <https://docs.python.org/2/reference/datamodel.html#object.__lt__>`_,
    `<= <https://docs.python.org/2/reference/datamodel.html#object.__le__>`_,
    `== <https://docs.python.org/2/reference/datamodel.html#object.__eq__>`_,
    `!= <https://docs.python.org/2/reference/datamodel.html#object.__ne__>`_,
    `>= <https://docs.python.org/2/reference/datamodel.html#object.__ge__>`_,
    `> <https://docs.python.org/2/reference/datamodel.html#object.__gt__>`_),
    and :meth:`sort`, which relies on them, use the full filenames (with
    absolute path) for comparison.

    The following methods are overloaded for convenience:

    - :meth:`append` - Add simulation(s) to the end of the list of simulations
      (accepts a :class:`SimRes` instance, directory, or filename).

    - :meth:`__getitem__` - Retrieve a simulation using an index, simulations
      using a slice, or a variable across the list of simulations using a
      variable name.

    - :meth:`__contains__` - Return *True* iff:

         - a simulation is in the list of simulations or
         - a variable name is present in all of the simulations in the list.

    The following methods are added to those in the standard Python_ list:

    - :meth:`basedir` - Return the highest common directory that the result files
      share.

    - :meth:`fnames` - Return a list of filenames from which the results were
      loaded.

    - :meth:`names` - Return a list of names of variables that are present in all
      of the simulations and that match a pattern.

    - :meth:`nametree` - Return a tree of the common variable names of the
      simulations based on the Modelica_ model hierarchy.

    - :meth:`plot` - Plot data from the simulations in 2D Cartesian coordinates.

    - :meth:`unique_IVs` - Return a dictionary of initial values that are
      different among the variables that the simulations share.

    - :meth:`unique_names` - Return a dictionary of variable names that are not
      in all of the simulations.
    """
    # TODO: Add browse method to plot any common variable across all simulations.

    def __init__(self, *args):
        """Initialize as a list of :class:`SimRes` instances, loading files as
        necessary.

        Initialization signatures:

        - :class:`SimResList`(): Returns an empty simulation list

        - :class:`SimResList`(*sims*), where sims is a list of :class:`SimRes`
          instances:  Casts the list into a :class:`SimResList`

        - :class:`SimResList`(*filespec*), where *filespec* is a filename or
          directory, possibly with wildcards a la `glob
          <https://docs.python.org/2/library/glob.html>`_:  Returns a
          :class:`SimResList` of :class:`SimRes` instances loaded from the
          matching or contained files

             The filename or directory must include the absolute path or be
             resolved to the current directory.

             An error is only raised if no files can be loaded.

        - :class:`SimResList`(*filespec1*, *filespec2, ...): Loads all files
          matching or contained by *filespec1*, *filespec2*, etc. as above.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/ChuaCircuit/*/*.mat')
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../ModelicaRes/examples/ChuaCircuit directory:
              1/dsres.mat
              2/dsres.mat
        """
        if not args:
            list.__init__(self, [])
        elif isinstance(args[0], string_types):
            # The arguments are filenames or directories.

            # Get a unique list of matching filenames.
            fnames = set()
            for arg in args:
                if os.path.isdir(arg):
                    fnames = fnames.union(set(glob(os.path.join(arg, '*.mat'))))
                elif '*' in arg or '?' in arg or '[' in arg:
                    fnames = fnames.union(set(glob(arg)))
                else:
                    fnames.add(arg)

            # Load simulations from the filenames.
            list.__init__(self, _get_sims(fnames))

        elif len(args) == 1:
            # The argument is a list or iterable of SimRes instances.
            sims = list(args[0])
            for sim in sims:
                assert isinstance(sim, SimRes), ("All entries in the list must "
                                                 "be SimRes instances.")
            list.__init__(self, sims)

    def append(self, item):
        """Add a simulation to the end of the list of simulations.

        **Arguments:**

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

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/ChuaCircuit/*/*.mat')
           >>> sims.append('examples/ThreeTanks.mat')
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../ModelicaRes/examples directory:
              ChuaCircuit/1/dsres.mat
              ChuaCircuit/2/dsres.mat
              ThreeTanks.mat
        """
        if isinstance(item, SimRes):
            list.append(self, item)
        else:
            assert isinstance(item, string_types), ("The simulation list can "
                "ony be appended by providing a SimRes instance, filename, or "
                "directory.")

            # Get the matching filenames.
            if os.path.isdir(item):
                fnames = glob(os.path.join(item, '*.mat'))
            elif '*' in item or '?' in item or '[' in item:
                fnames = glob(item)
            else:
                fnames = [item]

            # Load simulations from the filenames.
            self.extend(SimResList(_get_sims(fnames)))

    def names(self, pattern=None, re=False, constants_only=False):
        r"""Return a list of names of variables that are present in all of the
        simulations and that match a pattern.

        By default, all of the common variables are returned.

        **Arguments:**

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
            beginning or the end of the pattern.  For example, 'x\*' matches
            variables that begin with "x", whereas '\*x\*' matches all variables
            that contain "x".

          - If *re* is *True*, regular expressions are used a la `Python's re
            module <http://docs.python.org/2/library/re.html>`_.  See also
            http://docs.python.org/2/howto/regex.html#regex-howto.

            Since :mod:`re.search` is used to produce the matches, it is as if
            wildcards ('.*') are automatically added at the beginning and the
            end.  For example, 'x' matches all variables that contain "x".  Use
            '^x$' to match only the variables that begin with "x" and 'x$' to
            match only the variables that end with "x".

            Note that '.' is a subclass separator in Modelica_ but a wildcard in
            regular expressions.  Escape the subclass separator as '\\.'.

        - *re*: *True* to use regular expressions (*False* to use shell style)

        - *constants_only*: *True* to include only the variables that do not
          change over time

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/ChuaCircuit/*/*.mat')

           >>> # Names for voltages across all of the components:
           >>> sims.names('^[^.]*.v$', re=True)
           ['G.v', 'L.v', 'C2.v', 'Nr.v', 'Ro.v', 'C1.v']
        """
        sets = [set(sim.names(constants_only=constants_only)) for sim in self]
        return util.match(set.intersection(*sets), pattern, re)

    def nametree(self, pattern=None, re=False, constants_only=False):
        """Return a tree of the common variable names of the simulations based
        on the Modelica_ model hierarchy.

        The tree is returned as a nested dictionary.  The keys are the Modelica_
        class instances (including the index if there are arrays) and the values
        are are subclasses.  The value at the end of each branch is the full
        variable name.

        All names are included by default, but the names can be filtered using
        *pattern*, *re*, and *constants_only*.  See :mod:`names` for a
        description of those arguments.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/ChuaCircuit/*/*.mat')
           >>> sims.nametree('L*v') # doctest: +ELLIPSIS
           {'L': {'p': {'v': 'L.p.v'}, 'n': {'v': 'L.n.v'}, 'v': 'L.v'}}
        """
        return util.tree(self.names(pattern, re, constants_only))

    def unique_IVs(self, constants_only=False):
        """Return a dictionary of initial values that are different among the
        variables that the simulations share.  Each key is a variable name and
        each value is an initial value.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/ChuaCircuit/*/*.mat')
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../ModelicaRes/examples/ChuaCircuit directory:
              1/dsres.mat
              2/dsres.mat
           >>> sims.unique_IVs()['L.L']
           [18.0, 10.0]
        """
        unique_IVs = {}
        for name in self.names(constants_only=constants_only):
            IVs = self[name].IV()
            if len(set(IVs)) > 1:
                unique_IVs[name] = IVs
        return unique_IVs

    def unique_names(self):
        """Return a dictionary of variable names that are not in all of the
        simulations.  Each key is a variable name and each value is a Boolean
        list indicating if the associated variable appears in each of the
        simulations.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/*')
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../ModelicaRes/examples directory:
              ThreeTanks.mat
              ChuaCircuit.mat
           >>> sims.unique_names()['L.L']
           [False, True]
        """
        sets = [set(sim.names()) for sim in self]
        all_names = set.union(*sets)
        unique_names = all_names - set(self.names())
        return {name: [name in sim for sim in self] for name in unique_names}

    def __contains__(self, key):
        """Return key in self.

        This method is overloaded.  If y is a :class:`SimRes` instance, then
        it returns *True* iff the instance is in the list of simulation results.
        If y is a string, then it returns *True* iff the string is the name of a
        variable that is included in all of the simulations in the list.
        """
        if isinstance(item, string_types):
            return all(item in sim for sim in self)
        else:
            return list.__contains__(self, item)

    def __getitem__(self, i):
        """x.__getitem__(y) <==> x[y]

        This method is overloaded beyond the standard indexing and slicing.  If
        the index (*i*) is a variable name (string), then a specialized list of
        variables is returned with references to the corresponding variable in
        each of the simulations.  That list can be queried for the attributes
        listed in :meth:`SimRes.__getitem__`.  The same call signature applies
        here except that :meth:`arrays` in this class correponds to
        :meth:`Variable.array`.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/ChuaCircuit/*/*.mat')
           >>> sims['L.v'].mean()
           [0.014733823, 0.0044694417]
        """
        if isinstance(i, slice):
            # Slice the simulation list and cast it as a SimResList.
            return self.__class__(list.__getitem__(self, i))
        elif isinstance(i, string_types):
            # Return a list containing the variable from each of the simulations.
            return _VarList([sim[i] for sim in self])
        else:
            # Return a single simulation (SimRes instance).
            return list.__getitem__(self, i)

    def __str__(self):
        """Return str(self).

        This provides a readable description of the :class:`SimResList`.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimResList
           >>> sims = SimResList('examples/ChuaCircuit/*/*.mat')
           >>> print(sims) # doctest: +ELLIPSIS
           List of simulation results (SimRes instances) from the following files
           in the .../ModelicaRes/examples/ChuaCircuit directory:
              1/dsres.mat
              2/dsres.mat
        """
        if len(self) == 0:
            return "Empty list of simulation results"
        elif len(self) == 1:
            return ("List of simulation results (SimRes instance) from\n"
                    + self[0].fname)
        else:
            basedir = self.basedir()
            start = len(basedir) + 1
            short_fnames = [fname[start:] for fname in self.fnames()]
            string = ("List of simulation results (SimRes instances) from the "
                      "following files")
            string += "\nin the %s directory:\n   " % basedir if basedir else ":\n   "
            string += "\n   ".join(short_fnames)
            return string

    def plot(self, *args, **kwargs):
        """Plot data from selected variables over all of the simulations in 2D
        Cartesian coordinates.

        This method calls :meth:`simres.SimRes.plot` from the included instances
        of :class:`simres.SimRes`.

        A new figure is created if necessary.

        **Arguments:**

        - *suffixes*: Suffix or list of suffixes for the legends (see
          :meth:`simres.SimRes.plot`)

             If *suffixes* is *None*, then no suffix will be used.  If it is an
             empty string (''), then the base filenames will be used.

        - *color*: Single entry, list, or :class:`itertools.cycle` of colors that
          will be used sequentially

             Each entry may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *dashes*: Single entry, list, or :class:`itertools.cycle` of dash styles
          that will be used sequentially

             Each style is a tuple of on/off lengths representing dashes.  Use
             (0, 1) for no line and (None ,None) for a solid line.

             .. Seealso:: http://matplotlib.sourceforge.net/api/collections_api.html

        - *\*args*, *\*\*kwargs*: Propagated to :meth:`simres.SimRes.plot` (and
          thus to :meth:`util.plot` and finally :meth:`matplotlib.pyplot.plot`)

        **Returns:**

        1. *ax1*: Primary y axes

        2. *ax2*: Secondary y axes

        **Example:**

        .. plot:: examples/ChuaCircuits.py
           :alt: plot of a Chua circuit with different inductances
        """
        # Get the local arguments.
        suffixes = kwargs.pop('suffixes', '')
        color = kwargs.pop('color', ['b', 'g', 'r', 'c', 'm', 'y', 'k'])
        dashes = kwargs.pop('dashes', [(None, None), (3, 3), (1, 1), (3, 2, 1, 2)])

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
        if suffixes == '':
            start = len(self.basedir())
            suffixes = [sim.fname[start:].lstrip(os.sep) for sim in self]
        elif suffixes is None:
            suffixes = ['']*len(self)

        # Generate the plots.
        for i, (sim, suffix) in enumerate(zip(self, suffixes)):
            ax1, ax2 = sim.plot(*args, suffix=suffix, **kwargs)
            if i == 0:
                kwargs.update({'ax1': ax1, 'ax2': ax2})
        return ax1, ax2


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
