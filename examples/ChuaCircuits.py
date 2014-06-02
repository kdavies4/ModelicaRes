#!/usr/bin/python
# Example of SimResList.plot()

from modelicares import SimResList

sims = SimResList('ChuaCircuit.mat', 'ChuaCircuit/*/')

# Create labels.
label = lambda L: 'w/ L.L = {L} {U}'.format(L=L.value(), U=L.unit)
for sim in sims:
    sim.label = label(sim['L.L'])

# Create the plot
sims.plot('L.i', ylabel1="Voltage", leg1_kwargs=dict(loc='upper right'),
          title="Chua circuit\nwith varying inductance")
