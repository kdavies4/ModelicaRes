#!/usr/bin/python
from modelicares import SimRes

sim = SimRes('ThreeTanks.mat')
sim.sankey(title="Sankey Diagrams of Modelica.Fluid.Examples.Tanks.ThreeTanks",
           times=[0, 50, 100, 150], n_rows=2, format='%.1f ',
           names=['tank1.ports[1].m_flow', 'tank2.ports[1].m_flow',
                  'tank3.ports[1].m_flow'],
           labels=['Tank 1', 'Tank 2', 'Tank 3'],
           orientations=[-1, 0, 1],
           scale=0.1, margin=6, offset=1.5,
           pathlengths=2, trunklength=10)
