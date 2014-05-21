#!/usr/bin/env python
# Build the html documentation for ModelicaRes.
#
# This file has been copied and modified from matplotlib v1.2.
# Kevin Davies, 9/17/2012

import os
import shutil
import sys


def make_dirs():
    build_dirs = ['build', 'build/doctrees', 'build/html', '_static',
                  '_templates']
    for d in build_dirs:
        try:
            os.mkdir(d)
        except OSError:
            pass

def html():
    make_dirs()
    options = ''
    if os.system('sphinx-build %s -b html -d build/doctrees . build/html' % options):
        raise SystemExit("The HTML build failed.")

def clean():
    shutil.rmtree('build', ignore_errors=True)

funcd = {'html'     : html,
         'clean'    : clean,
        }

if len(sys.argv)>1:
    for arg in sys.argv[1:]:
        func = funcd.get(arg)
        if func is None:
            raise SystemExit('Do not know how to handle %s; valid args are %s'%(
                    arg, funcd.keys()))
        func()
else:
    html()
