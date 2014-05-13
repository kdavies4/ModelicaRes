#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions to load results from Dymola and OpenModelica

- :meth:`loadsim` - TODO

- :meth:`loadlin` - TODO

TODO:
each
raises TypeError if the wrong results type (simulation vs. linearization)
raises LookupError if the file isn't formatted as expected
KeyError if an expected variable is missing
raises IOError if the file can't be accessed
raises ValueError if wrong file version
AssertionError if unrecognized data orientation

"""

import numpy as np

from collections import namedtuple
from functools import wraps
from scipy.io import loadmat
from scipy.interpolate import interp1d
from control.matlab import ss

from modelicares.util import chars_to_str#, applyfunction, applyindex
from modelicares._io import DataEntry as GenericDataEntry


# Named tuple to store the data for each variable
class DataEntry(GenericDataEntry):
    """Specialized named tuple that contains attributes and methods to
    represent a variable from a model simulated in Dymola or OpenModelica

TODO doc
    """

    def applyfunction(g):
        """Return a function that applies a function *f* to its output, given a
        function that doesn't (*g*).

        If *f* is *None*, then no function is applied (pass through or
        identity).
        """
        @wraps(g)
        def wrapped(self, f=None, *args, **kwargs):
            return (g(self, *args, **kwargs) if f is None else
                  f(g(self, *args, **kwargs)))

        return wrapped

    def applyindex(f):
        """Return a function that returns values at index or slice *i*, given a
        function that returns all values (*f*).

        If *i* is *None*, then all values are returned (pass through).
        """
        @wraps(f)
        def wrapped(self, i=None, *args, **kwargs):
            return (f(self, *args, **kwargs) if i is None else
                    f(self, *args, **kwargs)[i])

        return wrapped

    @applyindex
    @applyfunction
    def values(self):
        """Return function *f* of the values of the variable at index or slice
        *i*.

        If *i* is *None*, then all values are returned.  If *f* is *None*, then
        no function is applied (pass through or identity).
        """
        return -self.samples.values if self.samples.negated else self.samples.values

    def array(self, i=None, ft=None, fv=None):
        """Return an array with function *ft* of the times of the variable as
        the first column and function *fv* of the values of the variable as the
        second column.

        The times and values are taken at index or slice *i*.  If *i* is *None*,
        then all times and values are returned.
        """
        return np.array([self.times, self.values(i, fv)]).T

    def array_wi_times(self, t1=None, t2=None, ft=None, fv=None):
        """Return an array with function *ft* of the times of the variable as
        the first column and function *fv* of the values of the variable as the
        second column, all within time range [*t1*, *t2*].
        """
        return self.array(self._slice(t1, t2), ft, fv)



    def values_at_times(self, times, f=None):
        """Return function *f* of the values of the variable at *times*.
        """
        return interp1d(self.times, self.values(f=f), bounds_error=False)(times)

    def values_wi_times(self, t1=None, t2=None, f=None):
        """Return function *f* of the values of the variable in the time range
        [*t1*, *t2*].
        """
        return self.values(self._slice(t1, t2), f)

# Named tuple to store the value information of each variable
# This is used for the *samples* field of DataEntry.
Samples = namedtuple('Samples', ['values', 'negated'])


def _load(fname, constants_only=False):
    """Load Modelica_ simulation results from a MATLAB\ :sup:`®` file in
    Dymola\ :sup:`®` or OpenModelica format.

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
            mat = loadmat(fname, chars_as_strings=False,
                          variable_names=['Aclass', 'class', 'name', 'names',
                                          'description', 'dataInfo', 'data',
                                          'data_1', 'ABCD', 'nx', 'xuyName'])
        else:
            mat = loadmat(fname, chars_as_strings=False)
    except IOError:
        raise IOError('"{fname}" could not be opened.'
                      '  Check that it exists.'.format(fname=fname))

    # Check if the file contains the expected variables.
    try:
        Aclass = mat['Aclass']
    except KeyError:
        raise TypeError('"{fname}" does not appear to be an Dymola or '
                        'OpenModelica result file.  The "Aclass" variable is '
                        'missing.'.format(fname=fname))

    return mat, map(chars_to_str, Aclass)


def loadsim(fname, constants_only=False):
    """Load Modelica_ simulation results from a dictionary in Dymola\ :sup:`®`
    or OpenModelica format.

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
        description = chars_to_str(description)
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
    if Aclass[0] == 'AlinearSystem':
       raise TypeError('"%s" is a linearization result.  Use LinRes instead.'
                       % fname)
    else:
       assert Aclass[0] == 'Atrajectory', ('File "%s" is not a simulation '
                                           'or linearization result.' % fname)

    # Determine if the data is transposed.
    try:
        transposed = Aclass[3] == 'binTrans'
    except IndexError:
        transposed = False
    else:
        assert transposed or Aclass[3] == 'binNormal', ('The orientation of the'
            ' Dymola/OpenModelica results is not recognized.  The third line of'
            ' the "Aclass" or "class" variable is "%s", but it should be'
            ' "binNormal" or "binTrans".' % Aclass[3])

    # Get the format version.
    version = Aclass[1]
    assert version == '1.0' or version == '1.1', (
        'The version of the Dymola/OpenModelica result file ({v}) is not '
        'supported.'.format(v=version))

    # Process the name, description, parts of dataInfo, and data_i variables.
    data = {}
    if version == '1.0':
        d = mat['data'].T if transposed else mat['data']
        times = d[:, 0]
        names = map(chars_to_str, (mat['names'].T if transposed else
                                   mat['names']).astype('|S10'))
        data = {name: DataEntry(times, Samples(d[:, i], False), '', '', '')
                for i, name in enumerate(names)}
    else:
        dataInfo = mat['dataInfo'] if transposed else mat['dataInfo'].T
        description = mat['description'] if transposed else mat['description'].T
        names = map(chars_to_str, (mat['name'].T if transposed else
                                   mat['name']).astype('|S10'))
        data_sets = dataInfo[0, :]
        current_data_set = 1
        while True:
            try:
                d = (mat['data_%i' % current_data_set].T  if transposed else
                     mat['data_%i' % current_data_set])
                times = d[:, 0]
                for i, (data_set, name) in enumerate(zip(data_sets, names)):
                    if data_set == current_data_set:
                        sign_col = dataInfo[1, i]
                        data[name] = DataEntry(times,
                                               Samples(d[:, abs(sign_col)-1],
                                                       sign_col < 0),
                                               *parse(description[:, i]))
                current_data_set += 1
            except KeyError:
                break # There are no more "data_i" variables.
            except IndexError:
                raise LookupError("The variables in the Dymola/OpenModelica "
                            "simulation result do not have the expected shape.")
        # Time is from the last data set.
        data['Time'] = DataEntry(times, Samples(times, False), 'Time', 's', '')

    return data


def loadlin(fname):
    """Load Modelica_ linearization results from a dictionary in 
    Dymola\ :sup:`®` or OpenModelica format.

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
    mat, Aclass = _load(fname)

    # Check the type of results.
    if Aclass[0] == 'Atrajectory':
       raise TypeError('"%s" is a linearization result.  Use SimRes instead.' % fname)
    else:
       assert Aclass[0] == 'AlinearSystem', ('File "%s" is not a simulation '
                                           'or linearization result.' % fname)

    # Determine the number of states, inputs, and outputs.
    ABCD = mat['ABCD']
    nx = mat['nx'][0]
    nu = ABCD.shape[1] - nx
    ny = ABCD.shape[0] - nx
    assert nu >= 0 and ny >= 0, ('The number of states is larger than the size '
                                 'of the "ABCD" matrix.')

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
