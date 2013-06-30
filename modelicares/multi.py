#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions to load and plot data from multiple simulation and linearization
files at once

.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__credits__ = ["Kevin Bandy"]
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os

from modelicares.linres import LinRes
from modelicares.simres import SimRes

from glob import glob
from matplotlib.cbook import iterable
from itertools import cycle


def multiload(locations):
    """Load multiple Modelica_ simulation and/or linearization results.

    **Arguments:**

    - *locations*: Input filename, directory, or list of these

         Wildcards ('*') may be used in the filename(s).

    **Returns:**

    1. List of simulations (:class:`simres.SimRes` instances)

    2. List of linearizations (:class:`linres.LinRes` instances)

    Either may be an empty list.

    **Example:**

    .. code-block:: python

       >>> from modelicares import *

       # By file:
       >>> multiload(['examples/ChuaCircuit', 'examples/PID']) # doctest: +ELLIPSIS
       Valid: SimRes('...ChuaCircuit.mat')
       Valid: LinRes('...PID.mat')
       ([SimRes('...ChuaCircuit.mat')], [LinRes('...PID.mat')])

       # By directory:
       >>> multiload('examples') # doctest: +ELLIPSIS
       Valid: SimRes('...ChuaCircuit.mat')
       Valid: SimRes('...ChuaCircuit2.mat')...
       Valid: LinRes('...PID.mat')...
       ([SimRes('...ChuaCircuit.mat'), SimRes('...ChuaCircuit2.mat'), SimRes('...ThreeTanks.mat')], [LinRes('...PID.mat')])
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


def multiplot(sims, suffixes, dashes=[(1, 0), (3, 3), (1, 1), (3, 2, 1, 2)],
              **kwargs):
    """Plot data from multiple simulations in 2D Cartesian coordinates.

    This method simply calls :meth:`simres.SimRes.plot` from multiple instances
    of :class:`simres.SimRes`.

    A new figure is created if necessary.

    **Arguments:**

    - *sims*: Simulation result or list of results (instances of
      :class:`simres.SimRes`)

    - *suffixes*: Suffix or list of suffixes for the legends (see
      :meth:`simres.SimRes.plot`)

    - *\*\*kwargs*: Propagated to  :meth:`simres.SimRes.plot` (and thus to
      :meth:`base.plot` and finally :meth:`matplotlib.pyplot.plot`)

         The *dashes* sequence is iterated across all plots.

    **Example:**

    .. testsetup::
       >>> from modelicares import closeall
       >>> closeall()

    .. code-block:: python

       >>> from modelicares import SimRes, multiplot, saveall

       >>> sims = map(SimRes, ['examples/ChuaCircuit', 'examples/ChuaCircuit2'])
       >>> multiplot(sims, title="Chua Circuit", label='examples/ChuaCircuits',
       ...           suffixes=['L.L = %.0f H' % sim.get_IV('L.L')
       ...                     for sim in sims], # Read legend parameters.
       ...           ynames1='L.i', ylabel1="Current") # doctest: +ELLIPSIS
       (<matplotlib.axes.AxesSubplot object at 0x...>, None)
       >>> saveall()
       Saved examples/ChuaCircuits.pdf
       Saved examples/ChuaCircuits.png

    .. only:: html

       .. image:: examples/ChuaCircuits.png
          :scale: 70 %
          :alt: plot of Chua circuit with varying inductance

    .. only:: latex

       .. figure:: examples/ChuaCircuits.pdf
          :scale: 70 %

          Plot of Chua circuit with varying inductance
    """
    # Cycle the dashes to make the lines unique.
    if not isinstance(dashes, type(cycle([]))):
        if not iterable(dashes[0]):
            dashes = [dashes]
        dashes = cycle(dashes)
    kwargs['dashes'] = dashes

    try:
        ax1, ax2 = sims[0].plot(suffix=suffixes[0], **kwargs)
        kwargs.update({'ax1': ax1, 'ax2': ax2})
        for sim, suffix in zip(sims[1:], suffixes[1:]):
            sim.plot(suffix=suffix, **kwargs)
    except TypeError:
        # sims may be a single simulation result.
        ax1, ax2 = sims.plot(suffix=suffixes, **kwargs)
    return ax1, ax2


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
    exit()
