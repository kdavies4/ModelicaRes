:mod:`loadres`
==============

Load results from Modelica_ simulation(s) and provide a Python_ interpreter
to analyze the results.

This script can be executed at the command line.  It will accept as arguments
the names of result files or names of directories with result files.  The
filenames may contain wildcards.  If no arguments are given, the script
provides a dialog to choose a file or folder.  Finally, it provides working
session of `IPython <http://www.ipython.org/>`_ with the results preloaded.
PyLab_ is directly imported (``from pylab import *``) to provide many functions
of NumPy_ and matplotlib_ (e.g., :meth:`sin` and :meth:`plot`).  The essential
classes and functions of ModelicaRes are directly available as well.

**Example:**

.. code-block:: sh

   $ loadres examples
   Valid: SimRes('.../examples/ChuaCircuit.mat')
   Valid: SimRes('.../examples/ThreeTanks.mat')
   Valid: LinRes('.../examples/PID.mat')
   Simulation results have been loaded into sims[0] through sims[1].
   A linearization result has been loaded into lin.

where '...' depends on the local system.

You can now explore the simulation results or create plots using the methods in
:class:`~modelicares.simres.SimRes`.  For example,

.. code-block:: python

   >>> sims[0].get_FV('L.v')
   -0.25352862
   >>> sims[0].get_unit('L.v')
   'V'

If a variable cannot be found, then suggestions are given:

.. code-block:: python

   >>> sims[0].get_description('L.vv')
   L.vv is not a valid variable name.
   <BLANKLINE>
   Did you mean one of the these?
          L.v
          L.p.v
          L.n.v
   >>> sims[0].get_description('L.v')
   'Voltage drop between the two pins (= p.v - n.v)'

To return all values of a variable, use its string as an index:

.. code-block:: python

   >>> sim['L.v']
   array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)

or an argument:

.. code-block:: python

   >>> sim('L.v')
   array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)

To see all the methods, use

   >>> help(sims[0])

or go to :class:`~modelicares.simres.SimRes`.  To search for variable names, use
:meth:`~modelicares.simres.SimRes.glob` with wildcards:

   >>> sims[0].glob('L.p*')
   [u'L.p.i', u'L.p.v']

Likewise, you can explore the linearization result or create diagrams using the
methods in :class:`~modelicares.linres.LinRes`:

.. code-block:: python

   >>> print lin
   Modelica linearization results from ".../examples/PID.mat"
   >>> lin.sys.A
   matrix([[   0.,    0.],
           [   0., -100.]])

.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _PyLab: http://www.scipy.org/PyLab
.. _NumPy: http://numpy.scipy.org/
.. _matplotlib: http://www.matplotlib.org/
