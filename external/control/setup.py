#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

setup(name = 'control',
      version = '0.6c',
      description = 'Python Control Systems Library',
      author = 'Richard Murray',
      author_email = 'murray@cds.caltech.edu',
      url = 'http://python-control.sourceforge.net',
      # ModelicaRes 7/3/13:
      #requires = ['scipy', 'matplotlib'],
      requires = ['scipy (>= 0.10.0)', 'matplotlib'],
      package_dir = {'control' : 'src'},
      packages = ['control'],
     )
