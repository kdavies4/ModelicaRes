#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions to load and plot data from multiple simulation and linearization
files at once

- :meth:`multiload` - Load multiple Modelica_ simulation and/or linearization
  results

- :meth:`multiplot` - Plot data from multiple simulations in 2D Cartesian
  coordinates

- :meth:`multibode` - Plot multiple linearizations onto a single Bode diagram

- :meth:`multinyquist` - Plot multiple linearizations onto a single Nyquist
  diagram


.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__credits__ = ["Kevin Bandy"]
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
import numpy as np

from glob import glob
from matplotlib.cbook import iterable
from itertools import cycle

from freqplot import bode_plot, nyquist_plot
from modelicares.linres import LinRes
from modelicares.simres import SimRes
from modelicares.base import figure, add_hlines, add_vlines


def multiload(locations='*'):
    """Load multiple Modelica_ simulation and/or linearization results.

    **Arguments:**

    - *locations*: Input filename, directory, or list of these

         Wildcards ('*') may be used in the path(s).

    **Returns:**

    1. List of simulations (:class:`simres.SimRes` instances)

    2. List of linearizations (:class:`linres.LinRes` instances)

    Either may be an empty list.

    **Example:**

    .. code-block:: python

       >>> from modelicares import *

       # By file:
       >>> multiload(['examples/ChuaCircuit.mat', 'examples/PID/*/*.mat']) # doctest: +ELLIPSIS
       Valid: SimRes('.../examples/ChuaCircuit.mat')
       Valid: LinRes('.../examples/PID/1/dslin.mat')
       Valid: LinRes('.../examples/PID/2/dslin.mat')
       ([SimRes('.../examples/ChuaCircuit.mat')], [LinRes('.../examples/PID/1/dslin.mat'), LinRes('.../examples/PID/2/dslin.mat')])


       # By directory:
       >>> multiload('examples') # doctest: +ELLIPSIS
       Valid: SimRes('...ChuaCircuit.mat')
       Valid: LinRes('...PID.mat')...
       Valid: SimRes('...ThreeTanks.mat')
       ([SimRes('...ChuaCircuit.mat'), SimRes('...ThreeTanks.mat')], [LinRes('...PID.mat')])
    """

    # Make a list of files.
    fnames = []
    if isinstance(locations, basestring):
        locations = [locations]
    for location in locations:
        if os.path.isdir(location):
            fnames += glob(os.path.join(location, '*.mat'))
        else:
            if '*' in location:
                fnames += glob(location)
            else:
                fnames.append(location)

    # Load the files.
    sims = [] # Simulation results
    lins = [] # Linearization results
    for fname in fnames:
        try:
            sims.append(SimRes(fname))
            print("Valid: " + sims[-1].__repr__())
        except:
            try:
                lins.append(LinRes(fname))
                print("Valid: " + lins[-1].__repr__())
            except:
                print("Could not load simulation or linearization data from "
                      "'%s'." % fname)
    return sims, lins

def multiplot(sims, suffixes='', color=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
              dashes=[(None, None), (3, 3), (1, 1), (3, 2, 1, 2)], **kwargs):
    """Plot data from multiple simulations in 2D Cartesian coordinates.

    This method simply calls :meth:`simres.SimRes.plot` from multiple instances
    of :class:`simres.SimRes`.

    A new figure is created if necessary.

    **Arguments:**

    - *sims*: Simulation result or list of results (instances of
      :class:`simres.SimRes`)

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

    - *\*\*kwargs*: Propagated to :meth:`simres.SimRes.plot` (and thus to
      :meth:`base.plot` and finally :meth:`matplotlib.pyplot.plot`)

    **Returns:**

    1. *ax1*: Primary y axes

    2. *ax2*: Secondary y axes

    **Example:**

    .. testsetup::
       >>> from modelicares import closeall
       >>> closeall()

    .. code-block:: python

       >>> from glob import glob
       >>> from modelicares import SimRes, multiplot, save

       >>> sims = map(SimRes, glob('examples/ChuaCircuit/*/*.mat'))
       >>> multiplot(sims, title="Chua Circuit", label='examples/ChuaCircuits',
       ...           suffixes=['L.L = %.0f H' % sim.get_IV('L.L')
       ...                     for sim in sims], # Read legend parameters.
       ...           ynames1='L.i', ylabel1="Current") # doctest: +ELLIPSIS
       (<matplotlib.axes...AxesSubplot object at 0x...>, None)

       >>> save()
       Saved examples/ChuaCircuits.pdf
       Saved examples/ChuaCircuits.png

    .. only:: html

       .. image:: ../examples/ChuaCircuits.png
          :scale: 70 %
          :alt: plot of Chua circuit with varying inductance

    .. only:: latex

       .. figure:: ../examples/ChuaCircuits.pdf
          :scale: 70 %

          Plot of Chua circuit with varying inductance
    """
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
        suffixes = [sim.fbase for sim in sims]
    elif suffixes == None:
        suffixes = ['']*len(sims)

    # Generate the plots.
    try:
        ax1, ax2 = sims[0].plot(suffix=suffixes[0], **kwargs)
        kwargs.update({'ax1': ax1, 'ax2': ax2})
        for sim, suffix in zip(sims[1:], suffixes[1:]):
            sim.plot(suffix=suffix, **kwargs)
    except TypeError:
        # sims may be a single simulation result.
        ax1, ax2 = sims.plot(suffix=suffixes, **kwargs)
    return ax1, ax2

def multibode(lins, axes=None, pair=(0, 0), label='bode', title="Bode Plot",
              labels='', colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
              styles=[(None,None), (3,3), (1,1), (3,2,1,2)], leg_kwargs={},
              **kwargs):
    r"""Plot multiple linearizations onto a single Bode diagram.

    **Arguments:**

    - *lins*: Linearization result or list of results (instances of
      :class:`linres.LinRes`)

    - *axes*: Tuple (pair) of axes for the magnitude and phase plots

         If *axes* is not provided, then axes will be created in a new figure.

    - *pair*: Tuple of (input index, output index) for the transfer function
      to be chosen from each system (applied to all)

         This is ignored if the system is SISO.

    - *label*: Label for the figure (ignored if axes is provided)

         This will be used as the base filename if the figure is saved.

    - *title*: Title for the figure

    - *labels*: Label or list of labels for the legends

         If *labels* is *None*, then no label will be used.  If it is an
         empty string (''), then the base filenames will be used.

    - *colors*: Color or list of colors that will be used sequentially

         Each may be a character, grayscale, or rgb value.

         .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

    - *styles*: Line/dash style or list of line/dash styles that will be
      used sequentially

         Each style is a string representing a linestyle (e.g., "--") or a
         tuple of on/off lengths representing dashes.  Use "" for no line
         and "-" for a solid line.

         .. Seealso::
            http://matplotlib.sourceforge.net/api/collections_api.html

    - *leg_kwargs*: Dictionary of keyword arguments for
      :meth:`matplotlib.pyplot.legend`

         If *leg_kwargs* is *None*, then no legend will be shown.

    - *\*\*kwargs*: Additional arguments for :meth:`control.freqplot.bode`

    **Returns:**

    1. *axes*: Tuple (pair) of axes for the magnitude and phase plots

    **Example:**

    .. testsetup::
       >>> from modelicares import closeall
       >>> closeall()

    .. code-block:: python

       >>> import os

       >>> from glob import glob
       >>> from modelicares import LinRes, multibode, save, read_params
       >>> from numpy import pi, logspace

       >>> lins = map(LinRes, glob('examples/PID/*/*.mat'))
       >>> labels = ["Ti=%g" % read_params('Ti', os.path.join(lin.dir, 'dsin.txt'))
       ...           for lin in lins]
       >>> multibode(lins,
       ...           title="Bode Plot of Modelica.Blocks.Continuous.PID",
       ...           label='examples/PIDs-bode', omega=2*pi*logspace(-2, 3),
       ...           labels=labels, leg_kwargs=dict(loc='lower right')) # doctest: +ELLIPSIS
       (<matplotlib.axes...AxesSubplot object at 0x...>, <matplotlib.axes...AxesSubplot object at 0x...>)

       >>> save()
       Saved examples/PIDs-bode.pdf
       Saved examples/PIDs-bode.png

    .. only:: html

       .. image:: ../examples/PIDs-bode.png
          :scale: 70 %
          :alt: Bode plot of PID with varying parameters

    .. only:: latex

       .. figure:: ../examples/PIDs-bode.pdf
          :scale: 70 %

          Bode plot of PID with varying parameters
    """
    # Create axes if necessary.
    if not axes:
        fig = figure(label)
        axes = (fig.add_subplot(211), fig.add_subplot(212))

    # Process the lins input.
    if not iterable(lins):
        lins = [lins]

    # Process the labels input.
    if labels == '':
        labels = [lin.fbase for lin in lins]
    elif labels == None:
        labels = ['']*len(lins)

    # Set up the color(s) and line style(s).
    if not iterable(colors):
        # Use the single color for all plots.
        colors = (colors,)
    if not iterable(styles):
        # Use the single line style for all plots.
        styles = [styles]
    elif type(styles[0]) is int:
        # One dashes tuple has been provided; use its value for all plots.
        styles = [styles]
    n_colors = len(colors)
    n_styles = len(styles)

    # Create the plots.
    for i, (lin, label) in enumerate(zip(lins, labels)):
        if lin.sys.inputs > 1 or lin.sys.outputs > 1:
            # Extract the SISO TF. TODO: Is there a better way to do this?
            sys = ss(self.sys.A, self.sys.B[:, pair[0]], self.sys.C[pair[1], :],
                     self.sys.D[pair[1], pair[0]])
        else:
            sys = lin.sys
        bode_plot(sys, Hz=True, label=label,
                  color=colors[np.mod(i, n_colors)], axes=axes,
                  style=styles[np.mod(i, n_styles)], **kwargs)

    # Decorate and finish.
    axes[0].set_title(title)
    if leg_kwargs is not None:
        loc = leg_kwargs.pop('loc', 'best')
        axes[0].legend(loc=loc, **leg_kwargs)
        axes[1].legend(loc=loc, **leg_kwargs)
    return axes

def multinyquist(lins, ax=None, pair=(0, 0), label='nyquist',
                 title="Nyquist Plot",  xlabel="Real Axis",
                 ylabel="Imaginary Axis", labels='',
                 colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
                 leg_kwargs={}, **kwargs):
    """Plot multiple linearizations onto a single Nyquist diagram.

    **Arguments:**

    - *lins*: Linearization result or list of results (instances of
      :class:`linres.LinRes`)

    - *ax*: Axes onto which the Nyquist diagrams should be plotted

         If *ax* is not provided, then axes will be created in a new figure.

    - *pair*: Tuple of (input index, output index) for the transfer function
      to be chosen from each system (applied to all)

         This is ignored if the system is SISO.

    - *label*: Label for the figure (ignored if axes is provided)

         This will be used as the base filename if the figure is saved.

    - *title*: Title for the figure

        - *xlabel*: x-axis label

        - *ylabel*: y-axis label

    - *labels*: Label or list of labels for the legends

         If *labels* is *None*, then no label will be used.  If it is an
         empty string (''), then the base filenames will be used.

    - *colors*: Color or list of colors that will be used sequentially

         Each may be a character, grayscale, or rgb value.

         .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

    - *leg_kwargs*: Dictionary of keyword arguments for
      :meth:`matplotlib.pyplot.legend`

         If *leg_kwargs* is *None*, then no legend will be shown.

    - *\*\*kwargs*: Additional arguments for :meth:`control.freqplot.nyquist`

         If *textFreq* is not specified, then only the frequency points of the
         first system will have text labels.

    **Returns:**

        1. *ax*: Axes of the Nyquist plot

    **Example:**

    .. testsetup::
       >>> from modelicares import closeall
       >>> closeall()

    .. code-block:: python

       >>> import os

       >>> from glob import glob
       >>> from modelicares import LinRes, multinyquist, save, read_params
       >>> from numpy import pi, logspace

       >>> lins = map(LinRes, glob('examples/PID/*/*.mat'))
       >>> labels = ["Td=%g" % read_params('Td', os.path.join(lin.dir, 'dsin.txt'))
       ...           for lin in lins]
       >>> multinyquist(lins,
       ...              title="Nyquist Plot of Modelica.Blocks.Continuous.PID",
       ...              label='examples/PIDs-nyquist', textFreq=True,
       ...              omega=2*pi*logspace(-1, 3, 81), labelFreq=20,
       ...              labels=labels) # doctest: +ELLIPSIS
       <matplotlib.axes...AxesSubplot object at 0x...>

       >>> save()
       Saved examples/PIDs-nyquist.pdf
       Saved examples/PIDs-nyquist.png

    .. only:: html

       .. image:: ../examples/PIDs-nyquist.png
          :scale: 70 %
          :alt: Nyquist plot of PID with varying parameters

    .. only:: latex

       .. figure:: ../examples/PIDs-nyquist.pdf
          :scale: 70 %

          Nyquist plot of PID with varying parameters
    """
    # Create axes if necessary.
    if not ax:
        fig = figure(label)
        ax = fig.add_subplot(111, aspect='equal')

    # Process the lins input.
    if not iterable(lins):
        lins = [lins]


    # Process the labels input.
    if labels == '':
        labels = [lin.fbase for lin in lins]
    elif labels == None:
        labels = ['']*len(lins)

    # Set up the color(s).
    if not iterable(colors):
        # Use the single color for all plots.
        colors = (colors,)
    n_colors = len(colors)

    # Create the plots.
    textFreq = kwargs.pop('textFreq', None)
    for i, (lin, label) in enumerate(zip(lins, labels)):
        if lin.sys.inputs > 1 or lin.sys.outputs > 1:
            # Extract the SISO TF. TODO: Is there a better way to do this?
            sys = ss(self.sys.A, self.sys.B[:, pair[0]], self.sys.C[pair[1], :],
                     self.sys.D[pair[1], pair[0]])
        else:
            sys = lin.sys
        nyquist_plot(sys, mark=False, label=label, ax=ax,
                     textFreq=i==0 if textFreq is None else textFreq,
                     color=colors[np.mod(i, n_colors)], **kwargs)

    # Decorate and finish.
    add_hlines(ax, color='k', linestyle='--', linewidth=0.5)
    add_vlines(ax, color='k', linestyle='--', linewidth=0.5)
    ax.set_title(title)
    if xlabel: # Without this check, xlabel=None will give a label of "None".
        ax.set_xlabel(xlabel)
    if ylabel: # Same purpose
        ax.set_ylabel(ylabel)
    if leg_kwargs is not None:
        loc = leg_kwargs.pop('loc', 'best')
        ax.legend(loc=loc, **leg_kwargs)
    return ax

if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
    exit()
