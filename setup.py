#!/usr/bin/python
"""Set up the ModelicaRes package.

See README.md for instructions.
"""

from glob import glob

from distutils.core import setup
#try:
#    from setuptools import setup
#except ImportError:
#    try:
#        from setuptools.core import setup
#    except ImportError:
#        from distutils.core import setup

setup(name='ModelicaRes',
      version="{version}",
      description='Utilities to set up and analyze Modelica simulation experiments',
      long_description=open('README.txt').read(),
      author='Kevin Davies',
      author_email='kdavies4@gmail.com',
      url='http://kdavies4.github.io/ModelicaRes/',
      packages=['modelicares', 'modelicares.exps', 'modelicares._io'],
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
                'Dymola', 'matplotlib', 'pandas'],
      provides=['modelicares'],
      install_requires=['numpy', 'scipy>=0.10.0', 'matplotlib>=1.3.1', 'pandas',
                        'control'],
      requires=['numpy', 'scipy (>=0.10.0)', 'matplotlib (>=1.3.1)', 'pandas',
                'PyQt4', 'control'],
      platforms='any',
      )
      # This package may run with scipy as early as 0.7.0.  However, the control
      # package seems to need scipy >= 0.10.0 but does not stipulate the
      # version.
