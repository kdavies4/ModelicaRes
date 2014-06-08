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
RUN = True

# Name of the Modelica script (may include the path)
FNAME = 'run_sims.mos'

# Working directory
WORKING_DIR = '~/Documents/Modelica'

# List of Modelica packages that should be preloaded (besides the Modelica
# Standard Library)
# Each may be a *.mo file or a path where a package.mo file resides, e.g.,
# "/opt/dymola/Modelica/Library/VehicleInterfaces 1.1.1".
PACKAGES = []

# List or generator of simulations to run
EXPERIMENTS = gen_experiments(
    models=['Modelica.Electrical.Analog.Examples.ChuaCircuit'],
    params={'L.L': [15, 21]}, # Can use none for default
    args=dict(stopTime=[2500]))

# Formats in which to save the figures (e.g., ['pdf', 'eps', 'svg', 'png'])
# If the figures shouldn't be saved, specify an empty list.
FORMATS = ['pdf', 'png']

# End customize----------------------------------------------------------------

if RUN:
    # Create the script to load the packages, simulate, and save the results.
    MODELS, RESULTS_DIR = write_script(EXPERIMENTS, working_dir=WORKING_DIR,
                                       packages=PACKAGES, fname=FNAME)

    # Ask Dymola to run the script.
    os.system('dymola ' + FNAME) # For Linux
    # TODO: Add support for Windows.
    # os.system(r'C:\Program files\Dymola\bin\Dymola.exe ' + FNAME) # For Windows
else:
    MODELS = [experiment.model[experiment.model.rfind('.')+1:]
              for experiment in EXPERIMENTS]
    RESULTS_DIR = os.path.split(FNAME)[0]

# Create plots.
# Begin customize--------------------------------------------------------------

for i, model in enumerate(MODELS):
    sim = SimRes(os.path.join(RESULTS_DIR, str(i + 1), 'dsres.mat'))
    sim.plot(title="Chua Circuit with L = %.0f %s" % (sim['L.L'].IV(),
                                                      sim['L.L'].unit),
             ynames1=['L.i'], ylabel1='Current',
             ynames2=['L.der(i)'], ylabel2='Derivative of current',
             label=os.path.join(str(i + 1), model))

# End customize----------------------------------------------------------------

# Save the plots.
saveall(FORMATS)
plt.show()
