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

-------------
**Tutorial:**
-------------

**Setup:**

First, copy this script (*loadres*) to the current directory along with the 
*examples* folder.  Then, execute the following command:

.. code-block:: sh

   $ loadres examples
   Valid: SimRes('.../examples/ChuaCircuit.mat')
   Valid: SimRes('.../examples/ThreeTanks.mat')
   Valid: LinRes('.../examples/PID.mat')
   Simulation results have been loaded into sims[0] through sims[1].
   A linearization result has been loaded into lin.

where '...' depends on the local system.  If this fails, install the `easygui 
package <http://easygui.sourceforge.net/>`_.

We can now explore the simulation results or create plots using the methods in
:class:`~modelicares.simres.SimRes`.  We'll look at the first simulation---the
Chua circuit:

.. testsetup::
  >>> from modelicares import SimRes, LinRes
  >>> sims = map(SimRes, ['../examples/ChuaCircuit.mat', '../examples/ThreeTanks.mat'])
  >>> lin = LinRes('examples/PID.mat')

.. code-block:: python

   >>> sim = sims[0]
   >>> print(sim) # doctest: +ELLIPSIS
   Modelica simulation results from ".../examples/ChuaCircuit.mat"

To get the final value and unit of the current flowing through the inductor 
('L.i'), use :meth:`~modelicares.simres.SimRes.get_FV` and 
:meth:`~modelicares.simres.SimRes.get_unit`:

.. code-block:: python

   >>> sim.get_FV('L.i')
   2.0486615
   >>> sim.get_unit('L.i')
   'A'

There are other *get_* methods.  For example,

.. code-block:: python

   >>> dict(final=sim.get_FV('L.i'), minimum=sim.get_min('L.i'), maximum=sim.get_max('L.i'), mean=sim.get_mean('L.i'))
   {'mean': 0.43196017, 'minimum': -3.3101323, 'final': 2.0486615, 'maximum': 3.9185011}

If a variable can't be found, then suggestions are given:

.. code-block:: python

   >>> sim.get_description('L.ii')
   L.ii is not a valid variable name.
   <BLANKLINE>
   Did you mean one of these?
          L.i
          L.p.i
          L.n.i

   >>> sim.get_description('L.i')
   'Current flowing from pin p to pin n'

To search for variable names, use
:meth:`~modelicares.simres.SimRes.names` with wildcards:

   >>> sim.names('L.p*')
   [u'L.p.i', u'L.p.v']

To see how many variables are in a simulation, use Python_'s built-in 
:meth:`len` function:

.. code-block:: python

   >>> len(sim)
   62

To return all values of 'L.i', use 
:meth:`~modelicares.simres.SimRes.get_values`:

.. code-block:: python

   >>> sim.get_values('L.i') # doctest: +ELLIPSIS
   array([ 0.        , ...,  2.04866147], dtype=float32)

To return a tuple of time and value vectors, use 
:meth:`~modelicares.simres.SimRes.get_tuple`:

.. code-block:: python

   >>> sim.get_tuple('L.i') # doctest: +ELLIPSIS
   (array([    0.        , ...,  2500.        ], dtype=float32), array([ 0.        , ...,  2.04866147], dtype=float32))

or simply index the variable name or provide it as an argument:

.. code-block:: python

   >>> sim['L.i'] # doctest: +ELLIPSIS
   (array([    0.        , ...,  2500.        ], dtype=float32), array([ 0.        , ...,  2.04866147], dtype=float32))
   >>> sim('L.i') # doctest: +ELLIPSIS
   (array([    0.        , ...,  2500.        ], dtype=float32), array([ 0.        , ...,  2.04866147], dtype=float32))

To plot 'L.i', use :meth:`~modelicares.simres.SimRes.plot`:

   >>> sim.plot(ynames1='L.i') # doctest: +ELLIPSIS
   (<matplotlib.axes.AxesSubplot object at 0x...>, None)
   >>> import matplotlib.pyplot as plt
   >>> plt.show()

.. testsetup::
   >>> sim.plot(ynames1='L.i') # doctest: +ELLIPSIS
   (<matplotlib.axes.AxesSubplot object at 0x...>, None)
   >>> plt.savefig('examples/ChuaCircuit1.png')
   >>> plt.savefig('examples/ChuaCircuit1.pdf')

.. only:: html

   .. image:: ../examples/ChuaCircuit1.png
      :scale: 70 %
      :alt: plot of Chua circuit

.. only:: latex

   .. figure:: ../examples/ChuaCircuit1.pdf
      :scale: 70 %

      Plot of Chua circuit

Notice that the title and labels were generated automatically.  However, they 
can be customized using the arguments to :meth:`~modelicares.simres.SimRes.plot`
or the functions in :mod:`matplotlib.pyplot`.  For more information on 
:meth:`~modelicares.simres.SimRes.plot` or any of the other methods, use 
Python's :meth:`help` function:

   >>> help(sim.plot) # doctest: +ELLIPSIS
   Help on method plot in module modelicares.simres:
   ...

or click on the links in this documentation.

Likewise, we can explore the linearization result and create diagrams using the
methods in :class:`~modelicares.linres.LinRes`:

.. code-block:: python

   >>> print(lin) # doctest: +ELLIPSIS
   Modelica linearization results from ".../examples/PID.mat"
   >>> lin.sys.A
   matrix([[   0.,    0.],
           [   0., -100.]])
   >>> lin.bode() # doctest: +ELLIPSIS
   (<matplotlib.axes.AxesSubplot object at 0x...>, <matplotlib.axes.AxesSubplot object at 0x...>)
   >>> plt.show()

.. testsetup::
   >>> lin.bode() # doctest: +ELLIPSIS
   (<matplotlib.axes.AxesSubplot object at 0x...>, <matplotlib.axes.AxesSubplot object at 0x...>)
   >>> plt.savefig('examples/PID-bode1.png')
   >>> plt.savefig('examples/PID-bode1.pdf')

.. only:: html

   .. image:: ../examples/PID-bode1.png
      :scale: 70 %
      :alt: example for LinRes.bode()

.. only:: latex

   .. figure:: ../examples/PID-bode1.pdf
      :scale: 70 %

      Example for :class:`~modelicares.linres.LinRes.bode`

.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _PyLab: http://www.scipy.org/PyLab
.. _NumPy: http://numpy.scipy.org/
.. _matplotlib: http://www.matplotlib.org/
