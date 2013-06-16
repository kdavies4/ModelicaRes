The goal of ModelicaRes_ is to provide an open-source tool to effectively manage
manage Modelica_ simulations, interpret results, and create publishable figures.
It is currently possible to

- Auto-generate simulation scripts,
- Run model executables with varying parameters,
- Browse data,
- Perform custom calculations, and
- Produce various plots and diagrams.

The figures are generated via matplotlib_, which offers a rich set of plotting
routines.  ModelicaRes_ includes convenient functions to automatically
pre-format and label some figures, like xy plots, Bode and Nyquist plots, and
Sankey diagrams.  ModelicaRes_ can be scripted or run from a Python_ interpreter
with math and matrix functions from NumPy_.

For more information, please see the `main project site
<http://kdavies4.github.io/ModelicaRes/>`_ or the "doc" folder of the package
for the full documentation and many examples.  The development site is
https://github.com/kdavies4/modelicares.

Installation
------------
An installable copy of this package can be downloaded from the `main project
site`_ or the `PyPI page <http://pypi.python.org/pypi/ModelicaRes>`_.  To
install the package, first download and extract it.  Then run the set up script
(setup.py) from the base folder.  On Windows, use the following command::

   python setup.py install

On Linux, use::

   sudo python setup.py install

The matplotlibrc file in the base folder has some recommended revisions to
matplotlib_'s defaults.  To use it, copy or move the file to the working
directory or matplotlib_'s configuration directory.  See
http://matplotlib.org/users/customizing.html for details.

Credits
-------
Kevin Bandy helped to develop this package.  Third-party code has been included
from Jason Grout (`ArrowLine
<http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html>`_
class), Jason Heeris (`efficient base-10 logarithm
<http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html>`_),
Richard Murray (`python-control
<http://sourceforge.net/apps/mediawiki/python-control>`_), and Joerg Raedler
(method to expand a Modelica_ variable tree - from `DyMat
<http://www.j-raedler.de/projects/dymat/>`_).

License terms
-------------
ModelicaRes_ is published under the terms of the BSD license (see LICENSE.txt).
Please share any modifications you make (preferably on a Github fork from
https://github.com/kdavies4/ModelicaRes) so that others may benefit from your
work.

See also
--------
The `pysimulator <https://code.google.com/p/pysimulator/>`_, `BuildingsPy
<http://simulationresearch.lbl.gov/modelica/buildingspy/>`_, DyMat_, and
`awesim <https://github.com/saroele/awesim>`_ projects provide related Python_ modules.  pysimulator_ includes an elaborate GUI and supports the Functional
Model Interface (FMI).  BuildingsPy_ has a :class:`Tester` class that can be
used for unit testing.  DyMat_ has functions to export Modelica_ simulation data
to comma separated values (CSV), `Gnuplot <http://www.gnuplot.info/>`_, MATLAB
\ :sup:`®`, and `Network Common Data Form (netCDF)
<http://www.unidata.ucar.edu/software/netcdf/>`_.  awesim_ provides tools to
help run simulation experiments and organize the results.


.. _ModelicaRes: http://kdavies4.github.io/ModelicaRes/
.. _Modelica: http://www.modelica.org
.. _Python: http://www.python.org
.. _matplotlib: http://www.matplotlib.org
.. _NumPy: http://numpy.scipy.org
