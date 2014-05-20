#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Bode and Nyquist plots for control systems
"""
# Kevin Davies 5/14/14:
# This file has been modified from version 0.6d of control.freqplot (license
# below):
# 1.  Added label and axes arguments to bode_plot()
# 2.  Added label, mark, show_axes, textFreq and ax arguments to nyquist_plot()
# 3.  Updated the docstrings
# 4.  The default_frequency_range function is imported from the freqplot
#     submodule of the installed control package.
# 5.  The get_pow1000 and si_prefix functions, which I contributed to the
#     control package, have been imported from modelicares.util rather than
#     defined here.
# 6.  Eliminated the scipy import; using functions from numpy instead
# 7.  Labeled frequencies are shown with a dot in the Bode plot.
# 8.  bode_plot() also returns the axes.
# 9.  No longer using a configuration file to establish the defaults in
#     bode_plot()
# 10. Removed the Plot argument to bode_plot() and nyquist_plot_plot(); assuming
#     it is always True
# 11. Both plotting functions now only accept a single system (sys instead of
#     syslist).
# 12. Using modelicares.texunit.number_label to label the axes
# 13. Removed color as argument to nyquist_plot(); deferring to *args and
#     **kwargs

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

from control.ctrlutil import unwrap
from control.freqplot import default_frequency_range

from modelicares.util import get_pow1000, si_prefix, add_hlines, add_vlines
from modelicares.texunit import number_label


def bode_plot(sys, omega=None, dB=False, Hz=False, deg=True, label=None,
              axes=None, *args, **kwargs):
    """Create a Bode plot for a system.

    **Arguments:**

    - *sys*: Linear input/output system (Lti)

    - *omega*: Range of frequencies (list or bounds) in rad/s (freq_range)

    - *dB*: If *True*, plot the magnitude in dB

    - *Hz*: If *True*, plot the frequency in Hz

         Regardless, *omega* must be provided in rad/s.

    - *deg*: If *True*, plot the phase in degrees (else radians)

    - *label*: Label for the legend, if added

    - *axes*: Tuple (pair) of axes to plot into

         If *None* or (*None*, None*), then axes are created

    - *\*args*, *\*\*kwargs*: Additional options to matplotlib (color,
      linestyle, etc.)

    **Returns:**

    1. magnitude (array)

    2. phase (array)

    3. omega (array)

    4. axes  for the magnitude and phase plots (tuple (pair) of matplotlib axes)

    **Example:**

    .. plot::
       :include-source:

       >>> from control.matlab import ss

       >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
       >>> mag, phase, omega, axes = bode_plot(sys)
    """

    if omega is None:
        omega = default_frequency_range(sys)

    if sys.inputs > 1 or sys.outputs > 1:
        raise NotImplementedError(
                "This function is currently only implemented for SISO systems.")
        # TODO: Support MIMO.

    # Get the magnitude and phase of the system.
    mag_tmp, phase_tmp, omega = sys.freqresp(omega)
    mag = np.atleast_1d(np.squeeze(mag_tmp))
    phase = np.atleast_1d(np.squeeze(phase_tmp))
    phase = unwrap(phase)
    if Hz:
        omega = omega/(2*np.pi)
    if dB:
        mag = 20*np.log10(mag)
    if deg:
        phase = phase * 180 / np.pi

    # Create axes if necessary.
    if axes is None or (None, None):
        axes = (plt.subplot(211), plt.subplot(212))

    # Magnitude plot
    if dB:
        axes[0].semilogx(omega, mag, label=label, *args, **kwargs)
    else:
        axes[0].loglog(omega, mag, label=label, *args, **kwargs)

    # Add a grid and labels.
    axes[0].grid(True)
    axes[0].grid(True, which='minor')
    axes[0].set_ylabel("Magnitude in dB" if dB else "Magnitude")

    # Phase plot
    axes[1].semilogx(omega, phase, label=label, *args, **kwargs)

    # Add a grid and labels.
    axes[1].grid(True)
    axes[1].grid(True, which='minor')
    axes[1].set_xlabel(number_label("Frequency" , "Hz" if Hz else "rad/s"))
    axes[1].set_ylabel("Phase / deg" if deg else "Phase / rad")

    return mag, phase, omega, axes


def nyquist_plot(sys, omega=None, label=None, mark=False, show_axes=True,
                 labelFreq=0, textFreq=True, ax=None, *args, **kwargs):
    """Create a Nyquist plot for a system.

    **Arguments:**

    - *sys*: Linear input/output system (Lti)

    - *omega*: Range of frequencies (list or bounds) in rad/s (freq_range)

    - *label*: Label for the legend, if added

    - *mark*: *True*, if the -1 point should be marked on the plot

    - *show_axes*: *True*, if the axes should be shown

    - *labelFreq*: Label every nth frequency on the plot (int)

    - *textFreq*: If *True*, if the frequency labels should include text

         Otherwise, just dots are used.

    - *ax*: Axes to plot into

         If *None*, then axes are created.

    - *\*args*, *\*\*kwargs*: Additional options to matplotlib (color, etc.)

         kwargs['linestyle'] is ignored if present.

    **Returns:**

    1. Real part of the frequency response (array)

    2. Imaginary part of the frequency response (array)

    2. Frequencies (array)

    3. Axes of the Nyquist plot (matplotlib axes)

    **Example:**

    .. plot::
       :include-source:

       >>> from control.matlab import ss

       >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
       >>> x, y, omega, ax = nyquist_plot(sys)
    """
    if sys.inputs > 1 or sys.outputs > 1:
        raise NotImplementedError(
                "This function is currently only implemented for SISO systems.")
        # TODO: Support MIMO.

    if omega is None:
        omega = default_frequency_range(sys)
        # TODO: Do something smarter for discrete.
    elif isinstance(omega, list) or isinstance(omega, tuple):
        # Interpolate between wmin and wmax.
        try:
            omega = np.logspace(np.log10(omega[0]), np.log10(omega[1]), num=50,
                                endpoint=True, base=10)
        except IndexError:
            raise ValueError("Supported frequency arguments are (wmin, wmax) "
                             "tuple or list, or frequency vector.")

    # Get the magnitude and phase of the system.
    mag_tmp, phase_tmp, omega = sys.freqresp(omega)
    mag = np.squeeze(mag_tmp)
    phase = np.squeeze(phase_tmp)

    # Compute the primary curve.
    x = np.multiply(mag, np.cos(phase))
    y = np.multiply(mag, np.sin(phase))

    # Create axes if necessary.
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')

    # Plot the primary curve and mirror image.
    kwargs.pop('linestyle', None) # Ignore this.
    ax.plot(x, y, linestyle='-', label=label, *args, **kwargs)
    ax.plot(x, -y, linestyle='--', *args, **kwargs)

    # Mark the -1 point.
    if mark:
        ax.plot([-1], [0], 'r+')

    # Show the axes.
    if show_axes:
        add_hlines(ax, color='k', linestyle='--', linewidth=0.5)
        add_vlines(ax, color='k', linestyle='--', linewidth=0.5)

    # Label the frequencies.
    if labelFreq:
        for xpt, ypt, omegapt in zip(x[::labelFreq], y[::labelFreq], omega[::labelFreq]):
            # Convert to Hz.
            f = omegapt/(2*np.pi)

            # Get the SI prefix.
            pow1000 = max(min(get_pow1000(f), 8), -8)
            prefix = si_prefix(pow1000)

            # Apply the text.
            # Use a space before the text to prevent overlap with the data.
            if textFreq:
                ax.text(xpt, ypt,
                        ' ' + str(int(np.round(f/1000**pow1000, 0))) +
                        ' ' + prefix + 'Hz')
                # np.round() is used because 0.99... appears instead of 1.0, and
                # this would otherwise be truncated to 0.

            # Show the freqencies with a dot.
            color = kwargs.pop('color', 'b')
            ax.plot(xpt, ypt, '.', color=color)

    return x, y, omega, ax
