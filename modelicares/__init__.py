#!/usr/bin/python
"""Functions and classes to set up Modelica_ simulations and load, analyze, and
plot the results.

This module provides convenient access to the most important functions and
classes from its submodules.  These are:

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
__version__ = "0.11.x"

# Essential functions and classes
#
# These will be available directly from modelicares; others must be loaded from
# their submodules.
from modelicares.util import (add_arrows, add_hlines, add_vlines, ArrowLine,
    closeall, figure, load_csv, save, saveall, setup_subplots)
from modelicares.exps import (Experiment, gen_experiments, ParamDict,
    read_params, run_models, write_params, write_script, doe)
from modelicares.linres import LinRes
from modelicares.multi import multiload, multiplot, multibode, multinyquist
from modelicares.simres import SimRes
from modelicares.texunit import label_number, label_quantity, unit2tex


def load(fname, constants_only=False):
    """Load a single Modelica_ simulation or linearization result and return an
    instance of the appropriate class (:class:`~simres.SimRes` or
    :class:`~linres.LinRes`).

    **Arguments:**

    - *fname*: Name of the results file, including the path

    - *constants_only*: *True* to load only the variables from the first data
      matrix, if the result is from a simulation

    **Returns:** An instance of the appropriate class (:class:`~simres.SimRes`
    or :class:`~linres.LinRes`) or *None* if the file could not be loaded

    **Examples:**

    .. code-block:: python

        >>> sim = load('examples/ChuaCircuit')
        >>> sim # doctest: +ELLIPSIS
        SimRes('.../examples/ChuaCircuit.mat')

        >>> lin = load('examples/PID')
        >>> lin # doctest: +ELLIPSIS
        LinRes('.../examples/PID.mat')
    """
    try:
        return SimRes(fname, constants_only)
    except TypeError:
        try:
            return LinRes(fname)
        except TypeError:
            raise TypeError('"%s" does not appear to be a valid simulation '
                            'or linearization file.' % fname)


if __name__ == '__main__':
    """Test the contents of this module."""
    import doctest
    from modelicares import *
    from modelicares import _gui, _freqplot, _io


# TODO: clean up, enable tests.txt

    doctest.testmod(_io.ompy)
    exit()
    doctest.testmod(exps)
    doctest.testmod(_freqplot)
    doctest.testmod(_gui)
    doctest.testmod(linres)
    doctest.testmod(multi)
    doctest.testmod(simres)
    doctest.testmod(texunit)
    doctest.testmod(util)

    #doctest.testfile('tests.txt')
