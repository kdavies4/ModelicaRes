#!/usr/bin/python

from modelicares import LinRes

lin = LinRes('PID.mat')
lin.nyquist(title="Nyquist plot of Modelica.Blocks.Continuous.PID",
            freqs=(0.1, 1000))
