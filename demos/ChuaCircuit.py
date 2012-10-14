#!/usr/bin/env python
"""This a demo script to set up and run cell or general simulations in Dymola,
and then create plots of the results.
"""
__author__ = "Kevin Davies"
__version__ = "2012-10-11"

import os
import matplotlib.pyplot as plt

from res import save_figs
from modelicares import SimRes, SimSpec, gen_sim_script

# Settings
# Run the simulations? (otherwise, just plot)
run = True
# Name of the Modelica script (including the path)
fname = os.path.abspath('run-sims.mos')
# Directory where the working files (e.g., dslog.txt) should be placed
working_dir = os.path.abspath('../'*5) # The root of the FCSys folder is 4 levels above this one.
# List of Modelica packages that should be loaded (besides the Modelica Standard
# Library)
# Each may be a *.mo file or a path where a package.mo file resides, e.g.,
# "/opt/dymola/Modelica/Library/VehicleInterfaces 1.1.1".
packages = []
# List of simulations to run
simspecs = [SimSpec('Modelica.Electrical.Analog.Examples.ChuaCircuit', # Name of model
                    startTime=None, # Start of simulation (default: 0)
                    stopTime=2500, # End of simulation (default: 1)
                    numberOfIntervals=None, # Number of output points (default: 0)
                    outputInterval=None, # Distance between output points (default: 0)
                    method=None, # Integration method (default: "Dassl")
                    tolerance=None, # Tolerance of integration (default: 0.0001)
                    fixedstepsize=None, # Fixed step size for Euler (default: 0)
                    resultFile='ChuaCircuit'), # Where to store result
            SimSpec('Modelica.Electrical.Analog.Examples.ChuaCircuit(L(L=10))',
                    startTime=None,
                    stopTime=2500,
                    numberOfIntervals=None,
                    outputInterval=None,
                    method=None,
                    tolerance=None,
                    fixedstepsize=None,
                    resultFile='ChuaCircuit2')
            ]
# Formats in which to save the figures, e.g., ['pdf', 'eps', 'svg', 'png']
# If the figures shouldn't be saved, specify an empty list.
formats = ['pdf', 'png']

if run:
    # Create the script to load the packages, simulate, and save the results.
    models, results_dir = gen_sim_script(simspecs, packages=packages,
                                         fname=fname, working_dir=working_dir)

    # Ask Dymola to run the script.
    os.system("bash /opt/dymola/bin/dymola.sh " + fname) # This is for Linux.
    # TODO: Add support for Windows.
else:
    models = [simspec.problem[simspec.problem.rfind('.')+1:] for simspec in simspecs]
    results_dir = os.path.split(fname)[0]

# Create plots.
# Note: The code between the '---' lines must be customized for each simulation
# and plot.
# ------------------------------

for simspec in simspecs:
    label = simspec.resultFile
    sim = SimRes(os.path.join(results_dir, label))
    title="Chua Circuit with L = %.0f %s"%(sim.get_IV('L.L'), sim.get_unit('L.L'))
    sim.plotfig(ynames1=['L.i'], ylabel1='Current',
                   ynames2=['L.der(i)'], ylabel2='Derivative of current',
                   title=title, label=label)

# ------------------------------

# Save the plots.
save_figs(formats)
plt.show()
