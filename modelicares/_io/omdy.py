#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions to load data from OpenModelica and Dymola result files
"""

from collections import namedtuple
from numpy import unique, concatenate
from scipy.io import loadmat
from control.matlab import ss

from modelicares.util import chars_to_str

# TODO: Add examples/docstrings.

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
    """
    # Load the file and check if it contains the expected variables.
    mat = loadmat(fname, chars_as_strings=False)
    try:
        Aclass = mat['Aclass']
    except KeyError:
        try:
            Aclass = mat['class']
        except KeyError:
            raise KeyError('"%s" does not appear to be a Dymola or OpenModelica result file.  '
                           '"Aclass" and "class" are both absent.' % fname)

    # Check if the result type is correct.
    result_type = chars_to_str(Aclass[0])
    if result_type == 'Atrajectory':
        loadsim(cls, mat, Aclass, constants_only)
        return 'simulation'
    elif result_type == 'AlinearSystem':
        loadlin(cls, mat)
        return 'linearization'
    else:
        print result_type
        raise TypeError('File "%s" does not appear to be a simulation '
                        'or linearization result.' % fname)

def loadsim(cls, mat, Aclass, constants_only=False):
    """Load Modelica_ simulation results from a dictionary in OpenModelica or
    Dymola\ :sup:`®` format.

    **Arguments:**

    - *cls*: Instance of a :class:`~modelicares.simres.SimRes` class

         The results are stored within *cls* as *_meta* and *_data*.  *_meta* is
         a dictionary where the keywords are the variable names.  The entries
         are a tuple of (index to the data array, row or column of the data
         array, a Boolean variable indicating if the values are negated,
         description of the variable, unit, and display unit).  *_data* is a
         list of NumPy_ arrays containing the sample times and values.

         Format-dependent helper methods are added as well.

    - *mat*: Dictionary of matrices

    - *Aclass*: A copy of the `Aclass` or `class` matrix, whichever is present

    - *constants_only*: *True* to load only the variables from the first data
      matrix

         The first data matrix usually contains all of the constants,
         parameters, and variables that don't vary.  If only that information is
         needed, it may save resources to set *constants_only* to *True*.

    There are no return values.


    .. _NumPy: http://numpy.scipy.org/
    """
    # This performs the task of mfiles/traj/tload.m from the Dymola
    # installation.

    MetaEntry = namedtuple('MetaEntry', ['data_set', 'row', 'negated',
                                         'description', 'unit', 'displayUnit'])
    """Named tuple class to represent an entry in the meta data"""


    def _parse_description(description):
        """Parse the variable description string into description, unit, and
        displayUnit.
        """
        description = chars_to_str(description)[0:-1]
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

    # Determine if the matrices are transposed.
    transposed = (len(Aclass) >= 4
                  and chars_to_str(Aclass[3]) == 'binTrans')

    # Load the name, description, parts of dataInfo, and data_i variables.
    cls._meta = {}
    n_data_sets = 0
    if transposed:
        for i in range(mat['dataInfo'].shape[1]):
            name = chars_to_str(mat['name'][:, i])
            data_set = mat['dataInfo'][0, i]
            sign_row = mat['dataInfo'][1, i]
            description, unit, displayUnit = _parse_description(
                mat['description'][:, i])
            if data_set == 1 or not constants_only:
                cls._meta[name] = MetaEntry(data_set=data_set-1,
                                            row=abs(sign_row)-1,
                                            negated=sign_row<0,
                                            description=description,
                                            unit=unit,
                                            displayUnit=displayUnit)
            n_data_sets = max(data_set, n_data_sets)
        if constants_only:
            cls._data = [mat['data_1']]
        else:
            cls._data = [mat['data_%i' % (i+1)]
                          for i in range(n_data_sets)]
    else:
        for i in range(mat['dataInfo'].shape[0]):
            name = chars_to_str(mat['name'][i, :])
            data_set = mat['dataInfo'][i, 0]
            sign_row = mat['dataInfo'][i, 1]
            description, unit, displayUnit = _parse_description(
                mat['description'][i, :])
            if data_set == 1 or not constants_only:
                cls._meta[name] = MetaEntry(data_set=data_set-1,
                                            row=abs(sign_row)-1,
                                            negated=sign_row<0,
                                            description=description,
                                            unit=unit,
                                            displayUnit=displayUnit)
            n_data_sets = max(data_set, n_data_sets)
        if constants_only:
            cls._data = [mat['data_1'].T]
        else:
            cls._data = [mat['data_%i' % (i+1)].T
                          for i in range(n_data_sets)]
    # Note 1: The indices are converted from Modelica (1-based) to Python
    # (0-based).
    # Note 2:  Dymola 7.4 uses the transposed version, so it's the standard here
    # (for optimal speed).  Therefore, the "normal" version is transposed, and
    # _meta[x].row is really the column of variable x.

    # Required helper functions
    # -------------------------
    # Return the description of a variable given its name.
    cls._description = lambda name: cls._meta[name].description
    # Return the unit of a variable given its name.
    cls._unit = lambda name: cls._meta[name].unit
    # Return the displayUnit of a variable given its name.
    cls._displayUnit = lambda name: cls._meta[name].displayUnit
    # Return the times of a variable given its entry.
    cls._times = lambda entry: cls._data[entry.data_set][0, :]
    # Return the values of a variable given its entry.
    cls._values = lambda entry: (-cls._data[entry.data_set][entry.row, :]
                                 if entry.negated else
                                 cls._data[entry.data_set][entry.row, :])
    # Return a vector of unique sampling times among a set of variables, given
    # their names.
    cls._unique_times = lambda names: \
        unique(concatenate([cls._data[data_set][0][:]
                            for data_set in {cls._meta[name].data_set
                                             for name in names}], 1))


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

    There are no return values.
    """
    # This performs same task as mfiles/traj/tloadlin.m from the Dymola
    # installation.

    # Extract variables from the dictionary (for convenience).
    ABCD = mat['ABCD']
    xuyName = mat['xuyName']

    # Determine the number of states, inputs, and outputs.
    n_x = mat['nx'][0]
    n_u = ABCD.shape[1] - n_x
    n_y = ABCD.shape[0] - n_x

    # Extract the system matrices.
    if n_x > 0:
        A = ABCD[:n_x, :n_x]
        if n_u > 0:
            B = ABCD[:n_x, n_x:]
        else:
            B = []
        if n_y > 0:
            C = ABCD[n_x:, :n_x]
        else:
            C = []
    else:
        A = []
        B = []
        C = []
    if n_u > 0 and n_y > 0:
        D = ABCD[n_x:, n_x:]
    else:
        D = []
    cls.sys = ss(A, B, C, D)

    # Extract the variable names.
    cls.sys.state_names = [chars_to_str(xuyName[i]) for i in range(n_x)]
    cls.sys.input_names = [chars_to_str(xuyName[i]) for i in range(n_x, n_x+n_u)]
    cls.sys.output_names = [chars_to_str(xuyName[i]) for i in range(n_x+n_u, n_x+n_u+n_y)]


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
    exit()
