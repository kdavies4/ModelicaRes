#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classes and functions to help plot and interpret experimental data

**Classes:**

- :class:`ArrowLine` - A matplotlib subclass to draw an arrowhead on a line

**Functions:**

- :meth:`add_arrows` - Overlay arrows with annotations on top of a pre-plotted
  line.

- :meth:`add_hlines` - Add horizontal lines to a set of axes with optional
  labels.

- :meth:`add_vlines` - Add vertical lines to a set of axes with optional
  labels.

- :meth:`cast_sametype` - Decorator to cast the output of a method as an instance of
  the containing class

- :meth:`color` - Plot 2D scalar data on a color axis in 2D Cartesian
  coordinates.

- :meth:`closeall` - Close all open figures (shortcut to the
  :meth:`destroy_all` from :class:`matplotlib._pylab_helpers.Gcf`).

- :meth:`expand_path` - Expand a file path by replacing '~' with the user
  directory and makes the path absolute.

- :meth:`flatten_dict` - Flatten a nested dictionary.

- :meth:`flatten_list` - Flatten a nested list.

- :meth:`figure` - Create a figure and set its label.

- :meth:`get_indices` - Return the pair of indices that bound a target value in
  a monotonically increasing vector.

- :meth:`get_pow10` - Return the exponent of 10 for which the significand
  of a number is within the range [1, 10).

- :meth:`get_pow1000` - Return the exponent of 1000 for which the
  significand of a number is within the range [1, 1000).

- :meth:`load_csv` - Load a CSV file into a dictionary.

- :meth:`match` - Reduce a list of strings to those that match a pattern.

- :meth:`plot` - Plot 1D scalar data as points and/or line segments in 2D
  Cartesian coordinates.

- :meth:`quiver` - Plot 2D vector data as arrows in 2D Cartesian coordinates.

- :meth:`save` - Save the current figures as images in a format or list of
  formats.

- :meth:`saveall` - Save all open figures as images in a format or list of
  formats.

- :meth:`setup_subplots` - Create an array of subplots and return their axes.

- :meth:`shift_scale_x` - Apply an offset and a factor as necessary to the x
  axis.

- :meth:`shift_scale_y` - Apply an offset and a factor as necessary to the y
  axis.

- :meth:`si_prefix` - Return the SI prefix for a power of 1000.

- :meth:`tree` - Return a tree of strings as a nested dictionary.
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__credits__ = ["Jason Grout", "Jason Heeris", "Joerg Raedler"]
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"

import os
import numpy as np
import matplotlib.pyplot as plt

from collections import MutableMapping
from decimal import Decimal
from fnmatch import fnmatchcase
from functools import wraps
from glob import glob
from itertools import cycle
from math import floor
from matplotlib import rcParams
from matplotlib._pylab_helpers import Gcf
from matplotlib.cbook import iterable
from matplotlib.lines import Line2D
from re import compile as re_compile
from six import string_types
from PySide.QtGui import QFileDialog


# Function to close all open figures
closeall = Gcf.destroy_all

def add_arrows(p, x_locs=[0], xstar_offset=0, ystar_offset=0,
               lstar=0.05, label='',
               orientation='tangent', color='r'):
    """Overlay arrows with annotations on a pre-plotted line.

    **Arguments:**

    - *p*: A plot instance (:class:`matplotlib.lines.Line2D` object)

    - *x_locs*: x-axis locations of the arrows

    - *xstar_offset*: Normalized x-axis offset from the middle of the arrow to
      the text

    - *ystar_offset*: Normalized y-axis offset from the middle of the arrow to
      the text

    - *lstar*: Length of each arrow in normalized xy axes

    - *label*: Annotation text

    - *orientation*: 'tangent', 'horizontal', or 'vertical'

    - *color*: Color of the arrows (from :mod:`matplotlib.colors`)

    **Example:**

    .. plot:: examples/util-add_arrows.py
       :alt: example of add_arrows()
    """
    from math import atan, cos, sin

    # Get data from the plot lines object.
    x_dat = plt.getp(p, 'xdata')
    y_dat = plt.getp(p, 'ydata')
    ax = p.get_axes()
    Deltax = np.diff(ax.get_xlim())[0]
    Deltay = np.diff(ax.get_ylim())[0]

    for x_loc in x_locs:
        # Get two unique indices.
        i_a, i_b = get_indices(x_dat, x_loc)
        if i_a == i_b:
            if i_a > 0:
                i_a -= 1
            if i_b < len(x_dat):
                i_b += 1

        # Find the midpoint and x, y lengths of the arrow such that it has the
        # given normalized length.
        x_pts = x_dat.take([i_a, i_b])
        y_pts = y_dat.take([i_a, i_b])
        if orientation == 'vertical':
            dx = lstar*Deltax
            dy = 0
        elif orientation == 'horizontal':
            dx = 0
            dy = lstar*Deltay
        else: # tangent
            theta = atan((y_pts[1] - y_pts[0])*Deltax/((x_pts[1] -
                                                        x_pts[0])*Deltay))
            dx = lstar*Deltax*cos(theta)
            dy = lstar*Deltay*sin(theta)
        x_mid = sum(x_pts)/2
        y_mid = sum(y_pts)/2

        # Add the arrow and text.
        line = ArrowLine([x_mid - dx, x_mid + dx], [y_mid - dy, y_mid + dy],
                         color=color, arrowfacecolor=color,
                         arrowedgecolor=color, ls='-', lw=3, arrow='>',
                         arrowsize=10)
        ax.add_line(line)
        if label:
            ax.text(x_mid + xstar_offset*Deltax, y_mid + ystar_offset*Deltax,
                    s=label, fontsize=12)


def add_hlines(ax=None, positions=[0], labels=[], **kwargs):
    """Add horizontal lines to a set of axes with optional labels.

    **Arguments:**

    - *ax*: Axes (:class:`matplotlib.axes` object)

    - *positions*: Positions (along the x axis)

    - *labels*: List of labels for the lines

    - *\*\*kwargs*: Line properties (propagated to
      :meth:`matplotlib.pyplot.axhline`)

         E.g., ``color='k', linestyle='--', linewidth=0.5``

    **Example:**

    .. plot:: examples/util-add_hlines.py
       :alt: example of add_hlines()
    """
    # Process the inputs.
    if not ax:
        ax = plt.gca()
    if not iterable(positions):
        xpositions = (xpositions,)
    if not iterable(labels):
        labels = (labels,)

    # Add and label lines.
    for position in positions:
        ax.axhline(y=position, **kwargs)
    xpos = sum(ax.axis()[0:2])/2.0
    for i, label in enumerate(labels):
        ax.text(xpos, positions[i], label, backgroundcolor='w',
                horizontalalignment='center', verticalalignment='center')


def add_vlines(ax=None, positions=[0], labels=[], **kwargs):
    """Add vertical lines to a set of axes with optional labels.

    **Arguments:**

    - *ax*: Axes (matplotlib.axes object)

    - *positions*: Positions (along the x axis)

    - *labels*: List of labels for the lines

    - *\*\*kwargs*: Line properties (propagated to
      :meth:`matplotlib.pyplot.axvline`)

         E.g., ``color='k', linestyle='--', linewidth=0.5``

    **Example:**

    .. plot:: examples/util-add_vlines.py
       :alt: example of add_vlines()
    """
    # Process the inputs.
    if not ax:
        ax = plt.gca()
    if not iterable(positions):
        positions = (positions,)
    if not iterable(labels):
        labels = (labels,)

    # Add and label lines.
    for position in positions:
        ax.axvline(x=position, **kwargs)
    ypos = sum(ax.axis()[2::])/2.0
    for i, label in enumerate(labels):
        ax.text(positions[i], ypos, label, backgroundcolor='w',
                horizontalalignment='center', verticalalignment='center')


def cast_sametype(f):
    """Decorator to cast the output of a method as an instance of the
    containing class.
    """
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        """Function that casts its output as self.__class__
        """
        return self.__class__(f(self, *args, **kwargs))

    return wrapped


def color(ax, c, *args, **kwargs):
    """Plot 2D scalar data on a color axis in 2D Cartesian coordinates.

    This uses a uniform grid.

    **Arguments:**

    - *ax*: Axis onto which the data should be plotted

    - *c*: color- or c-axis data (2D array)

    - *\*args*, *\*\*kwargs*: Additional arguments for
      :meth:`matplotlib.pyplot.imshow`

    **Example:**

    .. plot:: examples/util-color.py
       :alt: example of color()
    """
    return ax.imshow(c, *args, **kwargs)


def expand_path(path):
    r"""Expand a file path by replacing '~' with the user directory and making
    the path absolute.

    **Example:**

    .. code-block:: python

       >>> from modelicares import *

       >>> expand_path('~/Documents') # doctest: +ELLIPSIS
       '...Documents'
       >>> # where ... is '/home/user/' on Linux or 'C:\Users\user\' on
       >>> # Windows (and "user" is the user id).
    """
    return os.path.abspath(os.path.expanduser(path))


def figure(label='', *args, **kwargs):
    """Create a figure and set its label.

    **Arguments:**

    - *label*: String to apply to the figure's *label* property

    - *\*args*, *\*\*kwargs*: Additional arguments for
      :meth:`matplotlib.pyplot.figure`

    **Example:**

    .. code-block:: python

       >>> fig = figure("velocity_vs_time") # doctest: +ELLIPSIS
       >>> plt.getp(fig, 'label')
       'velocity_vs_time'

    .. Note::  The *label* property is used as the base filename in the
       :meth:`saveall` method.
    """
    fig = plt.figure(*args, **kwargs)
    plt.setp(fig, 'label', label)
    # Note:  As of matplotlib 1.2, matplotlib.pyplot.figure(label=label) isn't
    # supported directly.
    return fig


def flatten_dict(d, parent_key='', separator='.'):
    """Flatten a nested dictionary.

    **Arguments:**

    - *d*: Dictionary (may be nested to an arbitrary depth)

    - *parent_key*: Key of the parent dictionary, if any

    - *separator*: String or character that joins elements of the keys or path
      names

    **Example:**

       >>> from modelicares import *
       >>> flatten_dict(dict(a=1, b=dict(c=2, d='hello')))
       {'a': 1, 'b.c': 2, 'b.d': 'hello'}
    """
    # From
    # http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys,
    # 11/5/2012
    items = []
    for key, value in d.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten_dict(value, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


def flatten_list(l, ltypes=(list, tuple)):
    """Flatten a nested list.

    **Arguments:**

    - *l*: List (may be nested to an arbitrary depth)

          If the type of *l* is not in ltypes, then it is placed in a list.

    - *ltypes*: Tuple (not list) of accepted indexable types

    **Example:**

       >>> from modelicares import *
       >>> flatten_list([1, [2, 3, [4]]])
       [1, 2, 3, 4]
    """
    # Based on
    # http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html,
    # 10/28/2011
    ltype = type(l)
    if ltype not in ltypes: # So that strings aren't split into characters
        return [l]
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if l[i]:
                l[i:i + 1] = l[i]
            else:
                l.pop(i)
                i -= 1
                break
        i += 1
    return ltype(l)


def _gen_offset_factor(label, tick_lo, tick_up, eagerness=0.325):
    """Apply an offset and a scaling factor to a label if necessary.

    **Arguments:**

    - *tick_lo*: Lower tick value

    - *tick_up*: Upper tick value

    - *eagerness*: Parameter to adjust how little of an offset is required
      before the label will be recentered
       - 0: Offset is never applied.
       - 1: Offset is always applied if it will help.

    **Returns:**

    1. New label (label)

    2. Offset (offset)

    3. Exponent of 1000 which can be factored from the number (pow1000)
    """
    # TODO: Utilize matplotlib's support for units?

    def _label_offset_factor(label, offset_factor, offset_pow1000, pow1000):
        """Format an offset and factor into a LaTeX string and add to it an
        existing string.
        """
        DIVIDE = r'\,/\,' # LaTeX string for division

        # Add the offset string.
        if offset_factor:
            if DIVIDE in label:
                label = label.rstrip(r'$') + r'\,-\,%i$' % offset_factor
            else:
                label += r'$\,-\,%i$' % offset_factor
            if offset_pow1000:
                label = label.rstrip(r'$') + (r'\times10^{%i}$' %
                                              (3*offset_pow1000))

        # Add the scaling notation.
        if pow1000:
            if offset_factor:
                label = (r'$($' + label.rstrip(r'$') + r')' + DIVIDE +
                         r'10^{%i}$' % (3*pow1000))
            else:
                if DIVIDE in label:
                    desc, unit = label.split(DIVIDE, 1)
                    if unit.endswith(r')$'):
                        label = (desc + DIVIDE + r'(10^{%i}' % (3*pow1000) +
                                 unit.lstrip(r'('))
                    else:
                        label = (desc + DIVIDE + r'(10^{%i}' % (3*pow1000) +
                                 unit.rstrip(r'$') + r')$')
                else:
                    label += r'$' + DIVIDE + r'10^{%i}$' % (3*pow1000)
        return label

    offset = 0
    offset_factor = 0
    offset_pow1000 = 1
    outside = min(tick_lo, 0) + max(tick_up, 0)
    if outside != 0:
        inside = max(tick_lo, 0) + min(tick_up, 0)
        if inside/outside > 1 - eagerness:
            offset = inside - np.mod(inside, 1000**get_pow1000(inside))
            offset_pow1000 = get_pow1000(offset)
            offset_factor = offset/1000**offset_pow1000
            outside = min(tick_lo - offset, 0) + max(tick_up - offset, 0)
    pow1000 = get_pow1000(outside)
    label = _label_offset_factor(label, offset_factor, offset_pow1000, pow1000)
    return label, offset, pow1000


def get_indices(x, target):
    """Return the pair of indices that bound a target value in a monotonically
    increasing vector.

    **Arguments:**

    - *x*: Vector

    - *target*: Target value

    **Example:**

       >>> from modelicares import *
       >>> get_indices([0, 1, 2], 1.6)
       (1, 2)
    """
    if target <= x[0]:
        return 0, 0
    if target >= x[-1]:
        i = len(x) - 1
        return i, i
    else:
        i_1 = 0
        i_2 = len(x) - 1
        while i_1 < i_2 - 1:
            i_mid = (i_1 + i_2)/2
            if x[i_mid] == target:
                return i_mid, i_mid
            elif x[i_mid] > target:
                i_2 = i_mid
            else:
                i_1 = i_mid
    return i_1, i_2


def get_pow10(num):
    """Return the exponent of 10 for which the significand of a number is
    within the range [1, 10).

    **Example:**

       >>> get_pow10(50)
       1
    """
    # Based on an algorithm by Jason Heeris 11/18/2009:
    #

    dnum = Decimal(str(num))
    if dnum == 0:
        return 0
    elif dnum < 0:
        dnum = -dnum
    return int(floor(dnum.log10()))


def get_pow1000(num):
    """Return the exponent of 1000 for which the significand of a number is
    within the range [1, 1000).

    **Example:**

       >>> get_pow1000(1e5)
       1
    """
    # Based on an algorithm by Jason Heeris 11/18/2009:
    #     http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html

    dnum = Decimal(str(num))
    if dnum == 0:
        return 0
    elif dnum < 0:
        dnum = -dnum
    return int(floor(dnum.log10()/3))


def load_csv(fname, header_row=0, first_data_row=None, types=None, **kwargs):
    """Load a CSV file into a dictionary.

    The strings from the header row are used as dictionary keys.

    **Arguments:**

    - *fname*: Path and name of the file

    - *header_row*: Row that contains the keys (uses zero-based indexing)

    - *first_data_row*: First row of data (uses zero-based indexing)

         If *first_data_row* is not provided, then it is assumed that the data
         starts just after the header row.

    - *types*: List of data types for each column

         :class:`int` and :class:`float` data types will be cast into a
         :class:`numpy.array`.  If *types* is not provided, attempts will be
         made to cast each column into :class:`int`, :class:`float`, and
         :class:`str` (in that order).

    - *\*\*kwargs*: Additional arguments for :meth:`csv.reader`

    **Example:**

    >>> from modelicares import *
    >>> data = load_csv("examples/load-csv.csv", header_row=2)
    >>> print("The keys are: %s" % data.keys())
    The keys are: ['Price', 'Description', 'Make', 'Model', 'Year']
    """
    import csv

    try:
        reader = csv.reader(open(fname), **kwargs)
    except IOError:
        raise IOError('Unable to load "%s".  Check that it exists.' % fname)

    # Read the header row and create the dictionary from it.
    for i in range(header_row):
        next(reader)
    keys = next(reader)
    data = dict.fromkeys(keys)
    #print("The keys are: ")
    #print(keys)

    # Read the data.
    if first_data_row:
        for row in range(first_data_row - header_row - 1):
            next(reader)
    if types:
        for i, (key, column, t) in enumerate(zip(keys, zip(*reader), types)):
            # zip(*reader) groups the data by columns.
            try:
                if isinstance(t, string_types):
                    data[key] = column
                elif isinstance(t, (float, int)):
                    data[key] = np.array(map(t, column))
                else:
                    data[key] = map(t, column)
            except ValueError:
                raise ValueError("Could not cast column %i into %i." % (i, t))
    else:
        for key, column in zip(keys, zip(*reader)):
            try:
                data[key] = np.array(map(int, column))
            except:
                try:
                    data[key] = np.array(map(float, column))
                except:
                    data[key] = map(str, column)

    return data


def match(strings, pattern=None, re=False):
    r"""Reduce a list of strings to those that match a pattern.

    By default, all of the strings are returned.

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

    **Example:**

       >>> from modelicares.util import match
       >>> match(['apple', 'orange', 'banana'], '*e')
       ['apple', 'orange']


    .. _Modelica: http://www.modelica.org/
    """
    if pattern is None or (pattern in ['.*', '.+', '.', '.?', ''] if re
                           else pattern == '*'):
        return list(strings) # Shortcut
    else:
        if re:
            matcher = re_compile(pattern).search
        else:
            matcher = lambda name: fnmatchcase(name, pattern)
        return list(filter(matcher, strings))


def plot(y, x=None, ax=None, label=None,
         color=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
         marker=None,
         dashes=[(None,None), (3,3), (1,1), (3,2,1,2)],
         **kwargs):
    """Plot 1D scalar data as points and/or line segments in 2D Cartesian
    coordinates.

    This is similar to :meth:`matplotlib.pyplot.plot` (and actually calls that
    method), but provides direct support for plotting an arbitrary number of
    curves.

    **Arguments:**

    - *y*: y-axis data

         This may contain multiple series.

    - *x*: x-axis data

         If *x* is not provided, the y-axis data will be plotted versus its
         indices.  If *x* is a single series, it will be used for all of the
         y-axis series.  If it is a list of series, each x-axis series will be
         matched to a y-axis series.

    - *ax*: Axis onto which the data should be plotted.

         If *ax* is *None* (default), axes are created.

    - *label*: List of labels of each series (to be used later for the legend
      if applied)

    - *color*: Single entry, list, or :class:`itertools.cycle` of colors that
      will be used sequentially

         Each entry may be a character, grayscale, or rgb value.

         .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

    - *marker*: Single entry, list, or :class:`itertools.cycle` of markers that
      will be used sequentially

         Use *None* for no marker.  A good assortment is ["o", "v", "^", "<",
         ">", "s", "p", "*", "h", "H", "D", "d"]. All of the possible entries
         are listed at:
         http://matplotlib.sourceforge.net/api/artist_api.html#matplotlib.lines.Line2D.set_marker.

    - *dashes*: Single entry, list, or :class:`itertools.cycle` of dash styles
      that will be used sequentially

         Each style is a tuple of on/off lengths representing dashes.  Use
         (0, 1) for no line and (None, None) for a solid line.

         .. Seealso:: http://matplotlib.sourceforge.net/api/collections_api.html

    - *\*\*kwargs*: Additional arguments for :meth:`matplotlib.pyplot.plot`

    **Returns:** List of :class:`matplotlib.lines.Line2D` objects

    **Example:**

    .. plot:: examples/util-plot.py
       :alt: example of plot()
    """
    # Create axes if necessary.
    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    # Set up the color(s), marker(s), and dash style(s).
    cyc = type(cycle([]))
    if not isinstance(color, cyc):
        if not iterable(color):
            color = [color]
        color = cycle(color)
    if not isinstance(marker, cyc):
        if not iterable(marker):
            marker = [marker]
        marker = cycle(marker)
    if not isinstance(dashes, cyc):
        if not iterable(dashes[0]):
            dashes = [dashes]
        dashes = cycle(dashes)
    # 6/5/11: There is an ax.set_color_cycle() method that could be used, but
    # there doesn't seem to be a corresponding set_line_cycle() or
    # set_marker_cycle().
    # 10/27/11: There may be a way to do this automatically.  See:
    # http://matplotlib.sourceforge.net/api/collections_api.html

    # Plot the data.
    if x is None:
        # There is no x data; plot y vs its indices.
        plots = [ax.plot(yi, label=None if label is None else label[i],
                         color=next(color), marker=next(marker),
                         dashes=next(dashes), **kwargs)
                 for i, yi in enumerate(y)]
    elif not iterable(x[0]):
        # There is only one x series; use it repeatedly.
        plots = [ax.plot(x, yi, label=None if label is None else label[i],
                         color=next(color), marker=next(marker),
                         dashes=next(dashes), **kwargs)
                 for i, yi in enumerate(y)]
    else:
        # There is a x series for each y series.
        plots = [ax.plot(xi, yi, label=None if label is None else label[i],
                         color=next(color), marker=next(marker),
                         dashes=next(dashes), **kwargs)
                 for i, (xi, yi) in enumerate(zip(x, y))]

    return plots


def quiver(ax, u, v, x=None, y=None, pad=0.05, pivot='middle', **kwargs):
    """Plot 2D vector data as arrows in 2D Cartesian coordinates.

    Uses a uniform grid.

    **Arguments:**

    - *ax*: Axis onto which the data should be plotted

    - *u*: x-direction values (2D array)

    - *v*: y-direction values (2D array)

    - *pad*: Amount of white space around the data (relative to the span of the
      field)

    - *pivot*: "tail" | "middle" | "tip" (see :meth:`matplotlib.pyplot.quiver`)

    - *\*\*kwargs*: Additional arguments for :meth:`matplotlib.pyplot.quiver`

    **Example:**

    .. plot:: examples/util-quiver.py
       :alt: plot of quiver()
    """
    if x is None or y is None:
        p = ax.quiver(u, v, pivot=pivot, **kwargs)
    else:
        p = ax.quiver(x, y, u, v, pivot=pivot, **kwargs)
    plt.axis('tight')
    l, r, b, t = plt.axis()
    dx, dy = r-l, t-b
    plt.axis([l-pad*dx, r+pad*dx, b-pad*dy, t+pad*dy])
    return p


def save(formats=['pdf', 'png'], fname=None, fig=None):
    """Save a figure in an image format or list of formats.

    The base filename (with directory if necessary but without extension) is
    determined in this order of priority:

    1. *fname* argument if it is not *None*
    2. the *label* property of the figure, if it is not empty
    3. the response from a file dialog

    A forward slash ("/") can be used as a path separator, even if the operating
    system is Windows.  Folders are created as needed.

    **Arguments:**

    - *formats*: Format or list of formats in which the figure should be saved

    - *fname*: Filename (see above)

    - *fig*: `matplotlib <http://matplotlib.org/api/figure_api.html>`_ figure
      or list of figures to be saved

           If *fig* is *None* (default), then the current figure will be saved.

    .. Note::  In general, :meth:`save` should be called before
       :meth:`matplotlib.pyplot.show` so that the figure(s) are still present in
       memory.

    **Example:**

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> figure('examples/temp') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> plt.plot(range(10)) # doctest: +SKIP
       [<matplotlib.lines.Line2D object at 0x...>]
       >>> save() # doctest: +SKIP
       Saved examples/temp.pdf
       Saved examples/temp.png

    .. Note::  The :meth:`figure` method can be used to directly create a
       figure with a label.
    """
    # Get the figures.
    if fig is None:
        fig = plt.gcf()

    # Get the filename.
    if not fname:
        fname = fig.get_label()
        if not fname:
            fname, __ = QFileDialog.getSaveFileName(None,
                                                    "Choose a base filename.")
            if not fname:
                print("Cancelled.")
                return

    # Create folders if necessary.
    directory = os.path.dirname(fname)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Save in the desired formats.
    for fmt in list(formats):
        full_name = fname + '.' + fmt
        fig.savefig(full_name)
        print("Saved " + full_name)


def saveall(formats=['pdf', 'png']):
    """Save all open figures as images in a format or list of formats.

    The directory and base filenames (without extension) are taken from the
    *label* property of the present figures.  If a figure has an empty *label*,
    then a file dialog is opened to choose the filename.  Note that the
    :meth:`figure` method can be used to directly create a figure with a label.

    **Arguments:**

    - *formats*: Format or list of formats in which the figures should be saved

    .. Note::  In general, :meth:`saveall` should be called before
       :meth:`matplotlib.pyplot.show` so that the figure(s) are still present
       in memory.

    **Example:**

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> figure('examples/temp') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> plt.plot(range(10))  # doctest: +SKIP
       [<matplotlib.lines.Line2D object at 0x...>]
       >>> save() # doctest: +SKIP
       Saved examples/temp.pdf
       Saved examples/temp.png
    """

    # Get the figures.
    figs = [manager.canvas.figure for manager in Gcf.figs.values()]

    # Save the figures.
    for fig in figs:
        save(formats, fig=fig)


def setup_subplots(n_plots, n_rows, title="", subtitles=None,
                   label="multiplot",
                   xlabel="", xticklabels=None, xticks=None,
                   ylabel="", yticklabels=None, yticks=None,
                   ctype=None, clabel="",
                   margin_left=rcParams['figure.subplot.left'],
                   margin_right=1-rcParams['figure.subplot.right'],
                   margin_bottom=rcParams['figure.subplot.bottom'],
                   margin_top=1-rcParams['figure.subplot.top'],
                   margin_cbar=0.2,
                   wspace=0.1, hspace=0.25,
                   cbar_space=0.1, cbar_width=0.05):
    """Create an array of subplots and return their axes.

    **Arguments:**

    - *n_plots*: Number of (sub)plots

    - *n_rows*: Number of rows of (sub)plots

    - *title*: Title for the figure

    - *subtitles*: List of subtitles (i.e., titles for each subplot) or *None*
      for no subtitles

    - *label*: Label for the figure

         This will be used as a base filename if the figure is saved.

    - *xlabel*: Label for the x-axes (only shown for the subplots on the bottom
      row)

    - *xticklabels*: Labels for the x-axis ticks (only shown for the subplots
      on the bottom row)

         If *None*, then the default is used.

    - *xticks*: Positions of the x-axis ticks

         If *None*, then the default is used.

    - *ylabel*: Label for the y-axis (only shown for the subplots on the left
      column)

    - *yticklabels*: Labels for the y-axis ticks (only shown for the subplots
      on the left column)

         If *None*, then the default is used.

    - *yticks*: Positions of the y-axis ticks

         If *None*, then the default is used.

    - *ctype*: Type of colorbar (*None*, 'vertical', or 'horizontal')

    - *clabel*: Label for the color- or c-bar axis

    - *margin_left*: Left margin

    - *margin_right*: Right margin (ignored if
      ``cbar_orientation == 'vertical'``)

    - *margin_bottom*: Bottom margin (ignored if
      ``cbar_orientation == 'horizontal'``)

    - *margin_top*: Top margin

    - *margin_cbar*: Margin reserved for the colorbar (right margin if
      ``cbar_orientation == 'vertical'`` and bottom margin if
      ``cbar_orientation == 'horizontal'``)

    - *wspace*: The amount of width reserved for blank space between subplots

    - *hspace*: The amount of height reserved for white space between subplots

    - *cbar_space*: Space between the subplot rectangles and the colorbar

         If *cbar* is *None*, then this is ignored.

    - *cbar_width*: Width of the colorbar if vertical (or height if horizontal)

         If *cbar* is *None*, then this is ignored.

    **Returns:**

    1. List of subplot axes

    2. Colorbar axis (returned iff ``cbar != None``)

    3. Number of columns of subplots

    **Example:**

    .. plot:: examples/util-setup_subplots.py
       :alt: example of setup_subplots()
    """
    from matplotlib.figure import SubplotParams

    assert ctype == 'vertical' or ctype == 'horizontal' or ctype is None, \
        "cytpe must be 'vertical', 'horizontal', or None."

    # Create the figure.
    subplotpars = SubplotParams(left=margin_left, top=1-margin_top,
        right=1-(margin_cbar if ctype == 'vertical' else margin_right),
        bottom=(margin_cbar if ctype == 'horizontal' else margin_bottom),
        wspace=wspace, hspace=hspace)
    fig = figure(label, subplotpars=subplotpars)
    fig.suptitle(t=title, fontsize=rcParams['axes.titlesize'])
    # For some reason, the suptitle() function doesn't automatically follow the
    # default title font size.

    # Add the subplots.
    # Provide at least as many panels as needed.
    n_cols = int(np.ceil(float(n_plots)/n_rows))
    ax = []
    for i in range(n_plots):
        # Create the axes.
        i_col = np.mod(i, n_cols)
        i_row = (i - i_col)/n_cols
        a = fig.add_subplot(n_rows, n_cols, i+1)
        ax.append(a)

        # Scale and label the axes.
        if xticks is not None:
            a.set_xticks(xticks)
        if yticks is not None:
            a.set_yticks(yticks)
        # Only show the xlabel and xticklabels for the bottom row.
        if True:#i_row == n_rows - 1:
            a.set_xlabel(xlabel)
            if xticklabels is not None:
                a.set_xticklabels(xticklabels)
        else:
            a.set_xticklabels([])
        # Only show the ylabel and yticklabels for the left column.
        if i_col == 0:
            a.set_ylabel(ylabel)
            if yticklabels is not None:
                a.set_yticklabels(yticklabels)
        else:
            a.set_yticklabels([])

        # Add the subplot title.
        if subtitles:
            a.set_title(subtitles[i], fontsize=rcParams['axes.labelsize'])

    # Add the colorbar.
    if ctype:
        if ctype == 'vertical':
            #fig.subplots_adjust(left=margin_left, bottom=margin_top,
            #    right=1-margin_cbar, top=1-margin_top,
            #    wspace=wspace, hspace=hspace)
            cax = fig.add_axes([1 - margin_cbar + cbar_space, margin_bottom,
                                cbar_width, 1 - margin_bottom - margin_top])
            #cax.set_ylabel(clabel)
        else:
            #fig.subplots_adjust(left=margin_left, bottom=margin_cbar,
            #    right=1-margin_left, top=1-margin_top,
            #    wspace=wspace, hspace=hspace)
            cax = fig.add_axes([margin_left,
                                margin_cbar - cbar_space - cbar_width,
                                1 - margin_left - margin_right, cbar_width])
            #cax.set_xlabel(clabel)
        cax.set_ylabel(clabel)
        return ax, cax, n_cols
    else:
        return ax, n_cols

# TODO: Remove the "_" prefix and add it to the list once this is finished.
def _shift_scale_c(cbar, v_min, v_max, eagerness=0.325):
    """"Apply an offset and a factor as necessary to the colorbar.

    **Arguments:**

    - *cbar*: :class:`matplotlib.colorbar.Colorbar` object

    - *v_min*: Minimum of the color-axis data

    - *v_max*: Maximum of the color-axis data

    - *eagerness*: Parameter to adjust how little of an offset is allowed
      before the label will be recentered

         - 0: Offset is never applied.

         - 1: Offset is always applied if it will help.
    """
    # TODO: Add an example.
    # The concept here is based on:
    # http://efreedom.com/Question/1-3677368/Matplotlib-Format-Axis-Offset-Values-Whole-Numbers-Specific-Number
    # accessed 2010/11/10
    label = cbar.ax.get_ylabel()
    ticks = cbar.ax.get_yticks()
    offset, offset_factor, offset_pow1000, pow1000 = _gen_offset_factor(v_min,
                                                                        v_max)
    label, offset, pow1000 = _gen_offset_factor(label, v_min, v_max, eagerness)
    cbar.set_ticklabels(["%.1f" % x for x in (ticks - offset)/1000**pow1000])
    cbar.set_label(label)


def shift_scale_x(ax, eagerness=0.325):
    """Apply an offset and a factor as necessary to the x axis.

    **Arguments:**

    - *ax*: matplotlib.axes object

    - *eagerness*: Parameter to adjust how little of an offset is allowed
      before the label will be recentered

         - 0: Offset is never applied.

         - 1: Offset is always applied if it will help.

    **Example:**

    .. plot:: examples/util-shift_scale_x.py
       :alt: example of shift_scale_x()
    """
    # This concept is based on:
    # http://efreedom.com/Question/1-3677368/Matplotlib-Format-Axis-Offset-Values-Whole-Numbers-Specific-Number,
    # accessed 2010/11/10
    label = ax.get_xlabel()
    ticks = ax.get_xticks()
    label, offset, pow1000 = _gen_offset_factor(label, ticks[0], ticks[-1],
                                                eagerness)
    ax.set_xticklabels(["%.1f" % x for x in (ticks - offset)/1000**pow1000])
    ax.set_xlabel(label)


def shift_scale_y(ax, eagerness=0.325):
    """Apply an offset and a factor as necessary to the y axis.

    **Arguments:**

    - *ax*: matplotlib.axes object

    - *eagerness*: Parameter to adjust how little of an offset is allowed
      before the label will be recentered

         - 0: Offset is never applied.

         - 1: Offset is always applied if it will help.

    **Example:**

    .. plot:: examples/util-shift_scale_y.py
       :alt: example of shift_scale_y()
    """
    # This concept is based on:
    # http://efreedom.com/Question/1-3677368/Matplotlib-Format-Axis-Offset-Values-Whole-Numbers-Specific-Number,
    # accessed 2010/11/10
    label = ax.get_ylabel()
    ticks = ax.get_yticks()
    label, offset, pow1000 = _gen_offset_factor(label, ticks[0], ticks[-1],
                                                eagerness)
    ax.set_yticklabels(["%.1f" % x for x in (ticks - offset)/1000**pow1000])
    ax.set_ylabel(label)


def si_prefix(pow1000):
    """Return the SI prefix for a power of 1000.
    """
    # Prefixes according to Table 5 of BIPM 2006
    # (http://www.bipm.org/en/si/si_brochure/; excluding hecto, deca, deci,
    # and centi).
    try:
        return ['Y', # yotta (10^24)
                'Z', # zetta (10^21)
                'E', # exa (10^18)
                'P', # peta (10^15)
                'T', # tera (10^12)
                'G', # giga (10^9)
                'M', # mega (10^6)
                'k', # kilo (10^3)
                '', # (10^0)
                'm', # milli (10^-3)
                r'{\mu}', # micro (10^-6)
                'n', # nano (10^-9)
                'p', # pico (10^-12)
                'f', # femto (10^-15)
                'a', # atto (10^-18)
                'z', # zepto (10^-21)
                'y'][8 - pow1000] # yocto (10^-24)
    except IndexError:
        raise IndexError("The factor 1e%i is beyond the range covered by "
                         "the SI prefixes (1e-24 to 1e24)." % 3*pow1000)


def tree(strings, delimiter='.'):
    """Return a tree of strings as a nested dictionary.

    The levels of hierarchy in each string are marked with *delimiter*.
    The keys in the dictionary are the sub-branch names.  The value at the
    end of each branch is the full string.

    **Arguments:**

    - *strings*: List of strings

    - *delimiter*: String that marks a level of hierarchy

    **Example:**

       >>> from modelicares.util import tree
       >>> tree(['a.b.c', 'd.e', 'd.f'])
       {'a': {'b': {'c': 'a.b.c'}}, 'd': {'e': 'd.e', 'f': 'd.f'}}

    """
    # This method has been copied and modified from DyMat version 0.5
    # (Joerg Raedler,
    # http://www.j-raedler.de/2011/09/dymat-reading-modelica-results-with-python/,
    # BSD License).
    root = {}
    for string in strings:
        branch = root
        elements = string.split(delimiter)
        for element in elements[:-1]:
            if not element in branch:
                branch[element] = {}
            branch = branch[element]
        branch[elements[-1]] = string
    return root


# From http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html,
# accessed 2010/11/2012
class ArrowLine(Line2D):
    """A matplotlib subclass to draw an arrowhead on a line
    """
    __author__ = "Jason Grout"
    __copyright__ = "Copyright (C) 2008"
    __email__ = "jason-sage@..."
    __license__ = "Modified BSD License"

    from matplotlib.path import Path

    arrows = {'>' : '_draw_triangle_arrow'}
    _arrow_path = Path([[0.0, 0.0], [-1.0, 1.0], [-1.0, -1.0], [0.0, 0.0]],
                       [Path.MOVETO, Path.LINETO,Path.LINETO, Path.CLOSEPOLY])

    def __init__(self, *args, **kwargs):
        """Initialize the line and arrow.

        **Arguments:**

        - *arrow* (='-'): Type of arrow ('<' | '-' | '>')

        - *arrowsize* (=2*4): Size of arrow

        - *arrowedgecolor* (='b'): Color of arrow edge

        - *arrowfacecolor* (='b'): Color of arrow face

        - *arrowedgewidth* (=4): Width of arrow edge

        - *arrowheadwidth* (=\ *arrowsize*): Width of arrow head

        - *arrowheadlength* (=\ *arrowsize*): Length of arrow head

        - *\*args*, *\*\*kwargs*: Additional arguments for
          :class:`matplotlib.lines.Line2D`

        **Example:**

        .. plot:: examples/util-ArrowLine.py
           :alt: example of ArrowLine()
        """
        self._arrow = kwargs.pop('arrow', '-')
        self._arrowsize = kwargs.pop('arrowsize', 2*4)
        self._arrowedgecolor = kwargs.pop('arrowedgecolor', 'b')
        self._arrowfacecolor = kwargs.pop('arrowfacecolor', 'b')
        self._arrowedgewidth = kwargs.pop('arrowedgewidth', 4)
        self._arrowheadwidth = kwargs.pop('arrowheadwidth', self._arrowsize)
        self._arrowheadlength = kwargs.pop('arrowheadlength', self._arrowsize)
        Line2D.__init__(self, *args, **kwargs)

    def draw(self, renderer):
        """Draw the line and arrowhead using the passed renderer.
        """
        #if self._invalid:
        #    self.recache()
        renderer.open_group('arrowline2d')
        if not self._visible:
            return

        Line2D.draw(self, renderer)

        if self._arrow is not None:
            gc = renderer.new_gc()
            self._set_gc_clip(gc)
            gc.set_foreground(self._arrowedgecolor)
            gc.set_linewidth(self._arrowedgewidth)
            gc.set_alpha(self._alpha)
            funcname = self.arrows.get(self._arrow, '_draw_nothing')
        if funcname != '_draw_nothing':
            tpath, affine = self._transformed_path\
                                .get_transformed_points_and_affine()
            arrow_func = getattr(self, funcname)
            arrow_func(renderer, gc, tpath, affine.frozen())

        renderer.close_group('arrowline2d')

    def _draw_triangle_arrow(self, renderer, gc, path, path_trans):
        """Draw a triangular arrow.
        """
        from math import atan2
        from matplotlib.transforms import Affine2D

        segment = [i[0] for i in path.iter_segments()][-2:]
        startx, starty = path_trans.transform_point(segment[0])
        endx, endy = path_trans.transform_point(segment[1])
        angle = atan2(endy-starty, endx-startx)
        halfwidth = 0.5*renderer.points_to_pixels(self._arrowheadwidth)
        length = renderer.points_to_pixels(self._arrowheadlength)
        transform = Affine2D().scale(length, halfwidth).rotate(angle)\
                                                       .translate(endx, endy)
        rgbFace = self._get_rgb_arrowface()
        renderer.draw_path(gc, self._arrow_path, transform, rgbFace)

    def _get_rgb_arrowface(self):
        """Get the color of the arrow face.
        """
        from matplotlib.cbook import is_string_like
        from matplotlib.colors import colorConverter

        facecolor = self._arrowfacecolor
        if is_string_like(facecolor) and facecolor.lower() == 'none':
            rgbFace = None
        else:
            rgbFace = colorConverter.to_rgb(facecolor)
        return rgbFace


if __name__ == "__main__":
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
