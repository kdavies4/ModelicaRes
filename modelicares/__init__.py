#!/usr/bin/python
"""Functions and classes to set up Modelica_ simulations and load, analyze, and
plot the results.

This module provides convenient access to the most important functions and
classes from its submodules.  These are:

- To manage simulation experiments (:mod:`~modelicares.exps` module):
  :class:`~exps.Experiment`, :mod:`~modelicares.exps.doe`, :meth:`~exps.gen_experiments`,
  :class:`~exps.ParamDict`, :meth:`~exps.read_params`, :meth:`~exps.run_models`,
  :meth:`~exps.write_params`, and :meth:`~exps.write_script`

- For simulation results (:mod:`~modelicares.simres` module):
  :class:`~simres.SimRes`, :class:`~simres.SimResList`

- For linearization results (:mod:`~modelicares.linres` module):
  :class:`~linres.LinRes`, :class:`~linres.LinResList`

- To label numbers and quantities (:mod:`~modelicares.texunit` module):
  :meth:`~texunit.number_str`, :meth:`~texunit.quantity_str`, and
  :meth:`~texunit.unit2tex`

- Supporting classes and functions (:mod:`~modelicares.util` module):
  :meth:`~util.add_arrows`, :meth:`~util.add_hlines`, :meth:`~util.add_vlines`,
  :class:`~util.ArrowLine`, :meth:`~util.closeall`, :meth:`~util.figure`,
  :meth:`~util.load_csv`, :meth:`~util.save`, :meth:`~util.saveall`, and
  :meth:`~util.setup_subplots`

There is also one function defined here (see below).


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
    closeall, figure, load_csv, save, saveall, setup_subplots)
from modelicares.exps import (Experiment, gen_experiments, ParamDict,
    read_params, run_models, write_params, write_script, doe)
from modelicares.texunit import number_str, quantity_str, unit2tex


def load(locations='*'):
    """Load multiple Modelica_ simulation and/or linearization results.

    This function will load as many of the matching filenames as possible.  No
    errors will be given for files that cannot be loaded.

    **Arguments:**

    - *locations*: Filename, directory, or list of these from which to load the
      files

         Wildcards ('*') are accepted.

    **Returns:**

    1. List of simulations (:class:`simres.SimRes` instances)

    2. List of linearizations (:class:`linres.LinRes` instances)

    Either may be an empty list.

    **Example:**

    We can use this function in conjuction with methods from
    :class:`~modelicares.simres.Info` to conveniently retrieve information from
    multiple simulations.

    .. code-block:: python

       >>> from modelicares import multiload
       >>> from modelicares.simres import Info

       # Get the mean values of the first capacitor's voltage from two runs
       # of or the two
       >>> sims, __ = multiload('examples/ChuaCircuit/*/*.mat') # doctest: +ELLIPSIS
       >>> mean_C1_voltage = lambda sim: Info.mean(sim, 'C1.v')
       >>> map(mean_C1_voltage, sims)
       [0.76859528, 0.76859528]

       # The values are different because the inductance was set differently:
       >>> inductance = lambda sim: Info.IV(sim, 'L.L')
       >>> map(inductance, sims)
       [10, 18]
    """

    # Generate a list of files.
    fnames = []
    if isinstance(locations, basestring):
        locations = [locations]
    for location in locations:
        if os.path.isdir(location):
            fnames += glob(os.path.join(location, '*.mat'))
        else:
            if '*' in location or '?' in location or '[' in location:
                fnames += glob(location)
            else:
                fnames.append(location)

    # Load the files and append each result onto the appropriate list.
    sims = []
    lins = []
    for fname in fnames:
        try:
            sims.append(SimRes(fname))
        except (IOError, TypeError):
            continue
        except:
            lins.append(LinRes(fname))

    return sims, lins

if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
