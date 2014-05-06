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

**Setup and example:**

Copy this script (*loadres*) to the current directory along with the *examples* 
folder.  Then, execute the following command:

.. code-block:: sh

   $ loadres examples
   Valid: SimRes('.../examples/ChuaCircuit.mat')
   Valid: SimRes('.../examples/ThreeTanks.mat')
   Valid: LinRes('.../examples/PID.mat')
   Simulation results have been loaded into sims[0] through sims[1].
   A linearization result has been loaded into lin.

where '...' depends on the local system.  If this fails, install the `easygui 
package <http://easygui.sourceforge.net/>`_.

.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _PyLab: http://www.scipy.org/PyLab
.. _NumPy: http://numpy.scipy.org/
.. _matplotlib: http://www.matplotlib.org/
