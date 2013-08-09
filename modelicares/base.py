#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Basic methods to help plot and interpret experimental data

This module contains the following classes:

- :class:`ArrowLine` - A matplotlib subclass to draw an arrowhead on a line

- :class:`Quantity` - Named tuple class for a constant physical quantity

and the following functions:

- :meth:`add_arrows` - Overlays arrows with annotations on top of a pre-plotted
  line

- :meth:`add_hlines` - Adds horizontal lines to a set of axes with optional
  labels

- :meth:`add_vlines` - Adds vertical lines to a set of axes with optional
  labels

- :meth:`animate` - Encodes a series of PNG images as a MPG movie

- :meth:`color` - Plots 2D scalar data on a color axis in 2D Cartesian
  coordinates

- :meth:`closeall` - Closes all open figures

- :meth:`convert` - Converts the expression of a physical quantity between units

- :meth:`expand_path` - Expands a file path by replacing '~' with the user
  directory and makes the path absolute

- :meth:`flatten_dict` - Flattens a nested dictionary

- :meth:`flatten_list` - Flattens a nested list

- :meth:`figure` - Creates a figure and set its label

- :meth:`get_indices` - Returns the pair of indices that bound a target value in
  a monotonically increasing vector

- :meth:`get_pow10` - Returns the exponent of 10 for which the significand
  of a number is within the range [1, 10)

- :meth:`get_pow1000` - Returns the exponent of 1000 for which the
  significand of a number is within the range [1, 1000)

- :meth:`load_csv` - Loads a CSV file into a dictionary

- :meth:`plot` - Plots 1D scalar data as points and/or line segments in 2D
  Cartesian coordinates

- :meth:`quiver` - Plots 2D vector data as arrows in 2D Cartesian coordinates

- :meth:`save` - Saves the current figures as images in a format or list of
  formats

- :meth:`saveall` - Saves all open figures as images in a format or list of
  formats

- :meth:`setup_subplots` - Creates an array of subplots and return their axes

- :meth:`shift_scale_x` - Applies an offset and a factor as necessary to the x
  axis

- :meth:`shift_scale_y` - Applies an offset and a factor as necessary to the y
  axis
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__credits__ = ["Jason Grout", "Jason Heeris"]
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"

import os
import wx
import numpy as np
import matplotlib.pyplot as plt

from collections import MutableMapping, namedtuple
from itertools import cycle
from decimal import Decimal
from math import floor
from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.cbook import iterable


Quantity = namedtuple('Quantity', ['number', 'factor', 'offset', 'unit'])
"""Named tuple class for a constant physical quantity

The factor and then the offset are applied to the number to arrive at the
quantity expressed in terms of the unit.
"""


# Create a class to contain information about a unit conversion.
#Conversion = namedtuple('Conversion', ['unit', 'factor', 'offset', 'new_unit'])


def add_arrows(p, x_locs=[0], xstar_offset=0, ystar_offset=0,
               lstar=0.05, label='',
               orientation='tangent', color='r'):
    r"""Overlay arrows with annotations on top of a pre-plotted line.

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

    .. code-block:: python

       >>> import numpy as np
       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> # Create a plot.
       >>> figure('examples/add_arrows') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> x = np.arange(100)
       >>> p = plt.plot(x, np.sin(x/4.0))

       >>> # Add arrows and annotations.
       >>> add_arrows(p[0], x_locs=x.take(np.arange(20,100,20)),
       ...            label="Incr. time", xstar_offset=-0.15)
       >>> save()
       Saved examples/add_arrows.pdf
       Saved examples/add_arrows.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/add_arrows.png
          :scale: 70 %
          :alt: example of add_arrows()

    .. only:: latex

       .. figure:: ../examples/add_arrows.pdf
          :scale: 70 %

          Example of add_arrows()
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
    r"""Add horizontal lines to a set of axes with optional labels.

    **Arguments:**

    - *ax*: Axes (:class:`matplotlib.axes` object)

    - *positions*: Positions (along the x axis)

    - *labels*: List of labels for the lines

    - *\*\*kwargs*: Line properties (propagated to
      :meth:`matplotlib.pyplot.axhline`)

         E.g., ``color='k', linestyle='--', linewidth=0.5``

    **Example:**

    .. code-block:: python

       >>> import numpy as np
       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> # Create a plot.
       >>> figure('examples/add_hlines') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> x = np.arange(100)
       >>> y = np.sin(x/4.0)
       >>> plt.plot(x, y) # doctest: +ELLIPSIS
       [<matplotlib.lines.Line2D object at 0x...>]
       >>> plt.ylim([-1.2, 1.2])
       (-1.2, 1.2)

       >>> # Add horizontal lines and labels.
       >>> add_hlines(positions=[min(y), max(y)], labels=["min", "max"],
       ...            color='r', ls='--')
       >>> save()
       Saved examples/add_hlines.pdf
       Saved examples/add_hlines.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/add_hlines.png
          :scale: 70 %
          :alt: example of add_hlines()

    .. only:: latex

       .. figure:: ../examples/add_hlines.pdf
          :scale: 70 %

          Example of add_hlines()
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

    .. code-block:: python

       >>> import numpy as np
       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> # Create a plot.
       >>> figure('examples/add_vlines') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> x = np.arange(100)
       >>> y = np.sin(x/4.0)
       >>> plt.plot(x, y) # doctest: +ELLIPSIS
       [<matplotlib.lines.Line2D object at 0x...>]
       >>> plt.ylim([-1.2, 1.2])
       (-1.2, 1.2)

       >>> # Add horizontal lines and labels.
       >>> add_vlines(positions=[25, 50, 75], labels=["A", "B", "C"],
       ...            color='k', ls='--')
       >>> save()
       Saved examples/add_vlines.pdf
       Saved examples/add_vlines.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/add_vlines.png
          :scale: 70 %
          :alt: example of add_vlines()

    .. only:: latex

       .. figure:: ../examples/add_vlines.pdf
          :scale: 70 %

          Example of add_vlines()
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


def animate(imagebase='_tmp', fname="animation", fps=10, clean=False):
    """Encode a series of PNG images as a MPG movie.

    **Arguments:**

    - *imagebase*: Base filename for the PNG images

         The images should be located in the current directory as an
         "*imagebase**xx*.png" sequence, where *xx* is a frame index.

    - *fname*: Filename for the movie

         ".mpg" will be appended if necessary.

    - *fps*: Number of frames per second

    - *clean*: *True*, if the PNG images should be deleted afterward

    .. Note:: This function requires mencoder_.  On Linux, install it with the
       following command: ``sudo apt-get install mencoder``.  Currently, this
       function is not supported on Windows.

    .. _mencoder: http://en.wikipedia.org/wiki/MEncoder

    **Example:**

    .. code-block:: python

       import matplotlib.pyplot as plt
       from numpy.random import rand
       from modelicares import *

       # Create the frames.
       fig = plt.figure(figsize=(5,5))
       ax = fig.add_subplot(111)
       for i in range(50):  # 50 frames
           ax.cla()
           ax.imshow(rand(5,5), interpolation='nearest')
           fname = '_tmp%02d.png' % i
           print("Saving frame %i (file %s)" % (i, fname))
           fig.savefig(fname) # doctest: +ELLIPSIS

       # Assemble the frames into a movie.
       animate(clean=True)
    """
    # Note:  The output of the code above is too large for inline doctest.
    # TODO:  Consider using the animation module from matplotlib.  Should it
    # supercede this function?
    # TODO:  Add support for Windows.

    # Based on
    # http://matplotlib.sourceforge.net/faq/howto_faq.html#make-a-movie,
    # accessed 11/2/10
    if not fname.lower().endswith('.mpg'):
        fname += '.mpg'
    print('Making movie "%s".  This may take a while.' % fname)
    os.system("mencoder 'mf://%s*.png' -mf type=png:fps=%i -ovc lavc "
              "-lavcopts vcodec=wmv2 -oac copy -o %s"%(imagebase, fps, fname))
    if clean:
        from glob import glob
        for image in glob(imagebase + '*.png'):
            os.remove(image)


def color(ax, c, *args, **kwargs):
    """Plot 2D scalar data on a color axis in 2D Cartesian coordinates.

    This uses a uniform grid.

    **Arguments:**

    - *ax*: Axis onto which the data should be plotted

    - *c*: color- or c-axis data (2D array)

    - *\*args*, *\*\*kwargs*: Additional arguments for
      :meth:`matplotlib.pyplot.imshow`

    **Example:**

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> import numpy as np
       >>> from modelicares import *

       >>> figure('examples/color') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> x, y = np.meshgrid(np.arange(0, 2*np.pi, 0.2),
       ...                    np.arange(0, 2*np.pi, 0.2))
       >>> c = np.cos(x) + np.sin(y)
       >>> ax = plt.subplot(111)
       >>> color(ax, c) # doctest: +ELLIPSIS
       <matplotlib.image.AxesImage object at 0x...>
       >>> save()
       Saved examples/color.pdf
       Saved examples/color.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/color.png
          :scale: 70 %
          :alt: example of color()

    .. only:: latex

       .. figure:: ../examples/color.pdf
          :scale: 70 %

          Example of color()
    """
    return ax.imshow(c, *args, **kwargs)


def closeall():
    """Close all open figures.

    This is a shortcut for the following:

       >>> from matplotlib._pylab_helpers import Gcf
       >>> Gcf.destroy_all()
    """
    from matplotlib._pylab_helpers import Gcf
    Gcf.destroy_all()
    #for manager in Gcf.get_all_fig_managers():
    #    manager.canvas.figure.close()
    #plt.close("all")

def convert(quantity):
    """Convert the expression of a physical quantity between units.

    **Arguments:**

    - *quantity*: Instance of :class:`Quantity`

    **Example:**

    .. code-block:: python

       >>> from modelicares import *

       >>> T = 293.15 # Temperature in K
       >>> T_degC = convert(Quantity(T, factor=1, offset=-273.15, unit='C'))
       >>> print(str(T) + " K is " + str(T_degC) + " degC.")
       293.15 K is 20.0 degC.
    """
    return quantity.number*quantity.factor + quantity.offset


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
    # TODO: Utilize matplotlib's support for units.

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
       >>> get_indices([0,1,2],1.6)
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
            i_mid = int(np.floor((i_1 + i_2)/2))
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
        print('Unable to load "%s".  Check that it exists.' % fname)
        return

    # Read the header row and create the dictionary from it.
    for i in range(header_row):
        reader.next()
    keys = reader.next()
    data = dict.fromkeys(keys)
    #print("The keys are: ")
    #print(keys)

    # Read the data.
    if first_data_row:
        for row in range(first_data_row - header_row - 1):
            reader.next()
    if types:
        for i, (key, column, t) in enumerate(zip(keys, zip(*reader), types)):
            # zip(*reader) groups the data by columns.
            try:
                if isinstance(t, basestring):
                    data[key] = column
                elif isinstance(t, (float, int)):
                    data[key] = np.array(map(t, column))
                else:
                    data[key] = map(t, column)
            except ValueError:
                print("Could not cast column %i into %i." % (i, t))
                return
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

    .. testsetup::
       >>> closeall()

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> import numpy as np
       >>> from modelicares import *

       >>> figure('examples/plot') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> ax = plt.subplot(111)
       >>> plot([range(11), range(10, -1, -1)], ax=ax) # doctest: +ELLIPSIS
       [[<matplotlib.lines.Line2D object at 0x...>], [<matplotlib.lines.Line2D object at 0x...>]]
       >>> save()
       Saved examples/plot.pdf
       Saved examples/plot.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/plot.png
          :scale: 70 %
          :alt: example of plot()

    .. only:: latex

       .. figure:: ../examples/plot.pdf
          :scale: 70 %

          Example of plot()
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
                         color=color.next(), marker=marker.next(),
                         dashes=dashes.next(), **kwargs)
                 for i, yi in enumerate(y)]
    elif not iterable(x[0]):
        # There is only one x series; use it repeatedly.
        plots = [ax.plot(x, yi, label=None if label is None else label[i],
                         color=color.next(), marker=marker.next(),
                         dashes=dashes.next(), **kwargs)
                 for i, yi in enumerate(y)]
    else:
        # There is a x series for each y series.
        plots = [ax.plot(xi, yi, label=None if label is None else label[i],
                         color=color.next(), marker=marker.next(),
                         dashes=dashes.next(), **kwargs)
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

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> import numpy as np
       >>> from modelicares import *

       >>> figure('examples/quiver') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> x, y = np.meshgrid(np.arange(0, 2*np.pi, 0.2),
       ...                    np.arange(0, 2*np.pi, 0.2))
       >>> u = np.cos(x)
       >>> v = np.sin(y)
       >>> ax = plt.subplot(111)
       >>> quiver(ax, u, v) # doctest: +ELLIPSIS
       <matplotlib.quiver.Quiver object at 0x...>
       >>> save()
       Saved examples/quiver.pdf
       Saved examples/quiver.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/quiver.png
          :scale: 70 %
          :alt: example of quiver()

    .. only:: latex

       .. figure:: ../examples/quiver.pdf
          :scale: 70 %

          Example of quiver()
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

def save(formats=['pdf', 'png'], fbase='1'):
    """Save the current figures as images in a format or list of formats.

    The directory and base filenames are taken from the *label* property of the
    figures.  A slash ("/") can be used as a path separator, even if the
    operating system is Windows.  Folders are created as needed.  If the *label*
    property is empty, then a directory dialog is opened to chose a directory.

    **Arguments:**

    - *formats*: Format or list of formats in which the figure should be saved

    - *fbase*: Default directory and base filename

         This is used if the *label* attribute of the figure is empty ('').

    .. Note::  In general, :meth:`save` should be called before
       :meth:`matplotlib.pyplot.show` so that the figure(s) are still present
       in memory.

    **Example:**

    .. testsetup::
       >>> closeall()

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> figure('temp_plot') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> plt.plot(range(10)) # doctest: +ELLIPSIS
       [<matplotlib.lines.Line2D object at 0x...>]
       >>> save()
       Saved temp_plot.pdf
       Saved temp_plot.png

    .. Note::  The :meth:`figure` method can be used to directly create a
       figure with a label.
    """
    from wx import DirSelector, App

    # Initialize a dummy wx.App instance.  Dialogs can only be called after
    # this is done [http://warp.byu.edu/site/content/131, accessed 10/9/2012].
    app = App()

    # If formats is a singleton, turn it into a list.
    if not type(formats) is list:
        formats = [formats,]

    # Find the figure.
    fig = plt.gcf()

    # Save the figures, creating folders as necessary.
    (directory, fbase_fig) = os.path.split(plt.getp(fig, 'label'))
    if not fbase_fig:
        if not directory:
            # Initialize a dummy wx.App instance.  Dialogs can only be
            # called after this is done
            # [http://code.google.com/p/easywx/, accessed 10/7/2012].
            #app = App()
            directory = DirSelector("Choose a directory for the images.",
                                    defaultPath=os.path.join(*['..']*4))
            if not directory:
                return
    else:
        fbase = fbase_fig
    if directory and not os.path.isdir(directory):
        os.mkdir(directory)
    for format in formats:
        fname = os.path.join(directory, fbase + '.' + format)
        fig.savefig(fname, format=format)
        print("Saved " + fname)

def saveall(formats=['pdf', 'png']):
    """Save all open figures as images in a format or list of formats.

    The directory and base filenames are taken from the *label* property of the
    figures.  A slash ("/") can be used as a path separator, even if the
    operating system is Windows.  Folders are created as needed.  If the *label*
    property is empty, then a directory dialog is opened to chose a directory.
    In that case, the figures are saved as a sequence of numbers.

    **Arguments:**

    - *formats*: Format or list of formats in which the figures should be saved

    .. Note::  In general, :meth:`saveall` should be called before
       :meth:`matplotlib.pyplot.show` so that the figure(s) are still present
       in memory.

    **Example:**

    .. testsetup::
       >>> closeall()

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> figure('temp_plot') # doctest: +ELLIPSIS
       <matplotlib.figure.Figure object at 0x...>
       >>> plt.plot(range(10)) # doctest: +ELLIPSIS
       [<matplotlib.lines.Line2D object at 0x...>]
       >>> save()
       Saved temp_plot.pdf
       Saved temp_plot.png

    .. Note::  The :meth:`figure` method can be used to directly create a
       figure with a label.
    """
    from matplotlib._pylab_helpers import Gcf
    from wx import DirSelector, App

    # Initialize a dummy wx.App instance.  Dialogs can only be called after
    # this is done [http://warp.byu.edu/site/content/131, accessed 10/9/2012].
    app = App()

    # If formats is a singleton, turn it into a list.
    if not type(formats) is list:
        formats = [formats,]

    # Find the figures.
    figs = [manager.canvas.figure for manager in Gcf.get_all_fig_managers()]

    # Save the figures, creating folders as necessary.
    chosen_directory = None
    i = 0
    for fig in figs:
        (directory, fbase) = os.path.split(plt.getp(fig, 'label'))
        if not fbase:
            fbase = str(i)
            i += 1
            if not directory:
                if chosen_directory is None:
                    # Initialize a dummy wx.App instance.  Dialogs can only be
                    # called after this is done
                    # [http://code.google.com/p/easywx/, accessed 10/7/2012].
                    #app = App()
                    chosen_directory = DirSelector(
                        "Choose a directory for the images.",
                        defaultPath=os.path.join(*['..']*4))
                    if not chosen_directory:
                        return
                directory = chosen_directory
        if directory and not os.path.isdir(directory):
            os.mkdir(directory)
        for format in formats:
            fname = os.path.join(directory, fbase + '.' + format)
            fig.savefig(fname, format=format)
            print("Saved " + fname)

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

    .. testsetup::
       >>> closeall()

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> from modelicares import *

       >>> setup_subplots(4, 2, label='examples/setup_subplots') # doctest: +ELLIPSIS
       ([<matplotlib.axes._subplots.AxesSubplot object at 0x...>, <matplotlib.axes._subplots.AxesSubplot object at 0x...>, <matplotlib.axes._subplots.AxesSubplot object at 0x...>, <matplotlib.axes._subplots.AxesSubplot object at 0x...>], 2)
       >>> save()
       Saved examples/setup_subplots.pdf
       Saved examples/setup_subplots.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/setup_subplots.png
          :scale: 70 %
          :alt: example of setup_subplots()

    .. only:: latex

       .. figure:: ../examples/setup_subplots.pdf
          :scale: 70 %

       Example of setup_subplots()
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

# TODO: Remove the "_" prefix once this is tested and ready.
def _shift_scale_c(cbar, v_min, v_max, eagerness=0.325):
    """"Apply an offset and a factor as necessary to the colorbar.

    **Arguments:**

    - *cbar*: :class:`matplotlib.colorbar.Colorbar` object

    - *v_min*: Minimum of the color-axis data

    - *v_max*: Maximum of the color-axis data

    - *eagerness*: Parameter to adjust how little of an offset is required
      before the label will be recentered

         - 0: Offset is never applied.

         - 1: Offset is always applied if it will help.
    """
    # TODO: Provide an example.
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

    - *eagerness*: Parameter to adjust how little of an offset is required
      before the label will be recentered

         - 0: Offset is never applied.

         - 1: Offset is always applied if it will help.

    **Example:**

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> import numpy as np
       >>> from texunit import label_number
       >>> from modelicares import *

       >>> # Generate some random data.
       >>> x = np.linspace(55478, 55486, 100) # Small range and large offset
       >>> xlabel = label_number('Time', 's')
       >>> y = np.cumsum(np.random.random(100) - 0.5)

       >>> # Plot the data.
       >>> ax = setup_subplots(2, 2, label='examples/shift_scale_x')[0]
       >>> for a in ax:
       ...     a.plot(x, y)
       ...     a.set_xlabel(xlabel) # doctest: +ELLIPSIS
       [<matplotlib.lines.Line2D object at 0x...>]
       <matplotlib.text.Text object at 0x...>
       [<matplotlib.lines.Line2D object at 0x...>]
       <matplotlib.text.Text object at 0x...>

       >>> # Shift and scale the axes.
       >>> ax[0].set_title('Original plot') # doctest: +ELLIPSIS
       <matplotlib.text.Text object at 0x...>
       >>> ax[1].set_title('After applying offset and factor') # doctest: +ELLIPSIS
       <matplotlib.text.Text object at 0x...>
       >>> shift_scale_x(ax[1])
       >>> save()
       Saved examples/shift_scale_x.pdf
       Saved examples/shift_scale_x.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/shift_scale_x.png
          :scale: 70 %
          :alt: example of shift_scale_x()

    .. only:: latex

       .. figure:: ../examples/shift_scale_x.pdf
          :scale: 70 %

          Example of shift_scale_x()
    """
    # The concept here is based on:
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

    - *eagerness*: Parameter to adjust how little of an offset is required
      before the label will be recentered

         - 0: Offset is never applied.

         - 1: Offset is always applied if it will help.

    **Example:**

    .. code-block:: python

       >>> import matplotlib.pyplot as plt
       >>> import numpy as np
       >>> from texunit import label_number
       >>> from modelicares import *

       >>> # Generate some random data.
       >>> x = range(100)
       >>> y = np.cumsum(np.random.random(100) - 0.5)
       >>> y -= y.min()
       >>> y *= 1e-3
       >>> y += 1e3 # Small magnitude and large offset
       >>> ylabel = label_number('Velocity', 'mm/s')

       >>> # Plot the data.
       >>> ax = setup_subplots(2, 2, label='examples/shift_scale_y')[0]
       >>> for a in ax:
       ...     a.plot(x, y)
       ...     a.set_ylabel(ylabel) # doctest: +ELLIPSIS
       [<matplotlib.lines.Line2D object at 0x...>]
       <matplotlib.text.Text object at 0x...>
       [<matplotlib.lines.Line2D object at 0x...>]
       <matplotlib.text.Text object at 0x...>

       >>> # Shift and scale the axes.
       >>> ax[0].set_title('Original plot') # doctest: +ELLIPSIS
       <matplotlib.text.Text object at 0x...>
       >>> ax[1].set_title('After applying offset and factor') # doctest: +ELLIPSIS
       <matplotlib.text.Text object at 0x...>
       >>> shift_scale_y(ax[1])
       >>> save()
       Saved examples/shift_scale_y.pdf
       Saved examples/shift_scale_y.png
       >>> plt.show()

    .. only:: html

       .. image:: ../examples/shift_scale_y.png
          :scale: 70 %
          :alt: example of shift_scale_y()

    .. only:: latex

       .. figure:: ../examples/shift_scale_y.pdf
          :scale: 70 %

          Example of shift_scale_y()
    """
    # The concept here is based on:
    # http://efreedom.com/Question/1-3677368/Matplotlib-Format-Axis-Offset-Values-Whole-Numbers-Specific-Number,
    # accessed 2010/11/10
    label = ax.get_ylabel()
    ticks = ax.get_yticks()
    label, offset, pow1000 = _gen_offset_factor(label, ticks[0], ticks[-1],
                                                eagerness)
    ax.set_yticklabels(["%.1f" % x for x in (ticks - offset)/1000**pow1000])
    ax.set_ylabel(label)


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

        .. code-block:: python

           >>> import matplotlib.pyplot as plt
           >>> from modelicares import *

           >>> fig = figure('examples/ArrowLine') # doctest: +ELLIPSIS
           >>> ax = fig.add_subplot(111, autoscale_on=False)
           >>> t = [-1,2]
           >>> s = [0,-1]
           >>> line = ArrowLine(t, s, color='b', ls='-', lw=2, arrow='>',
           ...                  arrowsize=20)
           >>> ax.add_line(line) # doctest: +ELLIPSIS
           <modelicares.base.ArrowLine object at 0x...>
           >>> ax.set_xlim(-3, 3)
           (-3, 3)
           >>> ax.set_ylim(-3, 3)
           (-3, 3)
           >>> save()
           Saved examples/ArrowLine.pdf
           Saved examples/ArrowLine.png
           >>> plt.show()

        .. only:: html

           .. image:: ../examples/ArrowLine.png
              :scale: 70 %
              :alt: example of ArrowLine

        .. only:: latex

           .. figure:: ../examples/ArrowLine.pdf
              :scale: 70 %

              Example of ArrowLine
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
