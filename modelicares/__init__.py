#!/usr/bin/python
"""Functions and classes to run Modelica_ simulation experiments and load,
analyze, and plot the results

This module provides convenient access to the most important functions and
classes from the submodules.  These are:

- To run simulation experiments (:mod:`~modelicares.exps` submodule):
  :mod:`~modelicares.exps.doe`, :func:`~exps.read_params`, and
  :func:`~exps.write_params`

- To load, analyze, and plot simulation results (:mod:`~modelicares.simres`
  submodule): :class:`~simres.SimRes` and :class:`~simres.SimResList`

- To load, analyze, and plot linearization results (:mod:`~modelicares.linres`
  submodule): :class:`~linres.LinRes` and :class:`~linres.LinResList`

- Supporting classes and functions (:mod:`~modelicares.util` submodule):
  :func:`~util.add_arrows`, :func:`~util.add_hlines`, :func:`~util.add_vlines`,
  :class:`~util.ArrowLine`, :func:`~util.closeall`, :func:`~util.figure`,
  :func:`~util.load_csv`, :class:`~util.ParamDict`, :func:`~util.save`,
  :func:`~util.saveall`, and :func:`~util.setup_subplots`

There is also a local function:


.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=I0011, W0611

# Essential functions and classes
#
# These will be available directly from modelicares; others must be loaded from
# their submodules.
from .simres import SimRes, SimResList, SimResSequence
from .linres import LinRes, LinResList
from .util import (add_arrows, add_hlines, add_vlines, ArrowLine, closeall,
                   figure, load_csv, ParamDict, save, saveall, setup_subplots)
from .exps import (doe, read_options, read_params, write_options, write_params,
                   simulators)

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

       # Get the mean values of the first capacitor's voltage from two runs of
       # the Chua circuit.
       >>> sims, __ = load('examples/ChuaCircuit/*/')
       >>> sims.sort()

       >>> sims['C1.v'].mean()
       [-1.6083468, 0.84736514]

       # The voltage is different because the inductance is different:
       >>> sims['L.L'].value()
       [15.0, 21.0]
    """
    from natu.util import multiglob

    # Get the set of matching filenames.
    fnames = multiglob(args)

    # Load the files and append each result onto the appropriate list.
    sims = SimResList()
    lins = LinResList()
    for fname in fnames:
        try:
            sims.append(SimRes(fname))
        except IOError:
            continue
        except (AssertionError, IndexError, KeyError, TypeError,
                ValueError):
            try:
                lins.append(LinRes(fname))
            except (AssertionError, IndexError, IOError, KeyError, TypeError,
                    ValueError):
                continue

    return sims, lins


if __name__ == '__main__':
    # Test the contents of this file.

    import os
    import doctest

    if os.path.isdir('examples'):
        doctest.testmod(raise_on_error=True)
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
