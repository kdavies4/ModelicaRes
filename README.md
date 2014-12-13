ModelicaRes
-----------

**Set up and analyze Modelica simulations in Python**

ModelicaRes is a free, open-source tool that can be used to
- [generate simulation scripts](http://kdavies4.github.io/ModelicaRes/modelicares.exps.html#modelicares.exps.write_script),
- [load](http://kdavies4.github.io/ModelicaRes/modelicares.html#modelicares.load),
  [analyze](http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb#Analyzing-a-simulation-result), and
  [browse](http://kdavies4.github.io/ModelicaRes/modelicares.simres.html#modelicares.simres.SimRes.browse)
  data,
- [filter](http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/advanced.ipynb#Testing-simulations-based-on-criteria)
  and
  [sort](http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb#Simulations)
  groups of results,
- produce various
  [plots](http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb)
  and
  [diagrams](http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/advanced.ipynb#Sankey-diagrams),
  and
- [export data via pandas](http://kdavies4.github.io/ModelicaRes/modelicares.simres.html#modelicares.simres.SimRes.to_pandas).

[![Plot of Chua circuit with varying parameters](doc/_static/ChuaCircuit-small.png)](http://kdavies4.github.io/ModelicaRes/examples2/ChuaCircuit.hires.png)
![ ](doc/_static/hspace.png)
[![Sankey diagram of three tanks example](doc/_static/ThreeTanks-small.png)](http://kdavies4.github.io/ModelicaRes/examples2/ThreeTanks.hires.png)
![ ](doc/_static/hspace.png)
[![Bode diagram of PID with varying parameters](doc/_static/PIDs-bode-small.png)](http://kdavies4.github.io/ModelicaRes/examples2/PIDs-bode.hires.png)

The goal of ModelicaRes is to leverage [Python] to make these tasks easy and
complex tasks feasible.  Publication-quality figures can be created with
[matplotlib] using built-in methods that automatically add titles, labels, and
legends.  ModelicaRes can be scripted or used in an interactive [Python] session
with math and matrix functions from [NumPy].

Please see the tutorial, which is available as an
[IPython notebook](examples/tutorial.ipynb) or online as a
[static page](http://nbviewer.ipython.org/github/kdavies4/ModelicaRes/blob/master/examples/tutorial.ipynb).
For the full documentation and many more examples, see the
[main website].

Currently, ModelicaRes only loads Dymola/[OpenModelica]-formatted binary and
text results (*.mat and *.txt), but the interface is modular so that other
formats can be added easily.

### Installation

First, install the dependencies.  Most are installed automatically, but
[SciPy] >= 0.10.0 must be installed according to the instructions at
http://www.scipy.org/install.html.  The GUIs require [Qt], which can be
installed via [PyQt4], [guidata], or [PySide].

Then install ModelicaRes.  The easiest way is to use [pip]:

    > pip install modelicares

On Linux, it may be necessary to have root privileges:

    $ sudo pip install modelicares

The [matplotlibrc file](examples/matplotlibrc) has some recommended revisions to
[matplotlib]'s defaults.  To use it, copy it to the working directory or
[matplotlib]'s configuration directory.  See
http://matplotlib.org/users/customizing.html for details.

### License terms and development

ModelicaRes is published under a [BSD-compatible license](LICENSE.txt).   Please
share any improvements you make, preferably as a pull request to the ``master``
branch of the [GitHub repository].  There are useful development scripts in the
[hooks folder](hooks).  If you find a bug, have a suggestion, or just want to
leave a comment, please
[open an issue](https://github.com/kdavies4/ModelicaRes/issues/new).

[![Build Status](https://travis-ci.org/kdavies4/ModelicaRes.svg?branch=travis)](https://travis-ci.org/kdavies4/ModelicaRes)
![ ](doc/_static/hspace.png)
[![Code Health](https://landscape.io/github/kdavies4/ModelicaRes/master/landscape.png)](https://landscape.io/github/kdavies4/ModelicaRes/master)

### See also

- [awesim]\: helps run simulation experiments and organize results
- [BuildingsPy]\: supports unit testing
- [DyMat]\: exports [Modelica] simulation data to [Gnuplot], MATLAB&reg;, and
  Network Common Data Form ([netCDF])
- [PyFMI]\: tools to work with models through the Functional Mock-Up Interface
  ([FMI]) standard
- [PySimulator]\: elaborate GUI; supports [FMI]


[main website]: http://kdavies4.github.io/ModelicaRes
[PyPI page]: http://pypi.python.org/pypi/ModelicaRes
[GitHub repository]: https://github.com/kdavies4/ModelicaRes

[Modelica]: http://www.modelica.org/
[Python]: http://www.python.org/
[matplotlib]: http://www.matplotlib.org/
[NumPy]: http://numpy.scipy.org/
[SciPy]: http://www.scipy.org/index.html
[OpenModelica]: https://www.openmodelica.org/
[setuptools]: https://pypi.python.org/pypi/setuptools
[Qt]: http://qt-project.org/
[PyQt4]: http://www.riverbankcomputing.co.uk/software/pyqt/
[guidata]: https://code.google.com/p/guidata/
[PySide]: http://qt-project.org/wiki/pyside
[pip]: https://pypi.python.org/pypi/pip
[awesim]: https://github.com/saroele/awesim
[BuildingsPy]: http://simulationresearch.lbl.gov/modelica/buildingspy
[DyMat]: http://www.j-raedler.de/projects/dymat
[PyFMI]: https://pypi.python.org/pypi/PyFMI
[PySimulator]: https://github.com/PySimulator/PySimulator
[Gnuplot]: http://www.gnuplot.info/
[netCDF]: http://www.unidata.ucar.edu/software/netcdf
[FMI]: https://www.fmi-standard.org/
[python-control]: http://sourceforge.net/apps/mediawiki/python-control
[ArrowLine]: http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html
[efficient base-10 logarithm]: http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html
