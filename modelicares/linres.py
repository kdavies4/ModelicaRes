#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This submodule contains two classes to help load, analyze, and plot results
from Modelica_ linearizations:

- :class:`LinRes` - Class to load, contain, and analyze results from a Modelica_
  linearization

- :class:`LinResList` - Specialized list of linearization results
  (:class:`LinRes` instances)


.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import os
import numpy as np

from control.matlab import ss
from functools import wraps
from glob import glob
from matplotlib.cbook import iterable
from scipy.signal import ss2tf
from six import string_types

from modelicares import util
from modelicares._freqplot import bode_plot, nyquist_plot
from modelicares._res import ResList

# File loading functions
from modelicares._io.dymola import loadlin as dymola
loaders = [('dymola', dymola)] # LinRes tries these in order.
# All of the keys should be in lowercase.


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

    - *tool* - String indicating the function used to load the results (named
      after the corresponding linearization tool)

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

        - *fname*: Name of the file (including the directory if necessary)

             The file must contain four matrices:  *Aclass* (specifies the class
             name, which must be "AlinearSystem"), *nx*, *xuyName*, and *ABCD*.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID.mat')
        """

        # Load the file.
        if tool is None:
            # Load the file and store the data.
            for (tool, load) in loaders[:-1]:
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
            (tool, load) = loaders[-1]
        else:
            loaderdict = dict(loaders)
            try:
                load = loaderdict[tool.lower()]
            except:
                raise LookupError('"%s" is not one of the available tools ("%s").'
                                  % (tool, '", "'.join(list(loaderdict))))
        self.sys = load(fname)

        # Remember the tool and filename.
        self.tool = tool
        self.fname = os.path.abspath(fname)


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
           Modelica linearization results from ...PID.mat
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

        .. code-block:: python

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID.mat')
           >>> print(lin) # doctest: +ELLIPSIS
           Modelica linearization results from ...PID.mat
        """
        return "Modelica linearization results from {f}".format(f=self.fname)

    def _to_siso(self, iu, iy):
        """Return a SISO system given input and output indices.
        """
        return ss(self.sys.A,         self.sys.B[:, iu],
                  self.sys.C[iy, :], self.sys.D[iy, iu])

    def to_tf(self, iu=None, iy=None):
        """Return a transfer function given input and output names.

        **Arguments:**

        - *iu*: Index or name of the input

             This must be specified unless the system has only one input.

        - *iy*: Index or name of the output

             This must be specified unless the system has only one output.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinRes
           >>> lin = LinRes('examples/PID.mat')
           >>> lin.to_tf()
           (array([[  11.,  102.,  200.]]), array([   1.,  100.,    0.]))
        """
        # Get the input index.
        if iu is None:
            if len(self.sys.input_names) == 1:
                iu = 0
            else:
                raise IndexError("iu must be specified since this is a MI system.")
        else:
            try:
                iu = self.sys.input_names.index(iu)
            except ValueError:
                raise(ValueError('The input "%s" is invalid.' % iu))

        # Get the output index.
        if iy is None:
            if len(self.sys.output_names) == 1:
                iy = 0
            else:
                raise IndexError("iy must be specified since this is a MO system.")
        else:
            try:
                iy = self.sys.output_names.index(iy)
            except ValueError:
                raise(ValueError('The output "%s" is invalid.' % iy))

        # Return the TF.
        return ss2tf(self.sys.A,        self.sys.B,
                     self.sys.C[iy, :], self.sys.D[iy, :], input=iu)

    def bode(self, axes=None, pairs=None, label='bode',
             title=None, colors=['b','g','r','c','m','y','k'],
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

        .. plot:: examples/PID-bode.py
           :alt: Bode plot of PID
        """
        # Create axes if necessary.
        if axes is None or (None, None):
            fig = util.figure(label)
            axes = (fig.add_subplot(211), fig.add_subplot(212))

        # Create a title if necessary.
        if title is None:
            title = "Bode plot of %s" % self.fbase()

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
            bode_plot(self._to_siso(iu, iy), axes=axes,
                      label='$Y_{%i}/U_{%i}$' % (iy, iu),
                      Hz=True, color=colors[np.mod(i, n_colors)], **kwargs)
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

        .. plot:: examples/PID-nyquist.py
           :alt: Nyquist plot of PID
        """
        # Create axes if necessary.
        if not ax:
            fig = util.figure(label)
            ax = fig.add_subplot(111, aspect='equal')

        # Create a title if necessary.
        if title is None:
            title = "Nyquist plot of %s" % self.fbase()

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
            nyquist_plot(self._to_siso(iu, iy), ax=ax,
                         label=r'$Y_{%i}/U_{%i}$' % (iy, iu),
                         color=colors[np.mod(i, n_colors)], **kwargs)
            # Note: modelicares._freqplot.nyquist() is currently only
            # implemented for SISO systems.

        # Decorate and finish.
        if len(pairs) > 1:
            ax.legend()
        ax.set_title(title)
        if xlabel: # Without this check, xlabel=None will give a label of "None".
            ax.set_xlabel(xlabel)
        if ylabel: # Same purpose
            ax.set_ylabel(ylabel)
        return ax


def _cast_LinResList(f):
    """Return a method that casts its output as a :class:`LinResList`, given one
    that doesn't (*f*).
    """
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        """Function that casts its output as a :class:`LinResList`
        """
        return LinResList(f(self, *args, **kwargs))

    return wrapped


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
    """Specialized list of linearization results

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
    and :meth:`__sizeof__`).

    The comparison methods
    (`< <https://docs.python.org/2/reference/datamodel.html#object.__lt__>`_,
    `<= <https://docs.python.org/2/reference/datamodel.html#object.__le__>`_,
    `== <https://docs.python.org/2/reference/datamodel.html#object.__eq__>`_,
    `!= <https://docs.python.org/2/reference/datamodel.html#object.__ne__>`_,
    `>= <https://docs.python.org/2/reference/datamodel.html#object.__ge__>`_,
    `> <https://docs.python.org/2/reference/datamodel.html#object.__gt__>`_),
    and :meth:`sort`, which relies on them, use the full filenames (with
    absolute path) for comparison.

    The following method is overloaded for convenience:

    - :meth:`append` - Add linearization(s) to the end of the list of
      linearizations (accepts a :class:`LinRes` instance, directory, or
      filename).

    The following methods are added to those in the standard Python_ list:

    - :meth:`basedir` - Return the highest common directory that the result files
      share.

    - :meth:`bode` - Plot the linearizations onto a single Bode diagram.

    - :meth:`fnames` - Return a list of filenames from which the results were
      loaded.

    - :meth:`nyquist` - Plot the linearizations onto a single Bode diagram.


    .. _Python: http://www.python.org
    """

    def __init__(self, *args):
        """Initialize as a list of :class:`LinRes` instances, loading files as
        necessary.

        Initialization signatures:

        - :class:`LinResList`(): Returns an empty linearization list

        - :class:`LinResList`(*lins*), where lins is a list of :class:`LinRes`
          instances:  Casts the list into a :class:`LinResList`

        - :class:`LinResList`(*filespec*), where *filespec* is a filename or
          directory, possibly with wildcards a la `glob
          <https://docs.python.org/2/library/glob.html>`_:  Returns a
          :class:`LinResList` of :class:`LinRes` instances loaded from the
          matching or contained files

             The filename or directory must include the absolute path or be
             resolved to the current directory.

             An error is only raised if no files can be loaded.

        - :class:`LinResList`(*filespec1*, *filespec2, ...): Loads all files
          matching or contained by *filespec1*, *filespec2*, etc. as above.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinResList
           >>> lins = LinResList('examples/PID/*/*.mat')
           >>> print(lins) # doctest: +ELLIPSIS
           List of linearization results (LinRes instances) from the following files
           in the .../ModelicaRes/examples/PID directory:
              1/dslin.mat
              2/dslin.mat
        """

        if not args:
            list.__init__(self, [])
        elif len(args) == 1 and isinstance(args[0], list):
            # The argument is a list of LinRes instances.
            for lin in args[0]:
                assert isinstance(lin, LinRes), ("All entries in the list must "
                                                 "be LinRes instances.")
            list.__init__(self, args[0])
        else:
            # The arguments are filenames or directories.

            # Get a unique list of matching filenames.
            fnames = set()
            for arg in args:
                assert isinstance(arg, string_types), ("The linearization list "
                    "can only be initialized by providing a list of LinRes "
                    "instances or a series of arguments, each of which is a "
                    "filename or directory.")
                if os.path.isdir(arg):
                    fnames = fnames.union(set(glob(os.path.join(arg, '*.mat'))))
                elif '*' in arg or '?' in arg or '[' in arg:
                    fnames = fnames.union(set(glob(arg)))
                else:
                    fnames.add(arg)

            # Load linearizations from the filenames.
            list.__init__(self, _get_lins(fnames))

    def append(self, item):
        """Add a linearization to the end of the list of linearizations.

        **Arguments:**

        - *item*: :class:`LinRes` instance or a file specification

             The file specification may be a filename or directory, possibly
             with wildcards a la `glob
             <https://docs.python.org/2/library/glob.html>`_, where linearization
             results can be loaded by :class:`LinRes`.  The filename or
             directory must include the absolute path or be resolved to the
             current directory.  An error is only raised if no files can be
             loaded.

         Unlike the `append
         <https://docs.python.org/2/tutorial/datastructures.html>`_ method of a
         standard Python_ list, this method may add more than one item.  If
         *item* is a directory or a wildcarded filename, it may match multiple
         valid files.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinResList
           >>> lins = LinResList('examples/PID/*/*.mat')
           >>> lins.append('examples/PID.mat')
           >>> print(lins) # doctest: +ELLIPSIS
           List of linearization results (LinRes instances) from the following files
           in the .../ModelicaRes/examples directory:
              PID/1/dslin.mat
              PID/2/dslin.mat
              PID.mat
        """
        if isinstance(item, LinRes):
            list.append(self, item)
        else:
            assert isinstance(item, string_types), ("The linearization list "
                "can only be appended by providing a LinRes instance, "
                "filename, or directory.")

            # Get the matching filenames.
            if os.path.isdir(item):
                fnames = glob(os.path.join(item, '*.mat'))
            elif '*' in item or '?' in item or '[' in item:
                fnames = glob(item)
            else:
                fnames = [item]

            # Load linearizations from the filenames.
            self.extend(LinResList(_get_lins(fnames)))

    def __str__(self):
        """Return str(self).

        This provides a readable description of the :class:LinResList`.

        **Example:**

        .. code-block:: python

           >>> from modelicares import LinResList
           >>> lins = LinResList('examples/PID/*/*.mat')
           >>> print(lins) # doctest: +ELLIPSIS
           List of linearization results (LinRes instances) from the following files
           in the .../ModelicaRes/examples/PID directory:
              1/dslin.mat
              2/dslin.mat
        """
        if len(self) == 0:
            return "Empty list of linearization results"
        elif len(self) == 1:
            return ("List of linearization results (LinRes instance) from\n"
                    + self[0].fname)
        else:
            basedir = self.basedir()
            start = len(basedir) + 1
            short_fnames = [fname[start:] for fname in self.fnames()]
            string = ("List of linearization results (LinRes instances) from "
                      "the following files")
            string += "\nin the %s directory:\n   "  % basedir if basedir else ":\n   "
            string += "\n   ".join(short_fnames)
            return string

    def _get_labels(self, labels):
        """Create labels for the legend of a Bode or Nyquist plot.

        If *labels* is *None*, then no label will be used.  If it is an empty
        string (''), then the base filenames will be used.
        """
        if labels == None:
            labels = ['']*len(self)
        elif labels == '':
            start = len(self.basedir())
            labels = [lin.fname[start:].lstrip(os.sep) for lin in self]

        return labels

    def bode(self, axes=None, pair=(0, 0), label='bode', title="Bode plot",
             labels='', colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
             styles=[(None,None), (3,3), (1,1), (3,2,1,2)], leg_kwargs={},
             **kwargs):
        """Plot the linearizations onto a single Bode diagram.

        This method calls :meth:`LinRes.bode` from the included instances
        of :class:`LinRes`.

        **Arguments:**

        - *axes*: Tuple (pair) of axes for the magnitude and phase plots

             If *axes* is not provided, then axes will be created in a new figure.

        - *pair*: Tuple of (input index, output index) for the transfer function
          to be chosen from each system (applied to all)

             This is ignored if the system is SISO.

        - *label*: Label for the figure (ignored if axes is provided)

             This will be used as the base filename if the figure is saved.

        - *title*: Title for the figure

        - *labels*: Label or list of labels for the legends

             If *labels* is *None*, then no label will be used.  If it is an
             empty string (''), then the base filenames will be used.

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

        - *leg_kwargs*: Dictionary of keyword arguments for
          :meth:`matplotlib.pyplot.legend`

             If *leg_kwargs* is *None*, then no legend will be shown.

        - *\*\*kwargs*: Additional arguments for :meth:`control.freqplot.bode`

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
                sys = self._to_siso(pair[0], pair[1])
            else:
                sys = lin.sys
            bode_plot(sys, Hz=True, label=label,
                      color=colors[np.mod(i, n_colors)], axes=axes,
                      **kwargs)

        # Decorate and finish.
        axes[0].set_title(title)
        if leg_kwargs is not None:
            loc = leg_kwargs.pop('loc', 'best')
            axes[0].legend(loc=loc, **leg_kwargs)
            axes[1].legend(loc=loc, **leg_kwargs)
        return axes

    def nyquist(self, ax=None, pair=(0, 0), label='nyquist',
                title="Nyquist plot",  xlabel="Real axis",
                ylabel="Imaginary axis", labels='',
                colors=['b', 'g', 'r', 'c', 'm', 'y', 'k'],
                leg_kwargs={}, **kwargs):
        """Plot the linearizations onto a single Nyquist diagram.

        This method calls :meth:`linres.LinRes.nyquist` from the included
        instances of :class:`linres.LinRes`.

        **Arguments:**

        - *ax*: Axes onto which the Nyquist diagrams should be plotted

             If *ax* is not provided, then axes will be created in a new figure.

        - *pair*: Tuple of (input index, output index) for the transfer function
          to be chosen from each system (applied to all)

             This is ignored if the system is SISO.

        - *label*: Label for the figure (ignored if axes is provided)

             This will be used as the base filename if the figure is saved.

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

        - *\*\*kwargs*: Additional arguments for :meth:`control.freqplot.nyquist`

             If *textFreq* is not specified, then only the frequency points of the
             first system will have text labels.

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
        textFreq = kwargs.pop('textFreq', None)
        for i, (lin, label) in enumerate(zip(self, labels)):
            if lin.sys.inputs > 1 or lin.sys.outputs > 1:
                sys = self._to_siso(pair[0], pair[1])
            else:
                sys = lin.sys
            nyquist_plot(sys, mark=False, label=label, ax=ax,
                         textFreq=i==0 if textFreq is None else textFreq,
                         color=colors[np.mod(i, n_colors)], **kwargs)

        # Decorate and finish.
        ax.set_title(title)
        if xlabel: # Without this check, xlabel=None will give a label of "None".
            ax.set_xlabel(xlabel)
        if ylabel: # Same purpose
            ax.set_ylabel(ylabel)
        if leg_kwargs is not None:
            loc = leg_kwargs.pop('loc', 'best')
            ax.legend(loc=loc, **leg_kwargs)
        return ax


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
