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
of NumPy_ and matplotlib_ (e.g., :meth:`sin` and :meth:`plot`).

**Example:**

.. code-block:: sh

   $ loadres examples/
   Valid: SimRes('.../examples/ChuaCircuit.mat')
   Valid: SimRes('.../examples/ChuaCircuit2.mat')
   Valid: SimRes('.../examples/ThreeTanks.mat')
   Valid: LinRes('.../examples/PID.mat')
   Simulation results have been loaded into sims[0] through sims[2].
   A linearization result has been loaded into lin.

   In [1]:

where '...' depends on the local system.

.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _PyLab: http://www.scipy.org/PyLab
.. _NumPy: http://numpy.scipy.org/
.. _matplotlib: http://www.matplotlib.org/
