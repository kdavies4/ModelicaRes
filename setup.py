#!/usr/bin/python
"""Set up the ModelicaRes package.

See README.md for instructions.
"""

# pylint: disable=E0611, F0401

import re

from glob import glob

try:
    from setuptools import setup
except ImportError:
    try:
        from setuptools.core import setup
    except ImportError:
        try:
            from distutils.core import setup
        except ImportError:
            from numpy.distutils.core import setup

def get_version(fname):
    """Return the version number of the module in file *fname*.
    """
    with open(fname) as module:
        try:
            return re.search('__version__ *= *["'"'"'](.*)["'"'"']',
                             module.read()).group(1)
        except AttributeError:
            return

VERSION = get_version('modelicares/__init__.py')

setup(name='ModelicaRes',
      version=VERSION if VERSION else '0-unreleased_copy',
      description=('Utilities to set up and analyze Modelica simulation '
                   'experiments'),
      long_description=open('README.txt').read(),
      author='Kevin Davies',
      author_email='kdavies4@gmail.com',
      url='http://kdavies4.github.io/ModelicaRes/',
      download_url=('https://github.com/kdavies4/ModelicaRes/archive/v%s.zip'
                    % VERSION if VERSION else ''),
      packages=['modelicares', 'modelicares.exps', 'modelicares._io'],
      scripts=glob('bin/*'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Microsoft :: Windows',
          'Environment :: Console',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Topic :: Utilities',
      ],
      license='BSD-compatible (see LICENSE.txt)',
      keywords=['Modelica', 'plot', 'results', 'simulation', 'experiment',
                'Dymola', 'matplotlib', 'pandas'],
      provides=['modelicares'],
      install_requires=['numpy', 'matplotlib>=1.3.1', 'pandas', 'control',
                        'six'],
      requires=['numpy', 'scipy (>=0.10.0)', 'matplotlib (>=1.3.1)', 'pandas',
                'control', 'six'],
      platforms='any',
      zip_safe=True,
     )
      # ModelicaRes may run with scipy as early as 0.7.0.  However, the control
      # package seems to need scipy >= 0.10.0 but does not stipulate the
      # version.
