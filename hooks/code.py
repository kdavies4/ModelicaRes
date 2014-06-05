#!/usr/bin/env python
# Script to clean, build, and release the ModelicaRes code.

import sys
import os
import sh
import shutil

from collections import namedtuple
from docutils.core import publish_string
from sh import bash, git, python, rm
from modelicares import util

setup = python.bake('setup.py')

def set_version(version, fname='modelicares/__init__.py'):
    """Update the version in a file.
    """
    util.replace(fname, [('(__version__) *= *.+', r"\1 = %s" % version)])

def build():
    """Build/make the code.

    """

    # Check that README.txt is a valid ReST file (otherwise, the PyPI page will
    # not show correctly).
    README = 'README.txt'
    ERROR_START = 'Docutils System Messages\n'
    with open(README, 'r') as rstfile:
        parsed = publish_string(rstfile.read())
    if ERROR_START in parsed:
        print("Errors in " + README)
        util.delayed_exit()

    # Run other setup tests.
    if setup.check('-rms').exit_code:
        print("The setup.py check failed.")
        util.delayed_exit()

    # Update the version number.
    lastversion = git.describe('--tags', abbrev=0).stdout.rstrip()[1:]
    version = raw_input("Enter the version number (last was %s): "
                        % lastversion)
    set_version("'%s'" % version)

    # TODO: Update date and version in top line of CHANGES.txt.
    # TODO: Add a download link in CHANGES.txt.

    # Build, install, and test the code.
    setup.build()
    os.system('sudo python setup.py install')
    os.system('sudo python3 setup.py install')
    print(bash('runtests.sh'))

    # Create a tarball (*.tar.gz).
    setup.sdist(formats='gztar')

    # From the tarball, create a zip version (*.zip) with Windows line endings.
    name = python('setup.py', '--fullname').stdout.rstrip()
    FOLDER = 'dist'
    path = os.path.join(FOLDER, name)
    sh.tar('-xf', path + '.tar.gz', '-C', FOLDER)
    sh.zip('-rl', path + '.zip', path)
    shutil.rmtree(path)

    # Tag the version (will prompt for message).
    git.tag('-af', 'v' + version)

def clean():
    """Clean/remove the built code.
    """
    setup.clean('--all')
    rm('-rf', "ModelicaRes.egg-info")

def release():
    """Release/publish the code.
    """

    # Rebase and push the master with tags to origin.
    print("Here are the remaining TODO items:")
    print(bash('TODO.sh'))
    print()
    if not util.yes("Do you still want to rebase and push the master with tags "
                    "to origin (y/n)?"):
        util.delayed_exit()
    git.rebase('-i', 'origin/master')
    #git.push('--tags', 'origin', 'master')

    # Upload to PyPI.
    if not util.yes("Do you want to upload to PyPI (this is permanent!) "
                    "(y/n)?"):
        util.delayed_exit()
    #setup.sdist.upload(formats='gztar,zip')

    # Reset the version number and start a new list in CHANGES.txt.
    set_version('None')
    # TODO Add blank lines to CHANGES.txt.

    #with open('CHANGES.txt', 'r+') as f:

        # TODO use re, rewrite whole file
        #f.write("vx.x.x_ (YYYY-MM-DD) -- Updates:")
        #f.write("")
        #f.write("   -")
    #".. _vx.x.x: https://github.com/kdavies4/ModelicaRes/archive/vx.x.x.zip"

F = namedtuple("F", ['f', 'description'])
funcs = {'clean'      : F(clean,   "Clean/remove the built code."),
         'build'      : F(build,   "Build/make the code."),
         'release'    : F(release, "Release/publish the code."),
        }

def funcs_str():
    """Return a string listing the valid functions and their descriptions.
    """
    return "\n".join(["  %s: %s" % (arg.ljust(8), function.description)
                      for (arg, function) in funcs.items()])


# Main
if len(sys.argv) != 2:
    raise SystemExit("Exactly one argument is required; valid args are\n"
                     + funcs_str())
arg = sys.argv[1]
try:
    funcs[arg].f()
except KeyError:
    raise SystemExit("Do not know how to handle %s; valid args are\n%s"
                     % (arg, funcs_str()))
