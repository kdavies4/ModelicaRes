ModelicaRes
-----------

`ModelicaRes <http://kdavies4.github.io/ModelicaRes/>`_ is an
open-source tool to manage `Modelica <http://www.modelica.org>`_
simulations, interpret results, and create publishable figures. It is
currently possible to

-  Auto-generate simulation scripts,
-  Run model executables with varying parameters,
-  Browse data,
-  Perform custom calculations, and
-  Produce various plots and diagrams.

The figures are generated via `matplotlib <http://www.matplotlib.org>`_,
which offers a rich set of plotting routines.
`ModelicaRes <http://kdavies4.github.io/ModelicaRes/>`_ includes
convenient functions to automatically pre-format and label some figures,
like xy plots, Bode and Nyquist plots, and Sankey diagrams.
`ModelicaRes <http://kdavies4.github.io/ModelicaRes/>`_ can be scripted
or run from a `Python <http://www.python.org>`_ interpreter with math
and matrix functions from `NumPy <http://numpy.scipy.org>`_.

For more information, please see the `main project
site <http://kdavies4.github.io/ModelicaRes/>`_ or the `doc <doc>`_
folder of the package for the full documentation and many examples. The
development site is https://github.com/kdavies4/modelicares.

Installation
~~~~~~~~~~~~

An installable copy of this package can be downloaded from the `main
project site <http://kdavies4.github.io/ModelicaRes/>`_ or the `PyPI
page <http://pypi.python.org/pypi/ModelicaRes>`_. To install the
package, first download and extract it. Then run the set up script
(`setup.py <setup.py>`_) from the base folder. On Windows, use the
following command:

::

    python setup.py install

On Linux, use:

::

    sudo python setup.py install

The `matplotlibrc <matplotlibrc>`_ file in the base folder has some
recommended revisions to `matplotlib <http://www.matplotlib.org>`_'s
defaults. To use it, copy or move the file to the working directory or
`matplotlib <http://www.matplotlib.org>`_'s configuration directory. See
http://matplotlib.org/users/customizing.html for details.

Credits
~~~~~~~

The main author is Kevin Davies. Kevin Bandy also helped in the
development of this package. Third-party code has been included from
Jason Grout
(`ArrowLine <http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html>`_
class), Jason Heeris (`efficient base-10
logarithm <http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html>`_),
Richard Murray
(`python-control <http://sourceforge.net/apps/mediawiki/python-control>`_),
and Joerg Raedler (method to expand a
`Modelica <http://www.modelica.org>`_ variable tree - from
`DyMat <http://www.j-raedler.de/projects/dymat/>`_).

License terms
~~~~~~~~~~~~~

`ModelicaRes <http://kdavies4.github.io/ModelicaRes/>`_ is published
under the terms of the BSD license (see `LICENSE.txt <LICENSE.txt>`_).
Please share any modifications you make (preferably on a Github fork
from https://github.com/kdavies4/ModelicaRes) so that others may benefit
from your work.

See also
~~~~~~~~

The `pysimulator <https://code.google.com/p/pysimulator/>`_,
`BuildingsPy <http://simulationresearch.lbl.gov/modelica/buildingspy/>`_,
`DyMat <http://www.j-raedler.de/projects/dymat/>`_, and
`awesim <https://github.com/saroele/awesim>`_ projects provide related
`Python <http://www.python.org>`_ modules.
`pysimulator <https://code.google.com/p/pysimulator/>`_ includes an
elaborate GUI and supports the Functional Model Interface (FMI).
`BuildingsPy <http://simulationresearch.lbl.gov/modelica/buildingspy/>`_
has a **Tester** class that can be used for unit testing.
`DyMat <http://www.j-raedler.de/projects/dymat/>`_ has functions to
export `Modelica <http://www.modelica.org>`_ simulation data to comma
separated values (CSV), `Gnuplot <http://www.gnuplot.info/>`_, MATLAB®,
and `Network Common Data Form
(netCDF) <http://www.unidata.ucar.edu/software/netcdf/>`_.
`awesim <https://github.com/saroele/awesim>`_ provides tools to help run
simulation experiments and organize the results.
