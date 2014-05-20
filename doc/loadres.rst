``loadres`` script
==================

Load results from Modelica_ simulation(s) and/or linearization(s) and provide
a Python_ session to analyze the results.

This script can be executed from the command line.  It accepts as arguments the
names of result files or directories with result files.  Wildcards can be used.
If no arguments are given, then the script provides a dialog to choose files or
a folder.  After loading files, it provides working session of `IPython
<http://www.ipython.org/>`_ with the results available.  PyLab_ is imported
(``from pylab import *``) to provide many functions of NumPy_ and matplotlib_
(e.g., :meth:`sin` and :meth:`plot`).  The essential classes and functions of
ModelicaRes_ are imported as well (``from modelicares import *``).

**Setup and example:**

Open a command prompt in the *examples* folder from the ModelicaRes_
distribution and execute the following command:

.. code-block:: sh

   $ loadres ChuaCircuit.mat PID.mat
   A simulation result has been loaded into sim (a SimRes instance).
   A linearization result has been loaded into lin (a LinRes instance).
   ...

If this does not work, then the *loadres* script probably has not been installed
to a location recognized by the operating system.  Instead, copy it into the
*examples* folder and try again.  If necessary, call Python_ explicitly
(``python loadres ChuaCircuit.mat PID.mat``).

Please also see the tutorial, which is available as an `IPython notebook
<https://github.com/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb>`_
or online as a `static page
<http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb>`_.


.. _ModelicaRes: http://kdavies4.github.io/ModelicaRes
.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _PyLab: http://www.scipy.org/PyLab
.. _NumPy: http://numpy.scipy.org/
.. _matplotlib: http://www.matplotlib.org/
