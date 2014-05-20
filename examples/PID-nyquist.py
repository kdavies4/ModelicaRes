#!/usr/bin/python

import numpy as np
from modelicares import LinRes

lin = LinRes('PID.mat')
lin.nyquist(omega=2*np.pi*np.logspace(0, 3, 61), labelFreq=20,
            title="Nyquist plot of Modelica.Blocks.Continuous.PID")
