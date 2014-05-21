#!/usr/bin/python

import numpy as np
from os.path import join, dirname
from modelicares import LinResList, read_params

lins = LinResList('PID/*/*.mat')
labels = ["Td=%g" % read_params('Td', join(dirname(lin.fname), 'dsin.txt'))
          for lin in lins]
lins.nyquist(title="Nyquist plot of Modelica.Blocks.Continuous.PID",
             textFreq=True, omega=2*np.pi*np.logspace(-1, 3, 81), labelFreq=20,
             labels=labels)
