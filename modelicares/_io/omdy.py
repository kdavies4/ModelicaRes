#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions to load results from OpenModelica and Dymola
"""

from collections import namedtuple
from numpy import unique, concatenate, take
from scipy.io import loadmat
from control.matlab import ss

from modelicares.util import chars_to_str

# TODO: Add examples/docstrings.


DataEntry = namedtuple('DataEntry', ['times', 'values', 'negated',
                                     'description', 'unit', 'displayUnit'])
"""Named tuple class to represent an entry in the data"""
# All fields except *negated* are standard and are required by SimRes.
# *negated* is specific to the OpenModelica/Dymola format and is only directly
# referenced in the functions below.


def load(cls, fname, constants_only=False):
    """Load Modelica_ simulation results from a MATLAB\ :sup:`®` file in
    OpenModelica or Dymola\ :sup:`®` format.

    **Arguments:**

    - *cls*: Instance of a :class:`~modelicares.simres.SimRes` or
      :class:`~modelicares.simres.SimRes` class

         The data and supporting methods will be attached to this instance.

    - *fname*: Name of the results file (may include the path)

         This may be from a simulation or linearization.  The file extension
         ('.mat') is optional.

    - *constants_only*: *True* to load only the variables from the first data
      matrix, if the result is from a simulation

    **Returns:** 'simulation' or 'linearization', depending on the type of
    results.

    **Example:**

    .. code-block:: python

       >>> from modelicares._io.omdy import load

       >>> class A(object):
       ...     pass
       >>> a = A()

       >>> load(a, 'examples/ChuaCircuit.mat')
       'asimulation'

       >>> a._data # doctest: +ELLIPSIS
       {'L.p.i': DataEntry(description='Current flowing into the pin', unit='A', displayUnit='', data_set=1, column=2, negated=False), ..., 'Ro.LossPower': DataEntry(description='Loss power leaving component via HeatPort', unit='W', displayUnit='', data_set=1, column=5, negated=False)}

       >>> a._values(a._data['L.v']) # doctest: +ELLIPSIS
       array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)

       >>> a._times(a._data['L.v']) # doctest: +ELLIPSIS
       array([    0.        , ...,  2500.        ], dtype=float32)

       >>> a._unique_times(['L.v', 'C1.v']) # doctest: +ELLIPSIS
       array([    0.        , ...,  2500.        ], dtype=float32)
    """

    # Load the file and check if it contains the expected variables.
    if constants_only:
        mat = loadmat(fname, chars_as_strings=False,
                      variable_names=['Aclass', 'class', 'name', 'dataInfo',
                                      'description', 'data_1', 'ABCD', 'nx',
                                      'xuyName'])
    else:
        mat = loadmat(fname, chars_as_strings=False)
    try:
        Aclass = mat['Aclass']
    except KeyError:
        try:
            Aclass = mat['class']
        except KeyError:
            raise KeyError('"%s" does not appear to be an OpenModelica or Dymola result file.  '
                           '"Aclass" and "class" are both absent.' % fname)

    # Process the rest of the data depending on the file type.
    file_type = chars_to_str(Aclass[0])
    if file_type == 'Atrajectory':
        loadsim(cls, mat, Aclass, constants_only)
        return 'simulation'
    elif file_type == 'AlinearSystem':
        loadlin(cls, mat)
        return 'linearization'
    else:
        raise TypeError('File "%s" does not appear to be a simulation '
                        'or linearization result.' % fname)

def loadsim(cls, mat, Aclass, constants_only=False):
    """Load Modelica_ simulation results from a dictionary in OpenModelica or
    Dymola\ :sup:`®` format.

    **Arguments:**

    - *cls*: Instance of a :class:`~modelicares.simres.SimRes` class

         TODO update: The results are stored within *cls* as *_data* and *_data*.  *_data* is
         a dictionary where the keywords are the variable names.  The entries
         are a tuple of (index to the data array, row or column of the data
         array, a Boolean variable indicating if the values are negated,
         description of the variable, unit, and display unit).  *_data* is a
         list of NumPy_ arrays containing the sample times and values.

         Format-dependent helper methods are added as well:

         - :meth:`_values`: Return the values of a variable given its *_data*
           entry

         - :meth:`_times`: Return the times of a variable given its _data entry

         - :meth`_unique_times`: Return a vector of unique sampling times among
           a set of variables, given their names.

    - *mat*: Dictionary of matrices

    - *Aclass*: A copy of the `Aclass` or `class` matrix, whichever is present

    - *constants_only*: *True* to load only the variables from the first data
      matrix

         The first data matrix usually contains all of the constants,
         parameters, and variables that don't vary.  If only that information is
         needed, it may save resources to set *constants_only* to *True*.

    There are no return values.  TODO update: *_data*, *_data*, :meth:`_values`,
    :meth:`_times`, :meth`_unique_times`, and  are monkey-patched to the
    :class:`~modelicares.simres.SimRes` instance (see above).


    .. _NumPy: http://numpy.scipy.org/
    """
    # This performs the task of mfiles/traj/tload.m from the Dymola
    # installation.

    def _parse_description(description):
        """Parse the variable description string into description, unit, and
        displayUnit.
        """
        description = chars_to_str(description)[:-1]
        try:
            description, unit = description.rsplit(' [', 1)
            try:
                unit, displayUnit = unit.rsplit('|', 1)
            except ValueError:
                return description, unit, ''
        except ValueError:
            return description, '', ''
        return description, unit, displayUnit

    # Check the version of the simulation results format.
    version = chars_to_str(Aclass[1])
    assert version == '1.1', ('Only mat files of version 1.1 are supported, '
                              'but the version is %s.' % version)

    # Determine if the data is transposed.
    try:
        transposed = chars_to_str(Aclass[3]) == 'binTrans'
    except IndexError:
        transposed = False

    # Process the name, description, parts of dataInfo, and data_i variables.
    cls._data = {}
    dataInfo = mat['dataInfo'].T if transposed else mat['dataInfo']
    data_sets = dataInfo[:, 0]
    current_data_set = 1
    while True:
        try:
            data = (mat['data_%i' % current_data_set].T  if transposed else
                    mat['data_%i' % current_data_set])
            data.flags.writeable = False
            times = data[:, 0]
            for i, data_set in enumerate(data_sets):
                if data_set == current_data_set:
                    name = chars_to_str(mat['name'][:, i] if transposed else mat['name'][i, :])
                    sign_column = dataInfo[i, 1]
                    cls._data[name] = DataEntry(times,
                                                data[:, abs(sign_column)-1],
                                                sign_column<0,
                                                *_parse_description(mat['description'][:, i] if transposed else mat['description'][i, :]))
            current_data_set += 1
        except:
            break
    # Note that numpy doesn't TODO transpose doesn't move or copy data (only the indexing scheme), and data in _data[].values and _data[].times is linked to (not copied from) the loaded data.

    # Time is from the last data set.
    cls._data['Time'] = DataEntry(times, times, False, 'Time', 's', '')

    # Required helper function
    # ------------------------
    # Return the values of a variable given its _data entry.
    cls._values = lambda entry: -entry.values if entry.negated else entry.values

def loadlin(cls, mat):
    """Load Modelica_ linearization results from a dictionary in OpenModelica or
    Dymola\ :sup:`®` format.

    **Arguments:**

    - *cls*: Instance of a :class:`~modelicares.linres.LinRes` class

         The state-space system is stored within *cls* as *sys*---an instance of
         :class:`control.StateSpace`

         It contains:

         - *A*, *B*, *C*, *D*: Matrices of the linear system

              .. code-block:: modelica

                 der(x) = A*x + B*u;
                      y = C*x + D*u;

         - *state_names*: List of names of the states (*x*)

         - *input_names*: List of names of the inputs (*u*)

         - *output_names*: List of names of the outputs (*y*)

    - *mat*: Dictionary of matrices

    - *Aclass*: A copy of the `Aclass` or `class` matrix, whichever is present

    There are no return values.  *sys* is monkey-patched to the
    :class:`~modelicares.linres.LinRes` instance (see above).
    """
    # This performs same task as mfiles/traj/tloadlin.m from the Dymola
    # installation.

    # Determine the number of states, inputs, and outputs.
    ABCD = mat['ABCD']
    n_x = mat['nx'][0]
    n_u = ABCD.shape[1] - n_x
    n_y = ABCD.shape[0] - n_x

    # Extract the system matrices.
    A = ABCD[:n_x, :n_x] if n_x > 0 else [[]]
    B = ABCD[:n_x, n_x:] if n_x > 0 and n_u > 0 else [[]]
    C = ABCD[n_x:, :n_x] if n_x > 0 and n_y > 0 else [[]]
    D = ABCD[n_x:, n_x:] if n_u > 0 and n_y > 0 else [[]]
    cls.sys = ss(A, B, C, D)

    # Extract the variable names.
    xuyName = mat['xuyName']
    cls.sys.state_names = [chars_to_str(xuyName[i]) for i in range(n_x)]
    cls.sys.input_names = [chars_to_str(xuyName[i]) for i in range(n_x, n_x+n_u)]
    cls.sys.output_names = [chars_to_str(xuyName[i]) for i in range(n_x+n_u, n_x+n_u+n_y)]


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
