#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Bode and Nyquist plots for control systems
"""
# Kevin Davies 5/14/14:
# This file has been modified from version 0.6d of control.freqplot (license
# below):
# 1.  Added label and axes arguments to bode_plot()
# 2.  Added label, mark, show_axes, label_freq, in_Hz, and ax arguments to
#     nyquist_plot()
# 3.  Updated the docstrings
# 4.  Using quantity_str() instead of the get_pow1000 and si_prefix functions.
# 5.  Eliminated the scipy import; using functions from numpy instead
# 6.  Labeled frequencies are shown with a dot in the Bode plot
# 7.  bode_plot() and nyquist_plot() only return the axes.
# 8.  No longer using a configuration file to establish the defaults in
#     bode_plot()
# 9.  Removed the Plot argument to bode_plot() and nyquist_plot_plot(); assuming
#     it is always True
# 10. Both plotting functions now only accept a single system (sys instead of
#     syslist).
# 11. Using modelicares.texunit.number_label to label the axes
# 12. Removed color as argument to nyquist_plot(); deferring to *args and
#     **kwargs
# 13. Renamed the omega argument to freqs in bode_plot() and nyquist_plot().
#     The frequencies may now be specified in Hz or rad/s.
# 14. Renamed the dB, Hz, and deg arguments to bode_plot to in_dB, in_Hz, and
#     in_deg.
# 15. The default frequency range goes two orders of magnitude beyond the
#     widest features (previously, one order of magnitude).
# 16. The default frequency range rounds to decades of Hz or rad/s, depending on
#     the unit used to plot frequency.

# Author: Richard M. Murray
# Date: 24 May 09
#
# Copyright (c) 2010 by California Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the California Institute of Technology nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CALTECH
# OR THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import numpy as np
import matplotlib.pyplot as plt

from functools import wraps
from control.ctrlutil import unwrap

from modelicares.util import add_hlines, add_vlines
from modelicares.texunit import quantity_str, number_label

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915,
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=C0103, E1101

# Units
rad = 1
s = 1
cyc = 2*np.pi*rad
deg = cyc/360
Hz = cyc/s
to_dB = lambda x: 20*np.log10(x)

def default_frequency_range(syslist, in_Hz=True):
    """Examine the poles and zeros of systems and return a reasonable frequency
    range for frequency domain plots.

    This function looks at the poles and zeros of all of the systems and sets
    the frequency range to be one decade above and below the min and max feature
    frequencies, rounded to the nearest integer.  It excludes poles and zeros at
    the origin.  If no features are found, it turns logspace(-1, 1).

    **Parameters:**

    - *syslist*: List of linear input/output systems (single system is OK)

    - *in_Hz*: If *True*, the frequencies (*freqs*) are rounded to decades of
      Hz (otherwise, rad/s)

    **Returns:**

    1. Range of frequencies (array)

    **Example:**

    >>> from control.matlab import ss

    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> default_frequency_range(sys) # doctest: +ELLIPSIS
    array([  6.28318531e-03,   7.04984987e-03,   7.91006165e-03,
             ...
             6.28318531e+03])
    """
    # Find the list of all poles and zeros in the systems.
    features = np.array([])

    # Put the single system in a list if necessary.
    if not getattr(syslist, '__iter__', False):
        syslist = [syslist,]

    for sys in syslist:
        try:
            # Add new features to the list.
            features = np.concatenate((features, np.abs(sys.pole())*rad/s))
            features = np.concatenate((features, np.abs(sys.zero())*rad/s))
        except:
            pass

    # Get rid of poles and zeros at the origin.
    features = features[features != 0]

    # Make sure there is at least one point in the range.
    if features.shape[0] == 0:
        features = [1]

    # Take the log of the features.
    features = np.log10(features)

    # TODO: Add a check in discrete case to make sure we don't get aliasing.

    # Set the range to be two orders of magnitude beyond any features.
    unit = Hz if in_Hz else rad/s
    e0 = np.floor(np.min(features)/unit) - 2
    e1 = np.ceil(np.max(features)/unit) + 2
    return np.logspace(e0, e1, (e1 - e0)*20 + 1)*unit
    # 20 matches the default skip in nyquist_plot().


def require_SISO(func):
    """Decorator to require that the system is SISO.
    """
    @wraps(func)
    def wrapped(sys, *args, **kwargs):
        """Function that requires that the system is SISO
        """
        if sys.inputs > 1 or sys.outputs > 1:
            raise NotImplementedError("This function is currently only "
                                      "implemented for SISO systems.")
        return func(sys, *args, **kwargs)

    return wrapped

def overload_freqs(func):
    """Decorator to allow frequencies to be specified via (min, max) or default
    (*None*), as well as a list of frequencies.
    """
    @wraps(func)
    def wrapped(sys, freqs=None, in_Hz=True, *args, **kwargs):
        """Decorator that allows frequencies to be specified via (min, max) or
        default (*None*), as well as a list of frequencies.
        """
        if freqs is None:
            f = default_frequency_range(sys, in_Hz)
            # TODO: Do something smarter for discrete.
        elif isinstance(freqs, tuple):
            # Interpolate between the minimum and maximum frequencies.
            assert len(freqs) == 2, ("The freqs tuple must be a pair with the "
                                     "minimum and maximum frequencies.")
            e = np.log10(freqs)
            f = np.logspace(e[0], e[1], np.diff(e)*20 + 1)*(Hz if in_Hz else
                                                            rad/s)
            # 20 matches the default skip in nyquist_plot().
        else:
            f = freqs*(Hz if in_Hz else rad/s)

        return func(sys, f, in_Hz, *args, **kwargs)

    return wrapped


def via_system(func):
    """Decorator to specify magnitude and phase via a system.
    """
    @wraps(func)
    def wrapped(sys, f, *args, **kwargs):
        """Function that accepts a system.
        """
        mag, phase = sys.freqresp(f/(rad/s))[0:2]
        mag = np.squeeze(mag)
        phase = np.squeeze(phase)*rad

        return func(mag, phase, f, *args, **kwargs)

    return wrapped

@require_SISO # TODO: Support MIMO.
@overload_freqs
@via_system
def bode_plot(mag, phase, f, in_Hz=True, in_dB=True, in_deg=True, label=None,
              axes=None, *args, **kwargs):
    r"""Create a Bode plot for a system.

    **Arguments:**

    - *sys*: Linear input/output system (Lti)

    - *freqs*: List or frequencies or tuple of (min, max) frequencies over which
      to plot the system response.

         If *freqs* is *None*, then an appropriate range will be determined
         automatically.

    - *in_Hz*: If *True*, the frequencies (*freqs*) are in Hz and should be
      plotted in Hz (otherwise, rad/s)

    - *in_dB*: If *True*, plot the magnitude in dB

    - *in_deg*: If *True*, plot the phase in degrees (otherwise, radians)

    - *label*: Label for the legend, if added

    - *axes*: Tuple (pair) of axes to plot into

         If *None* or (*None*, None*), then axes are created

    - *\*args*, *\*\*kwargs*: Additional options to matplotlib (color,
      linestyle, etc.)

    **Returns:**

    1. Axes of the magnitude and phase plots (tuple (pair) of matplotlib axes)

    **Example:**

    .. plot::
       :include-source:

       >>> from control.matlab import ss

       >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
       >>> axes = bode_plot(sys)
    """
    phase = unwrap(phase)
    freq_unit = Hz if in_Hz else rad/s

    # Create axes if necessary.
    if axes is None or (None, None):
        axes = (plt.subplot(211), plt.subplot(212))

    # Magnitude plot
    axes[0].semilogx(f/freq_unit, to_dB(mag) if in_dB else mag,
                     label=label, *args, **kwargs)

    # Add a grid and labels.
    axes[0].grid(True)
    axes[0].grid(True, which='minor')
    axes[0].set_ylabel("Magnitude in dB" if in_dB else "Magnitude")

    # Phase plot
    axes[1].semilogx(f/freq_unit, phase/(deg if in_deg else rad),
                     label=label, *args, **kwargs)

    # Add a grid and labels.
    axes[1].grid(True)
    axes[1].grid(True, which='minor')
    axes[1].set_xlabel(number_label("Frequency", "Hz" if in_Hz else "rad/s"))
    axes[1].set_ylabel(number_label("Phase", "deg" if in_deg else "rad"))

    return axes


@require_SISO # TODO: Support MIMO.
@overload_freqs
@via_system
def nyquist_plot(mag, phase, f, in_Hz=True, label=None, mark=False,
                 show_axes=True, skip=20, label_freq=True, ax=None, *args,
                 **kwargs):
    r"""Create a Nyquist plot for a system.

    **Arguments:**

    - *sys*: Linear input/output system (Lti)

    - *freqs*: List or frequencies or tuple of (min, max) frequencies over which
      to plot the system response.

         If *freqs* is *None*, then an appropriate range will be determined
         automatically.

    - *in_Hz*: *True*, if the frequencies (*freqs*) are in Hz (otherwise, rad/s)

    - *label*: Label for the legend, if added

    - *mark*: *True*, if the -1 point should be marked on the plot

    - *show_axes*: *True*, if the axes should be shown

    - *skip*: Mark every nth frequency on the plot with a dot (int)

         If *skip* is 0 or *None*, then the frequencies are not marked.

    - *label_freq*: If *True*, if the marked frequencies should be labeled

    - *ax*: Axes to plot into

         If *None*, then axes are created.

    - *\*args*, *\*\*kwargs*: Additional options to matplotlib (color, etc.)

         kwargs['linestyle'] is ignored if present.

    **Returns:**

    1. Axes of the Nyquist plot (matplotlib axes)

    **Example:**

    .. plot::
       :include-source:

       >>> from control.matlab import ss

       >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
       >>> ax = nyquist_plot(sys)
    """

    # Compute the primary curve.
    x = np.multiply(mag, np.cos(phase))
    y = np.multiply(mag, np.sin(phase))

    # Create axes if necessary.
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')

    # Plot the primary curve and mirror image.
    kwargs.pop('linestyle', None) # Ignore the linestyle argument.
    ax.plot(x, y, linestyle='-', label=label, *args, **kwargs)
    ax.plot(x, -y, linestyle='--', *args, **kwargs)

    # Show the axes.
    if show_axes:
        add_hlines(ax, color='k', linestyle='--', linewidth=0.5)
        add_vlines(ax, color='k', linestyle='--', linewidth=0.5)

    # Mark the -1 point.
    if mark:
        ax.plot([-1], [0], 'r+')

    # Mark and label the frequencies.
    if skip:
        for xpt, ypt, fpt in zip(x[::skip], y[::skip], f[::skip]):
            # Mark the freqencies with a dot.
            color = kwargs.pop('color', 'b')
            ax.plot(xpt, ypt, '.', color=color)

            # Apply the text.
            if label_freq:
                # Use a space before the text to prevent overlap with the data.
                ax.text(xpt, ypt, ' ' + quantity_str(fpt/Hz, 'Hz', '%.0e',
                                                     roman=False))

    # Set the x and y limits the same.
    # lim = np.max(np.abs(ax.axis()))
    # ax.axis([-lim, lim, -lim, lim])

    return ax
