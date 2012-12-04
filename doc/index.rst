###############
  ModelicaRes
###############
   **Python utilities to set up and analyze Modelica simulation experiments**

   The goal of ModelicaRes is to provide an open-source tool to effectively
   manage Modelica_ simulations, interpret results, and create publishable
   figures.  It is currently possible to auto-generate simulation scripts, run
   model executables with varying parameters, browse data, perform
   calculations, and produce various plots and diagrams.  The figures are
   generated via matplotlib_, which offers a rich set of plotting routines.
   ModelicaRes includes convenient functions to automatically pre-format and
   label some figures, like xy plots, Bode and Nyquist plots, and Sankey
   diagrams.  ModelicaRes can be scripted or run from a Python_ command-line
   interpreter with math and matrix functions from NumPy_.

   .. only:: html

      .. image:: _static/browse.png
         :scale: 45 %
         :alt: variable browser

      .. image:: examples/ThreeTanks.png
         :scale: 35 %
         :alt: Sankey digarams of three tanks model

      |

      .. image:: examples/ChuaCircuit.png
         :scale: 35 %
         :alt: plot of Chua circuit

      .. image:: examples/PID-nyquist.png
         :scale: 35 %
         :alt: example for modelicares.LinRes.nyquist()

      The  links below describe the components of ModelicaRes.  The
      top-level module, :mod:`modelicares`, provides direct access to the
      most important classes and functions.  Others must be accessed through
      their submodules.  The :mod:`modelicares.base` submodule has general
      supporting functions.  The :mod:`modelicares.exps` submodule has classes
      and functions to set up and manage simulation experiments.  The
      :mod:`modelicares.linres` submodule has a class to load, analyze, and
      plot results from linearizing a model.  The :mod:`modelicares.simres`
      submodule has classes to load, analyze, and plot simulation results.  The
      :mod:`modelicares.multi` submodule has functions to load and plot results
      from multiple data files at once.  The last submodule,
      :mod:`modelicares.texunit`, has functions to translate Modelica_ *unit*
      and *displayUnit* strings into LaTeX_-formatted strings.  Finally, the
      :mod:`loadres` script loads data files and provides a Python_
      command-line interpreter to help analyze them.

   .. only:: latex

      .. figure:: _static/browse.png
         :scale: 60 %

      .. figure:: examples/ChuaCircuit.pdf
         :scale: 50 %

      .. figure:: examples/ThreeTanks.pdf
         :scale: 50 %

      .. figure:: examples/PID-nyquist.pdf
         :scale: 50 %

      The following chapters describe the components of ModelicaRes.  The
      top-level module, :mod:`modelicares`, provides direct access to the
      most important classes and functions.  Others must be accessed through
      their submodules.  The :mod:`modelicares.base` submodule has general
      supporting functions.  The :mod:`modelicares.exps` submodule has classes
      and functions to set up and manage simulation experiments.  The
      :mod:`modelicares.linres` submodule has a class to load, analyze, and
      plot results from linearizing a model.  The :mod:`modelicares.simres`
      submodule has classes to load, analyze, and plot simulation results.  The
      :mod:`modelicares.multi` submodule has functions to load and plot results
      from multiple data files at once.  The last submodule,
      :mod:`modelicares.texunit`, has functions to translate Modelica_ *unit*
      and *displayUnit* strings into LaTeX_-formatted strings.  Finally, the
      :mod:`loadres` script loads data files and provides a Python_
      command-line interpreter to help analyze them.

      Updates to ModelicaRes may be available at the
      `main project site <http://kdavies4.github.com/ModelicaRes/>`_.
      ModelicaRes is also listed in the `Python Package Index
      <http://pypi.python.org/>`_ (`direct link
      <http://pypi.python.org/pypi/ModelicaRes/>`_).  The development site is
      https://github.com/kdavies4/ModelicaRes.

      .. Seealso:: The `pysimulator <https://code.google.com/p/pysimulator/>`_,
         `BuildingsPy
         <http://simulationresearch.lbl.gov/modelica/buildingspy/>`_, and
         `DyMat`_ projects provide other Python_ modules that are related.
         pysimulator_ includes a complete GUI and supports the Functional Model
         Interface (FMI).  BuildingsPy_ has a :class:`Tester` class that can be
         used for unit testing.  DyMat_ has functions to export Modelica_
         simulation data to comma separated values (CSV), `Gnuplot
         <http://www.gnuplot.info/>`_, MATLAB\ :sup:`®`, and `Network Common
         Data Form (netCDF) <http://www.unidata.ucar.edu/software/netcdf/>`_.

   .. toctree::

      modelicares
      base
      exps
      linres
      multi
      simres
      texunit
      loadres

   .. only:: html

      The authors are Kevin Davies and Kevin Bandy.  Third-party code has been
      included from Jason Grout (`ArrowLine
      <http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html>`_
      class), Jason Heeris (`efficient base-10 logarithm
      <http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html>`_),
      Richard Murray (`python-control
      <http://sourceforge.net/apps/mediawiki/python-control>`_), and Joerg
      Raedler (method to expand a Modelica_ variable tree---from `DyMat
      <http://www.j-raedler.de/projects/dymat/>`_).

      A PDF version of this documentation is available `here
      <ModelicaRes.pdf>`_.  Updates to ModelicaRes may be available at the
      `main project site`_.  ModelicaRes is also listed in the `Python Package
      Index`_ (`direct link`_).  The development site is
      https://github.com/kdavies4/ModelicaRes.

      .. Seealso:: The `pysimulator <https://code.google.com/p/pysimulator/>`_,
         `BuildingsPy
         <http://simulationresearch.lbl.gov/modelica/buildingspy/>`_, and
         `DyMat`_ projects provide other Python_ modules that are related.
         pysimulator_ includes a complete GUI and supports the Functional Model
         Interface (FMI).  BuildingsPy_ has a :class:`Tester` class that can be
         used for unit testing.  DyMat_ has functions to export Modelica_
         simulation data to comma separated values (CSV), `Gnuplot
         <http://www.gnuplot.info/>`_, MATLAB\ :sup:`®`, and `Network Common
         Data Form (netCDF) <http://www.unidata.ucar.edu/software/netcdf/>`_.

.. _Python: http://www.python.org/
.. _Modelica: http://www.modelica.org/
.. _matplotlib: http://www.matplotlib.org/
.. _NumPy: http://numpy.scipy.org/
.. _LaTeX: http://www.latex-project.org/
