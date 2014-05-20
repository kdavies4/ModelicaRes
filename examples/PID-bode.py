#!/usr/bin/python

import numpy as np
from modelicares import LinRes

lin = LinRes('PID.mat')
lin.bode(omega=2*np.pi*np.logspace(-2, 3),
         title="Bode plot of Modelica.Blocks.Continuous.PID")
