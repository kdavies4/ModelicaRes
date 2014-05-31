#!/usr/bin/python

from modelicares import LinRes

lin = LinRes('PID.mat')
lin.bode(title="Bode plot of Modelica.Blocks.Continuous.PID")
