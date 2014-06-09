#############
 ModelicaRes
#############

**Set up and analyze Modelica simulations**

ModelicaRes is a free, open-source tool that can be used to

- generate simulation scripts,
- load and browse data,
- perform custom calculations,
- filter and sort groups of results,
- produce various plots and diagrams, and
- export data to various formats via pandas_.

The figures are generated via matplotlib_, which offers a rich set of
publication-quality plotting routines.  ModelicaRes has methods to create and
automatically label xy plots, Bode and Nyquist plots, and Sankey diagrams.
ModelicaRes can be scripted or used in an interactive Python_ session with math
and matrix functions from NumPy_.

The figures are generated via matplotlib_, which offers a rich set of plotting
routines.  ModelicaRes has methods to create and automatically label
`xy plots`_, Bode_ and Nyquist_ plots, and `Sankey diagrams`_.  ModelicaRes can
be scripted or used in an interactive Python_ session with math and matrix
functions from NumPy_.

Currently, ModelicaRes only loads Dymola/OpenModelica_-formatted results
(\*.mat), but the loading functions are modular so that other formats can be
added easily.

Please see the tutorial, which is available as an `IPython notebook
<https://github.com/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb>`_
or online as a `static page
<http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb>`_.
For the full documentation and many more examples, see the `main website`_.

For a list of changes, please see the `change log
<http://kdavies4.github.io/ModelicaRes/changelog.html>`_.

Installation
~~~~~~~~~~~~

The easiest way to install this package is to use pip_::

    pip install modelicares

On Linux, it may be necessary to have root privileges::

    sudo pip install modelicares

Another way is to download and extract a copy of the package.  The `main
website`_, the `GitHub repository`_, and the `PyPI page`_ have copies which
include the source code as well as examples and supporting files to build the
documentation and run tests.  Once you have a copy, run the following command
from the base folder::

    python setup.py install

Or, on Linux::

    sudo python setup.py install

Some of the required packages may not install automatically.

- SciPy_ can be installed according to the instructions at
  http://www.scipy.org/install.html.
- The GUIs require Qt_, which can be installed via PyQt4_, guidata_, or PySide_.

The `matplotlibrc file
<https://github.com/kdavies4/ModelicaRes/blob/master/examples/matplotlibrc>`_
file has some recommended revisions to matplotlib_'s defaults.  To use it, copy
it to the working directory or matplotlib_'s configuration directory.  See
http://matplotlib.org/users/customizing.html for details.

Credits
~~~~~~~

The main author is Kevin Davies.  Code has been included from:

- Richard Murray (**control.freqplot**---part of python-control_),
- Joerg Raedler (method to expand a Modelica_ variable tree---from DyMat_),
- Jason Grout (`ArrowLine class`_), and
- Jason Heeris (`efficient base-10 logarithm`_).

Suggestions and bug fixes have been provided by Arnout Aertgeerts, Kevin Bandy,
Thomas Beutlich, Moritz Lauster, Martin Sjölund, Mike Tiller, and Michael
Wetter.

License terms and development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ModelicaRes is published under a `BSD-compatible license
<https://github.com/kdavies4/ModelicaRes/blob/release/LICENSE.txt>`_.  Please
share any modifications you make (preferably as a pull request to the ``master``
branch of the `GitHub repository`_) in order to help others.  There are useful
development scripts in the `hooks folder
<https://github.com/kdavies4/ModelicaRes/blob/master/hooks/>`_.  If you find a
bug, please `report it
<https://github.com/kdavies4/ModelicaRes/issues/new>`_.  If you have
suggestions, please `share them
<https://github.com/kdavies4/ModelicaRes/wiki/Suggestions>`_.

See also
~~~~~~~~

- awesim_: helps run simulation experiments and organize results
- BuildingsPy_: supports unit testing
- DyMat_: exports Modelica_ simulation data to comma-separated values
  (CSV_), Gnuplot_, MATLAB®, and Network Common Data Form (netCDF_)
- PyFMI_: tools to work with models through the Functional Mock-Up Interface
  (FMI_) standard
- PySimulator_: elaborate GUI; supports FMI_


.. _main website: http://kdavies4.github.io/ModelicaRes/
.. _PyPI page: http://pypi.python.org/pypi/ModelicaRes
.. _GitHub repository: https://github.com/kdavies4/ModelicaRes

.. _xy plots: http://kdavies4.github.io/ModelicaRes/simres.html#modelicares.simres.SimRes.plot
.. _Bode: http://kdavies4.github.io/ModelicaRes/linres.html#modelicares.linres.LinRes.bode
.. _Nyquist: http://kdavies4.github.io/ModelicaRes/linres.html#modelicares.linres.LinRes.nyquist
.. _Sankey diagrams: http://kdavies4.github.io/ModelicaRes/simres.html#modelicares.simres.SimRes.sankey

.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _pandas: http://pandas.pydata.org/
.. _matplotlib: http://www.matplotlib.org/
.. _NumPy: http://numpy.scipy.org/
.. _SciPy: http://www.scipy.org/index.html
.. _OpenModelica: https://www.openmodelica.org/
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
.. _CSV: http://en.wikipedia.org/wiki/Comma-separated_values
.. _netCDF: http://www.unidata.ucar.edu/software/netcdf/
.. _FMI: https://www.fmi-standard.org
.. _python-control: http://sourceforge.net/apps/mediawiki/python-control
.. _ArrowLine class: http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html
.. _efficient base-10 logarithm: http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html
