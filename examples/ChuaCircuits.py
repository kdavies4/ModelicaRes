#!/usr/bin/python
"""Example of SimResList.plot()
"""

# pylint: disable=I0011, C0103

from modelicares import SimResList

sims = SimResList('ChuaCircuit.mat', 'ChuaCircuit/*/')

# Create labels.
label = lambda L: 'w/ L.L = {L} {U}'.format(L=L.value(), U=L.unit)
sims.label = map(label, sims['L.L'])

# Create the plot.
sims.plot('L.i', ylabel1="Voltage", leg1_kwargs=dict(loc='upper right'),
          title="Chua circuit\nwith varying inductance")
