#!/usr/bin/python
"""Set up the ModelicaRes module.

See README.txt for instructions.
"""

from distutils.core import setup
from glob import glob

setup(name='ModelicaRes',
      version="0.10.0",
      description='Utilities to set up and analyze Modelica simulation experiments',
      long_description=open('README.txt').read(),
      author='Kevin Davies',
      author_email='kdavies4@gmail.com',
      url='http://kdavies4.github.io/ModelicaRes/',
      packages=['modelicares', 'modelicares.exps'],
      scripts=glob('bin/*'),
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
      license='BSD-compatible (see LICENSE.txt)',
      keywords=['Modelica', 'plot', 'results', 'simulation', 'experiment', 
                'Dymola', 'matplotlib'],
      provides=['modelicares'],
      requires=['python (==2.7)', 'scipy (>=0.10.0)', 'numpy', 
                'matplotlib (>=1.1.0)', 'control', 'wx', 'easygui', ],
      # Note: This package may run with scipy as early as 0.7.0.  However, the 
      # control package seems to need scipy >= 0.10.0 but does not stipulate the 
      # version.
      )
