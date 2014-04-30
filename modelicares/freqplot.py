# freqplot.py - frequency domain plots for control systems
#
# Author: Richard M. Murray
# Date: 24 May 09
#
# This file contains some standard control system plots: Bode plots,
# Nyquist plots and pole-zero diagrams.  The code for Nichols charts
# is in nichols.py.
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
#
# $Id$


# Kevin Davies 4/29/14:
# This module has been modified from version 0.6d of control.freqplot.  The
# changes to bode_plot() and nyquist_plot() are marked with "ModelicaRes". 
# Other functions have been removed or referenced to the standard installation 
# of the control package.

import matplotlib.pyplot as plt
import scipy as sp
import numpy as np

from control.ctrlutil import unwrap
from control.freqplot import get_pow1000, gen_prefix, default_frequency_range

#
# Main plotting functions
#
# This section of the code contains the functions for generating
# frequency domain plots
#

# Bode plot
def bode_plot(syslist, omega=None, dB=False, Hz=False, deg=True,
# ModelicaRes 7/2/13:
#        Plot=True, *args, **kwargs):
        Plot=True, style='-', label=None, axes=None, *args, **kwargs):
# ModelicaRes 7/5/13: Added description of axes argument and output
    """Bode plot for a system

    Plots a Bode plot for the system over a (optional) frequency range.

    Parameters
    ----------
    syslist : linsys
        List of linear input/output systems (single system is OK)
    omega : freq_range
        Range of frequencies (list or bounds) in rad/sec
    dB : boolean
        If True, plot result in dB
    Hz : boolean
        If True, plot frequency in Hz (omega must be provided in rad/sec)
    deg : boolean
        If True, return phase in degrees (else radians)
    Plot : boolean
        If True, plot magnitude and phase
    axes : tuple (pair) of axes to plot into
        If None or (None, None), then axes are created
    *args, **kwargs:
        Additional options to matplotlib (color, linestyle, etc)

    Returns
    -------
    mag : array (list if len(syslist) > 1)
        magnitude
    phase : array (list if len(syslist) > 1)
        phase
    omega : array (list if len(syslist) > 1)
        frequency
    axes
        tuple (pair) of axes for the magnitude and phase plots

    Notes
    -----
    1. Alternatively, you may use the lower-level method (mag, phase, freq)
    = sys.freqresp(freq) to generate the frequency response for a system,
    but it returns a MIMO response.

    2. If a discrete time model is given, the frequency response is plotted
    along the upper branch of the unit circle, using the mapping z = exp(j
    \omega dt) where omega ranges from 0 to pi/dt and dt is the discrete
    time base.  If not timebase is specified (dt = True), dt is set to 1.

    Examples
    --------
    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> mag, phase, omega = bode(sys)
    """
    
    # ModelicaRes 4/29/14:
    # Set default values for options
    #from . import config
    #if (dB is None): dB = config.bode_dB
    #if (deg is None): deg = config.bode_deg
    #if (Hz is None): Hz = config.bode_Hz

    # If argument was a singleton, turn it into a list
    if (not getattr(syslist, '__iter__', False)):
        syslist = (syslist,)

    mags, phases, omegas = [], [], []
    for sys in syslist:
        if (sys.inputs > 1 or sys.outputs > 1):
            #TODO: Add MIMO bode plots.
            raise NotImplementedError("Bode is currently only implemented for SISO systems.")
        else:
            if (omega == None):
                # Select a default range if none is provided
                omega = default_frequency_range(syslist)

            # Get the magnitude and phase of the system
            mag_tmp, phase_tmp, omega = sys.freqresp(omega)
            mag = np.atleast_1d(np.squeeze(mag_tmp))
            phase = np.atleast_1d(np.squeeze(phase_tmp))
            phase = unwrap(phase)
            if Hz: omega = omega/(2*sp.pi)
            if dB: mag = 20*sp.log10(mag)
            if deg: phase = phase * 180 / sp.pi

            mags.append(mag)
            phases.append(phase)
            omegas.append(omega)
            # Get the dimensions of the current axis, which we will divide up
            #! TODO: Not current implemented; just use subplot for now

            if (Plot):
                # ModelicaRes 7/5/13:
                # Create axes if necessary.
                if axes is None or (None, None):
                    axes = (plt.subplot(211), plt.subplot(212))

                # Magnitude plot
                # ModelicaRes 7/5/13:
                #plt.subplot(211);
                if dB:
                    # ModelicaRes 7/5/13:
                    #plt.semilogx(omega, mag, *args, **kwargs)
                    if type(style) is str:
                        axes[0].semilogx(omega, mag, linestyle=style, label=label, *args, **kwargs)
                    else:
                        axes[0].semilogx(omega, mag, dashes=style, label=label, *args, **kwargs)
                else:
                    # ModelicaRes 7/5/13:
                    #plt.loglog(omega, mag, *args, **kwargs)
                    if type(style) is str:
                        axes[0].loglog(omega, mag, linestyle=style, label=label, *args, **kwargs)
                    else:
                        axes[0].loglog(omega, mag, dashes=style, label=label, *args, **kwargs)
                # ModelicaRes 7/5/13:
                #plt.hold(True);

                # Add a grid to the plot + labeling
                # ModelicaRes 7/5/13:
                #plt.grid(True)
                #plt.grid(True, which='minor')
                #plt.ylabel("Magnitude (dB)" if dB else "Magnitude")
                axes[0].grid(True)
                axes[0].grid(True, which='minor')
                axes[0].set_ylabel("Magnitude in dB" if dB else "Magnitude")

                # Phase plot
                # ModelicaRes 7/5/13:
                #plt.subplot(212);
                # ModelicaRes 7/5/13:
                #plt.semilogx(omega, phase, *args, **kwargs)
                if type(style) is str:
                    axes[1].semilogx(omega, phase, linestyle=style, label=label, *args, **kwargs)
                else:
                    axes[1].semilogx(omega, phase, dashes=style, label=label, *args, **kwargs)
                # ModelicaRes 7/5/13:
                #plt.hold(True);

                # Add a grid to the plot + labeling
                # ModelicaRes 7/2/13:
                #plt.grid(True)
                #plt.grid(True, which='minor')
                #plt.ylabel("Phase (deg)" if deg else "Phase (rad)")
                axes[1].grid(True)
                axes[1].grid(True, which='minor')
                axes[1].set_ylabel("Phase / deg" if deg else "Phase / rad")

                # Label the frequency axis
                # ModelicaRes 7/5/13:
                #plt.xlabel("Frequency (Hz)" if Hz else "Frequency (rad/sec)")
                axes[1].set_xlabel("Frequency / Hz" if Hz else "Frequency / rad s$^{-1}$")

    if len(syslist) == 1:
        # ModelicaRes 7/5/13:
        #return mags[0], phases[0], omegas[0]
        return mags[0], phases[0], omegas[0], axes
    else:
        # ModelicaRes 7/5/13:
        #return mags, phases, omegas
        return mags, phases, omegas, axes

# Nyquist plot
# ModelicaRes 7/5/13:
#def nyquist_plot(syslist, omega=None, Plot=True, color='b',
#                 labelFreq=0, *args, **kwargs):
def nyquist_plot(syslist, omega=None, Plot=True, color='b', label=None, mark=True,
                 labelFreq=0, textFreq=True, ax=None, *args, **kwargs):
# ModelicaRes 7/5/13: Added description of ax argument and output, textFreq,
# argument
    """Nyquist plot for a system

    Plots a Nyquist plot for the system over a (optional) frequency range.

    Parameters
    ----------
    syslist : list of Lti
        List of linear input/output systems (single system is OK)
    omega : freq_range
        Range of frequencies (list or bounds) in rad/sec
    Plot : boolean
        If True, plot magnitude
    labelFreq : int
        Label every nth frequency on the plot
    textFreq : bool
        Include text with the label (otherwise just dots)
    ax : axes to plot into
        If None, then axes are created.
    *args, **kwargs:
        Additional options to matplotlib (color, linestyle, etc)

    Returns
    -------
    real : array
        real part of the frequency response array
    imag : array
        imaginary part of the frequency response array
    freq : array
        frequencies
    ax
        Axes of the Nyquist plot

    Examples
    --------
    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> real, imag, freq = nyquist_plot(sys)
    """
    # If argument was a singleton, turn it into a list
    if (not getattr(syslist, '__iter__', False)):
        syslist = (syslist,)

    # Select a default range if none is provided
    if (omega == None):
        #! TODO: think about doing something smarter for discrete
        omega = default_frequency_range(syslist)

    # ModelicaRes 7/5/13:
    # Create axes if necessary.
    if ax is None:
        ax = plt.axes()

    # Interpolate between wmin and wmax if a tuple or list are provided
    elif (isinstance(omega,list) | isinstance(omega,tuple)):
        # Only accept tuple or list of length 2
        if (len(omega) != 2):
            raise ValueError("Supported frequency arguments are (wmin,wmax) tuple or list, or frequency vector. ")
        omega = np.logspace(np.log10(omega[0]), np.log10(omega[1]),
                            num=50, endpoint=True, base=10.0)
    for sys in syslist:
        if (sys.inputs > 1 or sys.outputs > 1):
            #TODO: Add MIMO nyquist plots.
            raise NotImplementedError("Nyquist is currently only implemented for SISO systems.")
        else:
            # Get the magnitude and phase of the system
            mag_tmp, phase_tmp, omega = sys.freqresp(omega)
            mag = np.squeeze(mag_tmp)
            phase = np.squeeze(phase_tmp)

            # Compute the primary curve
            x = sp.multiply(mag, sp.cos(phase));
            y = sp.multiply(mag, sp.sin(phase));

            if (Plot):
                # Plot the primary curve and mirror image
                # ModelicaRes 7/5/13:
                #plt.plot(x, y, '-', color=color, *args, **kwargs);
                #plt.plot(x, -y, '--', color=color, *args, **kwargs);
                ax.plot(x, y, '-', color=color, label=label, *args, **kwargs);
                ax.plot(x, -y, '--', color=color, *args, **kwargs);
                # Mark the -1 point
                # ModelicaRes 7/2/13:
                #plt.plot([-1], [0], 'r+')
                if mark:
                    ax.plot([-1], [0], 'r+')

            # Label the frequencies of the points
            if (labelFreq):
                for xpt, ypt, omegapt in zip(x, y, omega)[::labelFreq]:
                    # Convert to Hz
                    f = omegapt/(2*sp.pi)

                    # Factor out multiples of 1000 and limit the
                    # result to the range [-8, 8].
                    pow1000 = max(min(get_pow1000(f),8),-8)

                     # Get the SI prefix.
                    prefix = gen_prefix(pow1000)

                    # Apply the text. (Use a space before the text to
                    # prevent overlap with the data.)
                    #
                    # np.round() is used because 0.99... appears
                    # instead of 1.0, and this would otherwise be
                    # truncated to 0.
                    # ModelicaRes 7/5/13:
                    #plt.text(xpt, ypt,
                    #         ' ' + str(int(np.round(f/1000**pow1000, 0))) +
                    #         ' ' + prefix + 'Hz')
                    if textFreq:
                        ax.text(xpt, ypt,
                                 ' ' + str(int(np.round(f/1000**pow1000, 0))) +
                                 ' ' + prefix + 'Hz')

                    # ModelicaRes 7/5/13:
                    # Mark the freqencies with a dot.
                    ax.plot(xpt, ypt, '.', color=color)
        # ModelicaRes 7/5/13:
        #return x, y, omega
        return x, y, omega, ax

