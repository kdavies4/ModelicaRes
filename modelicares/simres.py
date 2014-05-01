#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classes and functions to Load, analyze, and plot results from Modelica_ 
simulations


**Classes:**

- :class:`SimRes` - Class to load and analyze results from a Modelica_-based
  simulation

- :class:`Info` - Aliases for the "get" methods in :class:`SimRes`


**Functions:**

- :meth:`merge_times` - Merge a list of multiple time vectors into one vector


.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__credits__ = ["Kevin Bandy", "Joerg Raedler"]
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
import numpy as np

from re import compile as re_compile
from scipy.io import loadmat
from scipy.integrate import trapz
from matplotlib.pyplot import figlegend
from matplotlib import rcParams
from collections import namedtuple
from fnmatch import fnmatchcase
from difflib import get_close_matches

from modelicares.gui import Browser
from modelicares.texunit import unit2tex, label_number
from modelicares import base


def _chars_to_str(str_arr):
    """Convert a string array to a string.
    """
    # Copied from scipy.io.matlab.miobase (without the 'self'), 2010-10-25
    dt = np.dtype('U' + str(_small_product(str_arr.shape)))
    return np.ndarray(shape=(),
        dtype = dt,
        buffer = str_arr.copy()).item()


def _small_product(arr):
    """Find the product of all numbers in an array.

    This is faster than :meth:`product` for small arrays.
    """
    # Copied from scipy.io.matlab.miobase, 2010-10-25
    res = 1
    for e in arr:
        res *= e
    return res


def merge_times(times_list):
    """Merge a list of multiple time vectors into one vector.

    **Example:**

    .. code-block:: python

       >>> from modelicares.simres import SimRes, merge_times

       >>> sim = SimRes('examples/ChuaCircuit.mat')
       >>> times_list = sim.get_times(['L.v', 'G.T_heatPort'])
       >>> merge_times(times_list) # doctest: +ELLIPSIS
       array([    0.        , ... 2500.        ], dtype=float32)
    """
    all_times = times_list[0]
    for i in range(1, len(times_list)):
        if (len(times_list[i-1]) != len(times_list[i])
            or any(times_list[i-1] != times_list[i])):
            all_times = np.union1d(all_times, times_list[i])
    all_times.sort()
    return all_times

class SimRes(object):
    """Class to load and analyze results from a Modelica_-based simulation

    This class contains the following methods:

    - :meth:`browse` - Launch a variable browser

    - :meth:`get_description` - Return the description(s) of variable(s)

    - :meth:`get_displayUnit` - Return the Modelica_ *displayUnit* attribute(s)
      of variable(s)

    - :meth:`get_indices_wi_times` - Return the widest index pair(s) for which
      the time of signal(s) is within given limits

    - :meth:`get_IV` - Return the initial value(s) of variable(s)

    - :meth:`get_FV` - Return the final value(s) of variable(s)

    - :meth:`get_max` - Return the maximum value(s) of variable(s)

    - :meth:`get_mean` - Return the time-averaged value(s) of variable(s)

    - :meth:`get_min` - Return the minimum value(s) of variable(s)

    - :meth:`get_times` - Return vector(s) of the sample times of variable(s)

    - :meth:`get_tuple` - Return tuple(s) of time and value vectors for 
      variable(s)

    - :meth:`get_unit` - Return the *unit* attribute(s) of variable(s)

    - :meth:`get_values` - Return vector(s) of the values of the samples of
      variable(s)

    - :meth:`get_values_at_times` - Return vector(s) of the values of the
      samples of variable(s)

    - :meth:`names` - Return a list of variable names that match a pattern

    - :meth:`nametree` - Return a tree of all variable names with respect to
      the path names

    - :meth:`plot` - Plot data as points and/or curves in 2D Cartesian
      coordinates

    - :meth:`sankey` - Create a figure with Sankey diagram(s)
    """

    def __init__(self, fname='dsres.mat', constants_only=False):
        """On initialization, load Modelica_ simulation results from a
        MATLAB\ :sup:`®` file in Dymola\ :sup:`®` format.

        **Arguments:**

        - *fname*: Name of the file (may include the path)

             The file extension ('.mat') is optional.

        - *constants_only*: *True*, if only the variables from the first data
          table should be loaded

             The first data table typically contains all of the constants,
             parameters, and variables that don't vary.  If only that
             information is needed, it will save some time and memory to set
             *constants_only* to *True*.

        **Example:**

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
        """
        self._load(fname, constants_only)

        # Save the base filename and the directory.
        self.dir, self.fbase = os.path.split(fname)
        self.dir = os.path.abspath(self.dir)
        self.fbase = os.path.splitext(self.fbase)[0]

    # TODO: Remove the "_" prefix and NotImpletedError once this is fixed and
    # tested.
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

        - *\*\*kwargs*: Additional arguments for  :meth:`matplotlib.pyplot.bar`

        **Returns:**

        1. List of the axes within the figure
        """
        raise NotImplementedError

        # Indices for the bars (1, 2, ...)
        ind = np.arange(len(names)) + 1

        # Create a title if necessary.
        if title is None:
            title = self.fbase

        # Set up the subplots.
        n_plots = len(times) # Number of plots
        #if not subtitles:
        #    subtitles = self.gen_subtitles_time(times) # Method missing?
        ax = base.setup_subplots(n_plots=n_plots, n_rows=n_rows,
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

    def _load(self, fname='dsres.mat', constants_only=False):
        """Load Modelica_ results from a MATLAB\ :sup:`®` file.

        **Arguments:**

        - *fname*: Name of the file (may include the path)

        - *constants_only*: *True*, if only the variables from the first data
          table should be loaded

            The first data table typically contains all of the constants,
            parameters, and variables that don't vary.  If only that information
            is needed, it will save some time and memory to set *constants_only*
            to *True*.

        The results are stored within this class as *_traj* and *_data*.
        *_traj* is a dictionary with keywords that correspond to each variable
        name.  The entries are a tuple of (index to the data array, sign of the
        values, column of the data array, description of the variable, base
        unit of the variable, and display unit of the variable).  *_data* is a
        list of numpy arrays containing the trajectories.

        **Returns:** *None* if the file contains linearization results rather
        than simulation results.
        """
        # This performs the task of tload.m from Dymola version 7.4:
        #     on Unix/Linux: /opt/dymola/mfiles/traj/tload.m
        #     on Windows: C:\Program Files\Dymola 7.4\Mfiles\traj\tload.m

        TrajEntry = namedtuple('TrajEntry', ['data_set', 'sign', 'data_row',
                                             'description', 'unit',
                                             'displayUnit'])
        """Named tuple class to represent a Dymosim trajectory entry"""


        def _parse_description(description):
            """Parse the variable description string into (description, unit,
            displayUnit).
            """
            try:
                description, unit = description[0:-1].rsplit(' [', 1)
                try:
                    unit, displayUnit = unit.rsplit('|', 1)
                except ValueError:
                    return description, unit, ''
            except ValueError:
                return description, '', ''
            return description, unit, displayUnit

        # Load the file.
        try:
            dsres = loadmat(fname, struct_as_record=True,
                chars_as_strings=False)
        except IOError:
            print('File "%s" could not be loaded.  Check that it exists.' %
                  fname)
            raise

        # Check and extract the Aclass variable (for convenience).
        if 'Aclass' in dsres:
            Aclass = dsres['Aclass']
        elif 'class' in dsres:
            Aclass = dsres['class']
        else:
            raise AssertionError('Neither "Aclass" nor "class" is present in '
                                 '"%s".' % fname)

        # Check if the file has the correct class name.
        line = _chars_to_str(Aclass[0])
        if not line.startswith('Atrajectory'):
            if line.startswith('AlinearSystem'):
                raise AssertionError('File "%s" is not of class Atrajectory '
                                     'or AlinearSystem.' % fname)

        # Check the dsres version.
        version = _chars_to_str(Aclass[1])
        assert version.startswith('1.1'), ('Only dsres files of version 1.1 '
            'are supported, but "%s" is version %s.' % (fname, version))

        # Determine if the matrices are transposed.
        n_row = len(Aclass)
        assert n_row >= 2, ('"Aclass" or "class" has fewer than 2 lines in '
            '"%s".' % fname)
        transposed = (n_row >= 4
                      and _chars_to_str(Aclass[3]).startswith('binTrans'))

        # Load the name, description, parts of dataInfo, and data_i variables.
        self._traj = {}
        n_data_sets = 0
        try:
            if transposed:
                for i in range(dsres['dataInfo'].shape[1]):
                    name = _chars_to_str(dsres['name'][:, i]).rstrip()
                    data_set, sign_ind = dsres['dataInfo'][0:2, i]
                    description, unit, displayUnit = _parse_description(
                        _chars_to_str(dsres['description'][:, i]).encode('latin-1').rstrip())
                    if data_set == 1 or not constants_only:
                        self._traj[name] = TrajEntry(data_set=data_set-1,
                                                     sign=np.sign(sign_ind),
                                                     data_row=abs(sign_ind)-1,
                                                     description=description,
                                                     unit=unit,
                                                     displayUnit=displayUnit)
                    if data_set > n_data_sets: n_data_sets = data_set
                if constants_only:
                    self._data = [dsres['data_1']]
                else:
                    self._data = [dsres['data_%i' % (i+1)]
                                  for i in range(n_data_sets)]
            else:
                for i in range(dsres['dataInfo'].shape[0]):
                    name = _chars_to_str(dsres['name'][i, :]).encode('latin-1').rstrip()
                    data_set, sign_ind = dsres['dataInfo'][i, 0:2]
                    description, unit, displayUnit = _parse_description(
                        _chars_to_str(dsres['description'][i, :]).encode('latin-1').rstrip())
                    if data_set == 1 or not constants_only:
                        self._traj[name] = TrajEntry(data_set=data_set-1,
                                                     sign=np.sign(sign_ind),
                                                     data_row=abs(sign_ind)-1,
                                                     description=description,
                                                     unit=unit,
                                                     displayUnit=displayUnit)
                    if data_set > n_data_sets:
                        n_data_sets = data_set
                if constants_only:
                    self._data = [dsres['data_1'].T]
                else:
                    self._data = [dsres['data_%i' % (i+1)].T
                                  for i in range(n_data_sets)]
            # Note 1: The indices are converted from Modelica (1-based) to
            # Python (0-based).
            # Note 2:  Dymola 7.4 uses the transposed version, so it is the
            # standard here (for optimal speed).  Therefore, the "normal"
            # version is transposed, and what would be "data_column" is
            # "data_row".
            #print('Loaded simulation result from ' + fname + ".")
        except KeyError:
            print('"name" or "dataInfo" or "data_i" may be missing in "%s".' %
                  fname)
            raise

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

        def _do_work():
            """Launch the broswer."""
            app = wx.GetApp()
            if app is None:
                app = wx.App()
            frame = Browser(None, -1, self)
            frame.Show(True)
            app.SetTopWindow(frame)
            app.MainLoop()

        # TODO: Fix multithreading so that it can run in the background?
        #import threading
        #thread = threading.Thread(target=_do_work)
        #thread.setDaemon(True)
        #thread.start()

        _do_work()

    def _get(self, names, attr):
        """Return attribute(s) of variable(s).

        **Arguments:**

        - *names*: Name(s) of the variable(s) from which to get the
          attribute(s)

             This may be a string or (possibly nested) list of strings
             representing the names of the variables.

        - *attr*: Method to retrieve the attribute given the name of a single 
          variable

             E.g., for the *unit* attribute:
             ``attr = lambda name: self._traj[name].unit``

        If *names* is a string, then the output will be a single description.
        If *names* is a (optionally nested) list of strings, then the output
        will be a (nested) list of descriptions.
        """
        try:
            if isinstance(names, basestring):
                # This test is explicit (not duck-typing) since a string is
                # iterable.
                return attr(names)
            else:
                attrs = []
                for name in names:
                    a = self._get(name, attr) # Recursion
                    if a is None:
                        # Must be a KeyError---handled below.
                        return
                    else:
                        attrs.append(a)
                return attrs
        except KeyError:
            print('%s is not a valid variable name.\n' % names)
            print("Did you mean one of these?")
            for close_match in get_close_matches(names, self._traj.keys()):
                print("       " + close_match)
            return

    def get_description(self, names):
        """Return the description(s) of variable(s).

        **Arguments:**

        - *names*: Name(s) of the variable(s) from which to get the
          description(s)

             This may be a string or (possibly nested) list of strings
             representing the names of the variables.

        If *names* is a string, then the output will be a single description.
        If *names* is a (optionally nested) list of strings, then the output
        will be a (nested) list of descriptions.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_description('L.v')
           'Voltage drop between the two pins (= p.v - n.v)'
        """
        return self._get(names, lambda name: self._traj[name].description)

    def get_displayUnit(self, names):
        """Return the Modelica_ *displayUnit* attribute(s) of variable(s).

        **Arguments:**

        - *names*: Name(s) of the variable(s) from which to get the display
          unit(s)

             This may be a string or (possibly nested) list of strings
             representing the names of the variables.

        If *names* is a string, then the output will be a single display unit.
        If *names* is a (optionally nested) list of strings, then the output
        will be a (nested) list of display units.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_displayUnit('G.T_heatPort')
           'degC'
        """
        return self._get(names, lambda name: self._traj[name].displayUnit)

    def get_indices_wi_times(self, names, t_1=None, t_2=None):
        """Return the widest index pair(s) for which the time of signal(s) is
        within given limits.

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of the variable
          names

        - *t_1*: Lower bound of time

        - *t_2*: Upper bound of time

        If *names* is a string, then the output will be an array of values.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of arrays.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_indices_wi_times('L.v', t_1=500, t_2=2000)
           (104, 412)
        """
        assert t_1 is None or t_2 is None or t_1 <= t_2, (
            "The lower time limit is larger than the upper time limit.")

        def _get_indices_wi_times(name):
            """Return the sample times of a variable given its name
            """
            times = self.get_times(name)

            # Find the lower index.
            if t_1 != None:
                i_1 = base.get_indices(times, t_1)[1]
            else:
                i_1 = 0

            # Find the upper index and return.
            if t_2 != None:
                i_2 = base.get_indices(times, t_2)[0]
            else:
                i_2 = len(times) - 1

            return i_1, i_2

        return self._get(names, _get_indices_wi_times)

    def get_IV(self, names, f=lambda x: x):
        """Return the initial value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of the variable
          names

        - *f*: Function that should be applied to the value(s) (default is
          identity)

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
        return self.get_values(names, i=0, f=f)

    def get_FV(self, names, f=lambda x: x):
        """Return the final value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function that should be applied to the value(s) (default is
          identity)

        If *names* is a string, then the output will be a single value.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of values.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_FV('L.v')
           -0.25352862
        """
        return self.get_values(names, i=-1, f=f)

    def get_times(self, names, i=slice(0, None), f=lambda x: x):
        """Return vector(s) of the sample times of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of the variable
          names

        - *i*: Index (-1 for last), list of indices, or slice of the time(s) to
          return

             By default, all times are returned.

        - *f*: Function that should be applied to all times (default is
          identity)

        If *names* is a string, then the output will be an array of times.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of arrays.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_times('L.v') # doctest: +ELLIPSIS
           array([    0.        , ...  2500.        ], dtype=float32)
        """
        return self._get(names, lambda name:
                         f(self._data[self._traj[name].data_set][0, i]))

    def get_unit(self, names):
        """Return the *unit* attribute(s) of variable(s).

        **Arguments:**

        - *names*: Name(s) of the variable(s) from which to get the unit(s)

             This may be a string or (possibly nested) list of strings
             representing the names of the variables.

        If *names* is a string, then the output will be a single unit.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of units.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_unit('L.v')
           'V'
        """
        return self._get(names, lambda name: self._traj[name].unit)

    def get_values(self, names, i=slice(0, None), f=lambda x: x):
        """Return vector(s) of the values of the samples of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of the variable
          names

        - *i*: Index (-1 for last), list of indices, or slice of the values(s)
          to return

             By default, all values are returned.

        - *f*: Function that should be applied to all values (default is
          identity)

        If *names* is a string, then the output will be an array of values.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of arrays.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_values('L.v') # doctest: +ELLIPSIS
           array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)

        If the variable cannot be found, then possible matches are listed:

        .. code-block:: python

           >>> sim.get_values(['L.vv']) # doctest: +ELLIPSIS
           L.vv is not a valid variable name.
           <BLANKLINE>
           Did you mean one of these?
                  L.v
                  L.p.v
                  L.n.v

        The other *get_*\* methods also give this message when a variable cannot
        be found.
        """
        def _get_values(entry):
            """Return the values of a variable given its *_traj* entry.
            """
            return f(self._data[entry.data_set][entry.data_row, i]
                    if entry.sign == 1 else
                    -self._data[entry.data_set][entry.data_row, i])

        return self._get(names, lambda name: _get_values(self._traj[name]))

    def get_values_at_times(self, names, times, f=lambda x: x):
        """Return vector(s) of the values of the samples of variable(s) at
        given times.

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of the variable
          names

        - *times*: Scalar, numeric list, or a numeric array of the times from
          which to pull samples

        - *f*: Function that should be applied to all values (default is
          identity)

        If *names* is a string, then the output will be an array of values.  If
        *names* is a (optionally nested) list of strings, then the output will
        be a (nested) list of arrays.

        If *times* is not provided, all of the samples will be returned.  If
        necessary, the values will be interpolated over time.  The function *f*
        is applied before interpolation.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_values_at_times('L.v', [0, 2000])
           array([ 0.        ,  0.15459341])
        """
        from scipy.interpolate import interp1d

        def _get_value_at_times(name):
            """Return the values of a variable at times given its name
            """
            if isinstance(name, list):
                raise TypeError
                return
            get_values_at = interp1d(self.get_times(name),
                                     self.get_values(name, f=f),
                                     bounds_error=False)
            return get_values_at(times)

        return self._get(names, _get_value_at_times)

    def get_tuple(self, names, i=slice(0, None)):
        """Return tuple(s) of time and value vectors for variable(s).

        Each tuple contains two vectors: one for times and one for values.

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of the variable
          names

        - *i*: Index (-1 for last), list of indices, or slice of the values(s)
          to return

             By default, all values are returned.

        If *names* is a string, then the output will be a tuple.  If *names* is 
        a (optionally nested) list of strings, then the output will be a 
        (nested) list of tuples.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes

           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.get_tuple('L.v') # doctest: +ELLIPSIS
           (array([    0.        , ... ,  2500.        ], dtype=float32), array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32))

        Note that this is a tuple of vectors, not a vector of tuples. 
        """
        def _get_times(entry):
            """Return the times of a variable given its *_traj* entry.
            """
            return self._data[entry.data_set][0, i]

        def _get_values(entry):
            """Return the values of a variable given its *_traj* entry.
            """
            return (self._data[entry.data_set][entry.data_row, i]
                   if entry.sign == 1 else
                   -self._data[entry.data_set][entry.data_row, i])

        def _get_tuple(entry):
            """Return the (times, values) of a variable given its *_traj* entry.
            """
            return (_get_times(entry), _get_values(entry))

        return self._get(names, lambda name: _get_tuple(self._traj[name]))

    def get_max(self, names, f=lambda x: x):
        """Return the maximum value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function that should be applied before taking the maximum 
          (default is identity)

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
        return self.get_values(names, f=lambda x: max(f(x)))

    def get_mean(self, names, f=lambda x: x):
        """Return the time-averaged value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function that should be applied before taking the mean (default 
          is identity)

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
        integral = lambda name: trapz(self.get_values(name, f=f), 
                                      self.get_times(name))
        Deltat = lambda name: self.get_times(name, -1) - self.get_times(name, 0)
        mean = lambda name: integral(name)/Deltat(name)
        return self._get(names, mean)

    def get_min(self, names, f=lambda x: x):
        """Return the minimum value(s) of variable(s).

        **Arguments:**

        - *names*: String or (possibly nested) list of strings of variable
          names

        - *f*: Function that should be applied before taking the minimum 
          (default is identity)

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
        return self.get_values(names, f=lambda x: min(f(x)))

    def names(self, pattern=None, re=False):
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

            Note that '.' is a subclass separator in Modelica but a wildcard in 
            regular expressions.  Escape the subclass separator as '\\.'.

        - *re*: *True* to use regular expressions (*False* to use shell style)

        **Examples:**

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> # Names starting with "L.p", using shell-style matching:
           >>> sim.names('L.p*')
           [u'L.p.i', u'L.p.v']

           >>> # Names ending with "p.v", using re matching:
           >>> sim.names('p\.v$', re=True)
           [u'C2.p.v', u'Gnd.p.v', u'L.p.v', u'Nr.p.v', u'C1.p.v', u'Ro.p.v', u'G.p.v']
        """
        if pattern is None:
            return list(self._traj) # Shortcut
        else:
            if re:
                matcher = re_compile(pattern).search
            else:
                matcher = lambda name: fnmatchcase(name, pattern)
            return filter(matcher, self._traj.keys())

    def nametree(self):
        """Return a tree of all variable names with respect to the path names.

        The tree represents the structure of the Modelica_ model.  It is
        returned as a nested dictionary.  The keys are the path elements and
        the values are sub-dictionaries or variable names.

        There are no arguments.

        **Example:**

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim.nametree() # doctest: +ELLIPSIS
           {u'G': {u'G': u'G.G', ... u'n': {u'i': u'G.n.i', u'v': u'G.n.v'}, ...}, u'L': {...}, ...}
        """
        # This method has been copied and modified from DyMat version 0.5
        # (Joerg Raedler,
        # http://www.j-raedler.de/2011/09/dymat-reading-modelica-results-with-python/,
        # BSD License).
        root = {}
        for name in self._traj.keys():
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

        - *\*\*kwargs*: Propagated to :meth:`base.plot` (and thus to
          :meth:`matplotlib.pyplot.plot`)

             If both y axes are used (primary and secondary), then the *dashes*
             argument is ignored.  The curves on the primary axis will be solid
             and the curves on the secondary axis will be dotted.

        **Returns:**

        1. *ax1*: Primary y axes

        2. *ax2*: Secondary y axes

        **Example:**

        .. testsetup::
           >>> from modelicares import closeall
           >>> closeall()

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

        def _ystrings(ynames, ylabel, legends):
            """Generate a y-axis label and set of legend entries.
            """
            if ynames:
                if ylabel is None: # Try to create a suitable axis label.
                    descriptions = self.get_description(ynames)
                    # If the descriptions are the same, label the y axis with
                    # the 1st one.
                    ylabel = descriptions[0]
                    if len(set(descriptions)) != 1:
                        print("The y-axis variable descriptions are not all "
                              "the same.  The first has been used.  Please "
                              "provide the proper name via ylabel1 or ylabel2.")
                if legends == []:
                    legends = ynames
                if incl_prefix:
                    legends = [self.fbase + ': ' + leg for leg in legends]
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
        ynames1 = base.flatten_list(ynames1)
        ynames2 = base.flatten_list(ynames2)
        assert ynames1 or ynames2, "No signals were provided."
        if title is None:
            title = self.fbase

        # Create primary and secondary axes if necessary.
        if not ax1:
            fig = base.figure(label)
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
        ylabel1, legends1 = _ystrings(ynames1, ylabel1, legends1)
        ylabel2, legends2 = _ystrings(ynames2, ylabel2, legends2)

        # Read the data.
        if xname == 'Time':
            y_1 = self.get_values(ynames1)
            y_2 = self.get_values(ynames2)
        else:
            x = self.get_values(xname)
            times = self.get_times(xname)
            y_1 = self.get_values_at_times(ynames1, times)
            y_2 = self.get_values_at_times(ynames2, times)

        # Plot the data.
        if ynames1:
            if ynames2:
                # Use solid lines for primary axis and dotted lines for
                # secondary.
                kwargs['dashes'] = [(None, None)]
                base.plot(y_1, self.get_times(ynames1) if xname == 'Time'
                          else x, ax1, label=legends1, **kwargs)
                kwargs['dashes'] = [(3, 3)]
                base.plot(y_2, self.get_times(ynames2) if xname == 'Time'
                          else x, ax2, label=legends2, **kwargs)
            else:
                base.plot(y_1, self.get_times(ynames1) if xname == 'Time'
                          else x, ax1, label=legends1, **kwargs)
        elif ynames2:
            base.plot(y_2, self.get_times(ynames2) if xname == 'Time'
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

        - *\*\*kwargs*: Additional arguments for  :class:`matplotlib.sankey.Sankey`

        **Returns:**

        1. List of :class:`matplotlib.sankey.Sankey` instances of the subplots

        **Example:**

        .. testsetup::
           >>> from modelicares import closeall
           >>> closeall()

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
        start_time, stop_time = self.get_times('Time', [0, -1])

        # Create a title if necessary.
        if title is None:
            title = "Sankey Diagram of " + self.fbase

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
        axes = base.setup_subplots(n_plots=n_plots, n_rows=n_rows,
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

    def __call__(self, names, action=get_values, *args, **kwargs):
        """Upon a call to an instance of :class:`SimRes`, call a method on
        variable(s) given their name(s).

        **Arguments**:

        - *names*: String or (possibly nested) list of strings of the variable
          names

        - *action*: Method for retrieving information about the variable(s)

             The default is :meth:`get_values`.  *action* may be a list or
             tuple, in which case the return value is a list or tuple.

        - *\*args*, *\*\*kwargs*: Additional arguments for *action*

        **Examples:**

        .. code-block:: python

           >>> from modelicares.simres import SimRes, Info
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           # Values of a single variable
           >>> sim('L.v') # doctest: +ELLIPSIS
           array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)
           >>> # This is equivalent to:
           >>> sim.get_values('L.v') # doctest: +ELLIPSIS
           array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)

           # Values of a list of variables
           >>> sim(['L.L', 'C1.C'], SimRes.get_description)
           ['Inductance', 'Capacitance']
           >>> # This is equivalent to:
           >>> sim.get_description(['L.L', 'C1.C'])
           ['Inductance', 'Capacitance']

           # Other attributes
           >>> print("The final value of %s is %.3f %s." %
           ...       sim('L.i', (Info.description, Info.FV, Info.unit)))
           The final value of Current flowing from pin p to pin n is 2.049 A.
        """
        try:
            return action(self, names=names, *args, **kwargs)
        except TypeError:
            t = type(action)
            return t(act(self, names=names, *args, **kwargs)
                     for act in action)

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
        return self._traj.__contains__(name)

    def __getitem__(self, names):
        """Upon accessing a variable name within an instance of
        :class:`SimRes`, return its values.

        **Arguments**:

        - *names*: String or (possibly nested) list of strings of the variable
          names

        **Examples:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> sim['L.v'] # doctest: +ELLIPSIS
           array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)
           >>> # This is equivalent to:
           >>> sim.get_values('L.v') # doctest: +ELLIPSIS
           array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)
        """
        return self.get_values(names)

    def __len__(self):
        """Return the number of variables in the simulation.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')

           >>> print("There are %i variables in the %s simulation." %
           ...       (len(sim), sim.fbase))
           There are 62 variables in the ChuaCircuit simulation.
        """
        return self._traj.__len__()

    def __repr__(self):
        """Return a formal description of the :class:`SimRes` instance.

        **Example:**

        .. code-block:: python

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> sim # doctest: +ELLIPSIS
           SimRes('...ChuaCircuit.mat')
        """
        return "%s('%s')" % (self.__class__.__name__,
                             os.path.join(self.dir, self.fbase + '.mat'))
        # Note:  The class name is inquired so that this method will still be
        # valid if the class is extended.

    def __str__(self):
        """Return an informal description of the :class:`SimRes` instance.

        **Example:**

           >>> from modelicares import SimRes
           >>> sim = SimRes('examples/ChuaCircuit.mat')
           >>> print(sim) # doctest: +ELLIPSIS
           Modelica simulation results from "...ChuaCircuit.mat"
        """
        return ('Modelica simulation results from "%s"' %
                os.path.join(self.dir, self.fbase + '.mat'))


class Info:
    """Aliases for the "get" methods in :class:`SimRes`

    **Example:**

    .. code-block:: python

       >>> from modelicares.simres import SimRes, Info

       >>> sim = SimRes('examples/ChuaCircuit.mat')
       >>> Info.FV(sim, 'L.v')
       -0.25352862
    """
    description = SimRes.get_description
    """Alias for :meth:`SimRes.get_description`"""
    displayUnit = SimRes.get_displayUnit
    """Alias for :meth:`SimRes.get_displayUnit`"""
    indices_wi_times = SimRes.get_indices_wi_times
    """Alias for :meth:`SimRes.get_indices_wi_times`"""
    IV = SimRes.get_IV
    """Alias for :meth:`SimRes.get_IV`"""
    FV = SimRes.get_FV
    """Alias for :meth:`SimRes.get_FV`"""
    max = SimRes.get_max
    """Alias for :meth:`SimRes.get_max`"""
    mean = SimRes.get_mean
    """Alias for :meth:`SimRes.get_mean`"""
    min = SimRes.get_min
    """Alias for :meth:`SimRes.get_min`"""
    times = SimRes.get_times
    """Alias for :meth:`SimRes.get_times`"""
    tuple = SimRes.get_tuple
    """Alias for :meth:`SimRes.get_tuple`"""
    unit = SimRes.get_unit
    """Alias for :meth:`SimRes.get_unit`"""
    values = SimRes.get_values
    """Alias for :meth:`SimRes.get_values`"""
    values_at_times = SimRes.get_values_at_times
    """Alias for :meth:`SimRes.get_values_at_times`"""


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
    exit()
