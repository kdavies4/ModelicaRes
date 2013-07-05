#!/usr/bin/python
"""Set up and run linearizations in Dymola.
"""
__author__ = "Kevin Davies"
__version__ = "2013-7-4"

import os

from fcres import gen_experiments, write_script

# Settings
# Begin customize--------------------------------------------------------------

# Name of the Modelica script (may include the path)
fname = 'lin.mos'

# Working directory
working_dir = '~/Documents/Modelica'

# List of Modelica packages that should be preloaded (besides the Modelica
# Standard Library)
# Each may be a *.mo file or a path where a package.mo file resides, e.g.,
# "/opt/dymola/Modelica/Library/VehicleInterfaces 1.1.1".
packages = []

# List or generator of simulations to run
experiments = gen_experiments(['Modelica.Blocks.Continuous.PID'],
                              params=dict(Td=[0.1, 10]))

# End customize----------------------------------------------------------------

# Create the script to load the packages, simulate, and save the results.
write_script(experiments, working_dir=working_dir, packages=packages,
             fname=fname, command="linearizeModel", results=["dsin.txt",
             "dymolalg.txt", "dymosim", "dslog.txt", "dslin.mat"])

# Ask Dymola to run the script.
os.system('dymola ' + fname) # For Linux
# TODO: Add support for Windows.
#os.system(r'C:\Program files\Dymola\bin\Dymola.exe ' + fname) # For Windows
