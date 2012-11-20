#!/usr/bin/python
"""Set up the ModelicaRes modules.

Instructions for installation on Linux:

1. Build the modules.
   $ ./setup.py build

2. Install the modules.
   $ sudo ./setup.py install
"""

from distutils.core import setup

# Install the core Python modules.
setup(name='ModelicaRes',
      version='0.2',
      author='Kevin Davies',
      author_email='kdavies4@gmail.com',
      #credits=['Kevin Bandy', 'Jason Grout', 'Jason Heeris', 'Joerg Raedler'],
      packages=['control', 'modelicares'],
      scripts=['bin/loadres'],
      url='http://kdavies4.github.com/ModelicaRes/',
      license='LICENSE.txt',
      description='Utilities to set up and analyze Modelica simulation experiments',
      long_description=open('README.txt').read(),
      requires=['matplotlib', 'numpy', 'wx'],
      package_dir = {'control': 'external/control/src'},
      keywords = "modelica plot dymola mat simulation experiment",
      classifiers = ["Development Status :: 4 - Beta",
                     "Environment :: Console",
                     "License :: OSI Approved :: BSD License",
                     "Programming Language :: Python :: 2.7",
                     "Intended Audience :: Science/Research",
                     "Topic :: Scientific/Engineering",
                     "Topic :: Utilities",
                     ],
      )

# 10/30/11: Not currently using PyTables (but consider it for the future).
# Install PyTables (version 2.3.1, and maybe later, works).
# See http://www.pytables.org/moin/Downloads
#import subprocess
#subprocess.call("sudo easy_install tables")
