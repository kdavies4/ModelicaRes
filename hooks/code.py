#!/usr/bin/python
"""Script to clean, build, and release the ModelicaRes code.
"""

# pylint: disable=I0011, C0103, C0325, E0611

import sys
import os

from time import strftime
from collections import namedtuple
from docutils.core import publish_string
from sh import bash, git, python, rm
from natu.util import delayed_exit, replace, yes

setup = python.bake('setup.py')

def build():
    """Build the code to prepare for release.
    """

    # Check that long-description.txt is a valid ReST file (otherwise, the PyPI
    # page won't display correctly).
    readme = 'doc/long-description.txt'
    error_start = 'Docutils System Messages\n'
    with open(readme, 'r') as rstfile:
        parsed = publish_string(rstfile.read())
    if error_start in parsed:
        print("Errors in " + readme)
        delayed_exit()

    # Run other setup tests.
    if setup.check('-rms').exit_code:
        print("The setup.py check failed.")
        delayed_exit()

    # Get the new version number.
    commit = git('rev-list', '--tags', '--max-count=1').stdout.rstrip()
    lastversion = git.describe('--tags', commit).stdout.rstrip().lstrip('v')
    # This is simpler but doesn't always return the latest tag:
    # lastversion = git.describe('--tag', abbrev=0).stdout.rstrip()
    version = raw_input("Enter the version number (last was %s): "
                        % lastversion)

    # Tag the version (will prompt for message).
    git.tag('-af', 'v' + version)

    # Update the version number.
    # In CHANGES.txt:
    date = strftime('%Y-%-m-%-d')
    rpls = [(r'TBD.*( -- Updates:)',
             r'v{v}_ ({d})\1'.format(v=version, d=date)),
            (r'v%s_ \(.+\)( -- Updates:)' % version,
             r'v{v}_ ({d})\1'.format(v=version, d=date)),
            (r'(.. _)vx\.x\.x(.+)vx\.x\.x(\.zip)',
             r'\1v{v}\2v{v}\3'.format(v=version))]
    replace('CHANGES.txt', rpls)
    # Note that versioneer automatically handles the version number in
    # modelicares/__init__.py.

    # Build, install, and test the code.
    setup.build()
    os.system('sudo python setup.py install')
    os.system('sudo python3 setup.py install')
    os.system('python setup.py test')
    os.system('python3 setup.py test')

    # Create a tarball and zip (*.tar.gz and *.zip).
    setup.sdist(formats='gztar,zip')

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
    if not yes("Do you still want to rebase and push the master with tags to "
               " origin (y/n)?"):
        delayed_exit()
    git.rebase('-i', 'origin/master')
    git.push('--tags', 'origin', 'master')

    # Upload to PyPI.
    if not yes("Do you want to upload to PyPI (this is permanent!) (y/n)?"):
        delayed_exit()
    setup.sdist.upload()

    # Reset the version number.
    # In CHANGES.txt:
    newheading = ('TBD (in `GitHub <https://github.com/kdavies4/ModelicaRes>`_ '
                  'only) -- Updates:')
    newlink = ('.. _vx.x.x: '
               'https://github.com/kdavies4/ModelicaRes/archive/vx.x.x.zip')
    rpls = [(r'(<http://semver.org>`_\.)',
             r'\1\n\n' + newheading),
            (r'(Initial release\n\n\n)',
             r'\1%s\n' % newlink)]
    replace('CHANGES.txt', rpls)
    # Note that versioneer automatically handles the version number in
    # modelicares/__init__.py.

Action = namedtuple("Action", ['f', 'description'])
ACTIONS = {'clean'   : Action(clean, "Clean/remove the built code."),
           'build'   : Action(build, "Build the code to prepare for release."),
           'release' : Action(release, "Release the code."),
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
