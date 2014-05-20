#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classes and functions to load results from Dymola and OpenModelica

Classes:

- :class:`Variable` - Specialized namedtuple to represent a variable in a model
  simulated by Dymola or OpenModelica

- :class:`Samples` - Namedtuple to store the time and value information of
  each variable in the *samples* field of :class:`Variable`

Functions:

- :meth:`read` - Read variables from a MATLAB\ :sup:`®` file with
  Dymola\ :sup:`®` or OpenModelica results.

- :meth:`loadsim` - Load Dymola\ :sup:`®` or OpenModelica simulation results.

- :meth:`loadlin` - Load Dymola\ :sup:`®` or OpenModelica linearization results.

Errors are raised under the following conditions:

- **IOError**: The file cannot be accessed.

- **TypeError**: The file does not appear to be from Dymola or OpenModelica.

- **AssertionError**: The results are not of the expected type (simulation or
  linearization), the orientation of the data (normal or transposed) is
  unrecognized, or the format version is not supported.

- **KeyError**: An expected variable is missing.

- **IndexError**: A variable has the wrong shape.

The last three errors occur when the file does appear to be from Dymola or
OpenModelica but something else is wrong.
"""

import numpy as np
from collections import namedtuple
from itertools import count
from scipy.io import loadmat
from control.matlab import ss

from modelicares.simres import _VarDict, _select, _apply_function, _swap
from modelicares.simres import Variable as GenericVariable


# Namedtuple to store the time and value information of each variable
Samples = namedtuple('Samples', ['times', 'values', 'negated'])
# This is used for the *samples* field of Variable below.
# The negated field indicates if the values should be negated upon access.

# Named tuple to store the data for each variable
class Variable(GenericVariable):
    """Specialized namedtuple to represent a variable in a model simulated by
    Dymola or OpenModelica
    """

    @_swap           # We want the times (t) to be the first argument,
    @_apply_function # but for efficiency, it's best to
    @_select         # select the values first.
    def values(self):
        """Return function *f* of the values of the variable.

        **Arguments:**

        - *t*: Time index

             - Default or *None*: All samples are included.

             - *float*: Interpolate to a single time.

             - *list*: Interpolate to a list of times.

             - *tuple*: Extract samples from a range of times.  The structure is
               signature to the arguments of Python's slice_ function, except
               that the start and stop values can be floating point numbers.
               The samples within and up to the limits are included.
               Interpolation is not used.

                  - (*stop*,): All samples up to *stop* are included.

                       Be sure to include the comma to distinguish this from a
                       singleton.

                  - (*start*, *stop*): All samples between *start* and *stop*
                    are included.

                  - (*start*, *stop*, *skip*): Every *skip*th sample is included
                    between *start* and *stop*.

        - *f*: Function that operates on the vector of values (default or *None*
          is identity)
        """
        # The docstring has been copied from modelicares.simres.Variable.values.
        # Keep it updated there.
        return (-self.samples.values if self.samples.negated else
                self.samples.values)

    @_swap           # We want the times (t) to be the first argument,
    @_apply_function # but for efficiency, it's best to
    @_select         # select the values first.
    def times(self):
        """Return function *f* of the recorded times of the variable.

        **Arguments:**

        - *t*: Time index

             This may have any of the forms list in :meth:`values`, but the
             useful ones are:

             - Default or *None*: All times are included.

             - *tuple*: Extract recorded times from a range of times.  The
               structure is signature to the arguments of Python's slice_
               function, except that the start and stop values can be floating
               point numbers.  The times within and up to the limits are
               included.  Interpolation is not used.

                  - (*stop*,): All times up to *stop* are included.

                       Be sure to include the comma to distinguish this from a
                       singleton.

                  - (*start*, *stop*): All recorded times between *start* and
                    *stop* are included.

                  - (*start*, *stop*, *skip*): Every *skip*th recorded time is
                    included between *start* and *stop*.

        - *f*: Function that operates on the vector of recorded times (default
          or *None* is identity)
        """
        # The docstring has been copied from modelicares.simres.Variable.values.
        # Keep it updated there.
        return self.samples.times


def chars_to_str(str_arr):
    """Convert a string array to a string.

    Remove trailing whitespace and null characters.  Encode to ascii using
    latin-1, since that's how SciPy decodes the mat file.  Dymola only uses
    unicode for variable descriptions.
    """
    return ''.join(str_arr).rstrip().rstrip('\x00').encode('latin-1')


def read(fname, constants_only=False):
    """Read variables from a MATLAB\ :sup:`®` file with Dymola\ :sup:`®` or
    OpenModelica results.

    **Arguments:**

    - *fname*: Name of the results file, including the path

         This may be from a simulation or linearization.

    - *constants_only*: *True* to load only the variables from the first data
      matrix, if the result is from a simulation

    **Returns:**

    1. A dictionary of variables

    2. A list of strings from the lines of the 'Aclass' matrix
    """

    # Load the file.
    try:
        if constants_only:
            mat = loadmat(fname, chars_as_strings=False, appendmat=False,
                          variable_names=['Aclass', 'class', 'name', 'names',
                                          'description', 'dataInfo', 'data',
                                          'data_1', 'ABCD', 'nx', 'xuyName'])
        else:
            mat = loadmat(fname, chars_as_strings=False, appendmat=False)
    except IOError:
        raise IOError('"{f}" could not be opened.'
                      '  Check that it exists.'.format(f=fname))

    # Check if the file contains the Aclass variable.
    try:
        Aclass = mat['Aclass']
    except KeyError:
        raise TypeError('"{f}" does not appear to be a Dymola or OpenModelica '
                        'result file.  The "Aclass" variable is '
                        'missing.'.format(f=fname))

    return mat, [chars_to_str(line) for line in Aclass]


def loadsim(fname, constants_only=False):
    """Load Dymola\ :sup:`®` or OpenModelica simulation results.

    **Arguments:**

    - *fname*: Name of the results file, including the path

         The file extension ('.mat') is optional.

    - *constants_only*: *True* to load only the variables from the first data
      matrix

         The first data matrix usually contains all of the constants,
         parameters, and variables that don't vary.  If only that information is
         needed, it may save resources to set *constants_only* to *True*.

    **Returns:** An instance of :class:`~modelicares.simres._VarDict`, a
    specialized dictionary of variables (instances of :class:`Variable`)

    **Example:**

    .. code-block:: python

       >>> from modelicares._io.dymola import loadsim

       >>> variables = loadsim('examples/ChuaCircuit.mat')
       >>> variables['L.v'].unit
       'V'
    """
    # This does the task of mfiles/traj/tload.m from the Dymola installation.

    def parse(description):
        """Parse the variable description string into description, unit, and
        displayUnit.
        """
        description = chars_to_str(description).rstrip(']')
        displayUnit = ''
        try:
            description, unit = description.rsplit(' [', 1)
        except ValueError:
            unit = ''
        else:
            try:
                unit, displayUnit = unit.rsplit('|', 1)
            except ValueError:
                pass # (displayUnit = '')

        # Dymola uses utf-8 for descriptions.
        return description.decode('utf-8'), unit, displayUnit

    # Load the file.
    mat, Aclass = read(fname, constants_only)

    # Check the type of results.
    if Aclass[0] == 'AlinearSystem':
       raise AssertionError('"%s" is a linearization result.  Use LinRes '
                            'instead.' % fname)
    else:
       assert Aclass[0] == 'Atrajectory', ('File "%s" is not a simulation '
                                           'or linearization result.' % fname)

    # Determine if the data is transposed.
    try:
        transposed = Aclass[3] == 'binTrans'
    except IndexError:
        transposed = False
    else:
        assert transposed or Aclass[3] == 'binNormal', ('The orientation of '
            'the Dymola/OpenModelica results is not recognized.  The third '
            'line of the "Aclass" variable is "%s", but it should be '
            '"binNormal" or "binTrans".' % Aclass[3])

    # Get the format version.
    version = Aclass[1]

    # Process the name, description, parts of dataInfo, and data_i variables.
    # This section has been optimized for loading speed.  All time and value
    # data remains linked to the memory location where it is loaded by scipy.
    # The negated variable is carried through so that copies are not necessary.
    # If changes are made to this code, be sure to compare the performance
    # (e.g., using timeit in IPython).
    if version == '1.0':
        d = mat['data'].T if transposed else mat['data']
        times = d[:, 0]
        names = [chars_to_str(line)
                 for line in (mat['names'].T if transposed else mat['names'])]
        variables = {name: Variable(Samples(times, d[:, i], False), '', '', '')
                     for i, name in enumerate(names)}
        variables = _VarDict(variables)
    else:
        assert version == '1.1', ('The version of the Dymola/OpenModelica '
                                  'result file ({v}) is not '
                                  'supported.'.format(v=version))
        dataInfo = mat['dataInfo'] if transposed else mat['dataInfo'].T
        description = mat['description'] if transposed else mat['description'].T
        names = [chars_to_str(line)
                 for line in (mat['name'].T if transposed else mat['name'])]
        data_sets = dataInfo[0, :]
        variables = _VarDict()
        for current_data_set in count(1):
            try:
                d = (mat['data_%i' % current_data_set].T if transposed else
                     mat['data_%i' % current_data_set])
            except KeyError:
                break # There are no more "data_i" variables.
            else:
                if d.shape[1] > 1: # It's possible that a data set is empty.
                    times = d[:, 0]
                    for i, (data_set, name) in enumerate(zip(data_sets, names)):
                        if data_set == current_data_set:
                            sign_col = dataInfo[1, i]
                            variables[name] = Variable(Samples(times,
                                                               d[:, abs(sign_col)-1],
                                                               sign_col < 0),
                                                       *parse(description[:, i]))

        # Time is from the last data set.
        variables['Time'] = Variable(Samples(times, times, False), 'Time', 's', '')

    return variables


def loadlin(fname):
    """Load Dymola\ :sup:`®` or OpenModelica linearization results.

    **Arguments:**

    - *fname*: Name of the results file, including the path

         The file extension ('.mat') is optional.

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

    .. code-block:: python

       >>> from modelicares._io.dymola import loadlin

       >>> sys = loadlin('examples/PID.mat')
       >>> sys.state_names
       ['I.y', 'D.x']
    """
    # This does the task of mfiles/traj/tloadlin.m in the Dymola installation.

    # Load the file.
    mat, Aclass = read(fname)

    # Check the type of results.
    if Aclass[0] == 'Atrajectory':
       raise AssertionError('"%s" is a simulation result.  Use SimRes '
                            'instead.' % fname)
    else:
       assert Aclass[0] == 'AlinearSystem', ('File "%s" is not a simulation '
                                             'or linearization result.' % fname)

    # Determine the number of states, inputs, and outputs.
    ABCD = mat['ABCD']
    nx = mat['nx'][0]
    nu = ABCD.shape[1] - nx
    ny = ABCD.shape[0] - nx

    # Extract the system matrices.
    A = ABCD[:nx, :nx] if nx > 0 else [[]]
    B = ABCD[:nx, nx:] if nx > 0 and nu > 0 else [[]]
    C = ABCD[nx:, :nx] if nx > 0 and ny > 0 else [[]]
    D = ABCD[nx:, nx:] if nu > 0 and ny > 0 else [[]]
    sys = ss(A, B, C, D)

    # Extract the variable names.
    xuyName = mat['xuyName']
    sys.state_names = [chars_to_str(xuyName[i]) for i in range(nx)]
    sys.input_names = [chars_to_str(xuyName[i]) for i in range(nx, nx+nu)]
    sys.output_names = [chars_to_str(xuyName[i]) for i in range(nx+nu, nx+nu+ny)]

    return sys


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
