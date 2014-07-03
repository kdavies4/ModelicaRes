#!/usr/bin/python
"""Set up the ModelicaRes package.

See README.md for instructions.
"""

# pylint: disable=C0103

import re

from glob import glob
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'modelicares', '__init__.py')) as f:
    hit = re.search('__version__ *= *["'"'"'](.*)["'"'"']', f.read())
    try:
        version = hit.group(1)
    except AttributeError:
        version = None

with open(path.join(here, 'README.txt')) as f:
    long_description = f.read()

setup(name='ModelicaRes',
      version=version if version else '0-unreleased_version',
      description=("Set up, plot, and analyze Modelica simulations in Python"),
      long_description=long_description,
      author='Kevin Davies',
      author_email='kdavies4@gmail.com',
      license='BSD-compatible (see LICENSE.txt)',
      keywords=('results dymola openmodelica data mat analysis script sort '
                'filter browse export diagram simulation linearization '
                'experiment matplotlib pandas'),
      url='http://kdavies4.github.io/ModelicaRes/',
      download_url=('https://github.com/kdavies4/ModelicaRes/archive/v%s.zip'
                    % version if version else ''),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Utilities',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Microsoft :: Windows',
      ],
      provides=['modelicares'],
      packages=['modelicares', 'modelicares.exps', 'modelicares._io'],
      scripts=glob('bin/*'),
      install_requires=['numpy', 'matplotlib>=1.3.1', 'pandas', 'natu',
                        'control', 'six'],
      requires=['numpy', 'scipy (>=0.10.0)', 'matplotlib (>=1.3.1)', 'pandas',
                'natu', 'control', 'six'],
      platforms='any',
      zip_safe=True,
      test_suite = 'tests.test_suite',
     )
# ModelicaRes may run with scipy as early as 0.7.0.  However, the control
# package needs scipy >= 0.10.0 but does not stipulate the version.
