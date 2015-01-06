#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011, C0301
"""Classes and functions to set up and run Modelica_ simulation experiments

The basic approach is to initiate a simulator and iterate over a `design of
experiments (DOE)`_. For example,

.. code-block:: python

   >>> from modelicares.exps.simulators import dymola_script
   >>> from modelicares.exps.doe import fullfact # Full-factorial DOE

   >>> with dymola_script() as simulator: # doctest: +SKIP
   ...     for params in fullfact({'C1.C': [8, 10], 'L.L': [18, 20]}):
   ...         simulator.run("Modelica.Electrical.Analog.Examples.ChuaCircuit", params)

This generates a Dymola\ :sup:`®`-formatted script (\*.mos) to simulate the
following:

===== ==================================================================
Run # Model & parameters
===== ==================================================================
1     Modelica.Electrical.Analog.Examples.ChuaCircuit(C1(C=8), L(L=18))
2     Modelica.Electrical.Analog.Examples.ChuaCircuit(C1(C=10), L(L=18))
3     Modelica.Electrical.Analog.Examples.ChuaCircuit(C1(C=8), L(L=20))
4     Modelica.Electrical.Analog.Examples.ChuaCircuit(C1(C=10), L(L=20))
===== ==================================================================

Please see the documentation of the items below for more examples, details, and
options.

**Functions:**

- :func:`read_options` - Read simulation options from a
  Dymola\ :sup:`®`-formatted initialization or final values file.

- :func:`read_params` - Read parameter values from a Dymola\ :sup:`®`-formatted
  initialization or final values file.

- :func:`write_options` - Write simulation options to a
  Dymola\ :sup:`®`-formatted initialization file.

- :func:`write_params` - Write model parameters and initial values to a
  Dymola\ :sup:`®`-formatted initialization file.

**Submodules:**

- :mod:`~modelicares.exps.doe` - Functions for the `design of experiments
  (DOE)`_

- :mod:`~modelicares.exps.simulators` - Context managers to be used as
  simulators


.. _Modelica: http://www.modelica.org/
.. _design of experiments (DOE): http://en.wikipedia.org/wiki/Design_of_experiments
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=I0011, C0103, E1101, W0102

import os
import re
import numpy as np

from six import string_types
from ..util import flatten_dict, read_values, write_values

# Some regular subexpressions
U = r'\d+'  # Unsigned integer
I = '[+-]?' + U  # Integer
F = I + r'(?:\.' + U + ')?(?:[Ee][+-]' + U + ')?'  # Float

def read_options(names, fname='dsin.txt'):
    """Read simulation options from a Dymola\ :sup:`®`-formatted initialization
    or final values file (e.g., dsin.txt or dsfinal.txt).

    **Parameters:**

    - *names*: Parameter name or list of names

    - *fname*: Name of the file (may include the file path)

    **Example:**

    >>> read_options('StopTime', 'examples/dsin.txt')
    1
    """
    PATTERNS = [
        # For Dymola experiment parameters, method tuning parameters, and output
        # parameters:
        r'^\s*({I})\s*#\s*%s\s'.format(I=I),
        r'^\s*({F})\s*#\s*%s\s'.format(F=F),
    ]
    return read_values(names, fname, PATTERNS)

def read_params(names, fname='dsin.txt'):
    """Read parameter values from a Dymola\ :sup:`®`-formatted initialization or
    final values file (e.g., dsin.txt or dsfinal.txt).

    **Parameters:**

    - *names*: Parameter name or list of names (with full model path in
      Modelica_ dot notation)

         A parameter name includes array indices (if any) in Modelica_
         representation (1-based indexing); the values are scalar.

    - *fname*: Name of the file (may include the file path)

    **Example:**

    >>> read_params(['Ti', 'Td'], 'examples/dsin.txt')
    [0.5, 0.1]
    """

    PATTERNS = [
        # For Dymola 1- or 2-line parameter specification:
        r'^\s*{I}\s+({F})\s+{F}\s+{F}\s+{U}\s+{U}\s*#\s*%s\s*$'.format(I=I, F=F,
                                                                       U=U),
        # From Dymola:
        # column 1: Type of initial value
        #           = -2: special case: for continuing simulation
        #                               (column 2 = value)
        #           = -1: fixed value   (column 2 = fixed value)
        #           =  0: free value, i.e., no restriction
        #                               (column 2 = initial value)
        #           >  0: desired value (column 1 = weight for
        #                                           optimization
        #                                column 2 = desired value)
        #                 use weight=1, since automatic scaling usually
        #                 leads to equally weighted terms
        # column 2: fixed, free or desired value according to column 1.
        # column 3: Minimum value (ignored, if Minimum >= Maximum).
        # column 4: Maximum value (ignored, if Minimum >= Maximum).
        #           Minimum and maximum restrict the search range in
        #           initial value calculation. They might also be used
        #           for scaling.
        # column 5: Category of variable.
        #           = 1: parameter.
        #           = 2: state.
        #           = 3: state derivative.
        #           = 4: output.
        #           = 5: input.
        #           = 6: auxiliary variable.
        # column 6: Data type of variable.
        #           = 0: real.
        #           = 1: boolean.
        #           = 2: integer.
    ]
    return read_values(names, fname, PATTERNS)

def write_options(options, fname='dsin.txt'):
    """Write simulation options to a Dymola\ :sup:`®`-formatted initialization
    file (e.g., dsin.txt).

    The options include those listed as "Experiment parameters", "Method tuning
    parameters", and "Output parameters" in the initialization file.  To write
    model parameters or variables with tunable initial values, use
    :func:`write_params`.

    **Parameters:**

    - *options*: Dictionary of simulation options

         Each key is a name of an option and each entry its value.

    - *fname*: Name of the file (may include the file path)

    **Example:**

    >>> write_options(dict(StopTime=1000), 'examples/dsin.txt')

    .. testcleanup::

       >>> write_options(dict(StopTime=1), 'examples/dsin.txt')

    This updates the appropriate line in *examples/dsin.txt*:

    .. code-block:: python

       1000                # StopTime     Time at which integration stops
    """
    PATTERNS = [
        # For Dymola experiment parameters, method tuning parameters, and output
        # parameters:
        r'(^\s*)' + I + r'(\s*#\s*%s\s)',
        r'(^\s*)' + F + r'(\s*#\s*%s\s)',
    ]
    write_values(options, fname, PATTERNS)

def write_params(params, fname='dsin.txt'):
    """Write model parameters and initial values to a Dymola\ :sup:`®`-formatted
    initialization file (e.g., dsin.txt).

    To write simulation options instead, use :func:`write_options`.

    **Parameters:**

    - *params*: Dictionary of model parameters or variables with tunable initial
      values

         Each key is a parameter or variable name (including the full model path
         in Modelica_ dot notation) and each entry is a value.  The name
         includes array indices (if any) in Modelica_ representation (1-based
         indexing).  The values must be representable as scalar numbers (integer
         or floating point).  *True* and *False* (not 'true' and 'false') are
         automatically mapped to 1 and 0.  Enumerations must be given explicitly
         as the unsigned integer equivalent.  Strings, functions,
         redeclarations, etc. are not supported.

    - *fname*: Name of the file (may include the file path)

    **Example:**

    >>> write_params(dict(Ti=5, Td=1), 'examples/dsin.txt')

    .. testcleanup::

       >>> write_params(dict(Ti=0.5, Td=0.1), 'examples/dsin.txt')

    This updates the appropriate lines in *examples/dsin.txt*:

    .. code-block:: python

       -1      5 ...
        ...   # Ti
       -1      1 ...
        ...   # Td
    """
    # Pre-process the values.
    params = flatten_dict(params)
    for key, value in params.items():
        if isinstance(value, bool):
            params[key] = 1 if value else 0
        assert not isinstance(value, np.ndarray), (
            "Arrays must be split into scalars for the simulation "
            "initialization file.")
        assert not isinstance(value, string_types), (
            "Strings cannot be used as values in the simulation initialization "
            "file.")

    PATTERNS = [
        # For Dymola 1- or 2-line parameter specification:
        r'(^\s*{I}\s+)'.format(I=I) + F
                  + r'(\s+{F}\s+{F}\s+{U}\s+{U}\s*#\s*%s\s*$)'.format(F=F, U=U),
        # See read_params() for a description of the columns.
    ]
    write_values(params, fname, PATTERNS)

if __name__ == '__main__':
    # Test the contents of this file.

    import doctest

    if os.path.isdir('examples'):
        doctest.testmod()
    else:
        # Create a link to the examples folder.
        for example_dir in ['../examples', '../../examples']:
            if os.path.isdir(example_dir):
                break
        else:
            raise IOError("Could not find the examples folder.")
        try:
            # pylint: disable=I0011, W0631
            os.symlink(example_dir, 'examples')
        except AttributeError:
            raise AttributeError("This method of testing isn't supported in "
                                 "Windows.  Use runtests.py in the base "
                                 "folder.")

        # Test the docstrings in this file.
        doctest.testmod()

        # Remove the link.
        os.remove('examples')
