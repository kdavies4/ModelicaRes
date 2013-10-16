#############
 ModelicaRes
#############

`ModelicaRes`_ is a free, open-source tool to manage `Modelica`_ simulations,
interpret results, and create publishable figures. It is currently possible to

-  Auto-generate simulation scripts,
-  Browse data,
-  Perform custom calculations, and
-  Produce various plots and diagrams.

The figures are generated via `matplotlib`_, which offers a rich set of plotting
routines.  `ModelicaRes`_ includes convenient functions to automatically
pre-format and label some figures, like xy plots, Bode and Nyquist plots, and
Sankey diagrams.  `ModelicaRes`_ can be scripted or run from a `Python`_
interpreter with math and matrix functions from `NumPy`_.

For more information, please see the `main project site`_ or the doc folder of
the package for the full documentation and many examples.  The  development site
is https://github.com/kdavies4/modelicares.

Installation
~~~~~~~~~~~~

An installable copy of this package can be downloaded from the `main project
site`_ or the `PyPI page`_.  After extracting the package, run the set up script
(*setup.py*) from the base folder.  On Windows, use the following command::

    python setup.py install

On Linux, use::

    sudo python setup.py install

The *matplotlibrc* file in the *bin* folder has some recommended revisions to
`matplotlib`_'s defaults.  To use it, move or copy the file to the working
directory or `matplotlib`_'s configuration directory.  See
http://matplotlib.org/users/customizing.html for details.

Credits
~~~~~~~

The main author is Kevin Davies.  Improvements and bug fixes have been provided 
by Arnout Aertgeerts, Kevin Bandy, Thomas Beutlich, Martin Sjölund, and Mike 
Tiller.  

Third-party code has been included from:

- Jason Grout (`ArrowLine
  <http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html>`_
  class),
- Jason Heeris (`efficient base-10 logarithm
  <http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html>`_),
- Richard Murray (`python-control
  <http://sourceforge.net/apps/mediawiki/python-control>`_), and
- Joerg Raedler (method to expand a `Modelica`_ variable tree - from `DyMat`_).

License terms and development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`ModelicaRes`_ is published under the terms of the BSD license (see
LICENSE.txt).  Please share any modifications you make (preferably on a Github
fork from https://github.com/kdavies4/ModelicaRes) so that others may benefit
from your work.  If you find a bug, please `report it
<https://github.com/kdavies4/ModelicaRes/issues/new>`_.  If you have suggestions
for improvements, please `share them here
<https://github.com/kdavies4/ModelicaRes/wiki/Possible-Enhancements>`_.

See also
~~~~~~~~

The following `Python`_ projects are related:

- `awesim`_: helps run simulation experiments and organize results
- `BuildingsPy`_: supports unit testing
- `DyMat`_: exports `Modelica`_ simulation data to comma-separated values (CSV),
  `Gnuplot <http://www.gnuplot.info/>`_, MATLAB®, and `Network Common Data Form
  (netCDF) <http://www.unidata.ucar.edu/software/netcdf/>`_
- `PyFMI`_: tools to work with models through the Functional Mock-Up Interface
  (FMI) standard
- `PySimulator`_: elaborate GUI; supports FMI


.. _ModelicaRes: http://kdavies4.github.io/ModelicaRes/
.. _Modelica: http://www.modelica.org
.. _matplotlib: http://www.matplotlib.org
.. _Python: http://www.python.org
.. _NumPy: http://numpy.scipy.org
.. _main project site: http://kdavies4.github.io/ModelicaRes/
.. _PyPI page: http://pypi.python.org/pypi/ModelicaRes
.. _awesim: https://github.com/saroele/awesim
.. _BuildingsPy: http://simulationresearch.lbl.gov/modelica/buildingspy/
.. _DyMat: http://www.j-raedler.de/projects/dymat/
.. _PyFMI: https://pypi.python.org/pypi/PyFMI
.. _PySimulator: https://github.com/PySimulator/PySimulator
