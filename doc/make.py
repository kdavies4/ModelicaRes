#!/usr/bin/env python
# Make the html or latex documentation of the FCSys Utilities.
#
# This file has been copied and modified from the same file in matplotlib v1.2.
# Kevin Davies, 9/17/2012

from __future__ import print_function
from shutil import ignore_patterns, copytree
import fileinput
import glob
import os
import shutil
import sys

def check_build():
    build_dirs = ['build', 'build/doctrees', 'build/html', 'build/latex',
                  '_static', '_templates']
    for d in build_dirs:
        try:
            os.mkdir(d)
        except OSError:
            pass

def html():
    check_build()
    options = ''
    if os.system('sphinx-build %s -b html -d build/doctrees . build/html' % options):
        raise SystemExit("Building HTML failed.")

    # Make hard link to the files from the help directory (hack).
    #os.system('cd build/html; for s in *.html *.inv *.js; do ln -f $s  ../../../help/$s; done')

    # Clean out PDF files from the _images directory
    for filename in glob.glob('build/html/_images/*.pdf'):
        os.remove(filename)

def latex():
    check_build()
    if sys.platform != 'win32':
        # LaTeX format
        if os.system('sphinx-build -b latex -d build/doctrees . build/latex'):
            raise SystemExit("Building LaTeX failed.")

        # Produce pdf.
        os.chdir('build/latex')

        # Replace ">>>" "..." that are included for examples.
        os.system('echo Confirmation is needed to remove the ">>>" and "..." that prefix lines of example code.')
        os.system(r'rpl -q "\PYG{g+gp}{\textgreater{}\textgreater{}\textgreater{} }" "" *.tex')
        os.system(r'rpl -q "\PYG{g+gp}{... }" "" *.tex')

        # Call the makefile produced by sphinx.
        if os.system('make'):
            raise SystemExit("Rendering LaTeX failed.")

        # Make hard link to PDF file from the help directory (hack).
        #os.system('ln -f FCSysUtilities.pdf  ../../../help/FCSysUtilities.pdf')

        os.chdir('../..')
    else:
        print('The Latex build has not been tested on Windows.')

def clean():
    shutil.rmtree("build", ignore_errors=True)
#    for pattern in []:
#        for filename in glob.glob(pattern):
#            if os.path.exists(filename):
#                os.remove(filename)

def all():
    html()
    latex()

funcd = {
    'html'     : html,
    'latex'    : latex,
    'clean'    : clean,
    'all'      : all,
    }

small_docs = False

# Change directory to the one containing this file.
current_dir = os.getcwd()
os.chdir(os.path.dirname(os.path.join(current_dir, __file__)))

if len(sys.argv)>1:
    if '--small' in sys.argv[1:]:
        small_docs = True
        sys.argv.remove('--small')
    for arg in sys.argv[1:]:
        func = funcd.get(arg)
        if func is None:
            raise SystemExit('Do not know how to handle %s; valid args are %s'%(
                    arg, funcd.keys()))
        func()
else:
    small_docs = False
    all()
os.chdir(current_dir)
