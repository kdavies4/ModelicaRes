#!/usr/bin/env python
# Script to clean, build, and release the ModelicaRes code.

import sys
import sh

from collections import namedtuple
from sh import bash, git, python
from modelicares import util

setup = python.bake('setup.py')

def build():
    """Build/make the code.
    """
    setup.build()
    setup.sdist(formats='gztar,zip')

def clean():
    """Clean/remove the built code.
    """
    setup.clean('--all')

def release():
    """Release/publish the code.
    """

    # Confirm to continue.
    print("Here's a list of the TODO items:")
    print(bash('../TODO.sh'))
    print()
    if not util.yes("Do you want to continue (y/n)?"):
        util.delayed_exit()

    # Run tests.
    if bash('runtests.sh').exit_code:
        print("The tests failed.")
        util.delayed_exit()
    if setup('check', '-s', '--metadata', '--restructuredtext').exit_code:
        print("setup.py check failed.")
        util.delayed_exit()

    # Get the version number.
    last_version = git.describe('--tag', abbrev=0).stdout.rstrip()
    version = raw_input("Enter the version number (last was %s): "
                        % last_version)

    # Use the zip command to change the line endings to Windows format.  TODO: Is there a better way?
    name = python('setup.py', '--fullname').stdout.rstrip()
    #(cd dist
    os.remove(name + '.zip')
    sh.tar('-xf', name + '.tar.gz')
    sh.zip('-rl', name + '.zip', name)
    shutil.rmtree(name)
    #)

    # Rebase the release branch at the current master.
    git.rebase('-i', 'master')

    print("The package has been built as TODO.")
    if util.yes("Do you want to upload it to PyPI (this is permanent!) (y/n)?"):
        setup('sdist', 'upload')
        git.push('--tags', 'origin', 'master')


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
