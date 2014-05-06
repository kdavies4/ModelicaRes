###############
  ModelicaRes
###############

**Python utilities to set up and analyze Modelica simulation experiments**

ModelicaRes is a free, open-source tool to manage Modelica_ simulations,
interpret results, and create publishable figures.  It is possible to

- Auto-generate simulation scripts,
- Browse data,
- Perform custom calculations, and
- Produce various plots and diagrams.

The figures are generated via matplotlib_, which offers a rich set of plotting
routines.  ModelicaRes includes convenient functions to automatically pre-format
and label some figures, like xy plots, Bode and Nyquist plots, and Sankey
diagrams.  ModelicaRes can be scripted or run from a Python_ interpreter with
math and matrix functions from NumPy_.

.. only:: html

  .. image:: _static/browse.png
     :scale: 45 %
     :alt: Variable browser

  .. image:: ../examples/PIDs-nyquist.png
     :scale: 35 %
     :alt: Nyquist plot of PID with varying differential time constant

  |

  .. image:: ../examples/ChuaCircuit.png
     :scale: 35 %
     :alt: Plot of Chua circuit

  .. image:: ../examples/ThreeTanks.png
     :scale: 35 %
     :alt: Sankey digarams of three tanks model

  The links below and in the sidebar describe the components of ModelicaRes.
  For an introduction, please see the `tutorial <loadres.html>`_.

.. only:: latex

  .. image:: _static/browse.png
     :scale: 60 %

  .. image:: ../examples/PIDs-nyquist.pdf
     :scale: 50 %

  .. image:: ../examples/ThreeTanks.pdf
     :scale: 50 %

  .. image:: ../examples/ChuaCircuit.pdf
     :scale: 50 %

  The following chapters describe the components of ModelicaRes.  For an
  introduction, please the tutorial.

  The top-level module, :mod:`modelicares`, provides direct access to the most
  important classes and functions.  Others must be accessed through their
  submodules.  The :mod:`modelicares.simres` submodule has classes to load,
  analyze, and plot simulation results.  The :mod:`modelicares.linres` submodule
  has a class to load, analyze, and plot results from linearizing a model.  The
  :mod:`modelicares.multi` submodule has functions to load and plot results from
  multiple data files at once. The :mod:`modelicares.exps` submodule has tools
  to set up and manage simulation experiments.  The :mod:`modelicares.texunit`
  submodule has functions to translate Modelica_ *unit* and *displayUnit*
  strings into LaTeX_-formatted strings.  The last submodule,
  :mod:`modelicares.util`, has general supporting functions.

  **Installation**

  The easiest way to install this package is to use pip_::

      pip install modelicares

  On Linux, it may be necessary to have root privileges::

      sudo pip install modelicares

  Another way is to download and extract a copy of the package from the 
  `main project site`_, the `master branch at GitHub 
  <https://github.com/kdavies4/ModelicaRes>`_, or the `PyPI page`_.  Run 
  the following command from the base folder::

      python setup.py install

  Or, on Linux::

      sudo python setup.py install

  The *matplotlibrc* file in the base folder has some recommended revisions to
  matplotlib_'s defaults.  To use it, copy or move it to the working directory
  or matplotlib_'s configuration directory.  See
  http://matplotlib.org/users/customizing.html for details.

  **Credits**

  The main author is Kevin Davies.  Improvements, bug fixes, and suggestions 
  have been provided by Arnout Aertgeerts, Kevin Bandy, Thomas Beutlich, 
  Martin Sjölund, Mike Tiller, and Michael Wetter.  

  Third-party code has been included from:

  - Jason Grout (`ArrowLine
    <http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html>`_
    class),
  - Jason Heeris (`efficient base-10 logarithm
    <http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html>`_),
  - Richard Murray (`python-control
    <http://sourceforge.net/apps/mediawiki/python-control>`_), and
  - Joerg Raedler (method to expand a Modelica_ variable tree---from
    DyMat_).

  **License terms and development**

  ModelicaRes_ is published under a BSD license (see LICENSE.txt).  Please share 
  any modifications you make (preferably on a Github fork from 
  https://github.com/kdavies4/ModelicaRes) in order to help others.  If you find 
  a bug, please `report it
  <https://github.com/kdavies4/ModelicaRes/issues/new>`_.  If you have 
  suggestions, please `share them
  <https://github.com/kdavies4/ModelicaRes/wiki/Suggestions>`_.

  **See also**

  The following Python_ projects are related:

  - awesim_: helps run simulation experiments and organize results
  - BuildingsPy_: supports unit testing
  - DyMat_: exports Modelica_ simulation data to comma-separated values (CSV),
    `Gnuplot <http://www.gnuplot.info/>`_, MATLAB®, and `Network Common Data Form
    (netCDF) <http://www.unidata.ucar.edu/software/netcdf/>`_
  - PyFMI_: tools to work with models through the Functional Mock-Up Interface
    (FMI) standard
  - PySimulator_: elaborate GUI; supports FMI

.. toctree::

  Tutorial and loadres script <loadres>
  modelicares
  simres
  linres
  multi
  exps
  texunit
  util

.. only:: html

  The top-level module, :mod:`modelicares`, provides direct access to the most
  important classes and functions.  Others must be accessed through their
  submodules.  The :mod:`modelicares.simres` submodule has classes to load,
  analyze, and plot simulation results.  The :mod:`modelicares.linres` submodule
  has a class to load, analyze, and plot results from linearizing a model.
  The :mod:`modelicares.multi` submodule has functions to load and plot results
  from multiple data files at once. The :mod:`modelicares.exps` submodule has
  tools to set up and manage simulation experiments.  The
  :mod:`modelicares.texunit` submodule has functions to translate Modelica_
  *unit* and *displayUnit* strings into LaTeX_-formatted strings.  The last
  submodule, :mod:`modelicares.util`, has general supporting functions.

  For a list of changes, please see the `change log <Changelog.html>`_.  A PDF
  version of this documentation is available `here <ModelicaRes.pdf>`_.

  **Installation**

  The easiest way to install this package is to use pip_::

      pip install modelicares

  On Linux, it may be necessary to have root privileges::

      sudo pip install modelicares

  Another way is to download and extract a copy of the package from the 
  `main project site`_, the `master branch at GitHub 
  <https://github.com/kdavies4/ModelicaRes>`_, or the `PyPI page`_.  Run the
  following command from the base folder::

      python setup.py install

  Or, on Linux::

      sudo python setup.py install

  The *matplotlibrc* file in the base folder has some recommended revisions to
  matplotlib_'s defaults.  To use it, copy or move it to the working
  directory or matplotlib_'s configuration directory.  See
  http://matplotlib.org/users/customizing.html for details.

  **Credits**

  The main author is Kevin Davies.  Improvements, bug fixes, and suggestions 
  have been provided by Arnout Aertgeerts, Kevin Bandy, Thomas Beutlich, 
  Martin Sjölund, Mike Tiller, and Michael Wetter.  

  Third-party code has been included from:

  - Jason Grout (`ArrowLine
    <http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html>`_
    class),
  - Jason Heeris (`efficient base-10 logarithm
    <http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html>`_),
  - Richard Murray (`python-control
    <http://sourceforge.net/apps/mediawiki/python-control>`_), and
  - Joerg Raedler (method to expand a `Modelica`_ variable tree---from
    DyMat_).

  **License terms and development**

  ModelicaRes_ is published under a BSD license (see LICENSE.txt).  Please share 
  any modifications you make (preferably on a Github fork from 
  https://github.com/kdavies4/ModelicaRes) in order to help others.  If you find 
  a bug, please `report it
  <https://github.com/kdavies4/ModelicaRes/issues/new>`_.  If you have 
  suggestions, please `share them
  <https://github.com/kdavies4/ModelicaRes/wiki/Suggestions>`_.

  **See also**

  The following Python_ projects are related:

  - awesim_: helps run simulation experiments and organize results
  - BuildingsPy_: supports unit testing
  - DyMat_: exports Modelica_ simulation data to comma-separated values
    (CSV), `Gnuplot <http://www.gnuplot.info/>`_, MATLAB®, and `Network Common
    Data Form (netCDF) <http://www.unidata.ucar.edu/software/netcdf/>`_
  - PyFMI_: tools to work with models through the Functional Mock-Up Interface
    (FMI) standard
  - PySimulator_: elaborate GUI; supports FMI


.. _Modelica: http://www.modelica.org/
.. _main project site: http://kdavies4.github.io/ModelicaRes/
.. _Python: http://www.python.org/
.. _matplotlib: http://www.matplotlib.org/
.. _NumPy: http://numpy.scipy.org/
.. _PyPI page: http://pypi.python.org/pypi/ModelicaRes
.. _pip: https://pypi.python.org/pypi/pip
.. _LaTeX: http://www.latex-project.org/
.. _awesim: https://github.com/saroele/awesim
.. _BuildingsPy: http://simulationresearch.lbl.gov/modelica/buildingspy/
.. _DyMat: http://www.j-raedler.de/projects/dymat/
.. _PyFMI: https://pypi.python.org/pypi/PyFMI
.. _PySimulator: https://github.com/PySimulator/PySimulator
