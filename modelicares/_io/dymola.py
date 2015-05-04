#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""Classes and functions to read Dymola\ :sup:`®`-formatted binary (*.mat) and
text (*.txt) results

This format is also used by OpenModelica_ and by PyFMI_ via JModelica.org_.

Classes:

- :class:`Samples` - Specialized namedtuple to store the time and value
  information of a variable from Dymola\ :sup:`®`-formatted simulation results

Functions:

- :func:`read` - Read variables from a MATLAB\ :sup:`®` (*.mat) or text (*.txt)
  file with Dymola\ :sup:`®`-formatted results.

- :func:`readsim` - Load Dymola\ :sup:`®`-formatted simulation results.

- :func:`readlin` - Load Dymola\ :sup:`®`-formatted linearization results.

Errors are raised under the following conditions:

- **IOError**: The file cannot be accessed.

- **TypeError**: The file does not use the Dymola\ :sup:`®` format.

- **AssertionError**: The results are not of the expected type (simulation or
  linearization), the orientation of the data (normal or transposed) is unknown,
  or the format version is not supported.

- **KeyError**: An expected variable is missing.

- **IndexError**: A variable has the wrong shape.

The last three errors occur when the file uses the Dymola\ :sup:`®` format but
something else is wrong.


_OpenModelica: https://www.openmodelica.org/
_PyFMI: http://www.pyfmi.org/
_JModelica.org: http://www.jmodelica.org/
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
# pylint: disable=I0011, C0103, C0301

import numpy as np
import re

from collections import namedtuple
from control.matlab import ss
from itertools import count
from natu import core as nc
from natu import units as U
from natu.exponents import Exponents
from natu.units import s as second
from scipy.io import loadmat
from scipy.io.matlab.mio_utils import chars_to_strings
from six import PY2

#from .._display import default_display_units
from ..simres import Variable
from ..util import next_nonblank


class Samples(namedtuple('Samples', ['times', 'signed_values', 'negated'])):

   """Specialized namedtuple to store the time and value information of a
   variable from Dymola\ :sup:`®`-formatted simulation results

   The negated field indicates if the values should be negated upon access.  By
   keeping the sign separate, the same savings that Dymola\ :sup:`®` achieves in
   file size is achieved in active memory.  It stems from the fact that many
   Modelica_ variables have opposite sign due to flow balances.


   .. _Modelica: http://www.modelica.org/
   """
   @property
   def values(self):
       """The values of the variable
       """
       return -self.signed_values if self.negated else self.signed_values


if PY2:
    # For most strings (those besides the description), Unicode isn't
    # necessary.  Unicode support is less integrated in Python 2; Unicode
    # strings are a special case that are represented by u'...' (which is
    # distracting in the examples).  Therefore, in Python 2 we'll only use
    # Unicode for the description strings.
    def get_strings(str_arr):
        """Return a list of strings from a character array.

        Strip the whitespace from the right and return it to the character set
        it was saved in.
        """
        return [line.rstrip(' \0').encode('latin-1')
                for line in chars_to_strings(str_arr)]
        # The encode part undoes scipy.io.loadmat's decoding.
else:
    # In Python 3, literal strings are Unicode by default
    # (http://stackoverflow.com/questions/6812031/how-to-make-unicode-string-with-python3),
    # and we need to leave the strings decoded because encoded strings are bytes
    # objects.
    def get_strings(str_arr):
        """Return a list of strings from a character array.

        Strip the whitespace from the right and recode it as utf-8.
        """
        return [line.rstrip(' \0').encode('latin-1').decode('utf-8')
                for line in chars_to_strings(str_arr)]
        # Modelica encodes using utf-8 but scipy.io.loadmat decodes using
        # latin-1, thus the encode ... decode part.


def _apply_unit(number, unit):
    """Apply the value of a unit to a number (in place).
    """
    unit_value = nc.value(unit)
    if unit_value <> 1.0:
        # Apply the unit.
        number *= unit_value

def loadtxt(file_name, variable_names=None, skip_header=1):
    r"""Read variables from a  Dymola\ :sup:`®`-formatted text file (*.txt).

    **Parameters:**

    - *file_name*: Name of the results file, including the path and extension

    - *variable_names*: List of the names of the variables to read

         Any variable with a name not in this list will be skipped, possibly
         saving some processing time.  If *variable_names* is *None*, then all
         variables will be read.

     - *skip_header*: Number of lines to skip at the beginning of the file

    **Returns:**

    1. A dictionary of variable names and values
    """

    SPLIT_DEFINITION = re.compile('(\w*) *(\w*) *\( *(\d*) *, *(\d*) *\)').match
    PARSERS = {'char': lambda get, rows:
                   [get().rstrip() for row in rows],
               'float': lambda get, rows:
                   np.array([np.fromstring(get().split('#')[0], float, sep=' ')
                             for row in rows]).T,
               'int': lambda get, rows:
                   np.array([np.fromstring(get().split('#')[0], int, sep=' ')
                             for row in rows])}

    with open(file_name) as f:

        # Skip the header.
        for i in range(skip_header):
            f.next()

        # Collect the variables and values.
        data = {}
        while True:

            # Read and parse the next variable definition.
            try:
                line = next_nonblank(f)
            except StopIteration:
                break # End of file
            type_string, name, nrows, ncols = SPLIT_DEFINITION(line).groups()

            # Parse the variable's value, if it is selected
            rows = range(int(nrows))
            if variable_names is None or name in variable_names:
                try:
                    parse = PARSERS[type_string]
                except KeyError:
                    raise KeyError('Unknown variable type: ' + type_string)
                try:
                    data[name] = parse(f.next, rows)
                except StopIteration:
                    raise ValueError('Unexpected end of file')
            else:
                # Skip the current variable.
                for row in rows:
                    f.next()
    return data


def read(fname, constants_only=False):
    r"""Read variables from a MATLAB\ :sup:`®` (*.mat) or text file (*.txt) with
    Dymola\ :sup:`®`-formatted results.

    **Parameters:**

    - *fname*: Name of the results file, including the path and extension

         This may be from a simulation or a linearization.

    - *constants_only*: *True* to assume the result is from a simulation and
      read only the variables from the first data matrix

    **Returns:**

    1. A dictionary of variable names and values

    2. A list of strings from the lines of the 'Aclass' matrix
    """

    # Load the file.
    variable_names = ['Aclass', 'name', 'names', 'description', 'dataInfo',
                      'data', 'data_1'] if constants_only else None
    try:
        data = loadmat(fname, variable_names=variable_names,
                       chars_as_strings=False, appendmat=False)
        binary = True
    except ValueError:
        data = loadtxt(fname, variable_names=variable_names)
        binary = False
    except IOError:
        raise IOError('"{}" could not be opened.  '
                      'Check that it exists.'.format(fname))

    # Get the Aclass variable and transpose the data if necessary.
    try:
        Aclass = data.pop('Aclass')
    except KeyError:
        raise TypeError('"{}" does not appear to use the Dymola format.  '
                        'The "Aclass" variable is missing.'.format(fname))
    if binary:
        Aclass = get_strings(Aclass)

        # Determine if the data is transposed.
        try:
            transposed = Aclass[3] == 'binTrans'
        except IndexError:
            transposed = False
        else:
            assert transposed or Aclass[3] == 'binNormal', (
                'The orientation of the Dymola-formatted results is not '
                'recognized.  The third line of the "Aclass" variable is "%s", '
                'but it should be "binNormal" or "binTrans".' % Aclass[3])

        # Undo the transposition and convert character arrays to strings.
        for name, value in data.items():
            if value.dtype == '<U1':
                data[name] = get_strings(value.T if transposed else value)
            elif transposed:
                data[name] = value.T

    else:
        # In a text file, only the data_1, data_2, etc. matrices are transposed.
        for name, value in data.items():
            if name.startswith('data_'):
                data[name] = value.T

    return data, Aclass

def readsim(fname, constants_only=False):
    r"""Load Dymola\ :sup:`®`-formatted simulation results.

    **Parameters:**

    - *fname*: Name of the results file, including the path and extension

    - *constants_only*: *True* to read only the variables from the first data
      matrix

         The first data matrix typically contains all of the constants,
         parameters, and variables that don't vary.  If only that information is
         needed, it may save resources to set *constants_only* to *True*.

    **Returns:** A dictionary of variables (instances of
    :class:`~modelicares.simres.Variable`)

    **Example:**

    >>> variables = readsim('examples/ChuaCircuit.mat')
    >>> variables['L.v'].unit
    'V'
    """
    # This does the task of mfiles/traj/tload.m from the Dymola installation.

    def parse_description(description):
        """Parse a variable description string into description, unit, and
        displayUnit.

        If the display unit is not specified, use the unit instead.  Convert the
        unit into an :class:`natu.exponents.Exponents` instance.
        """
        description = description.rstrip(']')
        displayUnit = ''
        try:
            description, unit = description.rsplit('[', 1)
        except ValueError:
            unit = ''
        else:
            unit = unit.replace('.', '*').replace('Ohm', 'ohm')
            try:
                unit, displayUnit = unit.rsplit('|', 1)
            except ValueError:
                pass  # (displayUnit = None)
        description = description.rstrip()
        if PY2:
            description = description.decode('utf-8')

        return description, unit, displayUnit

    # Load the file.
    data, Aclass = read(fname, constants_only)

    # Check the type of results.
    if Aclass[0] == 'AlinearSystem':
        raise AssertionError(fname + " is a linearization result.  Use LinRes "
                             "instead.")
    assert Aclass[0] == 'Atrajectory', (fname + " isn't a simulation or "
                                        "linearization result.")

    # Process the name, description, parts of dataInfo, and data_i variables.
    # This section has been optimized for speed.  All time and value data
    # remains linked to the memory location where it is loaded by scipy.  The
    # negated variable is carried through so that copies aren't necessary.  If
    # changes are made to this code, be sure to compare the performance (e.g.,
    # using %timeit in IPython).
    version = Aclass[1]
    if version == '1.1':
        names = data['name']

        # Extract the trajectories.
        trajectories = []
        for i in count(1):
            try:
                trajectories.append(data['data_%i' % i])
            except KeyError:
                break # No more data sets
            else:
                value = _apply_unit(trajectories[-1][:, 0], second)

        # Create the variables.
        variables = []
        for name, description, [data_set, sign_col] \
            in zip(names, data['description'], data['dataInfo'][:, 0:2]):
            description, unit_str, display_unit = parse_description(description)
            negated = sign_col < 0
            traj = trajectories[data_set - 1]
            signed_values =  traj[:, (-sign_col if negated else sign_col) - 1]
            times = traj[:, 0]
            if unit_str == ':#(type=Integer)':
                variables.append(Variable(Samples(times,
                                                  signed_values.astype(int),
                                                  False),
                                          nc.Exponents(), '', description))
            elif unit_str == ':#(type=Boolean)':
                variables.append(Variable(Samples(times,
                                                  signed_values.astype(bool),
                                                  False),
                                          nc.Exponents(), '', description))
            else:
                try:
                    if unit_str.startswith(' '):
                        # The dimension is entered in Modelica as the unit.
                        dimension = nc.Exponents.fromstr(unit_str.lstrip())
                        if not display_unit:
                            display_unit = default_display_units.find(dimension)
                    else:
                        if not display_unit:
                            display_unit = unit_str
                        unit = U._units(**nc.Exponents.fromstr(unit_str))
                        try:
                            _apply_unit(signed_values, unit)
                        except TypeError or AttributeError:
                            # The unit is a LambdaUnit.
                            if negated:
                                signed_values = -signed_values
                                negated = False
                            get_value = np.vectorize(lambda n:
                                                     unit._toquantity(n)._value)
                            signed_values = get_value(signed_values)
                        dimension = nc.Exponents(nc.dimension(unit))
                    variables.append(Variable(Samples(times,
                                                      signed_values,
                                                      negated),
                                              dimension, display_unit, description))
                except AttributeError:
                    # Something went wrong parsing the units so add with default values
                    variables.append(Variable(Samples(times,
                                                      signed_values,
                                                      negated),
                                              '1', '/', description))
        variables = dict(zip(names, variables))

        # Time is from the last data set.
        #variables['Time'] = Variable(Samples(times, times, False),
        #                             nc.dimension(second), 's', 'Time')
        return variables

    elif version == '1.0':
        traj = data['data']
        times = traj[:, 0]*value(second)
        return {name:
                Variable(Samples(times, traj[:, i], False), None, None, '')
                for i, name in enumerate(data['names'])}

    raise AssertionError("The version of the Dymola-formatted result file (%s) "
                         "isn't supported.")

       # TODOunit: assert these equal to natu (values and dimensions):
       #            'unitSystem.R_inf', 'unitSystem.c',
       #            'unitSystem.k_J', 'unitSystem.R_K',
       #            'unitSystem.k_F', 'unitSystem.R',
       #            'unitSystem.k_Aprime'

def readlin(fname):
    r"""Load Dymola\ :sup:`®`-formatted linearization results.

    **Parameters:**

    - *fname*: Name of the results file, including the path and extension

    **Returns:**

    - An instance of :class:`control.StateSpace`, which contains:

         - *A*, *B*, *C*, *D*: Matrices of the linear system

              .. code-block:: modelica

                 der(x) = A*x + B*u;
                      y = C*x + D*u;

         - *state_names*: List of names of the states (*x*)

         - *input_names*: List of names of the inputs (*u*)

         - *output_names*: List of names of the outputs (*y*)

    **Example:**

    >>> sys = readlin('examples/PID.mat')
    >>> sys.state_names
    ['I.y', 'D.x']
    """
    # This does the task of mfiles/traj/tloadlin.m in the Dymola installation.

    # pylint: disable=I0011, W0621

    # Load the file.
    data, Aclass = read(fname)

    # Check the type of results.
    if Aclass[0] == 'Atrajectory':
        raise AssertionError(fname + " is a simulation result.  Use SimRes "
                             "instead.")
    assert Aclass[0] == 'AlinearSystem', (fname + " isn't a simulation or "
                                          "linearization result.")

    # Determine the number of states, inputs, and outputs.
    ABCD = data['ABCD']
    nx = data['nx'][0]
    nu = ABCD.shape[1] - nx
    ny = ABCD.shape[0] - nx

    # Extract the system matrices.
    A = ABCD[:nx, :nx] if nx > 0 else [[]]
    B = ABCD[:nx, nx:] if nx > 0 and nu > 0 else [[]]
    C = ABCD[nx:, :nx] if nx > 0 and ny > 0 else [[]]
    D = ABCD[nx:, nx:] if nu > 0 and ny > 0 else [[]]
    sys = ss(A, B, C, D)

    # Extract the variable names.
    xuyName = data['xuyName']
    sys.state_names = xuyName[:nx]
    sys.input_names = xuyName[nx:nx + nu]
    sys.output_names = xuyName[nx + nu:]

    return sys


if __name__ == '__main__':
    # Test the contents of this file.

    # pylint: disable=I0011, W0631

    import os
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
            os.symlink(example_dir, 'examples')
        except AttributeError:
            raise AttributeError("This method of testing isn't supported in "
                                 "Windows.  Use runtests.py in the base "
                                 "folder.")

        # Test the docstrings in this file.
        doctest.testmod()

        # Remove the link.
        os.remove('examples')
