#!/usr/bin/python
"""Example of LinRes.nyquist()
"""

# pylint: disable=I0011, C0103, R0801

from modelicares import LinRes

lin = LinRes('PID.mat')
lin.nyquist(title="Nyquist plot of Modelica.Blocks.Continuous.PID",
            freqs=(0.1, 1000))
