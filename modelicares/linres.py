#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Load, analyze, and plot the result of linearizing a Modelica_ model.

This module contains one class: :class:`LinRes`.  It relies on python-control_,
which is included in the distribution.

.. _Modelica: http://www.modelica.org/
.. _python-control: http://sourceforge.net/apps/mediawiki/python-control
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
import numpy as np


from scipy.io import loadmat
from matplotlib.cbook import iterable

from control.matlab import ss
from freqplot import bode_plot, nyquist_plot
from modelicares.base import figure, add_hlines, add_vlines

class LinRes(object):
    """Class for Modelica_-based linearization results and methods to analyze
    those results

    This class contains two user-accessible methods:

    - :meth:`bode` - Create a Bode plot of the system's response

    - :meth:`nyquist` - Create a Nyquist plot of the system's response
    """

    def __init__(self, fname='dslin.mat'):
        """On initialization, load and preprocess a linearized Modelica_ model
        (MATLAB\ :sup:`®` format).  
        
        The model is in state space:

        .. code-block:: modelica

             der(x) = A*x + B*u;
                  y = C*x + D*u;

        The linear system is stored as *sys* within this class.  It is an
        instance of :class:`control.StateSpace`, which emulates the structure
        of a continuous-time model in MATLAB\ :sup:`®` (e.g., the output of
        :meth:`ss` in MATLAB\ :sup:`®`).  It contains:

           - *A*, *B*, *C*, *D*: Matrices of the linear system

           - *stateName*: List of name(s) of the states (x)

           - *inputName*: List of name(s) of the inputs (u)

           - *outputName*: List of name(s) of the outputs (y)

        **Arguments:**

        - *fname*: Name of the file (may include the path)

             The file extension ('.mat') is optional.  The file must contain
             four matrices:  *Aclass* (specifies the class name, which must be
             "AlinearSystem"), *nx*, *xuyName*, and *ABCD*.

        **Example:**

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID')
        """
        self._load(fname)

        # Save the base filename and the directory.
        self.dir, self.fbase = os.path.split(fname)
        self.dir = os.path.abspath(self.dir)
        self.fbase = os.path.splitext(self.fbase)[0]

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

    def _load(self, fname='dslin.mat'):
        """Load a linearized Modelica_ model from *fname*.

        See :meth:`__init__` for details about the file format.

        Returns *None* if the file contains simulation results rather than
        linearization results.  Otherwise, it raises an error.
        """
        # This performs the task of tloadlin.m from Dymola version 7.4:
        #     on Unix/Linux: /opt/dymola/mfiles/traj/tloadlin.m
        #     on Windows: C:\Program Files\Dymola 7.4\Mfiles\traj\tloadlin.m

        # Load the file.
        try:
            dslin = loadmat(fname)
        except IOError:
            print('File "%s" could not be loaded.  Check that it exists.' %
                  fname)
            raise

        # Check if the file contains the correct variable names.
        assert 'Aclass' in dslin, ('There is no linear system in file "%s" '
            '(matrix "Aclass" is missing).' % fname)
        assert 'nx' in dslin, ('There is no linear system in file "%s" '
            '(matrix "nx" is missing).' % fname)
        assert 'xuyName' in dslin, ('There is no linear system in file "%s" '
            '(matrix "xuyName" is missing).' % fname)
        assert 'ABCD' in dslin, ('There is no linear system in file "%s" '
            '(matrix "ABCD" is missing).' % fname)

        # Check if the file has the correct class name.
        if not dslin['Aclass'][0].startswith('AlinearSystem'):
            if dslin['Aclass'][0].startswith('Atrajectory'):
                return None # The file contains simulation results.
            raise AssertionError('File "%s" is not of class AlinearSystem or '
                                 'Atrajectory.' % fname)

        # Extract variables from the dictionary (for convenience).
        ABCD = dslin['ABCD']
        xuyName = dslin['xuyName']

        # Check if the matrices have compatible dimensions.
        n_x = dslin['nx'][0]
        dim1 = ABCD.shape[0]
        dim2 = ABCD.shape[1]
        assert n_x <= dim1 and n_x <= dim2, (
            'nx > number of rows/columns of matrix ABCD in file "%s"' % fname)
        n_u = dim2 - n_x
        n_y = dim1 - n_x
        assert n_x > 0 and n_y > 0, ("As of version 0.4b, the control module "
            "cannot accept systems with empty matrixes.")

        # Extract the matrices.
        if n_x > 0:
            A = ABCD[:n_x, :n_x]
            if n_u > 0:
                B = ABCD[:n_x, n_x:]
            else:
                B = []
            if n_y > 0:
                C = ABCD[n_x:, :n_x]
            else:
                C = []
        else:
            A = []
            B = []
            C = []
        if n_u > 0 and n_y > 0:
            D = ABCD[n_x:, n_x:]
        else:
            D = []
        self.sys = ss(A, B, C, D)

        # Extract the names.
        if n_x > 0: # States
            self.sys.stateName = [name.rstrip() for name in xuyName[:n_x]]
        else:
            self.sys.stateName = []
        if n_u > 0: # Inputs
            self.sys.inputName = [name.rstrip() for name in xuyName[n_x:
                                                                    n_x+n_u]]
        else:
            self.sys.inputName = []
        if n_y > 0: # Outputs
            self.sys.outputName = [name.rstrip() for name in xuyName[n_x+n_u:]]
        else:
            self.sys.outputName = []

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
            title = r"Bode Plot of %s" % self.fbase

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
            # Extract the SISO TF. TODO: Is there a better way to do this?
            sys = ss(self.sys.A, self.sys.B[:, i_u], self.sys.C[i_y, :],
                     self.sys.D[i_y, i_u])
            bode_plot(sys, Hz=True, label=r'$Y_{%i}/U_{%i}$' % (i_y, i_u),
                      color=colors[np.mod(i, n_colors)], axes=axes,
                      style=styles[np.mod(i, n_styles)], **kwargs)
            # Note: controls.freqplot.bode() is currently only implemented for
            # SISO systems.
            # 5/23/11: Since controls.freqplot.bode() already uses subplots for
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

        .. testsetup::
           >>> from modelicares import closeall
           >>> closeall()

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
            title = r"Nyquist Plot of %s" % self.fbase

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
            # Extract the SISO TF. TODO: Is there a better way to do this?
            sys = ss(self.sys.A, self.sys.B[:, i_u], self.sys.C[i_y, :],
                     self.sys.D[i_y, i_u])
            nyquist_plot(sys, mark=False, label=r'$Y_{%i}/U_{%i}$' % (i_y, i_u),
                         color=colors[np.mod(i, n_colors)], ax=ax, **kwargs)
            # Note: controls.freqplot.nyquist() is currently only implemented
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
    exit()
