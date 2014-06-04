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
    # Run tests.
    if bash('runtests.sh').exit_code:
        print("The tests failed.")
        util.delayed_exit()
    if setup('check', '-s', '--metadata', '--restructuredtext').exit_code:
        print("setup.py check failed.")
        util.delayed_exit()

    # Update the version number.
    last_version = git.describe('--tags', abbrev=0).stdout.rstrip()
    version = raw_input("Enter the version number (last was %s): "
                        % last_version)
    # TODO: default: lightweight tag; last: only annotated

    # TODO: write version to modelicares/__init__.py

    # TODO: assert version isn't already an annotated tag (i.e., released version)

    # TODO: if version is listed at top of changes:
    #     update date
    # else:
    #     add list at top of changes w/ date and version
    #     add download link

    # Build the code.
    setup.build()
    setup.sdist(formats='gztar,zip')

    # Use the zip command to change the line endings to Windows format.  TODO: Is there a better way?  Run a script directly or build/* before sdist?
    name = python('setup.py', '--fullname').stdout.rstrip()
    #(cd dist
    os.remove(name + '.zip')
    sh.tar('-xf', name + '.tar.gz')
    sh.zip('-rl', name + '.zip', name)
    shutil.rmtree(name)
    #)

    # TODO lightweight tag

def clean():
    """Clean/remove the built code.
    """
    setup.clean('--all')

def release():
    """Release/publish the code.
    """

    # Rebase, annotate the release tag, and push the tag and master to origin.
    print("Here's a list of the TODO items:")
    print(bash('../TODO.sh'))
    print()
    if not util.yes("Do you want to rebase, annotate the release tag, and push "
                    "the tag and master to origin (y/n)?"):
        util.delayed_exit()
    git.rebase('-i', 'origin/master')
    # TODO: Assert the last tag is lightweight, and annotate it.
    git.push('--tags', 'origin', 'master')

    # Upload to PyPI.
    if not util.yes("Do you want to upload it to PyPI (this is permanent!) "
                    "(y/n)?"):
        util.delayed_exit()
    setup('sdist', 'upload')

    # TODO add blank lines to changes.txt, reset version in modelicares/__init__.py

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
