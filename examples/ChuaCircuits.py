#!/usr/bin/python

from modelicares import SimResList

sims = SimResList('ChuaCircuit/*/*.mat')
sims.plot(title="Chua circuit",
          suffixes=['L.L = %.0f H' % sim['L.L'].IV()
                    for sim in sims], # Read legend parameters.
          ynames1='L.i', ylabel1="Current", leg1_kwargs=dict(loc='upper right'))
