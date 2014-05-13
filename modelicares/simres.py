#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classes to load, analyze, and plot results from Modelica_ simulations

- :class:`SimRes` - Class to load and analyze results from a Modelica_-based
  simulation

- :class:`Info` - Aliases for the "get" methods of :class:`SimRes`


.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__credits__ = ["Joerg Raedler"]
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
import numpy as np

from functools import wraps
from re import compile as re_compile
from matplotlib.pyplot import figlegend
from matplotlib import rcParams
from fnmatch import fnmatchcase
from difflib import get_close_matches
from pandas import DataFrame

from modelicares import util
from modelicares.texunit import unit2tex, label_number
from modelicares._io import simloaders
from modelicares._gui import Browser


class SimRes(object):
    """Class to load and analyze results from a Modelica_-based simulation

    Methods:

    - :meth:`browse` - Launch a variable browser

    - :meth:`fbase` - Return the base filename from which the data was loaded,
      without the directory or file extension

    - :meth:`get_arrays` - Return array(s) of times and values for variable(s)

    - :meth:`get_arrays_wi_times` - Return array(s) of times and values for
      variable(s) within a time range

    - :meth:`get_description` - Return the description(s) of variable(s)

    - :meth:`get_displayUnit` - Return the Modelica_ *displayUnit* attribute(s)
      of variable(s)

    - :meth:`get_IV` - Return the initial value(s) of variable(s)

    - :meth:`get_FV` - Return the final value(s) of variable(s)

    - :meth:`get_max` - Return the maximum value(s) of variable(s)

    - :meth:`get_mean` - Return the time-averaged value(s) of variable(s)

    - :meth:`get_min` - Return the minimum value(s) of variable(s)

    - :meth:`get_times` - Return vector(s) of the sample times of variable(s)

    - :meth:`get_unit` - Return the *unit* attribute(s) of variable(s)

    - :meth:`get_values` - Return vector(s) of the values of variable(s)

    - :meth:`get_values_at_times` - Return vector(s) of the values of
      variable(s) at given times

    - :meth:`get_values_wi_times` - Return vector(s) of the values of
      variable(s) within a time range

    - :meth:`names` - Return a list of variable names that match a pattern

    - :meth:`nametree` - Return a tree of all variable names with respect to
      the path names

    - :meth:`plot` - Plot data as points and/or curves in 2D Cartesian
      coordinates

    - :meth:`set_displayUnit` - Set the the Modelica_ *displayUnit* attribute of
      a variable

    - :meth:`set_displayUnit` - Set the the Modelica_ *description* attribute of
      a variable

    - :meth:`to_pandas` - Return a `pandas DataFrame`_ with data from selected
      variables

    - :meth:`sankey` - Create a figure with Sankey diagram(s)

    Attributes:

    - *fname* - Filename from which the data was loaded, with full path and
      extension

TODO *tool*


    .. testsetup::
       >>> import numpy as np
       >>> np.set_printoptions(precision=4)

    .. _pandas DataFrame: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html?highlight=dataframe#pandas.DataFrame
    """


    def __init__(self, fname='dsres.mat', constants_only=False, tool=None):
        """Upon initialization, load Modelica_ simulation results from a file.

        **Arguments:**

        - *fname*: Name of the file (may include the path)

             The file extension (e.g., '.mat') is optional.

        - *constants_only*: *True* to load only the variables from the first
          data table

             The first data table typically contains all of the constants,
             parameters, and variables that don't vary.  If only that
             information is needed, it may save resources to set
             *constants_only* to *True*.

        **Example:**

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
        """

        # Load the file and store the data.
        for loader in simloaders:
            self.data = loader(fname, constants_only)
            try:
                self.data = loader(fname, constants_only)
            except IOError:
                raise
            except:
                continue
            else:
                break

        # Save the filename.
        self.fname = fname
# TODO: support tool argument, save it as an attribute and list in doc as argument and attribute.


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
            if isinstance(names, basestring):
                return f(self, names, *args, **kwargs)
            else:
                return [wrapped(self, name, *args, **kwargs) for name in names]

        return wrapped


    def _suggest(f):
        """Wrap a look-up in the data dictionary to provide suggestions if there
        is a key error.
        """
        @wraps(f)
        def wrapped(self, name, *args, **kwargs):
            """Catch a KeyError and raise a LookupError with suggestions."""
            try:
                return f(self, name, *args, **kwargs)
            except KeyError:
                msg = '%s is not a valid variable name.' % name
                close_matches = get_close_matches(name, self.names())
                if close_matches:
                    msg += "\n       ".join(["\n\nDid you mean one of these?"]
                                            + close_matches)
                raise LookupError(msg)

        return wrapped


    def _fromname(f):
        """Return a function that accepts a variable name, given a function that
        accepts a data entry.
        """
        @wraps(f)
        def wrapped(self, name, *args, **kwargs):
            """Look up the data entry and pass it to the original function."""
            return f(self.data[name], *args, **kwargs)

        return wrapped


    # TODO: Remove the "_" prefix and add it to the list once this is finished.
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

        - *names*: List of names of the data to be plotted

             The names should be fully qualified (i.e., relative to the root of
             the simulation results).

        - *times*: List of times at which the data should be sampled

             If multiple times are given, then subfigures will be generated.

        - *width*: Width of the bars

            At ``width = 1``, there is no overlap.

        - *n_rows*: Number of rows of (sub)plots

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be the base
             filename of the data.  Use '' for no title.

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

        - \*\**kwargs*: Additional arguments for  :meth:`matplotlib.pyplot.bar`

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
            axis.bar(ind-width/2., self.get_values_at_times(names, time),
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

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.browse()

        .. only:: html

           .. image:: _static/browse.png
              :scale: 90 %
              :alt: variable browser

        .. only:: latex

           .. image:: _static/browse.png
              :scale: 80 %
              :alt: variable browser
        """
        import wx

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
        """Return the base filename from which the data was loaded, without the
        directory or file extension.
        """
        return os.path.splitext(os.path.split(self.fname)[1])[0]


    @_acceptlists
    @_suggest
    @_fromname
    def get_arrays(entry, *args, **kwargs):
        """Return array(s) of times and values for variable(s).

        In each array, the first column is time and the second column contains
        the values.

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable names

        - *i*: Index (-1 for last, *None* for all), list of indices, or slice of
          the values(s) to return

             By default, all values are returned.

        - *f*: Function that operates on each array (default is identity)

        If *names* is a string, then the output will be an array.  If *names* is
        a (optionally nested) list of strings, then the output will be a
        (nested) list of arrays.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_arrays('L.v') # doctest: +NORMALIZE_WHITESPACE
           array([[  0.0000e+00,   0.0000e+00],
                  [  5.0000e+00,   1.0923e-01],
                  [  1.0000e+01,   2.1084e-01],
                  ...,
                  [  2.4950e+03,  -2.2577e-01],
                  [  2.5000e+03,  -2.5353e-01],
                  [  2.5000e+03,  -2.5353e-01]], dtype=float32)

        Note that this is the same result as from :meth:`__call__`.
        """
        return entry.get_array(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_arrays_wi_times(entry, *args, **kwargs):
        """Return arrays(s) of times and values of variable(s) within a time
        range.

        In each array, the first column is time and the second column contains
        the values.

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable names

        - *t1*: Lower time bound

        - *t2*: Upper time bound

        - *f*: Function that operates on each vector (default is identity)

        If *names* is a string, then the output will be an array.  If *names* is
        a (optionally nested) list of strings, then the output will be a
        (nested) list of arrays.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_arrays_wi_times('L.v', t1=0, t2=10)
           array([[  0.    ,   0.    ],
                  [  5.    ,   0.1092],
                  [ 10.    ,   0.2108]], dtype=float32)
        """
        return entry.array_wi_times(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_description(entry):
        """Return the description(s) of variable(s).

        **Arguments:**

        - *name*: Variable name or (possibly nested) list of variable names

        If *name* is a string, then the output will be a single description.
        If *name* is a (optionally nested) list of strings, then the output
        will be a (nested) list of descriptions.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_description('L.v')
           'Voltage drop between the two pins (= p.v - n.v)'
        """
        return entry.description


    @_acceptlists
    @_suggest
    @_fromname
    def get_displayUnit(entry):
        """Return the Modelica_ *displayUnit* attribute(s) of variable(s).

        **Arguments:**

        - *name*: Variable name or (possibly nested) list of variable names

        If *name* is a string, then the output will be a single display unit.
        If *name* is a (optionally nested) list of strings, then the output
        will be a (nested) list of display units.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_displayUnit('G.T_heatPort')
           'degC'
        """
        return entry.displayUnit


    @_acceptlists
    @_suggest
    @_fromname
    def get_FV(entry, *args, **kwargs):
        """Return the final value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function to be applied to each value (default is identity)

        If *names* is a string, then the output will be a single value.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of values.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_FV(['Time', 'L.v'])
           [2500.0, -0.25352862]
        """
        return entry.FV(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_IV(entry, *args, **kwargs):
        """Return the initial value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable names

        - *f*: Function to be applied to each value (default is identity)

        If *names* is a string, then the output will be a single value.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of values.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_IV('L.v')
           0.0
        """
        return entry.IV(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_max(entry, *args, **kwargs):
        """Return the maximum value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function to be applied before taking the maximum (default is
          identity)

        If *names* is a string, then the output will be a single value.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of values.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_max('L.v')
           0.77344114
        """
        return entry.max(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_mean(entry, *args, **kwargs):
        """Return the time-averaged value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function to be applied before taking the mean (default is
          identity)

        If *names* is a string, then the output will be a single value.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of values.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_mean('L.v')
           0.014733823
        """
        return entry.mean(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_min(entry, *args, **kwargs):
        """Return the minimum value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function to be applied before taking the minimum (default is
          identity)

        If *names* is a string, then the output will be a single value.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of values.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_min('L.v')
           -0.9450165
        """
        return entry.min(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_times(entry, *args, **kwargs):
        """Return vector(s) of the sample times of variable(s).

        **Arguments:**

        - *name*: Variable name or (possibly nested) list of variable names

        Passed to :meth:`DataEntry.times` via \**args* and \*\**kwargs*:

        - *i*: Index (-1 for last, *None* for all), list of indices, or slice of
          the values(s) to return

             By default, all values are returned.

        - *f*: Function that operates on each vector (default is identity)

        If *name* is a string, then the output will be a vector of times.  If
        *name* is a (optionally nested) list of strings, then the output will
        be a (nested) list of vectors.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_times('L.v') # doctest: +ELLIPSIS
           array([.TODO add numbers back here and elsewhere..], dtype=float32)
        """
        return entry.times(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_unit(entry):
        """Return the *unit* attribute(s) of variable(s).

        **Arguments:**

        - *name*: Variable name or (possibly nested) list of variable names

        If *name* is a string, then the output will be a single unit.  If
        *name* is a (optionally nested) list of strings, then the output will
        be a (nested) list of units.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_unit('L.v')
           'V'
        """
        return entry.unit


    @_acceptlists
    @_suggest
    @_fromname
    def get_values(entry, *args, **kwargs):
        """Return vector(s) of the values of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable names

        - *i*: Index (-1 for last, *None* for all), list of indices, or slice of
          the values(s) to return

             By default, all values are returned.

        - *f*: Function that operates on each vector (default is identity)

        If *names* is a string, then the output will be a vector of values.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of vectors.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_values('L.v') # doctest: +ELLIPSIS
           array([...], dtype=float32)

        If the variable cannot be found, then possible matches are listed:

        .. code-block:: python

           >>> sim.get_values(['L.vv']) # doctest: +SKIP
           ['L.vv'] is not a valid variable name.
           <BLANKLINE>
           Did you mean one of these?
                  L.v
                  L.p.v
                  L.n.v
           Traceback (most recent call last):
            ...
           KeyError: 'L.vv'

        The other *get_*\* methods also give this message when a variable cannot
        be found.
        """
        return entry.values(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_values_at_times(entry, *args, **kwargs):
        """Return vector(s) of the values of variable(s) at given times.

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable names

        - *times*: Scalar, numeric list, or a numeric array of the times from
          which to pull samples

        - *f*: Function that operates on each vector (default is identity)

        If *names* is a string, then the output will be a vector of values.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of vectors.

        If *times* is not provided, all of the samples will be returned.  If
        necessary, the values will be interpolated over time.  The function *f*
        is applied before interpolation.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_values_at_times('L.v', [0, 2000]) # doctest: +ELLIPSIS
           array([...])
        """
        return entry.values_at_times(*args, **kwargs)


    @_acceptlists
    @_suggest
    @_fromname
    def get_values_wi_times(entry, *args, **kwargs):
        """Return vector(s) of the values of variable(s) within a time range.

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable names

        - *t1*: Lower time bound

        - *t2*: Upper time bound

        - *f*: Function that operates on each vector (default is identity)

        If *names* is a string, then the output will be a vector of values.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of vectors.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_values_wi_times('L.v', t1=0, t2=15) # doctest: +NORMALIZE_WHITESPACE
           array([ 0. , 0.1092, 0.2108, 0.3046], dtype=float32)
        """
        return entry.values_wi_times(*args, **kwargs)


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

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> # Names for voltages across all of the components:
           >>> sim.names('^[^.]*.v$', re=True)
           ['G.v', 'L.v', 'C2.v', 'Nr.v', 'Ro.v', 'C1.v']
        """
        # Get a list of all the variables or just the constants.
        if constants_only:
            names = [item[0] for item in self.data.items() if item[1].is_constant()]
        else:
            names = list(self.data)

        # Search the list.
        if pattern is None or (pattern in ['.*', '.+', '.', '.?', ''] if re
                               else pattern == '*'):
            return names # Shortcut
        else:
            if re:
                matcher = re_compile(pattern).search
            else:
                matcher = lambda name: fnmatchcase(name, pattern)
            return filter(matcher, names)


    def n_constants(self, pattern=None, re=False):
        """Return the number of variables that do not change over time.

        There are no arguments.  Note that this number may be greater than the
        number of declared parameters and constants in the Modelica_ code, since
        a variable may be fixed in value even though it is not declared as a
        constant or parameter.
        """
        return sum([variable.is_constant() for variable in self.data.values()])


    def nametree(self, pattern=None, re=False):
        """Return a tree of all variable names with respect to the path names.

        The tree represents the structure of the Modelica_ model.  It is
        returned as a nested dictionary.  The keys are the path elements and
        the values are sub-dictionaries or variable names.

        All names are included by default, but the names can be filtered using
        *pattern* and *re*.  See :mod:`names` for a description of those
        arguments.

        **Example:**

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.nametree('L*v') # doctest: +ELLIPSIS
           {'L': {'p': {'v': 'L.p.v'}, 'n': {'v': 'L.n.v'}, 'v': 'L.v'}}
        """
        # This method has been copied and modified from DyMat version 0.5
        # (Joerg Raedler,
        # http://www.j-raedler.de/2011/09/dymat-reading-modelica-results-with-python/,
        # BSD License).
        root = {}
        for name in self.names(pattern, re):
            branch = root
            elements = name.split('.')
            for element in elements[:-1]:
                if not element in branch:
                    branch[element] = {}
                branch = branch[element]
            branch[elements[-1]] = name
        return root


    def plot(self, ynames1=[], ylabel1=None, legends1=[],
             leg1_kwargs={'loc': 'best'}, ax1=None,
             ynames2=[], ylabel2=None, legends2=[],
             leg2_kwargs={'loc': 'best'}, ax2=None,
             xname='Time', xlabel=None,
             title=None, label="xy", incl_prefix=False, suffix=None,
             use_paren=True, **kwargs):
        """Plot data as points and/or curves in 2D Cartesian coordinates.

        **Arguments:**

        - *ynames1*: Names of variables for the primary y axis

             If any names are invalid, then they will be skipped.

        - *ylabel1*: Label for the primary y axis

             If *ylabel1* is *None* (default) and all of the variables have the
             same Modelica_ description string, then the common description
             will be used.  Use '' for no label.

        - *legends1*: List of legend entries for variables assigned to the
          primary y axis

             If *legends1* is an empty list ([]), ynames1 will be used.  If
             *legends1* is *None* and all of the variables on the primary axis
             have the same unit, then no legend will be shown.

        - *leg1_kwargs*: Dictionary of keyword arguments for the primary legend

        - *ax1*: Primary y axes

             If *ax1* is not provided, then axes will be created in a new
             figure.

        - *ynames2*, *ylabel2*, *legends2*, *leg2_kwargs*, and *ax2*: Similar
          to *ynames1*, *ylabel1*, *legends1*, *leg1_kwargs*, and *ax1* but
          for the secondary y axis

        - *xname*: Name of the x-axis data

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

        - \*\**kwargs*: Propagated to :meth:`util.plot` (and thus to
          :meth:`matplotlib.pyplot.plot`)

             If both y axes are used (primary and secondary), then the *dashes*
             argument is ignored.  The curves on the primary axis will be solid
             and the curves on the secondary axis will be dotted.

        **Returns:**

        1. *ax1*: Primary y axes

        2. *ax2*: Secondary y axes

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes, save

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.plot(ynames1='L.i', ylabel1="Current",
           ...          ynames2='L.der(i)', ylabel2="Derivative of current",
           ...          title="Chua Circuit", label='examples/ChuaCircuit') # doctest: +ELLIPSIS
           (<matplotlib.axes...AxesSubplot object at 0x...>, <matplotlib.axes...AxesSubplot object at 0x...>)

           >>> save()
           Saved examples/ChuaCircuit.pdf
           Saved examples/ChuaCircuit.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()

        .. only:: html

           .. image:: ../examples/ChuaCircuit.png
              :scale: 70 %
              :alt: plot of Chua circuit

        .. only:: latex

           .. figure:: ../examples/ChuaCircuit.pdf
              :scale: 70 %

              Plot of Chua circuit
        """
        # Note:  ynames1 is the first argument (besides self) so that plot()
        # can be called with simply a variable name.

        def ystrings(ynames, ylabel, legends):
            """Generate a y-axis label and set of legend entries.
            """
            if ynames:
                if ylabel is None: # Try to create a suitable axis label.
                    descriptions = self.get_description(ynames)
                    # If the descriptions are the same, label the y axis with
                    # the 1st one.
                    ylabel = descriptions[0]
                    if len(set(descriptions)) != 1:
                        print("The y-axis variable descriptions are different. "
                              " The first has been used as the axis label. "
                              " Please check it and provide ylabel1 or ylabel2"
                              " if necessary.")
                if legends == []:
                    legends = ynames
                if incl_prefix:
                    legends = [self.fbase() + ': ' + leg for leg in legends]
                if suffix:
                    legends = ([leg + ' (%s)' % suffix for leg in legends]
                               if use_paren else
                               [leg + suffix for leg in legends])
                units = self.get_unit(ynames)
                if len(set(units)) == 1:
                    # The  units are the same, so show the 1st one on the axis.
                    if ylabel != "":
                        ylabel = label_number(ylabel, units[0])
                else:
                    # Show the units in the legend.
                    if legends:
                        legends = [label_number(entry, unit) for entry, unit in
                                   zip(legends, units)]
                    else:
                        legends = [label_number(entry, unit) for entry, unit in
                                   zip(ynames, units)]

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
            xlabel = 'Time' if xname == 'Time' else self.get_description(xname)
            # With Dymola 7.4, the description of the time variable will be
            # "Time in", which isn't good.
        if xlabel != "":
            xlabel = label_number(xlabel, self.get_unit(xname))

        # Generate the y-axis labels and sets of legend entries.
        ylabel1, legends1 = ystrings(ynames1, ylabel1, legends1)
        ylabel2, legends2 = ystrings(ynames2, ylabel2, legends2)

        # Read the data.
        if xname == 'Time':
            y_1 = self.get_values(ynames1)
            y_2 = self.get_values(ynames2)
        else:
            x = self.data[xname].values()
            times = self.data[xname].times
            y_1 = self.get_values_at_times(ynames1, times)
            y_2 = self.get_values_at_times(ynames2, times)

        # Plot the data.
        if ynames1:
            if ynames2:
                # Use solid lines for primary axis and dotted lines for
                # secondary.
                kwargs['dashes'] = [(None, None)]
                util.plot(y_1, self.get_times(ynames1) if xname == 'Time'
                          else x, ax1, label=legends1, **kwargs)
                kwargs['dashes'] = [(3, 3)]
                util.plot(y_2, self.get_times(ynames2) if xname == 'Time'
                          else x, ax2, label=legends2, **kwargs)
            else:
                util.plot(y_1, self.get_times(ynames1) if xname == 'Time'
                          else x, ax1, label=legends1, **kwargs)
        elif ynames2:
            util.plot(y_2, self.get_times(ynames2) if xname == 'Time'
                      else x, ax2, label=legends2, **kwargs)

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

        - *times*: List of times at which the data should be sampled

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

        - \*\**kwargs*: Additional arguments for  :class:`matplotlib.sankey.Sankey`

        **Returns:**

        1. List of :class:`matplotlib.sankey.Sankey` instances of the subplots

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes, save

           >>> sim = SimRes('examples/ThreeTanks')
           >>> sankeys = sim.sankey(label='examples/ThreeTanks',
           ...     title="Sankey Diagrams of Modelica.Fluid.Examples.Tanks.ThreeTanks",
           ...     times=[0, 50, 100, 150], n_rows=2, format='%.1f ',
           ...     names=['tank1.ports[1].m_flow', 'tank2.ports[1].m_flow',
           ...            'tank3.ports[1].m_flow'],
           ...     labels=['Tank 1', 'Tank 2', 'Tank 3'],
           ...     orientations=[-1, 0, 1],
           ...     scale=0.1, margin=6, offset=1.5,
           ...     pathlengths=2, trunklength=10)
           >>> save()
           Saved examples/ThreeTanks.pdf
           Saved examples/ThreeTanks.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()

        .. only:: html

           .. image:: ../examples/ThreeTanks.png
              :scale: 70 %
              :alt: Sankey digarams of three-tank model

        .. only:: latex

           .. figure:: ../examples/ThreeTanks.pdf
              :scale: 70 %

              Sankey digarams of three-tank model
        """
        from matplotlib.sankey import Sankey

        # Get the data.
        n_plots = len(times)
        Qdots = self.get_values_at_times(names, times)
        start_time = self.data['Time'].times[0]
        stop_time = self.data['Time'].times[-1]

        # Create a title if necessary.
        if title is None:
            title = "Sankey Diagram of " + self.fbase()

        # Determine the units of the data.
        flow_unit = self.get_unit(names)
        assert len(set(flow_unit)) == 1, (
            "The variables have inconsistent units.")
        flow_unit = flow_unit[0]

        # Set up the subplots.
        if not subtitles:
            unit = unit2tex(self.get_unit('Time'))
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


    def set_displayUnit(self, name, displayUnit):
        """Set the the Modelica_ *displayUnit* attribute of a variable.

        **Arguments:**

        - *name*: Name of the variable

        - *displayUnit*: String representing the display unit to be assigned

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.set_displayUnit('L.v', 'mV')
           >>> sim.get_displayUnit('L.v')
           'mV'
        """
        self.data[name] = self.data[name]._replace(displayUnit=displayUnit)


    def set_description(self, name, description):
        """Set the the Modelica_ *description* attribute of a variable.

        **Arguments:**

        - *name*: Name of the variable

        - *description*: Description to be assigned

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_description('L.v')
           'Voltage drop between the two pins (= p.v - n.v)'
           >>> sim.set_description('L.v', 'Voltage difference')
           >>> sim.get_description('L.v')
           'Voltage difference'
        """
        self.data[name] = self.data[name]._replace(description=description)


    def to_pandas(self, names=None, aliases={}):
        """Return a `pandas DataFrame`_ with data from selected variables.

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
             the entries are the names as they will be included in the column
             headings.  Any variables not in this list will not be aliased.

        **Examples:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit')
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

           >>> sim = SimRes('examples/ThreeTanks')
           >>> aliases = {'tank1.level': "Tank 1 level",
                          'tank2.level': "Tank 2 level",
                          'tank3.level': "Tank 3 level"}
           >>> sim.to_pandas(aliases.keys(), aliases) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE

        """
        # Simple function to label a variable with its unit:
        label = lambda name: name + ' / ' + self.data[name].unit

        # Create the list of variable names.
        if names is None:
            names = self.names()
        else:
            names = list(set(util.flatten_list(names)).add('Time'))

        # Determine the values.
        times = self.data['Time'].values()
        values = [self.data[name].values() # Save computation.
                  if np.array_equal(self.data[name].times, times) else
                  self.get_values_at_times(name, times) # Resample.
                  for name in names]
        # TODO: time this to see if the first branch is worth it.

        # Create a dictionary of values and labels (column headings).
        values = []
        labels = []
        for name in names:
            values.append(self.data[name].values()
                          if np.array_equal(self.data[name].times, times) else
                          self.get_values_at_times(name, times))
            try:
                labels.append(label(aliases[name]))
            except KeyError:
                labels.append(label(name))

        # Create the pandas data frame.
        return DataFrame(values).set_index('Time / s')


    def __call__(name, method=get_arrays, *args, **kwargs):
        """Upon a call to an instance of :class:`SimRes`, call a method on
        variable(s) given their name(s).

        **Arguments**:

        - *name*: Variable name

        - *method*: Method for retrieving information about the variable(s)

             The default is :meth:`get_arrays`.  *method* may be a list or
             tuple, in which case the return value is a list or tuple.

        - \**args*, \*\**kwargs*: Additional arguments for *method*

        **Examples:**

        .. code-block:: python

           >>> from modelicares.simres import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           # Array of time and value vectors for a variable:
           >>> sim('L.v') # doctest: +NORMALIZE_WHITESPACE
           array([[  0.0000e+00,   0.0000e+00],
                  [  5.0000e+00,   1.0923e-01],
                  [  1.0000e+01,   2.1084e-01],
                  ...,
                  [  2.4950e+03,  -2.2577e-01],
                  [  2.5000e+03,  -2.5353e-01],
                  [  2.5000e+03,  -2.5353e-01]], dtype=float32)

        Note that this is the same result as from :meth:`get_arrays`.

        .. code-block:: python

           # Other attributes
           >>> from modelicares.simres import Info
           >>> print("The final value of %s is %.3f %s." %
           ...       sim('L.i', (Info.description, Info.FV, Info.unit)))
           The final value of Current flowing from pin p to pin n is 2.049 A.
        """
        assert isinstance(name, basestring), "name must be a string."
        # It'd be possible to accept lists of variable names (in fact it'd work
        # without this assert statement), but the call structure is complex
        # enough already.

        try:
            return method(self, name=name, *args, **kwargs)
        except TypeError:
            t = type(method)
            return t(m(self, name=name, *args, **kwargs) for m in method)


    def __contains__(self, name):
        """Test if a variable is present in the simulation results.

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
        return name in self.data


    @_suggest
    @_fromname
    def __getitem__(entry):
        """Upon accessing a variable name within an instance of :class:`SimRes`,
        return its data entry.

        This provides access to non-vectorized versions of all of the *get_*
        methods of :class:`SimRes`, as attributes:

        - *description* - The Modelica_ variable's description string

        - *unit* - The Modelica_ variable's *unit* attribute

        - *displayUnit* - The Modelica_ variable's *displayUnit* attribute

        - :meth:`times` - Sample times of the variable

        or methods:

        - :meth:`array` - Return an array of times and values for the variable

        - :meth:`array_wi_times` - Return an array of times and values for the
          variable within a time range

        - :meth:`IV` - Return the initial value of the variable

        - :meth:`FV` - Return the final value of the variable

        - :meth:`max` - Return the maximum value of the variable

        - :meth:`mean` - Return the time-averaged value of the variable

        - :meth:`min` - Return the minimum value of the variable

        - :meth:`values` - Values of the variable

        - :meth:`values_at_times` - Values of the variable at given times

        - :meth:`values_wi_times` - Values of the variable within a time range

        also:

        - :meth:`is_constant` - *True*, if the variable does not change over
          time

        **Examples:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> sim['L.v'].unit
           'V'

           >>> sim['L.v'].values_wi_times(10, 25) # doctest: +NORMALIZE_WHITESPACE

        """
        return entry


    def __len__(self):
        """Return the number of variables in the simulation

        This includes the time variable.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> print("There are %i variables in the %s simulation." %
           ...       (len(sim), sim.fbase()))
           There are 62 variables in the ChuaCircuit simulation.
        """
        return len(self.data)


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

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> print(sim) # doctest: +ELLIPSIS
           Modelica simulation results from "...ChuaCircuit.mat"
        """
        return 'Modelica simulation results from "{f}"'.format(f=self.fname)


class Info:
    """Unbound aliases for the "get" methods in :class:`SimRes`

    **Example:**

    .. code-block:: python

       >>> from modelicares.simres import SimRes, Info
       >>> FV = Info.FV

       >>> sim = SimRes('examples/ChuaCircuit.mat')
       >>> FV(sim, 'L.v')
       -0.25352862
    """
    arrays = SimRes.get_arrays
    """Alias for :meth:`SimRes.get_arrays`"""
    arrays_wi_times = SimRes.get_arrays_wi_times
    """Alias for :meth:`SimRes.get_arrays_wi_times`"""
    description = SimRes.get_description
    """Alias for :meth:`SimRes.get_description`"""
    displayUnit = SimRes.get_displayUnit
    """Alias for :meth:`SimRes.get_displayUnit`"""
    FV = SimRes.get_FV
    """Alias for :meth:`SimRes.get_FV`"""
    IV = SimRes.get_IV
    """Alias for :meth:`SimRes.get_IV`"""
    max = SimRes.get_max
    """Alias for :meth:`SimRes.get_max`"""
    mean = SimRes.get_mean
    """Alias for :meth:`SimRes.get_mean`"""
    min = SimRes.get_min
    """Alias for :meth:`SimRes.get_min`"""
    times = SimRes.get_times
    """Alias for :meth:`SimRes.get_times`"""
    unit = SimRes.get_unit
    """Alias for :meth:`SimRes.get_unit`"""
    values = SimRes.get_values
    """Alias for :meth:`SimRes.get_values`"""
    values_at_times = SimRes.get_values_at_times
    """Alias for :meth:`SimRes.get_values_at_times`"""
    values_wi_times = SimRes.get_values_wi_times
    """Alias for :meth:`SimRes.get_values_wi_times`"""


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
