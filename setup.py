#!/usr/bin/env python
"""Set up the modelicares modules.

Instructions for installation on Linux:

1. Build the modules.
   $ python ./setup.py build

2. Install the modules.
   $ sudo python ./setup.py install
"""
#import subprocess

from distutils.core import setup

# Install the core Python modules.
setup(name='fcsys',
      version='1.0',
      description='Python plotting and analysis utilities for Modelica',
      author='Kevin Davies',
      author_email='kld@alumni.carnegiemellon.edu',
      license = "Modelica License Version 2",
      url='http://www.github.org/modelicares', # **Give full URL once available.
      requires=['scipy', 'matplotlib'],
      py_modules=['res', 'modelicares', 'texunit', 'arrow_line', 'easywx'],
     )

# Install the third-party Python control module.
# Copied from control/setup.py and modified to run from here
setup(name='control',
      version='0.5b',
      description='Python Control Systems Library',
      author='Richard Murray',
      author_email='murray@cds.caltech.edu',
      url='http://python-control.sourceforge.net',
      requires=['scipy', 'matplotlib'],
      package_dir = {'control':'control/src'},
      packages=['control'],
     )

# In order to run dymosim from the command line in Linux, add this line to
# /etc/environment or ~/.pam_environment:
# LD_LIBRARY_PATH=/opt/dymola/bin/lib

# 10/30/11: Not currently using PyTables (but consider it for the future).
# Install PyTables (version 2.3.1, and maybe later, works).
# See http://www.pytables.org/moin/Downloads
# subprocess.call("sudo easy_install tables")
