#!/usr/bin/python

import numpy as np
from os.path import join, dirname
from modelicares import LinResList, read_params

lins = LinResList('PID/*/*.mat')
labels = ["Ti=%g" % read_params('Ti', join(dirname(lin.fname), 'dsin.txt'))
          for lin in lins]
lins.bode(title="Bode plot of Modelica.Blocks.Continuous.PID",
          omega=2*np.pi*np.logspace(-2, 3), labels=labels,
          leg_kwargs=dict(loc='lower right'))
