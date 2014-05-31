#!/usr/bin/python

from modelicares import LinResList

results = ['PID.mat', 'PID/1/dslin.mat', 'PID/2/dslin.mat']
labels = ["Td = 0.1 s", "Td = 1 s", "Td = 10 s"]
lins = LinResList(*results)
lins.nyquist(title="Nyquist plot of Modelica.Blocks.Continuous.PID\n"
                   "with varying differential time constant",
             labels=labels, freqs=(0.1, 100));
# It's necessary to provide the differential time constants because they're not
# recorded in the files.  However, if each result is accompanied with a
# dsin-style parameter file, we can use read_params(), e.g.:
#from os.path import join, dirname
#from modelicares import LinResList, read_params
#lins = LinResList('PID/*/*.mat')
#labels = ["Td=%g" % read_params('Td', join(dirname(lin.fname), 'dsin.txt'))
#          for lin in lins]
#lins.nyquist(title="Nyquist plot of Modelica.Blocks.Continuous.PID\n"
#                   "with varying differential time constant",
#             labels=labels)
