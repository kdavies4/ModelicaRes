#!/usr/bin/python
"""Example of LinRes.bode()
"""

# pylint: disable=I0011, C0103

from modelicares import LinRes

lin = LinRes('PID.mat')
lin.bode(title="Bode plot of Modelica.Blocks.Continuous.PID")
