#!/usr/bin/python
# Create the static images for the HTML index page and the README.md file at the
# base of the project.

from os.path import join
import numpy as np
import matplotlib.pyplot as plt
from os.path import join, dirname
from modelicares import SimRes, SimResList, LinResList, read_params

# Options
dpi = 90 # DPI for the HTML index images
dpi_small = 45 # DPI for the README images
kwargs = dict(bbox_inches='tight', format='png') # Other options
indir = "../examples"
outdir = "_static"

# PIDs-nyquist
lins = LinResList(join(indir, 'PID/*/*.mat'))
labels = ["Td=%g" % read_params('Td', join(dirname(lin.fname), 'dsin.txt'))
          for lin in lins]
lins.nyquist(title="Nyquist plot of Modelica.Blocks.Continuous.PID",
             textFreq=True, omega=2*np.pi*np.logspace(-1, 3, 81), labelFreq=20,
             labels=labels)
plt.savefig(join(outdir, 'PIDs-nyquist.png'), dpi=dpi, **kwargs)
plt.close()

# ChuaCircuit
sim = SimRes(join(indir, 'ChuaCircuit.mat'))
sim.plot(ynames1='L.i', ylabel1="Current",
         ynames2='L.der(i)', ylabel2="Derivative of current",
         title="Chua circuit")
plt.savefig(join(outdir, 'ChuaCircuit.png'), dpi=dpi, **kwargs)
plt.close()

# ThreeTanks
sim = SimRes(join(indir, 'ThreeTanks.mat'))
sim.sankey(title="Sankey Diagrams of Modelica.Fluid.Examples.Tanks.ThreeTanks",
           times=[0, 50, 100, 150], n_rows=2, format='%.1f ',
           names=['tank1.ports[1].m_flow', 'tank2.ports[1].m_flow',
                  'tank3.ports[1].m_flow'],
           labels=['Tank 1', 'Tank 2', 'Tank 3'],
           orientations=[-1, 0, 1],
           scale=0.1, margin=6, offset=1.5,
           pathlengths=2, trunklength=10)
plt.savefig(join(outdir, 'ThreeTanks.png'), dpi=dpi, **kwargs)
plt.savefig(join(outdir, 'ThreeTanks-small.png'), dpi=dpi_small, **kwargs)
plt.close()

# ChuaCircuits
sims = SimResList(join(indir, 'ChuaCircuit/*/*.mat'))
sims.reverse()
sims.plot(title="Chua circuit",
          suffixes=['L.L = %.0f H' % sim['L.L'].IV()
                    for sim in sims], # Read legend parameters.
          ynames1='L.i', ylabel1="Current", leg1_kwargs=dict(loc='upper right'))
plt.savefig(join(outdir, 'ChuaCircuit-small.png'), dpi=dpi_small, **kwargs)
plt.close()
