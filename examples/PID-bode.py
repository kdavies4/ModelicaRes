#!/usr/bin/python
# Example of LinRes.bode()

from modelicares import LinRes

lin = LinRes('PID.mat')
lin.bode(title="Bode plot of Modelica.Blocks.Continuous.PID")
