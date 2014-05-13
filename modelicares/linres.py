#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Load, analyze, and plot the result of linearizing a Modelica_ model.

This module contains one class: :class:`LinRes`.

.. _Modelica: http://www.modelica.org/
.. _python-control: http://sourceforge.net/apps/mediawiki/python-control
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
import numpy as np

from scipy.signal import ss2tf
from matplotlib.cbook import iterable
from control.matlab import ss

from modelicares._freqplot import bode_plot, nyquist_plot
from modelicares.util import figure, add_hlines, add_vlines, chars_to_str
from modelicares._io import linloaders


class LinRes(object):
    """Class for Modelica_-based linearization results and methods to analyze
    those results

    This class contains two user-accessible methods:

    - :meth:`bode` - Create a Bode plot of the system's response

    - :meth:`fbase` - Return the base filename from which the data was loaded,
      without the directory or file extension

    - :meth:`nyquist` - Create a Nyquist plot of the system's response

    - :meth:`to_tf` - Return a transfer function given input and output names

    Attributes:

    - *fname* - filename from which the data was loaded, with the directory and
      file extension

    - *sys* - State-space system as an instance of :class:`control.StateSpace`

         It contains:

         - *A*, *B*, *C*, *D*: Matrices of the linear system

              .. code-block:: modelica

                 der(x) = A*x + B*u;
                      y = C*x + D*u;

         - *state_names*: List of names of the states (*x*)

         - *input_names*: List of names of the inputs (*u*)

         - *output_names*: List of names of the outputs (*y*)
    """

    def __init__(self, fname='dslin.mat', tool=None):
        """Upon initialization, load Modelica_ linearization results from a
        file.

        **Arguments:**

        - *fname*: Name of the file (may include the path)

             The file extension ('.mat') is optional.  The file must contain
             four matrices:  *Aclass* (specifies the class name, which must be
             "AlinearSystem"), *nx*, *xuyName*, and *ABCD*.

        **Example:**

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID')
        """

        from modelicares._io.dymola import linloader
        self.sys = linloader(fname)
        # Try to load as OpenModelica/Dymola.
        # Load the file and store the data.
        #for loader in linloaders:
        #    self.sys = loader(fname)
            #try:
            #    self.sys = loader(fname)
            #except IOError:
            #    raise
            #except:
            #    continue
            #else:
            #    break

        # Save the filename.
        self.fname = fname

# TODO: support tool argument, save it as an attribute and list in doc as argument and attribute.


    def fbase(self):
        """Return the base filename from which the data was loaded, without the
        directory or file extension.
        """
        return os.path.splitext(os.path.split(self.fname)[1])[0]


    def __repr__(self):
        """Return a formal description of the :class:`LinRes` instance.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID.mat')
           >>> lin # doctest: +ELLIPSIS
           LinRes('...PID.mat')
        """
        return "%s('%s')" % (self.__class__.__name__,
                             os.path.join(self.dir, self.fbase + '.mat'))
        # Note:  The class name is indirectly inquired so that this method will
        # still be valid if the class is extended.

    def __str__(self):
        """Return an informal description of the :class:`LinRes` instance.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID.mat')
           >>> print(lin) # doctest: +ELLIPSIS
           Modelica linearization results from "...PID.mat"
        """
        return ('Modelica linearization results from "%s"' %
                os.path.join(self.dir, self.fbase + '.mat'))

    def __repr__(self):
        """Return a formal description of the :class:`LinRes` instance.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID.mat')
           >>> lin # doctest: +ELLIPSIS
           LinRes('...PID.mat')
        """
        return "{Class}('{fname}')".format(Class=self.__class__.__name__,
                                           fname=self.fname)
        # Note:  The class name is inquired so that this method will still be
        # correct if the class is extended.


    def __str__(self):
        """Return an informal description of the :class:`LinRes` instance.

        **Example:**

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID.mat')
           >>> print(lin) # doctest: +ELLIPSIS
           Modelica linearization results from "...PID.mat"
        """
        return 'Modelica linearization results from "{f}"'.format(f=self.fname)

    def _to_siso(self, i_u, i_y):
        """Return a SISO system given input and output indices.
        """
        return ss(self.sys.A,         self.sys.B[:, i_u],
                  self.sys.C[i_y, :], self.sys.D[i_y, i_u])

    def to_tf(self, i_u=None, i_y=None):
        """Return a transfer function given input and output names.

        **Arguments:**

        - *i_u*: Index or name of the input

             This must be specified unless the system has only one input.

        - *i_y*: Index or name of the output

             This must be specified unless the system has only one output.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID')
           >>> lin.to_tf()
           (array([[  11.,  102.,  200.]]), array([   1.,  100.,    0.]))
        """
        # Get the input index.
        if i_u is None:
            if len(self.sys.input_names) == 1:
                i_u = 0
            else:
                raise IndexError("i_u must be specified since this is a MI system.")
        elif isinstance(i_u, basestring):
            try:
                i_u = self.sys.input_names.index(i_u)
            except ValueError:
                raise(ValueError('The input "%s" is invalid.' % i_u))

        # Get the output index.
        if i_y is None:
            if len(self.sys.output_names) == 1:
                i_y = 0
            else:
                raise IndexError("i_y must be specified since this is a MO system.")
        elif isinstance(i_y, basestring):
            try:
                i_y = self.sys.output_names.index(i_y)
            except ValueError:
                raise(ValueError('The output "%s" is invalid.' % i_y))

        # Return the TF.
        return ss2tf(self.sys.A,         self.sys.B,
                     self.sys.C[i_y, :], self.sys.D[i_y, :], input=i_u)

    def bode(self, axes=None, pairs=None, label='bode',
             title=None, colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
             styles=[(None,None), (3,3), (1,1), (3,2,1,2)], **kwargs):
        """Create a Bode plot of the system's response.

        The Bode plots of a MIMO system are overlayed. This is different than
        MATLAB\ :sup:`®`, which creates an array of subplots.

        **Arguments:**

        - *axes*: Tuple (pair) of axes for the magnitude and phase plots

             If *axes* is not provided, then axes will be created in a new
             figure.

        - *pairs*: List of (input index, output index) tuples of each transfer
          function to be evaluated

             If not provided, all of the transfer functions will be plotted.

        - *label*: Label for the figure (ignored if *axes* is provided)

             This will be used as the base filename if the figure is saved.

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be "Bode Plot
             of *fbase*", where *fbase* is the base filename of the data.  Use
             '' for no title.

        - *colors*: Color or list of colors that will be used sequentially

             Each may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *styles*: Line/dash style or list of line/dash styles that will be
          used sequentially

             Each style is a string representing a linestyle (e.g., "--") or a
             tuple of on/off lengths representing dashes.  Use "" for no line
             and "-" for a solid line.

             .. Seealso::
                http://matplotlib.sourceforge.net/api/collections_api.html

        - *\*\*kwargs*: Additional arguments for :meth:`control.freqplot.bode`

        **Returns:**

        1. *axes*: Tuple (pair) of axes for the magnitude and phase plots

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes, save
           >>> from numpy import pi, logspace

           >>> lin = LinRes('examples/PID.mat')
           >>> lin.bode(label='examples/PID-bode', omega=2*pi*logspace(-2, 3),
           ...          title="Bode Plot of Modelica.Blocks.Continuous.PID") # doctest: +ELLIPSIS
           (<matplotlib.axes...AxesSubplot object at 0x...>, <matplotlib.axes...AxesSubplot object at 0x...>)
           >>> save()
           Saved examples/PID-bode.pdf
           Saved examples/PID-bode.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()

        .. only:: html

           .. image:: ../examples/PID-bode.png
              :scale: 70 %
              :alt: example for LinRes.bode()

        .. only:: latex

           .. figure:: ../examples/PID-bode.pdf
              :scale: 80 %

              Results of example for :meth:`LinRes.bode`.
        """
        # Create axes if necessary.
        if axes is None or (None, None):
            fig = figure(label)
            axes = (fig.add_subplot(211), fig.add_subplot(212))

        # Create a title if necessary.
        if title is None:
            title = "Bode Plot of %s" % self.fbase

        # Set up the color(s) and line style(s).
        if not iterable(colors):
            # Use the single color for all plots.
            colors = (colors,)
        if not iterable(styles):
            # Use the single line style for all plots.
            styles = [styles]
        elif type(styles[0]) is int:
            # One dashes tuple has been provided; use its value for all plots.
            styles = [styles]
        n_colors = len(colors)
        n_styles = len(styles)

        # If input/output pair(s) aren't specified, generate a list of all
        # pairs.
        if not pairs:
            pairs = [(i_u, i_y) for i_u in range(self.sys.inputs)
                     for i_y in range(self.sys.outputs)]

        # Create the plots.
        for i, (i_u, i_y) in enumerate(pairs):
            bode_plot(self._to_siso(i_u, i_y),
                      label='$Y_{%i}/U_{%i}$' % (i_y, i_u),
                      Hz=True, color=colors[np.mod(i, n_colors)], axes=axes,
                      style=styles[np.mod(i, n_styles)], **kwargs)
            # Note: ._freqplot.bode() is currently only implemented for
            # SISO systems.
            # 5/23/11: Since ._freqplot.bode() already uses subplots for
            # the magnitude and phase plots, it would be difficult to modify
            # the code to put the Bode plots of a MIMO system into an array of
            # subfigures like MATLAB does.

        # Decorate and finish.
        axes[0].set_title(title)
        if len(pairs) > 1:
            axes[0].legend()
            axes[1].legend()
        return axes

    def nyquist(self, ax=None, pairs=None, label="nyquist", title=None,
                xlabel="Real Axis", ylabel="Imaginary Axis",
                colors=['b','g','r','c','m','y','k'], **kwargs):
        """Create a Nyquist plot of the system's response.

        The Nyquist plots of a MIMO system are overlayed. This is different
        than MATLAB\ :sup:`®`, which creates an array of subplots.

        **Arguments:**

        - *ax*: Axes onto which the Nyquist diagram should be plotted

             If *ax* is not provided, then axes will be created in a new figure.

        - *pairs*: List of (input index, output index) tuples of each transfer
          function to be evaluated

             If not provided, all of the transfer functions will be plotted.

        - *label*: Label for the figure (ignored if ax is provided)

             This will be used as the base filename if the figure is saved.

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be "Nyquist
             Plot of *fbase*", where *fbase* is the base filename of the data.
             Use '' for no title.

        - *xlabel*: x-axis label

        - *ylabel*: y-axis label

        - *colors*: Color or list of colors that will be used sequentially

             Each may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *\*\*kwargs*: Additional arguments for
          :meth:`control.freqplot.nyquist`

        **Returns:**

        1. *ax*: Axes of the Nyquist plot

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes, save
           >>> from numpy import pi, logspace

           >>> lin = LinRes('examples/PID.mat')
           >>> lin.nyquist(label='examples/PID-nyquist',
           ...             omega=2*pi*logspace(0, 3, 61), labelFreq=20,
           ...             title="Nyquist Plot of Modelica.Blocks.Continuous.PID") # doctest: +ELLIPSIS
           <matplotlib.axes...AxesSubplot object at 0x...>
           >>> save()
           Saved examples/PID-nyquist.pdf
           Saved examples/PID-nyquist.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()

        .. only:: html

           .. image:: ../examples/PID-nyquist.png
              :scale: 70 %
              :alt: example for LinRes.nyquist()

        .. only:: latex

           .. figure:: ../examples/PID-nyquist.pdf
              :scale: 70 %

              Results of example for :meth:`LinRes.nyquist`.
        """
        # Create axes if necessary.
        if not ax:
            fig = figure(label)
            ax = fig.add_subplot(111, aspect='equal')

        # Create a title if necessary.
        if title is None:
            title = "Nyquist Plot of %s" % self.fbase

        # Set up the color(s).
        if not iterable(colors):
            # Use the single color for all plots.
            colors = (colors,)
        n_colors = len(colors)

        # If input/output pair(s) aren't specified, generate a list of all
        # pairs.
        if not pairs:
            pairs = [(i_u, i_y) for i_u in range(self.sys.inputs)
                     for i_y in range(self.sys.outputs)]

        # Create the plots.
        for i, (i_u, i_y) in enumerate(pairs):
            nyquist_plot(self._to_siso(i_u, i_y),
                         label=r'$Y_{%i}/U_{%i}$' % (i_y, i_u), mark=False,
                         color=colors[np.mod(i, n_colors)], ax=ax, **kwargs)
            # Note: ._freqplot.nyquist() is currently only implemented
            # for SISO systems.

        # Decorate and finish.
        if len(pairs) > 1:
            ax.legend()
        add_hlines(ax, color='k', linestyle='--', linewidth=0.5)
        add_vlines(ax, color='k', linestyle='--', linewidth=0.5)
        ax.set_title(title)
        if xlabel: # Without this check, xlabel=None will give a label of "None".
            ax.set_xlabel(xlabel)
        if ylabel: # Same purpose
            ax.set_ylabel(ylabel)
        return ax

if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
