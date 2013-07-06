#!/usr/bin/python
"""Set up and run simulations in Dymola, and then plot the results.
"""
__author__ = "Kevin Davies"
__version__ = "2012-10-11"

import os
import matplotlib.pyplot as plt

from modelicares import gen_experiments, SimRes, write_script, saveall

# Settings
# Begin customize--------------------------------------------------------------

# Run the simulations? (otherwise, just plot)
run = True

# Name of the Modelica script (may include the path)
fname = 'run-sims.mos'

# Working directory
working_dir = '~/Documents/Modelica'

# List of Modelica packages that should be preloaded (besides the Modelica
# Standard Library)
# Each may be a *.mo file or a path where a package.mo file resides, e.g.,
# "/opt/dymola/Modelica/Library/VehicleInterfaces 1.1.1".
packages = []

# List or generator of simulations to run
experiments = gen_experiments(
                    models=['Modelica.Electrical.Analog.Examples.ChuaCircuit'],
                    params={'L.L': [None, 10]}, # None uses default
                    args=dict(stopTime=[2500]))

# Formats in which to save the figures (e.g., ['pdf', 'eps', 'svg', 'png'])
# If the figures shouldn't be saved, specify an empty list.
formats = ['pdf', 'png']

# End customize----------------------------------------------------------------

if run:
    # Create the script to load the packages, simulate, and save the results.
    models, results_dir = write_script(experiments, working_dir=working_dir,
                                       packages=packages, fname=fname)

    # Ask Dymola to run the script.
    os.system('dymola ' + fname) # For Linux
    # TODO: Add support for Windows.
    #os.system(r'C:\Program files\Dymola\bin\Dymola.exe ' + fname) # For Windows
else:
    models = [experiment.model[experiment.model.rfind('.')+1:]
              for experiment in experiments]
    results_dir = os.path.split(fname)[0]

# Create plots.
# Begin customize--------------------------------------------------------------

for i, model in enumerate(models):
    sim = SimRes(os.path.join(results_dir, str(i + 1), 'dsres.mat'))
    sim.plot(title="Chua Circuit with L = %.0f %s" % (sim.get_IV('L.L'),
                                                      sim.get_unit('L.L')),
             ynames1=['L.i'], ylabel1='Current',
             ynames2=['L.der(i)'], ylabel2='Derivative of current',
             label=os.path.join(str(i + 1), model))

# End customize----------------------------------------------------------------

# Save the plots.
saveall(formats)
plt.show()
