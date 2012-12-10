The goal of ModelicaRes is to provide an open-source tool to effectively
manage Modelica_ simulations, interpret results, and create publishable
figures.  It is currently possible to auto-generate simulation scripts, run
model executables with varying parameters, browse data, perform calculations,
and produce various plots and diagrams.  The figures are generated via
matplotlib_, which offers a rich set of plotting routines.  ModelicaRes
includes convenient functions to automatically pre-format and label some
figures, like xy plots, Bode and Nyquist plots, and Sankey diagrams.
ModelicaRes can be scripted or run from a Python_ interpreter with math and
matrix functions from NumPy_.


Credits
=======

Kevin Bandy supported the development.  Third-party code has been included from
Jason Grout (`ArrowLine
<http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html>`_
class), Jason Heeris (`efficient base-10 logarithm
<http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg14433.html>`_),
Richard Murray (`python-control
<http://sourceforge.net/apps/mediawiki/python-control>`_), and Joerg Raedler
(method to expand a Modelica_ variable tree---from `DyMat
<http://www.j-raedler.de/projects/dymat/>`_).


Installation
============

To install the package, first download and extract it.  Then run the set up
script (setup.py) from the base folder.  On Windows, use the following
command::

   python setup.py install

On Linux, use::

   sudo python setup.py install


For More Information
====================

The `main project site <http://kdavies4.github.com/ModelicaRes>`_ has the full
documentation and many examples.  The development site is
https://github.com/kdavies4/modelicares.

.. _Modelica: http://www.modelica.org/
.. _Python: http://www.python.org/
.. _matplotlib: http://www.matplotlib.org/
.. _NumPy: http://numpy.scipy.org/
