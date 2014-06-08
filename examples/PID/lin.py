#!/usr/bin/python
"""Set up and run linearizations in Dymola.
"""
__author__ = "Kevin Davies"
__version__ = "2013-7-4"

import os

from modelicares import gen_experiments, write_script

# Settings
# Begin customize--------------------------------------------------------------

# Name of the Modelica script (may include the path)
FNAME = 'run_lins.mos'

# Working directory
WORKING_DIR = '~/Documents/Modelica'

# List of Modelica packages that should be preloaded (besides the Modelica
# Standard Library)
# Each may be a *.mo file or a path where a package.mo file resides, e.g.,
# "/opt/dymola/Modelica/Library/VehicleInterfaces 1.1.1".
PACKAGES = []

# List or generator of simulations to run
EXPERIMENTS = gen_experiments(['Modelica.Blocks.Continuous.PID'],
                              params=dict(Td=[1, 10]))

# End customize----------------------------------------------------------------

# Create the script to load the packages, simulate, and save the results.
write_script(EXPERIMENTS, working_dir=WORKING_DIR, packages=PACKAGES,
             fname=FNAME, command="linearizeModel",
             results=["dsin.txt", "dymolalg.txt", "dymosim", "dslog.txt",
                      "dslin.mat"])

# Ask Dymola to run the script.
os.system('dymola ' + FNAME) # For Linux
# TODO: Add support for Windows.
# os.system(r'C:\Program files\Dymola\bin\Dymola.exe ' + FNAME) # For Windows
