#!/usr/bin/python
"""Script to clean, build, and release the ModelicaRes code.
"""

# pylint: disable=E0611

import sys
import os

from time import strftime
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
    readme = 'README.txt'
    error_start = 'Docutils System Messages\n'
    with open(readme, 'r') as rstfile:
        parsed = publish_string(rstfile.read())
    if error_start in parsed:
        print("Errors in " + readme)
        util.delayed_exit()

    # Run other setup tests.
    if setup.check('-rms').exit_code:
        print("The setup.py check failed.")
        util.delayed_exit()

    # Update the version number.
    commit = git('rev-list', '--tags', '--max-count=1').stdout.rstrip()
    lastversion = git.describe('--tags', commit).stdout.rstrip().lstrip('v')
    # This is simpler but doesn't always return the latest tag:
    # lastversion = git.describe('--tag', abbrev=0).stdout.rstrip()
    version = raw_input("Enter the version number (last was %s): "
                        % lastversion)
    # In modelicares/__init__.py:
    set_version("'%s'" % version)
    # In CHANGES.txt:
    date = strftime('%Y-%-m-%-d')
    rpls = [(r'vx\.x\.x_ \(YYYY-MM-DD\)( -- Updates:)',
             r'v{v}_ ({d})\1'.format(v=version, d=date)),
            (r'v%s_ \(.+\)( -- Updates:)' % version,
             r'v{v}_ ({d})\1'.format(v=version, d=date)),
            (r'(.. _)vx\.x\.x(.+)vx\.x\.x(\.zip)',
             r'\1v{v}\2v{v}\3'.format(v=version))]
    util.replace('CHANGES.txt', rpls)

    # Build, install, and test the code.
    setup.build()
    os.system('sudo python setup.py install')
    os.system('sudo python3 setup.py install')
    print(bash('runtests.sh'))

    # Create a tarball and zip (*.tar.gz and *.zip).
    setup.sdist(formats='gztar,zip')

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
    git.push('--tags', 'origin', 'master')

    # Upload to PyPI.
    if not util.yes("Do you want to upload to PyPI (this is permanent!) "
                    "(y/n)?"):
        util.delayed_exit()
    setup.sdist.upload()

    # Reset the version number.
    # In modelicares/__init__.py:
    set_version('None')
    # In CHANGES.txt:
    newheading = 'vx.x.x_ (YYYY-MM-DD) -- Updates:'
    newlink = ('.. _vx.x.x: '
               'https://github.com/kdavies4/ModelicaRes/archive/vx.x.x.zip')
    rpls = [(r'(<http://semver.org>`_\.)',
             r'\1\n\n' + newheading),
            (r'\n(\nv[0-9]+\.[0-9]+\.[0-9]+_)',
             newlink + r'\n\1')]
    util.replace('CHANGES.txt', rpls)


Action = namedtuple("Action", ['f', 'description'])
ACTIONS = {'clean'   : Action(clean, "Clean/remove the built code."),
           'build'   : Action(build, "Build/make the code."),
           'release' : Action(release, "Release/publish the code."),
          }

def funcs_str():
    """Return a string listing the valid functions and their descriptions.
    """
    return "\n".join(["  %s: %s" % (arg.ljust(8), function.description)
                      for (arg, function) in ACTIONS.items()])


# Main
if len(sys.argv) != 2:
    raise SystemExit("Exactly one argument is required; valid args are\n"
                     + funcs_str())
ACTION = sys.argv[1]
try:
    ACTIONS[ACTION].f()
except KeyError:
    raise SystemExit("Do not know how to handle %s; valid args are\n%s"
                     % (ACTION, funcs_str()))
