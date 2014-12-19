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

**Classes:**

- :class:`ParamDict` - Dictionary that prints its items as nested tuple-based
  modifiers, formatted for Modelica_

**Functions:**

- :func:`read_params` - Read parameter values from a Dymola\ :sup:`®`-formatted
  initialization or final values file.

- :func:`write_params` - Write parameter values to a Dymola\ :sup:`®`-formatted
  initialization file.

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
from ..util import modelica_str


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
    # Some regular subexpressions
    u = r'\d+'  # Unsigned integer
    i = '[+-]?' + u  # Integer
    f = i + r'(?:\.' + u + ')?(?:[Ee][+-]?' + u + ')?'  # Float

    # Possible regular expressions for a parameter specification (with '%s' for
    # the parameter name and parentheses around the value)
    patterns = [
        # For Dymola 1- or 2-line parameter specification:
        r'^\s*{i}\s+({f})\s+{f}\s+{f}\s+{u}\s+{u}\s*#\s*%s\s*$'.format(i=i, f=f,
                                                                       u=u),
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

        # For Dymola experiment parameters, method tuning parameters, and output
        # parameters:
        r'^\s*({i})\s*#\s*%s\s'.format(i=i),
        r'^\s*({f})\s*#\s*%s\s'.format(f=f),
    ]
    # These are tried in order until there's a match.

    # Read the file.
    with open(fname, 'r') as src:
        text = src.read()

    # Read the parameters.
    def _read_param(name):
        """Read a single parameter.
        """
        namere = re.escape(name)  # Escape the dots, square brackets, etc.
        for pattern in patterns:
            try:
                return float(re.search(pattern % namere, text,
                                       re.MULTILINE).group(1))
            except AttributeError:
                pass  # Try the next pattern.
        else:
            # pylint: disable=I0011, W0120
            raise AssertionError(
                "Parameter %s does not exist or is not formatted as expected "
                "in %s." % (name, fname))

    if isinstance(names, string_types):
        return _read_param(names)
    else:
        return map(_read_param, names)


def write_params(params, fname='dsin.txt'):
    """Write parameter values to a Dymola\ :sup:`®`-formatted initialization
    file (e.g., dsin.txt).

    **Parameters:**

    - *params*: Dictionary of parameters

         Each key is a parameter name (including the full model path in
         Modelica_ dot notation) and each entry is a parameter value.  The
         parameter name includes array indices (if any) in Modelica_
         representation (1-based indexing).  The values must be representable
         as scalar numbers (integer or floating point).  *True* and *False*
         (not 'true' and 'false') are automatically mapped to 1 and 0.
         Enumerations must be given explicitly as the unsigned integer
         equivalent.  Strings, functions, redeclarations, etc. are not
         supported.

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
    for key, value in params.items():
        if isinstance(value, bool):
            params[key] = 1 if value else 0
        assert not isinstance(value, np.ndarray), (
            "Arrays must be split into scalars for the simulation "
            "initialization file.")
        assert not isinstance(value, string_types), (
            "Strings cannot be used as values in the simulation initialization "
            "file.")

    # Some regular subexpressions
    u = r'\d+'  # Unsigned integer
    i = '[+-]?' + u  # Integer
    f = i + r'(?:\.' + u + ')?(?:[Ee][+-]' + u + ')?'  # Float

    # Possible regular expressions for a parameter specification (with '%s' for
    # the parameter name and two pairs of parentheses: around everything before
    # the value and around everything after the value)
    patterns = [
        # For Dymola 1- or 2-line parameter specification:
        r'(^\s*{i}\s+)'.format(i=i) + f
                  + r'(\s+{f}\s+{f}\s+{u}\s+{u}\s*#\s*%s\s*$)'.format(f=f, u=u),
        # See read_params() for a description of the columns.

        # For Dymola experiment parameters, method tuning parameters, and output
        # parameters:
        r'(^\s*)' + i + r'(\s*#\s*%s\s)',
        r'(^\s*)' + f + r'(\s*#\s*%s\s)',
    ]
    # These are tried in order until there's a match.

    # Read the file.
    with open(fname, 'r') as src:
        text = src.read()

    # Set the parameters.
    for name, value in params.items():
        namere = re.escape(name) # Escape the dots, square brackets, etc.
        for pattern in patterns:
            text, num = re.subn(pattern % namere, r'\g<1>%s\2' % value, text, 1,
                                re.MULTILINE)
            if num: # Found a match
                break
        else:
            raise AssertionError(
                "Parameter %s does not exist or is not formatted as expected "
                "in %s." % (name, fname))

    # Re-write the file.
    with open(fname, 'w') as src:
        src.write(text)


class ParamDict(dict):

    """Dictionary that prints its items as nested tuple-based modifiers,
    formatted for Modelica_

    Otherwise, this class is the same as :class:`dict`.  The underlying
    structure is not nested or reformatted---only the string mapping
    (:meth:`__str__`).

    In the string mapping, each key is interpreted as a parameter name
    (including the full model path in Modelica_ dot notation) and each entry is
    a parameter value.  The value may be a number (:class:`int` or
    :class:`float`), Boolean constant (in Python_ format---*True* or *False*,
    not 'true' or 'false'), string, or NumPy_ arrays of these.  Modelica_
    strings must be given with double quotes included (e.g., '"hello"').
    Enumerations may be used as values (e.g., 'Axis.x').  Values may be
    functions or modified classes, but the entire value must be expressed as a
    Python_ string (e.g., 'fill(true, 2, 2)').  Items with a value of *None* are
    not shown.

    Redeclarations and other prefixes must be included in the key along with the
    name of the instance (e.g., 'redeclare Region regions[n_x, n_y, n_z]').  The
    single quotes must be explicitly included for instance names that contain
    symbols (e.g., "'H+'").

    Note that Python_ dictionaries do not preserve order.  The keys are printed
    in alphabetical order.

    **Examples:**

    .. code-block:: python

       >>> import numpy as np

       >>> d = ParamDict({'a': 1, 'b.c': np.array([2, 3]), 'b.d': False,
       ...                'b.e': '"hello"', 'b.f': None})
       >>> print(d)
       (a=1, b(c={2, 3}, d=false, e="hello"))

    The internal structure and formal representation (:meth:`__repr__`) is not
    affected:

    >>> d # doctest: +SKIP
    {'a': 1, 'b.c': array([2, 3]), 'b.d': False, 'b.e': '"hello"', 'b.f': None}

    An empty dictionary prints as an empty string (not "()"):

    >>> print(ParamDict({}))
    <BLANKLINE>


    .. _Python: http://www.python.org/
    .. _NumPy: http://numpy.scipy.org/
    """

    def __str__(self):
        """Map the :class:`ParamDict` instance to a string using tuple-based
        modifiers formatted for Modelica_.
        """
        def _str(dictionary):
            """Return a string representation of a dictionary in the form of
            tuple-based modifiers (e.g., (a=1, b(c={2, 3}, d=false))).

            Substitutions are made to properly represent Boolean variables and
            arrays in Modelica_.
            """
            elements = []
            for key, value in sorted(dictionary.items()):
                if isinstance(value, ParamDict):
                    elements.append('%s%s' % (key, value)) # Recursive
                elif isinstance(value, dict):
                    elements.append('%s%s' % (key, ParamDict(value))) # Ditto
                elif value is not None:
                    value = modelica_str(value)
                    elements.append(key + '=' + value)
            return '(%s)' % ', '.join(elements) if elements else ''

        # This method to build a nested dictionary adapted from DyMat version
        # 0.5 (Joerg Raedler,
        # http://www.j-raedler.de/2011/09/dymat-reading-modelica-results-with-python/,
        # BSD License).
        root = ParamDict()
        for name in self.keys():
            branch = root
            elements = name.split('.')
            for element in elements[:-1]:
                if element not in branch:
                    branch[element] = ParamDict()
                branch = branch[element]
            branch[elements[-1]] = self.__getitem__(name)

        return _str(root)


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
