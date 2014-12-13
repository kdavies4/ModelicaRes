#############
 ModelicaRes
#############

**Set up and analyze Modelica simulations in Python**

ModelicaRes is a free, open-source tool that can be used to

- `generate simulation scripts
  <http://kdavies4.github.io/ModelicaRes/modelicares.exps.html#modelicares.exps.write_script>`_,
- `load
  <http://kdavies4.github.io/ModelicaRes/modelicares.html#modelicares.load>`_,
  `analyze
  <http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb#Analyzing-a-simulation-result>`_, and `browse
  <http://kdavies4.github.io/ModelicaRes/modelicares.simres.html#modelicares.simres.SimRes.browse>`_
  data,
- `filter
  <http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/advanced.ipynb#Testing-simulations-based-on-criteria>`_
  and `sort
  <http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb#Simulations>`_ groups of results,
- produce various `plots
  <http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb>`_ and `diagrams
  <http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/advanced.ipynb#Sankey-diagrams>`_,
  and
- `export data via pandas
  <http://kdavies4.github.io/ModelicaRes/modelicares.simres.html#modelicares.simres.SimRes.to_pandas>`_.

The goal of ModelicaRes is to leverage Python_ to make these tasks easy and
complex tasks feasible.  Publication-quality figures can be created with
matplotlib_ using built-in methods that automatically add titles, labels, and
legends.  ModelicaRes can be scripted or used in an interactive Python_ session
with math and matrix functions from NumPy_.

.. image:: _static/browse.png
   :scale: 30 %
   :alt: Variable browser

.. image:: _static/ChuaCircuit.png
   :scale: 30 %
   :alt: Plot of Chua circuit

.. image:: _static/ThreeTanks.png
   :scale: 30 %
   :alt: Sankey diagrams of three tanks model

.. image:: _static/PIDs-bode.png
   :scale: 30 %
   :alt: Bode plot of PID with varying differential time constant

Please see the tutorial, which is available as an `IPython notebook
<https://github.com/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb>`_
or online as a `static page
<http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb>`_.  The links in the sidebar provide the full documentation and
many more examples.

Currently, ModelicaRes only loads Dymola/OpenModelica_-formatted binary and text
results (\*.mat and \*.txt), but the interface is modular so that other formats
can be added easily.

Installation
~~~~~~~~~~~~

First, install the dependencies.  Most are installed automatically, but
SciPy_ >= 0.10.0 must be installed according to the instructions at
http://www.scipy.org/install.html.  The GUIs require Qt_, which can be installed
via PyQt4_, guidata_, or PySide_.

Then install ModelicaRes.  The easiest way is to use pip_::

    > pip install modelicares

On Linux, it may be necessary to have root privileges::

    $ sudo pip install modelicares

Another way is to download and extract a copy of the package from the sidebar on
the left.  Run the following command from the base folder::

    > python setup.py install

Or, on Linux::

    $ sudo python setup.py install

The `matplotlibrc file
<https://github.com/kdavies4/ModelicaRes/blob/master/examples/matplotlibrc>`_
has some recommended revisions to matplotlib_'s defaults.  To use it, copy
it to the working directory or matplotlib_'s configuration directory.  See
http://matplotlib.org/users/customizing.html for details.

License terms and development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ModelicaRes is published under a `BSD-compatible license <license.html>`_.
Please share any improvements you make, preferably as a pull request to the
``master`` branch of the `GitHub repository`_.  There are useful development
scripts in the `hooks folder
<https://github.com/kdavies4/ModelicaRes/blob/master/hooks/>`_.  If you find a
bug, have a suggestion, or just want to leave a comment, please `open an issue
<https://github.com/kdavies4/ModelicaRes/issues/new>`_.

See also
~~~~~~~~

- awesim_: helps run simulation experiments and organize results
- BuildingsPy_: supports unit testing
- DyMat_: exports Modelica_ simulation data to Gnuplot_, MATLAB®, and Network
  Common Data Form (netCDF_)
- PyFMI_: tools to work with models through the Functional Mock-Up Interface
  (FMI_) standard
- PySimulator_: elaborate GUI; supports FMI_


.. toctree::
  :hidden:
  :glob:

  loadres
  modelicares*

.. _main website: http://kdavies4.github.io/ModelicaRes/
.. _PyPI page: http://pypi.python.org/pypi/ModelicaRes/
.. _GitHub repository: https://github.com/kdavies4/ModelicaRes

.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _matplotlib: http://www.matplotlib.org/
.. _NumPy: http://numpy.scipy.org/
.. _SciPy: http://www.scipy.org/index.html
.. _OpenModelica: https://www.openmodelica.org/
.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _Qt: http://qt-project.org/
.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _guidata: https://code.google.com/p/guidata/
.. _PySide: http://qt-project.org/wiki/pyside
.. _pip: https://pypi.python.org/pypi/pip
.. _awesim: https://github.com/saroele/awesim
.. _BuildingsPy: http://simulationresearch.lbl.gov/modelica/buildingspy/
.. _DyMat: http://www.j-raedler.de/projects/dymat/
.. _PyFMI: https://pypi.python.org/pypi/PyFMI
.. _PySimulator: https://github.com/PySimulator/PySimulator
.. _Gnuplot: http://www.gnuplot.info
.. _netCDF: http://www.unidata.ucar.edu/software/netcdf/
.. _FMI: https://www.fmi-standard.org
