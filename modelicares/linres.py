#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This submodule contains classes to help load, analyze, and plot results from
Modelica_ linearizations:

- :class:`LinRes` - Class to load, contain, and analyze results from a Modelica_
  linearization

- :class:`LinResList` - Specialized list of linearization results
  (:class:`LinRes` instances)


.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915,
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=C0103, E0611, E1101, W0102

import os
import numpy as np

from control.matlab import ss
from functools import wraps
from matplotlib.cbook import iterable
from scipy.signal import ss2tf
from six import string_types

from modelicares import util
from modelicares._freqplot import bode_plot, nyquist_plot
from modelicares._res import Res, ResList

# File loading functions
from modelicares._io.dymola import loadlin as dymola
LOADERS = [('dymola', dymola)] # LinRes tries these in order.
# All of the keys should be in lowercase.

def _from_names(func):
    """Return a method that accepts names or indices to identify system inputs
    and outputs, given a method that only accepts indices (*func*).

    I.e., a decorator to accept names or indices to identify inputs and outputs
    """
    @wraps(func)
    def wrapped(self, iu=None, iy=None):
        """Method that accepts names or indices to identify system inputs and
        outputs

        **Arguments:**

        - *iu*: Index or name of the input

             This must be specified unless the system has only one input.

        - *iy*: Index or name of the output

             This must be specified unless the system has only one output.
        """
        # Get the input index.
        if iu is None:
            if len(self.sys.input_names) == 1:
                iu = 0
            else:
                raise IndexError("iu must be specified since this is a MI "
                                 "system.")
        elif not isinstance(iu, int):
            try:
                iu = self.sys.input_names.index(iu)
            except ValueError:
                raise ValueError('The input "%s" is invalid.' % iu)

        # Get the output index.
        if iy is None:
            if len(self.sys.output_names) == 1:
                iy = 0
            else:
                raise IndexError("iy must be specified since this is a MO "
                                 "system.")
        elif not isinstance(iy, int):
            try:
                iy = self.sys.output_names.index(iy)
            except ValueError:
                raise ValueError('The output "%s" is invalid.' % iy)

        return func(self, iu, iy)

    return wrapped


class LinRes(Res):
    """Class for Modelica_-based linearization results and methods to analyze
    those results

    **Initialization arguments:**

    - *fname*: Name of the file (including the directory if necessary)

         The file must contain four matrices:  *Aclass* (specifies the class
         name, which must be "AlinearSystem"), *nx*, *xuyName*, and *ABCD*.

    - *tool*: String indicating the linearization tool that created the file
      and thus the function to be used to load it

         By default, the available functions are tried in order until one
         works (or none do).

    **Methods:**

    - :meth:`bode` - Create a Bode plot of the system's response.

    - :meth:`nyquist` - Create a Nyquist plot of the system's response.

    - :meth:`to_siso` - Return a SISO state-space system given input and output
      names.

    - :meth:`to_tf` - Return a transfer function given input and output names.

    **Properties:**

    - *dirname* - Directory from which the variables were loaded

    - *fbase* - Base filename from which the variables were loaded, without
      the directory or extension

    - *fname* - Filename from which the variables were loaded, with absolute
      path

    - *sys* - State-space system as an instance of :class:`control.StateSpace`

         It contains:

         - *A*, *B*, *C*, *D*: Matrices of the linear system

              .. code-block:: modelica

                 der(x) = A*x + B*u;
                      y = C*x + D*u;

         - *state_names*: List of names of the states (*x*)

         - *input_names*: List of names of the inputs (*u*)

         - *output_names*: List of names of the outputs (*y*)

    - *tool* - String indicating the function used to load the results (named
      after the corresponding Modelica_ tool)

    **Example:**

    >>> lin = LinRes('examples/PID.mat')
    >>> print(lin) # doctest: +ELLIPSIS
    Modelica linearization results from .../examples/PID.mat
    """

    def __init__(self, fname='dslin.mat', tool=None):
        """Upon initialization, load Modelica_ linearization results from a
        file.

        See the top-level class documentation.
        """

        # Load the file.
        if tool is None:
            # Load the file and store the data.
            for (tool, load) in LOADERS[:-1]:
                try:
                    self.sys = load(fname)
                except IOError:
                    raise
                except Exception as exception:
                    print("The %s loader gave the following error message:\n%s"
                          % (tool, exception.args[0]))
                    print("Trying the next loader...")
                    continue
                else:
                    break
            (tool, load) = LOADERS[-1]
        else:
            loaderdict = dict(LOADERS)
            try:
                load = loaderdict[tool.lower()]
            except:
                raise LookupError('"%s" is not one of the available tools '
                                  '("%s").' % (tool,
                                               '", "'.join(list(loaderdict))))
        self.sys = load(fname)

        # Remember the tool and filename.
        self.tool = tool
        super(LinRes, self).__init__(fname)

    def __str__(self):
        """Return an informal description of the :class:`LinRes` instance.

        **Example:**

        >>> lin = LinRes('examples/PID.mat')
        >>> print(lin) # doctest: +ELLIPSIS
        Modelica linearization results from .../examples/PID.mat
        """
        return "Modelica linearization results from " + self.fname

    @_from_names
    def to_siso(self, iu, iy):
        """Return a SISO system given input and output indices.

        **Arguments:**

        - *iu*: Index or name of the input

             This must be specified unless the system has only one input.

        - *iy*: Index or name of the output

             This must be specified unless the system has only one output.

        **Example:**

        >>> lin = LinRes('examples/PID.mat')
        >>> lin.to_siso()
        A = [[   0.    0.]
         [   0. -100.]]
        <BLANKLINE>
        B = [[   2.]
         [ 100.]]
        <BLANKLINE>
        C = [[  1. -10.]]
        <BLANKLINE>
        D = [[ 11.]]
        <BLANKLINE>
        """
        return ss(self.sys.A, self.sys.B[:, iu],
                  self.sys.C[iy, :], self.sys.D[iy, iu])

    @_from_names
    def to_tf(self, iu, iy):
        """Return a transfer function given input and output names.

        **Arguments:**

        - *iu*: Index or name of the input

             This must be specified unless the system has only one input.

        - *iy*: Index or name of the output

             This must be specified unless the system has only one output.

        **Example:**

        >>> lin = LinRes('examples/PID.mat')
        >>> lin.to_tf()
        (array([[  11.,  102.,  200.]]), array([   1.,  100.,    0.]))
        """
        # Return the TF.
        return ss2tf(self.sys.A, self.sys.B,
                     self.sys.C[iy, :], self.sys.D[iy, :], input=iu)

    def bode(self, axes=None, pairs=None, label='bode',
             title=None, colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
             styles=[(None, None), (3, 3), (1, 1), (3, 2, 1, 2)], **kwargs):
        r"""Create a Bode plot of the system's response.

        The Bode plots of a MIMO system are overlayed. This is different than
        MATLAB\ :sup:`®`, which creates an array of subplots.

        **Arguments:**

        - *axes*: Tuple (pair) of axes for the magnitude and phase plots

             If *axes* is not provided, then axes will be created in a new
             figure.

        - *pairs*: List of (input name or index, output name or index) tuples of
          each transfer function to be evaluated

             By default, all of the transfer functions will be plotted.

        - *label*: Label for the figure (ignored if *axes* is provided)

             This is used as the base filename if the figure is saved using
             :meth:`~modelicares.util.save` or
             :meth:`~modelicares.util.saveall`.

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be "Bode plot
             of fbase", where fbase is the base filename of the data.  Use ''
             for no title.

        - *colors*: Color or list of colors that will be used sequentially

             Each may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *styles*: Line/dash style or list of line/dash styles that will be
          used sequentially

             Each style is a string representing a linestyle (e.g., '--') or a
             tuple of on/off lengths representing dashes.  Use '' for no line
             or '-' for a solid line.

             .. Seealso::
                http://matplotlib.sourceforge.net/api/collections_api.html

        - *\*\*kwargs*: Additional plotting arguments:

             - *freqs*: List or frequencies or tuple of (min, max) frequencies
               over which to plot the system response.

                  If *freqs* is *None*, then an appropriate range will be
                  determined automatically.

             - *in_Hz*: If *True* (default), the frequencies (*freqs*) are in
               Hz and should be plotted in Hz (otherwise, rad/s)

             - *in_dB*: If *True* (default), plot the magnitude in dB

             - *in_deg*: If *True* (default), plot the phase in degrees
               (otherwise, radians)

             Other keyword arguments are passed to
             :meth:`matplotlib.pyplot.plot`.

        **Returns:**

        1. *axes*: Tuple (pair) of axes for the magnitude and phase plots

        **Example:**

        .. plot:: examples/PID-bode.py
           :alt: Bode plot of PID
        """
        # Create axes if necessary.
        if axes is None or (None, None):
            fig = util.figure(label)
            axes = (fig.add_subplot(211), fig.add_subplot(212))

        # Create a title if necessary.
        if title is None:
            title = "Bode plot of %s" % self.fbase

        # Set up the color(s) and line style(s).
        if not iterable(colors):
            # Use the single color for all plots.
            colors = (colors,)
        if not iterable(styles) or isinstance(styles[0], int):
            # Use the single line or dashes style for all plots.
            styles = [styles]
        n_colors = len(colors)
        n_styles = len(styles)

        # If input/output pair(s) aren't specified, generate a list of all
        # pairs.
        if not pairs:
            pairs = [(iu, iy) for iu in range(self.sys.inputs)
                     for iy in range(self.sys.outputs)]

        # Create the plots.
        for i, (iu, iy) in enumerate(pairs):
            style = styles[np.mod(i, n_styles)]
            if isinstance(style, string_types):
                kwargs['linestyle'] = style
                kwargs.pop('dashes', None)
            else:
                kwargs['dashes'] = style
                kwargs.pop('linestyle', None)
            bode_plot(self.to_siso(iu, iy), axes=axes,
                      label='$Y_{%i}/U_{%i}$' % (iy, iu),
                      color=colors[np.mod(i, n_colors)], **kwargs)
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
                xlabel="Real axis", ylabel="Imaginary axis",
                colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'], **kwargs):
        r"""Create a Nyquist plot of the system's response.

        The Nyquist plots of a MIMO system are overlayed. This is different
        than MATLAB\ :sup:`®`, which creates an array of subplots.

        **Arguments:**

        - *ax*: Axes onto which the Nyquist diagram should be plotted

             If *ax* is not provided, then axes will be created in a new figure.

        - *pairs*: List of (input name or index, output name or index) tuples of
          each transfer function to be evaluated

             By default, all of the transfer functions will be plotted.

        - *label*: Label for the figure (ignored if ax is provided)

             This is used as the base filename if the figure is saved using
             :meth:`~modelicares.util.save` or
             :meth:`~modelicares.util.saveall`.

        - *title*: Title for the figure

             If *title* is *None* (default), then the title will be "Nyquist
             plot of fbase", where fbase is the base filename of the data.  Use
             '' for no title.

        - *xlabel*: x-axis label

        - *ylabel*: y-axis label

        - *colors*: Color or list of colors that will be used sequentially

             Each may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *\*\*kwargs*: Additional plotting arguments:

             - *freqs*: List or frequencies or tuple of (min, max) frequencies
               over which to plot the system response.

                  If *freqs* is *None*, then an appropriate range will be
                  determined automatically.

             - *in_Hz*: If *True* (default), the frequencies (*freqs*) are in
               Hz and should be plotted in Hz (otherwise, rad/s)

             - *mark*: *True*, if the -1 point should be marked on the plot

             - *show_axes*: *True*, if the axes should be shown

             - *skip*: Mark every nth frequency on the plot with a dot

                  If *skip* is 0 or *None*, then the frequencies are not marked.

             - *label_freq*: If *True*, if the marked frequencies should be
               labeled

             Other keyword arguments are passed to
             :meth:`matplotlib.pyplot.plot`.

        **Returns:**

        1. *ax*: Axes of the Nyquist plot

        **Example:**

        .. plot:: examples/PID-nyquist.py
           :alt: Nyquist plot of PID
        """
        # Create axes if necessary.
        if not ax:
            fig = util.figure(label)
            ax = fig.add_subplot(111, aspect='equal')

        # Create a title if necessary.
        if title is None:
            title = "Nyquist plot of %s" % self.fbase

        # Set up the color(s).
        if not iterable(colors):
            # Use the single color for all plots.
            colors = (colors,)
        n_colors = len(colors)

        # If input/output pair(s) aren't specified, generate a list of all
        # pairs.
        if not pairs:
            pairs = [(iu, iy) for iu in range(self.sys.inputs)
                     for iy in range(self.sys.outputs)]

        # Create the plots.
        for i, (iu, iy) in enumerate(pairs):
            nyquist_plot(self.to_siso(iu, iy), ax=ax,
                         label=r'$Y_{%i}/U_{%i}$' % (iy, iu),
                         color=colors[np.mod(i, n_colors)], **kwargs)
            # Note: modelicares._freqplot.nyquist() is currently only
            # implemented for SISO systems.


        # Decorate.
        if len(pairs) > 1:
            ax.legend()
        ax.set_title(title)
        if xlabel: # Without this check, xlabel=None will give label of "None".
            ax.set_xlabel(xlabel)
        if ylabel: # Same purpose
            ax.set_ylabel(ylabel)

        return ax


def _get_lins(fnames):
    """Return a list of :class:`LinRes` instances from a list of filenames.

    No errors are given unless no files could be loaded.
    """
    lins = []
    for fname in fnames:
        try:
            lins.append(LinRes(fname))
        except:
            continue
    assert len(lins) > 0, "No linearizations were loaded."
    return lins


class LinResList(ResList):
    r"""Specialized list of linearization results

    **Initialization signatures:**

    - :class:`LinResList`\(): Returns an empty linearization list

    - :class:`LinResList`\(*lins*), where lins is a list of :class:`LinRes`
      instances:  Casts the list into a :class:`LinResList`

    - :class:`LinResList`\(*filespec*), where *filespec* is a filename or
      directory, possibly with wildcards a la `glob
      <https://docs.python.org/2/library/glob.html>`_:  Returns a
      :class:`LinResList` of :class:`LinRes` instances loaded from the
      matching or contained files

         The filename or directory must include the absolute path or be
         resolved to the current directory.

         An error is only raised if no files can be loaded.

    - :class:`LinResList`\(*filespec1*, *filespec2*, ...): Loads all files
      matching or contained by *filespec1*, *filespec2*, etc. as above.

         Each file will be opened once at most; duplicate filename matches are
         ignored.

    **Built-in methods:**

    The entries are :class:`LinRes` instances, but linearizations can be
    specified via filename when initializing or appending the list.  The list
    has all of the methods of a standard Python_ list (e.g.,
    + or `__add__
    <https://docs.python.org/2/reference/datamodel.html#object.__add__>`_/`__radd__
    <https://docs.python.org/2/reference/datamodel.html#object.__radd__>`_,
    :meth:`clear`,
    **in** or `__contains__
    <https://docs.python.org/2/reference/datamodel.html#object.__contains__>`_,
    **del** or `__delitem__
    <https://docs.python.org/2/reference/datamodel.html#object.__delitem__>`_,
    `__getitem__
    <https://docs.python.org/2/reference/datamodel.html#object.__getitem__>`_,
    += or `__iadd__
    <https://docs.python.org/2/reference/datamodel.html#object.__iadd__>`_,
    \*= or `__imul__
    <https://docs.python.org/2/reference/datamodel.html#object.__imul__>`_,
    :meth:`iter` or `__iter__
    <https://docs.python.org/2/reference/datamodel.html#object.__iter__>`_,
    :meth:`copy`,
    :meth:`extend`,
    :meth:`index`,
    :meth:`insert`,
    :meth:`len` or `__len__
    <https://docs.python.org/2/library/functions.html#len>`_,
    \* or `__mul__
    <https://docs.python.org/2/reference/datamodel.html#object.__mul__>`_/`__rmul__
    <https://docs.python.org/2/reference/datamodel.html#object.__rmul__>`_,
    :meth:`pop`,
    :meth:`remove`,
    :meth:`reverse`,
    :meth:`reversed` or `__reversed__
    <https://docs.python.org/2/reference/datamodel.html#object.__reversed__>`_,
    = or `__setitem__
    <https://docs.python.org/2/reference/datamodel.html#object.__setitem__>`_,
    :meth:`__sizeof__`, and :meth:`sort`).  By default, the :meth:`sort` method
    orders the list of linearizations by the full path of the result files.

    **Overloaded methods:**

    - :meth:`append` - Add linearization(s) to the end of the list of
      linearizations (accepts a :class:`LinRes` instance, directory, or
      filename).

    **Additional methods:**

    - :meth:`bode` - Plot the linearizations onto a single Bode diagram.

    - :meth:`nyquist` - Plot the linearizations onto a single Bode diagram.

    **Properties:**

    - *basedir* - Highest common directory that the result files share

    - Also, the properties of :class:`LinRes` (*basename*, *dirname*, *fname*,
      *sys*, and *tool*) can be retrieved as a list across all of the
      linearizations; see the example below.

    **Example:**

    >>> lins = LinResList('examples/PID/*/')
    >>> lins.dirname # doctest: +SKIP
    ['.../examples/PID/1', '.../examples/PID/2']

    .. testcleanup::

       >>> lins.sort()
       >>> lins.dirname # doctest: +ELLIPSIS
       ['.../examples/PID/1', '.../examples/PID/2']

    .. _Python: http://www.python.org
    """

    def __init__(self, *args):
        """Initialize as a list of :class:`LinRes` instances, loading files as
        necessary.

        See the top-level class documentation.
        """
        if not args:
            super(LinResList, self).__init__([])

        elif isinstance(args[0], string_types): # Filenames or directories
            try:
                fnames = util.multiglob(args)
            except TypeError:
                raise TypeError(
                    "The linearization list can only be initialized by "
                    "providing a list of LinRes instances or a series of "
                    "arguments, each of which is a filename or directory.")
            list.__init__(self, _get_lins(fnames))

        elif len(args) == 1: # List or iterable of LinRes instances
            lins = list(args[0])
            for lin in lins:
                assert isinstance(lin, LinRes), ("All entries in the list must "
                                                 "be LinRes instances.")
            list.__init__(self, lins)

        else:
            raise TypeError(
                "The linearization list can only be initialized by "
                "providing a list of LinRes instances or a series of "
                "arguments, each of which is a filename or directory.")

    def append(self, item):
        """Add linearization(s) to the end of the list of linearizations.

        **Arguments:**

        - *item*: :class:`LinRes` instance or a file specification

             The file specification may be a filename or directory, possibly
             with wildcards a la `glob
             <https://docs.python.org/2/library/glob.html>`_, where
             linearization results can be loaded by :class:`LinRes`.  The
             filename or directory must include the absolute path or be resolved
             to the current directory.  An error is only raised if no files can
             be loaded.

         Unlike the `append
         <https://docs.python.org/2/tutorial/datastructures.html>`_ method of a
         standard Python_ list, this method may add more than one item.  If
         *item* is a directory or a wildcarded filename, it may match multiple
         valid files.

         Linearization results will be appended to the list even if they are
         already included.

        **Example:**

        >>> lins = LinResList('examples/PID/*/')
        >>> lins.append('examples/PID.mat')
        >>> print(lins) # doctest: +SKIP
        List of linearization results (LinRes instances) from the following files
        in the .../examples directory:
           PID/1/dslin.mat
           PID/2/dslin.mat
           PID.mat

        .. testcleanup::

           >>> lins.sort()
           >>> print(lins) # doctest: +ELLIPSIS
           List of linearization results (LinRes instances) from the following files
           in the .../examples directory:
              PID.mat
              PID/1/dslin.mat
              PID/2/dslin.mat
        """
        if isinstance(item, LinRes):
            list.append(self, item)
        else:
            assert isinstance(item, string_types), (
                "The linearization list can only be appended by providing a "
                "LinRes instance, filename, or directory.")
            fnames = util.multiglob(item)
            self.extend(LinResList(_get_lins(fnames)))

    def __str__(self):
        """Return str(self).

        This provides a readable description of the :class:LinResList`.

        **Example:**

        >>> lins = LinResList('examples/PID/*/')
        >>> print(lins) # doctest: +SKIP
        List of linearization results (LinRes instances) from the following files
        in the .../examples/PID directory:
           1/dslin.mat
           2/dslin.mat

        .. testcleanup::

           >>> lins.sort()
           >>> print(lins) # doctest: +ELLIPSIS
           List of linearization results (LinRes instances) from the following files
           in the .../examples/PID directory:
              1/dslin.mat
              2/dslin.mat
        """
        if len(self) == 0:
            return "Empty list of linearization results"
        elif len(self) == 1:
            return ("List of linearization results (LinRes instance) from\n"
                    + self[0].fname)
        else:
            basedir = self.basedir
            string = ("List of linearization results (LinRes instances) from "
                      "the following files")
            string += ("\nin the %s directory:\n   "
                       % basedir if basedir else ":\n   ")
            string += "\n   ".join(self.fnames)
            return string

    def _get_labels(self, labels):
        """Create labels for the legend of a Bode or Nyquist plot.

        If *labels* is *None*, then no label will be used.  If it is an empty
        string (''), then the filenames will be used (resolved to the
        *basedir*).
        """
        if labels is None:
            try:
                labels = self.label
            except AttributeError:
                labels = self.fnames
        elif labels == '':
            labels = ['']*len(self)

        return labels

    def bode(self, axes=None, pair=(0, 0), label='bode', title="Bode plot",
             labels=None, colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
             styles=[(None, None), (3, 3), (1, 1), (3, 2, 1, 2)], leg_kwargs={},
             **kwargs):
        r"""Plot the linearizations onto a single Bode diagram.

        This method calls :meth:`LinRes.bode` from the included instances
        of :class:`LinRes`.

        **Arguments:**

        - *axes*: Tuple (pair) of axes for the magnitude and phase plots

             If *axes* is not provided, then axes will be created in a new
             figure.

        - *pair*: Tuple of (input name or index, output name or index) for the
          transfer function to be chosen from each system (applied to all)

             This is ignored if the system is SISO.

        - *label*: Label for the figure (ignored if axes is provided)

             This is used as the base filename if the figure is saved using
             :meth:`~modelicares.util.save` or
             :meth:`~modelicares.util.saveall`.

        - *title*: Title for the figure

        - *labels*: Label or list of labels for the legends

             If *labels* is *None*, then no label will be used.  If it is an
             empty string (''), then the base filenames will be used.

        - *colors*: Color or list of colors that will be used sequentially

             Each may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *styles*: Line/dash style or list of line/dash styles that will be
          used sequentially

             Each style is a string representing a linestyle (e.g., '--') or a
             tuple of on/off lengths representing dashes.  Use '' for no line
             and '-' for a solid line.

             .. Seealso::
                http://matplotlib.sourceforge.net/api/collections_api.html

        - *leg_kwargs*: Dictionary of keyword arguments for
          :meth:`matplotlib.pyplot.legend`

             If *leg_kwargs* is *None*, then no legend will be shown.

        - *\*\*kwargs*: Additional plotting arguments:

             - *freqs*: List or frequencies or tuple of (min, max) frequencies
               over which to plot the system response.

                  If *freqs* is *None*, then an appropriate range will be
                  determined automatically.

             - *in_Hz*: If *True* (default), the frequencies (*freqs*) are in
               Hz and should be plotted in Hz (otherwise, rad/s)

             - *in_dB*: If *True* (default), plot the magnitude in dB

             - *in_deg*: If *True* (default), plot the phase in degrees
               (otherwise, radians)

             Other keyword arguments are passed to
             :meth:`matplotlib.pyplot.plot`.

        **Returns:**

        1. *axes*: Tuple (pair) of axes for the magnitude and phase plots

        **Example:**

        .. plot:: examples/PIDs-bode.py
           :alt: Bode plot of PID with varying parameters
        """
        # Create axes if necessary.
        if not axes:
            fig = util.figure(label)
            axes = (fig.add_subplot(211), fig.add_subplot(212))

        # Process the labels input.
        labels = self._get_labels(labels)

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

        # Create the plots.
        for i, (lin, label) in enumerate(zip(self, labels)):
            style = styles[np.mod(i, n_styles)]
            if isinstance(style, string_types):
                kwargs['linestyle'] = style
                kwargs.pop('dashes', None)
            else:
                kwargs['dashes'] = style
                kwargs.pop('linestyle', None)
            if lin.sys.inputs > 1 or lin.sys.outputs > 1:
                sys = lin.to_siso(pair[0], pair[1])
            else:
                sys = lin.sys
            bode_plot(sys, label=label, color=colors[np.mod(i, n_colors)],
                      axes=axes, **kwargs)

        # Decorate and finish.
        axes[0].set_title(title)
        if leg_kwargs is not None:
            loc = leg_kwargs.pop('loc', 'best')
            axes[0].legend(loc=loc, **leg_kwargs)
            axes[1].legend(loc=loc, **leg_kwargs)
        return axes

    def nyquist(self, ax=None, pair=(0, 0), label='nyquist',
                title="Nyquist plot", xlabel="Real axis",
                ylabel="Imaginary axis", labels=None,
                colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
                leg_kwargs={}, **kwargs):
        r"""Plot the linearizations onto a single Nyquist diagram.

        This method calls :meth:`linres.LinRes.nyquist` from the included
        instances of :class:`linres.LinRes`.

        **Arguments:**

        - *ax*: Axes onto which the Nyquist diagrams should be plotted

             If *ax* is not provided, then axes will be created in a new figure.

        - *pair*: Tuple of (input name or index, output name or index) for the
          transfer function to be chosen from each system (applied to all)

             This is ignored if the system is SISO.

        - *label*: Label for the figure (ignored if axes is provided)

             This is used as the base filename if the figure is saved using
             :meth:`~modelicares.util.save` or
             :meth:`~modelicares.util.saveall`.

        - *title*: Title for the figure

            - *xlabel*: x-axis label

            - *ylabel*: y-axis label

        - *labels*: Label or list of labels for the legends

             If *labels* is *None*, then no label will be used.  If it is an
             empty string (''), then the base filenames will be used.

        - *colors*: Color or list of colors that will be used sequentially

             Each may be a character, grayscale, or rgb value.

             .. Seealso:: http://matplotlib.sourceforge.net/api/colors_api.html

        - *leg_kwargs*: Dictionary of keyword arguments for
          :meth:`matplotlib.pyplot.legend`

             If *leg_kwargs* is *None*, then no legend will be shown.

        - *\*\*kwargs*: Additional plotting arguments:

             - *freqs*: List or frequencies or tuple of (min, max) frequencies
               over which to plot the system response.

                  If *freqs* is *None*, then an appropriate range will be
                  determined automatically.

             - *in_Hz*: If *True* (default), the frequencies (*freqs*) are in
               Hz and should be plotted in Hz (otherwise, rad/s)

             - *mark*: *True*, if the -1 point should be marked on the plot

             - *show_axes*: *True*, if the axes should be shown

             - *skip*: Mark every nth frequency on the plot with a dot

                  If *skip* is 0 or *None*, then the frequencies are not marked.

             - *label_freq*: If *True*, if the marked frequencies should be
               labeled

             Other keyword arguments are passed to
             :meth:`matplotlib.pyplot.plot`.

        **Returns:**

            1. *ax*: Axes of the Nyquist plot

        **Example:**

        .. plot:: examples/PIDs-nyquist.py
           :alt: Nyquist plot of PID with varying parameters
        """
        # Create axes if necessary.
        if not ax:
            fig = util.figure(label)
            ax = fig.add_subplot(111, aspect='equal')

        # Process the labels input.
        labels = self._get_labels(labels)

        # Set up the color(s).
        if not iterable(colors):
            # Use the single color for all plots.
            colors = (colors,)
        n_colors = len(colors)

        # Create the plots.
        label_freq = kwargs.pop('label_freq', None)
        for i, (lin, label) in enumerate(zip(self, labels)):
            if lin.sys.inputs > 1 or lin.sys.outputs > 1:
                sys = lin.to_siso(pair[0], pair[1])
            else:
                sys = lin.sys
            nyquist_plot(sys, mark=False, label=label, ax=ax,
                         label_freq=(i == 0 if label_freq is None
                                     else label_freq),
                         color=colors[np.mod(i, n_colors)], **kwargs)

        # Decorate and finish.
        ax.set_title(title)
        if xlabel:
            # Without this check, xlabel=None will give a label of "None".
            ax.set_xlabel(xlabel)
        if ylabel: # Same purpose
            ax.set_ylabel(ylabel)
        if leg_kwargs is not None:
            loc = leg_kwargs.pop('loc', 'best')
            ax.legend(loc=loc, **leg_kwargs)

        return ax


if __name__ == '__main__':
    # Test the contents of this file.

    import doctest

    if os.path.isdir('examples'):
        doctest.testmod()
    else:
        # Create a link to the examples folder.
        EXAMPLE_DIR = '../examples'
        if not os.path.isdir(EXAMPLE_DIR):
            raise IOError("Could not find the examples folder.")
        try:
            os.symlink(EXAMPLE_DIR, 'examples')
        except AttributeError:
            raise AttributeError("This method of testing isn't supported in "
                                 "Windows.  Use runtests.py in the base "
                                 "folder.")

        # Test the docstrings in this file.
        doctest.testmod()

        # Remove the link.
        os.remove('examples')
