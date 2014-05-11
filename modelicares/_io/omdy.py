#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions to load results from OpenModelica and Dymola

- :meth:`loadsim` - TODO

- :meth:`loadlin` - TODO

TODO:
each
raises TypeError if the wrong results type (simulation vs. linearization)
raises LookupError if the file isn't formatted as expected
raises IOError if the file can't be accessed
raises ValueError if wrong file version
AssertionError if unrecognized data orientation

"""

import scipy

from collections import namedtuple
from control.matlab import ss

from modelicares.util import chars_to_str, applyfunction, applyindex
from . import DataEntry as GenericDataEntry
from . import _applyfunction, _applyindex


# Named tuple to store the data for each variable
class DataEntry(GenericDataEntry):
    """Specialized named tuple that contains attributes and methods to 
    represent a variable from a model simulated in OpenModelica or Dymola

TODO doc
    """

    @applyfunction
    @applyindex
    def times(self)
        """Return function *f* of the times of the variable at index or slice 
        *i*.

        If *i* is *None*, then all values are returned.  If *f* is *None*, then 
        no function is applied (pass through or identity).
        """
        return self._samples.times

    @applyfunction
    @applyindex
    def values(self)
        """Return function *f* of the values of the variable at index or slice 
        *i*.

        If *i* is *None*, then all values are returned.  If *f* is *None*, then 
        no function is applied (pass through or identity).
        """
        return -self._samples.values if self._samples.negated else self._samples.values


# Named tuple to store the time and value information of each variable
# This is used for the *_samples* field of DataEntry.
Samples = namedtuple('Samples', ['times', 'values', 'negated'])


def _load(fname, constants_only=False):
    """Load Modelica_ simulation results from a MATLAB\ :sup:`®` file in
    OpenModelica or Dymola\ :sup:`®` format.

    **Arguments:**

    - *fname*: Name of the results file, including the path

         This may be from a simulation or linearization.  The file extension
         ('.mat') is optional.

    - *constants_only*: *True* to load only the variables from the first data
      matrix, if the result is from a simulation

    **Returns:**

    1. A dictionary of matrices

    2. A list of the strings on the lines of the 'Aclass' or 'class' matrix,
       whichever is present
    """

    # Load the file.
    try:
        if constants_only:
            mat = scipy.io.loadmat(fname, chars_as_strings=False,
                                   variable_names=['Aclass', 'class', 'name',
                                                   'dataInfo', 'description',
                                                   'data_1', 'ABCD', 'nx',
                                                   'xuyName'])
        else:
            mat = scipy.io.loadmat(fname, chars_as_strings=False)
    except IOError:
        raise IOError('"{fname}" could not be opened.'
                      '  Check that it exists.'.format(fname=fname))

    # Check if the file contains the expected variables.
    try:
        Aclass = mat['Aclass']
    except KeyError:
        raise TypeError('"{fname}" does not appear to be an OpenModelica or '
                        'Dymola result file.  The "Aclass" variable is '
                        'absent.'.format(fname=fname))

    return mat, map(chars_to_str, Aclass)


def loadsim(fname, constants_only=False):
    """Load Modelica_ simulation results from a dictionary in OpenModelica or
    Dymola\ :sup:`®` format.

    **Arguments:**

    - *fname*: Name of the results file, including the path

         This may be from a simulation or linearization.  The file extension
         ('.mat') is optional.

    - *constants_only*: *True* to load only the variables from the first data
      matrix, if the result is from a simulation

         The first data matrix usually contains all of the constants,
         parameters, and variables that don't vary.  If only that information is
         needed, it may save resources to set *constants_only* to *True*.

    **Returns:** A dictionary ... TODO -

         TODO update: The results are stored within *cls* as *data* and *data*.  *data* is
         a dictionary where the keywords are the variable names.  The entries
         are a tuple of (index to the data array, row or column of the data
         array, a Boolean variable indicating if the values are negated,
         description of the variable, unit, and display unit).  *data* is a
         list of NumPy_ arrays containing the sample times and values.

         Format-dependent helper methods are added as well:

         - :meth:`_values`: Return the values of a variable given its *data*
           entry

    **Example:**

    .. code-block:: python

       >>> from modelicares._io.omdy import loadsim

       >>> s = loadsim('examples/ChuaCircuit.mat')

       >>> s.data # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
       {'L.p.i': DataEntry(description='Current flowing into the pin', unit='A',
                           displayUnit='', Samples(times=, values=, negated=_)}
       >>> s.data['L.v'].unit
       'V'

    .. _NumPy: http://numpy.scipy.org/
    """
    # This performs the task of mfiles/traj/tload.m from the Dymola
    # installation.

    def parse(description):
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

    # Load the file.
    mat, Aclass = _load(fname, constants_only)

    # Check the type of results.
    if Aclass[0] <> 'Atrajectory':
        if Aclass[0] == 'AlinearSystem':
           raise TypeError('File "{fname}" appears to be a linearization '
                           'result.  Try using LinRes instead.' % fname)
        else:
           raise TypeError('File "{fname}" does not appear to be a simulation '
                           'or linearization result.' % fname)

    # Check the version of the format.
    try:
        if Aclass[1] == '1.0':
            version = 0
        elif Aclass[1] == '1.1':
            version = 1
        else
            raise LookupError("The version of the OpenModelica/Dymola result file "
                              "is unknown.")
    except IndexError:
        raise LookupError("The version of the OpenModelica/Dymola result file "
                          "is unknown.")
    if version == '1.1':
        v, ('OpenModelica/Dymola Only mat files of version 1.1 are supported, '
                              'but the version is %s.' % version)

    # Determine if the data is transposed.
    try:
        transposed = Aclass[3] == 'binTrans'
    except IndexError:
        transposed = False
    else:
        assert transposed or Aclass[3] == 'binNormal', ('The orientation of the'
            ' OpenModelica/Dymola results is not recognized.  The third line of'
            ' the "Aclass" or "class" variable is "%s", but it should be'
            ' "binNormal" or "binTrans".' % Aclass[3])

    # Process the name, description, parts of dataInfo, and data_i variables.
    data = {}
    try:
        dataInfo = mat['dataInfo'].T if transposed else mat['dataInfo']
    except KeyError:
        raise LookupError('OpenModelica/Dymola simulation results must '
                          'contain a "dataInfo" variable.')
    data_sets = dataInfo[:, 0]
    current_data_set = 1
    while True:
        try:
            d = (mat['data_%i' % current_data_set].T  if transposed else
                 mat['data_%i' % current_data_set])
            times = d[:, 0]
            for i, data_set in enumerate(data_sets):
                if data_set == current_data_set:
                    try:
                        name = chars_to_str(mat['name'][:, i]
                                            if transposed else
                                            mat['name'][i, :])
                    except KeyError:
                        raise LookupError('OpenModelica/Dymola simulation '
                            'results must contain a "name" variable.')
                    sign_col = dataInfo[i, 1]
                    values = d[:, abs(sign_col)-1]
                    negated = sign_col < 0
                    try:
                        data[name] = DataEntry(*parse(mat['description'][:, i]
                                                      if transposed else
                                                      mat['description'][i, :]),
                                               Samples(times, values, negated))
                    except KeyError:
                        raise LookupError('OpenModelica/Dymola simulation '
                            'results must contain a "description" variable.')
            current_data_set += 1
        except KeyError:
            break # There are no more "data_i" variables.
        except IndexError:
            raise LookupError("The variables in the OpenModelica/Dymola "
                            "simulation result do not have the expected shape.")

    # Time is from the last data set.
    data['Time'] = DataEntry('Time', 's', '', Samples(times, times, False))

    return data


def loadlin(fname):
    """Load Modelica_ linearization results from a dictionary in OpenModelica or
    Dymola\ :sup:`®` format.

    **Arguments:**

    - *fname*: Name of the results file, including the path

         This may be from a simulation or linearization.  The file extension
         ('.mat') is optional.

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

    # TODO: add
    """
    # This performs same task as mfiles/traj/tloadlin.m from the Dymola
    # installation.

    # Load the file.
    mat, Aclass = _load(fname, constants_only)

    # Check the type of results.
    if Aclass[0] <> 'AlinearSystem':
        if Aclass[0] == 'Atrajectory':
           raise TypeError('File "{fname}" appears to be a simulation '
                           'result.  Try using SimRes instead.' % fname)
        else:
           raise LookupError('File "{fname}" does not appear to be a simulation '
                             'or linearization result.' % fname)

    # Determine the number of states, inputs, and outputs.
    try:
        ABCD = mat['ABCD']
    except KeyError:
        raise LookupError('OpenModelica/Dymola linearization results must contain'
                          ' the variable "ABCD".')
    n_u = ABCD.shape[1] - n_x
    n_y = ABCD.shape[0] - n_x

    # Extract the system matrices.
    try:
        n_x = mat['nx'][0]
    except KeyError:
        raise LookupError('OpenModelica/Dymola linearization results must contain'
                          ' the variable "n_x".')
    A = ABCD[:n_x, :n_x] if n_x > 0 else [[]]
    B = ABCD[:n_x, n_x:] if n_x > 0 and n_u > 0 else [[]]
    C = ABCD[n_x:, :n_x] if n_x > 0 and n_y > 0 else [[]]
    D = ABCD[n_x:, n_x:] if n_u > 0 and n_y > 0 else [[]]
    cls.sys = ss(A, B, C, D)

    # Extract the variable names.
    try:
        xuyName = mat['xuyName']
    except KeyError:
        raise LookupError('OpenModelica/Dymola linearization results must contain'
                          ' the variable "xuyName".')
    cls.sys.state_names = [chars_to_str(xuyName[i]) for i in range(n_x)]
    cls.sys.input_names = [chars_to_str(xuyName[i]) for i in range(n_x, n_x+n_u)]
    cls.sys.output_names = [chars_to_str(xuyName[i]) for i in range(n_x+n_u, n_x+n_u+n_y)]


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
