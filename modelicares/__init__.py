#!/usr/bin/python
"""Functions and classes to set up Modelica_ simulations and load, analyze, and
plot the results.

This module provides convenient access to the most important functions and
classes from its submodules.  These are:

- To manage simulation experiments (:mod:`~modelicares.exps` module):
  :mod:`~modelicares.exps.doe`, :class:`~exps.Experiment`,
  :meth:`~exps.gen_experiments`, :class:`~exps.ParamDict`,
  :meth:`~exps.run_models`, :meth:`~exps.write_params`, and
  :meth:`~exps.write_script`

- For simulation results (:mod:`~modelicares.simres` module):
  :class:`~simres.SimRes` and :class:`~simres.SimResList`

- For linearization results (:mod:`~modelicares.linres` module):
  :class:`~linres.LinRes` and :class:`~linres.LinResList`

- To label numbers and quantities (:mod:`~modelicares.texunit` module):
  :meth:`~texunit.number_label`, :meth:`~texunit.quantity_str`, and
  :meth:`~texunit.unit2tex`

- Supporting classes and functions (:mod:`~modelicares.util` module):
  :meth:`~util.add_arrows`, :meth:`~util.add_hlines`, :meth:`~util.add_vlines`,
  :class:`~util.ArrowLine`, :meth:`~util.closeall`, :meth:`~util.figure`,
  :meth:`~util.load_csv`, :meth:`~util.save`, :meth:`~util.saveall`, and
  :meth:`~util.setup_subplots`

A function is also provided:


.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"
__version__ = "0.11.0"


# Essential functions and classes
#
# These will be available directly from modelicares; others must be loaded from
# their submodules.
from modelicares.simres import SimRes, SimResList
from modelicares.linres import LinRes, LinResList
from modelicares.util import (add_arrows, add_hlines, add_vlines, ArrowLine,
                              closeall, figure, load_csv, save, saveall,
                              setup_subplots)
from modelicares.exps import (doe, Experiment, gen_experiments, ParamDict,
                              read_params, write_params, write_script)
# TODO: Add run_models and include in the doc list once supported.
from modelicares.texunit import number_label, quantity_str, unit2tex


def load(*args):
    """Load multiple Modelica_ simulation and/or linearization results.

    This function can be called with any number of arguments, each of which is
    a filename or directory with results to load.  The filenames or directory
    names may contain wildcards.  Each path must be absolute or resolved to the
    current directory.

    As many of the matching filenames will be loaded as possible.  No errors
    will be given for files that cannot be loaded.

    **Returns:**

    1. :class:`~simres.SimResList` of simulations

    2. :class:`~linres.LinResList` of linearizations

    Either may be an empty list.

    **Example:**

    .. code-block:: python

       >>> from modelicares import load

       # Get the mean values of the first capacitor's voltage from two runs
       # of the Chua circuit.
       >>> sims, __ = load('examples/ChuaCircuit/*/')
       >>> sims['C1.v'].mean()
       [0.76859528, 0.76859528]

       # The values are different because the inductance was set differently:
       >>> sims['L.L'].value()
       [10, 18]
    """

    import os
    from glob import glob

    # Get a unique list of matching filenames.
    fnames = set()
    for arg in args:
        if os.path.isdir(arg):
            fnames = fnames.union(set(glob(os.path.join(arg, '*.mat'))))
        elif '*' in arg or '?' in arg or '[' in arg:
            fnames = fnames.union(set(glob(arg)))
        else:
            fnames.add(arg)

    # Load the files and append each result onto the appropriate list.
    sims = SimResList()
    lins = LinResList()
    for fname in fnames:
        try:
            sims.append(SimRes(fname))
        except IOError:
            continue
        except:
            try:
                lins.append(LinRes(fname))
            except:
                continue

    return sims, lins


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
