#!/usr/bin/python
"""Set up the ModelicaRes package.

See README.md for instructions.
"""

# pylint: disable=C0103

import re
import versioneer

from glob import glob
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

versioneer.VCS = 'git'
versioneer.versionfile_source = 'modelicares/_version.py'
versioneer.versionfile_build = 'modelicares/_version.py'
versioneer.tag_prefix = 'v' # Tags are like 1.2.0
versioneer.parentdir_prefix = 'ModelicaRes-'
version = versioneer.get_version()

with open(path.join(here, 'doc/long-description.txt')) as f:
    long_description = f.read()

setup(name='ModelicaRes',
      version=version,
      cmdclass=versioneer.get_cmdclass(),
      description="Set up, plot, and analyze Modelica simulations in Python",
      long_description=long_description,
      author='Kevin Davies',
      author_email='kdavies4@gmail.com',
      license='BSD-compatible (see LICENSE.txt)',
      keywords=('results dymola openmodelica data mat file analysis script '
                'sort filter browse export diagram simulation linearization '
                'experiment matplotlib pandas'),
      url='http://kdavies4.github.io/ModelicaRes/',
      download_url=('https://github.com/kdavies4/ModelicaRes/archive/v%s.zip'
                    % version),
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
      package_data={'modelicares': ['display.ini']},
      scripts=glob('bin/*'),
      install_requires=['numpy', 'matplotlib>=1.3.1', 'natu', 'pandas',
                        'control', 'six'],
      requires=['numpy', 'scipy (>=0.10.0)', 'matplotlib (>=1.3.1)', 'natu',
                'pandas', 'control', 'six'],
      platforms='any',
      zip_safe=False, # because display.ini must be accessed
      test_suite = 'tests.test_suite',
     )
# ModelicaRes may run with scipy as early as 0.7.0.  However, the control
# package needs scipy >= 0.10.0 but does not stipulate the version.
