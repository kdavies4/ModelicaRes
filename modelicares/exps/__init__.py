#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011, C0301
"""Set up and help run Modelica_ simulation experiments.

This module supports two approaches to managing simulations.  The first is to
create a Dymola\ :sup:`®`-formatted script (\*.mos, using :func:`write_script`)
and run it with a compatible tool to translate and simulate the models with the prescribed settings (see the scripts in *examples/ChuaCircuit/*).  The second
approach is to run models that have been translated to executables or
Functional Mock-up Units (FMUs_). The :func:`run_models` method
handles this by writing to initialization file(s) (e.g, *dsin.txt*) and
launching the appropriate model executables.  The advantage of the first
approach is that formal parameters (those that are hard-coded during
translation) can be adjusted.  However, the second approach is faster because it
does not require a model to be recompiled when only tunable parameters (those
that are not hard-coded during translation) are changed.

The first step in either case is to create a dictionary to specify model
parameters and other settings for simulation experiment.  A single model
parameter may have multiple possible values.  The dictionary is passed to
:func:`gen_experiments`, which combines the values of all the variables (by
piecewise alignment or permutation) and returns a generator to step through the
experiments.  Finally, the generator is passed to :func:`write_script` or
:func:`run_models`.

**Classes:**

- :class:`ParamDict` - Dictionary that prints its items as nested tuple-based
  modifiers, formatted for Modelica_

- :class:`Experiment` - namedtuple_ to represent a simulation experiment

**Functions:**

- :func:`gen_experiments` - Return a generator for a set of simulation
  experiments using permutation or simple element-wise grouping.

- :func:`read_params` - Read parameter values from an initialization or final
  values file.

- :func:`write_params` - Write parameter values to a simulation initialization
  file.

**Submodules:**

- :mod:`~modelicares.exps.doe` - Functions for design of experiments (DOE)


.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _NumPy: http://numpy.scipy.org/
.. _FMUs: https://www.fmi-standard.org/
.. _namedtuple: https://docs.python.org/2/library/collections.html#collections.namedtuple
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

from collections import namedtuple
from six import string_types

from ..util import modelica_str, flatten_dict
from . import doe


class Experiment(namedtuple('Experiment', ['model', 'params', 'options'])):

    """namedtuple_ to represent a simulation experiment

    Instances of this class may be used in the *experiments* argument of
    :func:`write_script` and :func:`run_models`, although there are some
    differences in the entries (see those functions for details).

    **Example:**

    >>> experiment = Experiment('ChuaCircuit', params={'L.L': 18}, options={})
    >>> experiment.model
    'ChuaCircuit'
    """
    pass


class Experiments(object):

    """**
    """

    def __init__(models=None, params={}, options={}, design=doe.fullfact):
        """Return a generator for a set of simulation experiments using
        permutation or simple element-wise grouping.

        The generator yields instances of :class:`Experiment`---named tuples of
        (*model*, *params*, *options*), where *model* is the name of a single
        model (type :class:`str`), *params* is a specialized dictionary
        (:class:`ParamDict`) of model parameter names and values, and *options*
        is a dictionary (:class:`dict`) of command arguments (keyword and value)
        for the Modelica_ tool or environment.

        **Parameters:**

        - *models*: List of model names (including the full model path in
          Modelica_ dot notation)

        - *params*: Dictionary of model parameters

             Each key is a variable name and each entry is a list of values.
             The keys must indicate the hierarchy within the model---either in
             Modelica_ dot notation or via nested dictionaries.

        - *options*: Dictionary of command arguments for the Modelica_ tool or
          environment (e.g., to the :func:`simulateModel` command in Dymola)

             Each key is an argument name and each entry is a list of settings.

        - *design*: Method of generating the simulation experiments (i.e.,
          design of experiments)

             This is a function that returns a iterable object that contains or
             generates the simulation settings.  Several options are available
             in :mod:`~modelicares.exps.doe`.

        **Example 1 (element-wise list of experiments):**

        >>> experiments = gen_experiments(
        ...               ['Modelica.Electrical.Analog.Examples.ChuaCircuit']*3,
        ...               {'L.L': [16, 18, 20], 'C2.C': [80, 100, 120]},
        ...               design=doe.aslisted)
        >>> for experiment in experiments: # doctest: +SKIP
        ...     print(experiment.model + str(experiment.params))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=80), L(L=16))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=100), L(L=18))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=120), L(L=20))
        >>> # Note that the model name must be repeated in the models argument.

        **Example 2 (one-factor-at-a-time; first entries are baseline):**

        >>> experiments = gen_experiments(
        ...                 ['Modelica.Electrical.Analog.Examples.ChuaCircuit'],
        ...                 {'L.L': [16, 18, 20], 'C2.C': [80, 100, 120]},
        ...                 design=doe.ofat)
        >>> for experiment in experiments: # doctest: +SKIP
        ...     print(experiment.model + str(experiment.params))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=80), L(L=16))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=80), L(L=18))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=80), L(L=20))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=100), L(L=16))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=120), L(L=16))

        **Example 3 (permutation---full-factorial design of experiments):**

        >>> experiments = gen_experiments(
        ...                 ['Modelica.Electrical.Analog.Examples.ChuaCircuit'],
        ...                 {'L.L': [16, 18, 20], 'C2.C': [80, 100, 120]},
        ...                 design=doe.fullfact)
        >>> for experiment in experiments: # doctest: +SKIP
        ...     print(experiment.model + str(experiment.params))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=80), L(L=16))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=100), L(L=16))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=120), L(L=16))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=80), L(L=18))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=100), L(L=18))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=120), L(L=18))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=80), L(L=20))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=100), L(L=20))
        Modelica.Electrical.Analog.Examples.ChuaCircuit(C2(C=120), L(L=20))

        **Example 4 (parameters given in nested form):**

        >>> models = ['Modelica.Mechanics.MultiBody.Examples.Systems.RobotR3.oneAxis']
        >>> params = dict(axis=dict(motor=dict(i_max=[5, 15],
        ...                                    Ra=dict(R=[200, 300]))))
        >>> for experiment in gen_experiments(models, params):
        ...     print(experiment.model + str(experiment.params)) # doctest: +SKIP
        Modelica.Mechanics.MultiBody.Examples.Systems.RobotR3.oneAxis(axis(motor(i_max=5, Ra(R=200))))
        Modelica.Mechanics.MultiBody.Examples.Systems.RobotR3.oneAxis(axis(motor(i_max=15, Ra(R=200))))
        Modelica.Mechanics.MultiBody.Examples.Systems.RobotR3.oneAxis(axis(motor(i_max=5, Ra(R=300))))
        Modelica.Mechanics.MultiBody.Examples.Systems.RobotR3.oneAxis(axis(motor(i_max=15, Ra(R=300))))

        Note that the underlying representation of the parameters is actually
        flat:

        >>> for experiment in gen_experiments(models, params): # doctest: +SKIP
        ...     experiment.params
        {'axis.motor.Ra.R': 200, 'axis.motor.i_max': 5}
        {'axis.motor.Ra.R': 200, 'axis.motor.i_max': 15}
        {'axis.motor.Ra.R': 300, 'axis.motor.i_max': 5}
        {'axis.motor.Ra.R': 300, 'axis.motor.i_max': 15}

        Also note that Python dictionaries do not preserve order (and it is not
        necessary here).
        """
        params = flatten_dict(params) # TODO this is last usage of flatten_dict
        i_options = len(params) + 1
        experiment = lambda x: Experiment(model=x[0],
                                          params=ParamDict(zip(params.keys(),
                                                               x[1:i_options])),
                                          options=dict(zip(options.keys(),
                                                           x[i_options:])))
        try:
            return (experiment(x) for x in
                    design(*([models] + list(params.values())
                             + list(options.values()))))
        except TypeError:
            print("Error in call to gen_experiments(): models and all of the "
                  "entries in params and options must be lists.")


def read_params(names, fname='dsin.txt'):
    """Read parameter values from an initialization or final values file (e.g.,
    dsin.txt or dsfinal.txt).

    **Parameters:**

    - *names*: Parameter name or list of names (with full model path in
      Modelica_ dot notation)

         A parameter name includes array indices (if any) in Modelica_
         representation (1-based indexing); the values are scalar.

    - *fname*: Name of the file (may include the file path)

    **Example:**

    >>> read_params(['Td', 'Ti'], 'examples/dsin.txt')
    [0.1, 0.5]
    """
    # Aliases for some regular subexpressions
    u = r'\d+'  # Unsigned integer
    i = '[+-]?' + u  # Integer
    f = i + r'(?:\.' + u + ')?(?:[Ee][+-]?' + u + ')?'  # Floating point number

    # Possible regular expressions for a parameter specification (with '%s' for
    # the parameter name)
    patterns = [  # Dymola 1- or 2-line parameter specification
        (r'^\s*%s\s+(%s)\s+%s\s+%s\s+%s\s+%s\s*#\s*%s\s*$'
         % (i, f, f, f, u, u, '%s')),
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
    # These are tried in order until there is a match.  The group or pair of
    # parentheses contains the parameter value.

    # Read the file.
    with open(fname, 'r') as src:
        text = src.read()

    # Read the parameters.
    def _read_param(name):
        """Read a single parameter"""
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
        return [_read_param(name) for name in names]


def write_params(params, fname='dsin.txt'):
    """Write parameter values to a simulation initialization file (e.g.,
    dsin.txt).

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

    >>> write_params({'Td': 1, 'Ti': 5}, 'examples/dsin.txt')

    .. testcleanup::

       >>> write_params({'Td': 0.1, 'Ti': 0.5}, 'examples/dsin.txt')

    This updates the appropriate lines in *examples/dsin.txt*:

    .. code-block:: modelica

       -1      10                  0       0                  1  280   # L.L
       ...
       -1      15                  0  1.000000000000000E+100  1  280   # C1.C
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

    # Aliases for some regular subexpressions
    u = r'\d+'  # Unsigned integer
    i = '[+-]?' + u  # Integer
    f = i + r'(?:\.' + u + ')?(?:[Ee][+-]' + u + ')?'  # Floating point number

    # Possible regular expressions for a parameter specification (with '%s' for
    # the parameter name)
    patterns = [  # Dymola 1- or 2-line parameter specification
        (r'(^\s*%s\s+)%s(\s+%s\s+%s\s+%s\s+%s\s*#\s*%s\s*$)'
         % (i, f, f, f, u, u, '%s')),
        r'(^\s*)' + i + r'(\s*#\s*%s)',
        r'(^\s*)' + f + r'(\s*#\s*%s)',
        # See read_params() for a description of the columns.
    ]
    # These are tried in order until there is a match.  The first group or pair
    # of parentheses contains the text before the parameter value and the
    # second contains the text after it (minus one space on both sides for
    # clarity).

    # Read the file.
    with open(fname, 'r') as src:
        text = src.read()

    # Set the parameters.
    for name, value in params.items():
        namere = re.escape(name)  # Escape the dots, square brackets, etc.
        for pattern in patterns:
            text, num = re.subn(pattern % namere, r'\g<1>%s\2' % value, text, 1,
                                re.MULTILINE)
            if num == 1:
                break
        else:
            raise AssertionError(
                "Parameter %s does not exist or is not formatted as expected "
                "in %s." % (name, fname))

    # Re-write the file.
    with open(fname, 'w') as src:
        src.write(text)


class ParamDict(dict):

    """Dictionary that prints its items (string mapping) as nested tuple-based
    modifiers, formatted for Modelica_

    Otherwise, this class is the same as :class:`dict`.  The underlying
    structure is not nested or reformatted---only the informal representation
    (:meth:`__str__`).

    In printing this dictionary (string representation), each key is interpreted
    as a parameter name (including the full model path in Modelica_ dot
    notation) and each entry is a parameter value.  The value may be a number
    (integer or float), Boolean constant (in Python_ format---*True* or *False*,
    not 'true' or 'false'), string, or NumPy_ arrays of these.  Modelica_
    strings must be given with double quotes included (e.g., '"hello"').
    Enumerations may be used as values (e.g., 'Axis.x').  Values may include
    functions, but the entire value must be expressed as a Python_ string (e.g.,
    'fill(true, 2, 2)').  Items with a value of *None* are not shown.

    Redeclarations and other prefixes must be included in the key along with the
    name of the instance (e.g., 'redeclare Region regions[n_x, n_y, n_z]').  The
    single quotes must be explicitly included for instance names that contain
    symbols (e.g., "'H+'").

    Note that Python_ dictionaries do not preserve order.

    **Examples:**

    .. code-block:: python

       >>> import numpy as np

       >>> d = ParamDict({'a': 1, 'b.c': np.array([2, 3]), 'b.d': False,
       ...                'b.e': '"hello"', 'b.f': None})
       >>> print(d) # doctest: +SKIP
       (a=1, b(c={2, 3}, e="hello", d=false))

    The formal representation (and the internal structure) is not affected:

    >>> d # doctest: +SKIP
    {'a': 1, 'b.c': array([2, 3]), 'b.f': None, 'b.e': '"hello"', 'b.d': False}

    An empty dictionary prints as an empty string (not "()"):

    >>> print(ParamDict({}))
    <BLANKLINE>
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
