#!/usr/bin/python
"""Set up Modelica_ simulations and load, analyze, and plot the results.

This module provides direct access to the most important functions and classes
from its submodules.  These are:

- Basic supporting classes and functions (:mod:`~modelicares.base` module):
  :meth:`~base.add_arrows`, :meth:`~base.add_hlines`, :meth:`~base.add_vlines`,
  :meth:`~base.animate`, :class:`~base.ArrowLine`, :meth:`~base.closeall`,
  :meth:`~base.figure`, :meth:`~base.load_csv`, :meth:`~base.save`,
  :meth:`~base.saveall`, and :meth:`~base.setup_subplots`

- To manage simulation experiments (:mod:`~modelicares.exps` module):
  :class:`~exps.Experiment`, :mod:`~modelicares.exps.doe`, :meth:`~exps.gen_experiments`,
  :class:`~exps.ParamDict`, :meth:`~exps.read_params`, :meth:`~exps.run_models`,
  :meth:`~exps.write_params`, and :meth:`~exps.write_script`

- To handle multiple files at once (:mod:`~modelicares.multi` module):
  :meth:`~multi.multiload`, :meth:`~multi.multiplot`, :meth:`~multi.multibode`,
  and :meth:`~multi.multinyquist`

- For simulation results (:mod:`~modelicares.simres` module):
  :class:`~simres.SimRes`

- For linearization results (:mod:`~modelicares.linres` module):
  :class:`~linres.LinRes`

- To label numbers and quantities (:mod:`~modelicares.texunit` module):
  :meth:`~texunit.label_number`, :meth:`~texunit.label_quantity`, and
  :meth:`~texunit.unit2tex`

.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"
__version__ = "0.10.0"


import sys


# Check the Python version.
major, minor1, minor2, s, tmp = sys.version_info
#if not (major == 2 and minor1 == 7):
#    raise ImportError('Currently, modelicares requires Python 2.7.')
# TODO:  Add support for Python 3.x once wx supports it.


# All functions and classes
#__all__ = ['base', 'exps', 'linres', 'multi', 'simres', 'texunit']


# Essential functions and classes
#
# These will be available directly from modelicares; others must be loaded from
# their submodules.
from modelicares.base import (add_arrows, add_hlines, add_vlines, animate, ArrowLine, 
    closeall, figure, load_csv, save, saveall, setup_subplots)
from modelicares.exps import (Experiment, gen_experiments, ParamDict, read_params, 
    run_models, write_params, write_script, doe)
from modelicares.linres import LinRes
from modelicares.multi import multiload, multiplot, multibode, multinyquist
from modelicares.simres import SimRes
from modelicares.texunit import label_number, label_quantity, unit2tex
