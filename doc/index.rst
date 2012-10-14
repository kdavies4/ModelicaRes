################################
  modelicares User's Guide
################################

.. only:: html

   Welcome to the user's guide for the modelicares utilities.  These Python_
   modules can be used to analyze and plot results from Modelica_ simulations.
   The methods rely on scipy_, matplotlib_, and python-control_.

   The links below describe the modules.  The main module,
   :mod:`modelicares`, has classes and methods for loading, interpreting,
   and plotting Modelica_ results in the format used by Dymola.  The
   :mod:`texunit` module has methods to translate Modelica *unit* (and
   *displayUnit*) strings into TeX_-formatted strings.  Finally, the
   :mod:`res` module has general supporting methods.

.. only:: latex

   This is the user's guide of utilities for the modelicares utilities.  These Python_
   modules can be used to analyze and plot results from Modelica_ simulations.
   The methods rely on scipy_, matplotlib_, and python-control_. The methods
   rely on scipy_, matplotlib_, and python-control_.

   The following chapters describe the modules.  The main module,
   :mod:`modelicares`, has classes and methods for loading, interpreting,
   and plotting Modelica_ results in the format used by Dymola.  The
   :mod:`texunit` module has methods to translate Modelica *unit* (and
   *displayUnit*) strings into TeX_-formatted strings.  Finally, the
   :mod:`res` module has general supporting methods.

   .. Seealso:: The buildingspy_
      (http://simulationresearch.lbl.gov/modelica/buildingspy/) and DyMat_
      (http://www.j-raedler.de/projects/dymat/) projects provide other
      Python_ modules that are related.

.. _Python: http://www.python.org/
.. _Modelica: http://www.modelica.org/
.. _scipy: http://www.scipy.org/
.. _matplotlib: http://www.matplotlib.org/
.. _python-control: http://sourceforge.net/apps/mediawiki/python-control
.. _TeX: http://www.latex-project.org/
.. _buildingspy: http://simulationresearch.lbl.gov/modelica/buildingspy/
.. _DyMat: http://www.j-raedler.de/projects/dymat/

.. only:: html

  .. image:: _static/browse.png
     :scale: 45 %
     :alt: variable browser

  .. image:: demos/ThreeTanks.png
     :scale: 35 %
     :alt: Sankey digarams of three tanks model

  .. image:: demos/ChuaCircuit.png
     :scale: 35 %
     :alt: plot of Chua circuit

  .. image:: demos/PID-nyquist.png
     :scale: 35 %
     :alt: example for LinRes.nyquist()

  **Modules:**

.. only:: latex

   .. figure:: _static/browse.png
      :scale: 60 %

   .. figure:: demos/ChuaCircuit.pdf
      :scale: 50 %

   .. figure:: demos/ThreeTanks.pdf
      :scale: 50 %

..   .. figure:: demos/PID-nyquist.pdf
..      :scale: 40 %

.. toctree::
   :maxdepth: 1

   modelicares
   res
   texunit

.. only:: html

   .. Seealso:: The buildingspy_
      (http://simulationresearch.lbl.gov/modelica/buildingspy/) and DyMat_
      (http://www.j-raedler.de/projects/dymat/) projects provide other
      Python_ modules that are related.

   A PDF version of this user's guide is available here_.

.. _here: modelicares.pdf
