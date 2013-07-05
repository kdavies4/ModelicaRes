#!/usr/bin/python
"""Create small sample figures for Github.
"""

import os

from glob import glob
from modelicares import SimRes, multiplot, saveall

# Figure 1
sims = map(SimRes, glob('ChuaCircuit/*/*.mat'))
multiplot(sims, title="Chua Circuit", label='ChuaCircuits',
          suffixes=['L.L = %.0f H' % sim.get_IV('L.L')
                    for sim in sims], # Read legend parameters.
          ynames1='L.i', ylabel1="Current")

# Figure 2
sim = SimRes('ThreeTanks')
sankeys = sim.sankey(label='ThreeTanks',
    title="Sankey Diagrams of Modelica.Fluid.Examples.Tanks.ThreeTanks",
    times=[0, 50, 100, 150], n_rows=2, format='%.1f ',
    names=['tank1.ports[1].m_flow', 'tank2.ports[1].m_flow',
          'tank3.ports[1].m_flow'],
    labels=['Tank 1', 'Tank 2', 'Tank 3'],
    orientations=[-1, 0, 1],
    scale=0.100, margin=6, offset=1.5,
    pathlengths=2, trunklength=10)

# Finish.
saveall('svg')
