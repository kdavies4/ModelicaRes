#!/usr/bin/python
"""Set up the ModelicaRes module.

See the README.txt file for instructions.
"""

from distutils.core import setup
from glob import glob

import modelicares # Only to read the version number

setup(name='ModelicaRes',
      version=modelicares.__version__,
      author='Kevin Davies',
      author_email='kdavies4@gmail.com',
      #credits=['Kevin Bandy', 'Jason Grout', 'Jason Heeris', 'Joerg Raedler'],
      packages=['control', 'modelicares'],
      scripts=glob('bin/*'),
      url='http://kdavies4.github.com/ModelicaRes/',
      license='BSD-compatible (see LICENSE.txt)',
      description='Utilities to set up and analyze Modelica simulation experiments',
      long_description=open('README.txt').read(),
      provides=['modelicares'],
      requires=['python (==2.7)', 'matplotlib', 'numpy', 'wx'],
      package_dir={'control': 'external/control/src'},
      keywords=['Modelica', 'Dymola', 'plot', 'matplotlib', 'simulation',
                'experiment', 'results'],
      classifiers=['Development Status :: 4 - Beta',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: Microsoft :: Windows',
                   'Environment :: Console',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2.7',
                   'Intended Audience :: Science/Research',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Utilities',
                   ],
      )

# 10/30/11: Not currently using PyTables (TODO: Consider it for the future).
# Install PyTables (version 2.3.1, and maybe later, works).
# See http://www.pytables.org/moin/Downloads
#import subprocess
#subprocess.call("sudo easy_install tables")
