#!/usr/bin/env python
# Clean, build, and release the HTML documentation for ModelicaRes.

import os
import shutil
import sys

from sh import git, python, sphinx_build, ErrorReturnCode_1, ErrorReturnCode_128
from glob import glob
from collections import namedtuple
from modelicares import util

BUILD_DIR = 'build/html'

def build():
    """Build/make the HTML documentation.
    """

    # Rebuild the static images.
    if util.yes("Do you want to rebuild the static images (y/n)?"):
        static()

    # Update the download link.
    try:
        lastversion = git.describe('--tags').stdout.rstrip()
    except ErrorReturnCode_128:
        pass # No tags recorded; leave download link as is
    else:
        date = git.log('-1', lastversion,
                       date='short', format='%ad').stdout[8:18]
        rpls = [('(ModelicaRes)-.+(\.tar)', r'\1-%s\2' % lastversion[1:]),
                ('(Latest version<br>\().+(\)</a>)',
                 r'\1%s, %s\2' % (lastversion, date)),
               ]
        util.replace('_templates/download.html', rpls)

    # Build the documentation.
    make_dirs()
    sphinx = sphinx_build.bake(b='html', d='build/doctrees')
    print(sphinx('.', BUILD_DIR))

    # Spellcheck.
    if util.yes("Do you want to spellcheck the HTML documentation (y/n)?"):
        spellcheck()

def clean():
    """Clean/remove the built documentation.
    """
    shutil.rmtree('build', ignore_errors=True)

def make_dirs():
    """Create the directories required to build the documentation.
    """

    # Create regular directories.
    BUILD_DIRS = ['build/doctrees', 'build/html']
    for d in BUILD_DIRS:
        try:
            os.makedirs(d)
        except OSError:
            pass

    # Create a link to the examples folder.
    if not os.path.isdir('examples'):
        example_dir = '../examples'
        if not os.path.isdir(example_dir):
            raise IOError("Could not find the examples folder.")
        try:
            os.symlink(example_dir, 'examples')
        except AttributeError: # Symlinks aren't available in Windows.
            raise AttributeError('Create a doc/examples shortcut that points '
                                 'to the examples folder in the base '
                                 'directory.')

def release():
    """Release/publish the documentation to the webpage.
    """
    # Save the current state.
    branch = git('rev-parse', '--abbrev-ref', 'HEAD').stdout.rstrip()
    git.stash('save', "Work in progress while updating gh-pages branch")

    # Check out the gh-pages branch.
    try:
        git.checkout('gh-pages')
    except ErrorReturnCode_128: # Create the branch if necessary.
        git.checkout('-b', 'gh-pages')

    # Remove the existing files in the base folder.
    EXTENSIONS = ['*.html', '*.inv']
    fnames = util.multiglob('..', EXTENSIONS)
    for fname in fnames:
        os.remove(fname)

    # Copy the new files to the base folder.
    fnames = util.multiglob(BUILD_DIR, EXTENSIONS)
    for fname in fnames:
        shutil.copy(fname, '..')

    # Track the new files.
    fnames = util.multiglob('..', EXTENSIONS)
    git.add(*fnames)

    # Copy but rename the folders referenced in the HTML files.
    # Github only recognizes images, stylesheets, and javascripts as folders.
    FOLDERS = [('_images', 'images'),
               ('_static', 'javascripts'),
              ]
    for i, (src, dst) in enumerate(FOLDERS):
        dst = os.path.join('..', dst)
        # Remove the existing folder.
        shutil.rmtree(dst, ignore_errors=True)
        # Copy the new folder.
        shutil.copytree(os.path.join(BUILD_DIR, src), dst)
        # Track the new folder.
        git.add(dst)
    # Update the HTML files to reference the new folder names.
    html_fnames = glob(os.path.join('..', '*.html'))
    util.replace(html_fnames, FOLDERS)

    # Copy and rename the examples folder.
    src = os.path.join(BUILD_DIR, 'examples')
    dst = '../examples2'
    # Remove the existing folder.
    shutil.rmtree(dst, ignore_errors=True)
    # Copy the new files.
    os.mkdir(dst)
    for fname in os.listdir(src):
        shutil.copy(os.path.join(src, fname), os.path.join(dst, fname))
    # Track the new folder.
    git.add(dst)
    # Update the HTML files to reference the new folder names.
    util.replace(html_fnames, [('"\./examples/', '"./examples2/')])

    # Update the sitemap.
    print(python('sitemap_gen.py', config="sitemap_conf.xml"))

    # Commit the changes.
    try:
        git.commit('-a', m="Rebuilt documentation")
    except ErrorReturnCode_1:
        pass # No changes to commit

    # If desired, push the changes to origin.
    print("The gh-pages branch has been updated and is currently checked out.")
    if util.yes("Do you want to rebase it and push the changes to "
                "origin (y/n)?"):
        git.rebase('-i', 'origin/gh-pages')
        git.push.origin('gh-pages')

    # Return to the original state.
    git.checkout(branch)
    try:
        git.stash.pop()
    except ErrorReturnCode_1:
        pass # No stash was necessary in the first place.
    print("Now back on " + branch)

def spellcheck():
    """Spellcheck the HTML docs.
    """
    # Options
    WORDFILE = os.path.abspath('.modelicares.pws') # Name of custom word file
    EXTRAFILE = os.path.abspath('.modelica.pws') # Name of extra word file
    HTML_FILES = glob('build/html/*.html') # Names of the HTML files

    print("If there are misspellings, fix them in the Python or ReST "
          "source---not just in the HTML files.")

    # Remove unused words from the custom word file.
    def read(fname):
        with open(fname, 'r') as f:
            return f.read()
    html = "".join(map(read, HTML_FILES))
    with open(WORDFILE, 'r') as f:
        head = f.readline()
        lines = f.readlines()
    with open(WORDFILE, 'w') as f:
        f.write(head)
        for line in lines:
            if html.find(line.rstrip('\n').rstrip('\r')) != -1:
                f.write(line)

    # Check the spelling.
    for page in HTML_FILES:
        if os.system('aspell --dont-backup --personal={1} --extra-dicts={0} '
                     '-c {2}'.format(WORDFILE, EXTRAFILE, page)):
            raise SystemError("aspell (http://aspell.net/) must be installed.")

def static():
    """Create static images for the HTML documentation and the base README.md.
    """

    import numpy as np
    import matplotlib.pyplot as plt

    from modelicares import SimRes, SimResList, LinResList, read_params

    join = os.path.join

    # Options
    indir = "../examples" # Directory with the mat files.
    outdir = "_static" # Directory where the images should be generated
    dpi = 90 # DPI for the HTML index images
    dpi_small = 45 # DPI for the README images
    kwargs = dict(bbox_inches='tight', format='png') # Other savefig() options

    # ThreeTanks
    # ----------
    sim = SimRes(join(indir, 'ThreeTanks.mat'))
    sim.sankey(title="Sankey diagrams of Modelica.Fluid.Examples.Tanks.ThreeTanks",
               times=[0, 50, 100, 150], n_rows=2, format='%.1f ',
               names=['tank1.ports[1].m_flow', 'tank2.ports[1].m_flow',
                      'tank3.ports[1].m_flow'],
               labels=['Tank 1', 'Tank 2', 'Tank 3'],
               orientations=[-1, 0, 1],
               scale=0.1, margin=6, offset=1.5,
               pathlengths=2, trunklength=10)
    plt.savefig(join(outdir, 'ThreeTanks.png'), dpi=dpi, **kwargs)
    plt.savefig(join(outdir, 'ThreeTanks-small.png'), dpi=dpi_small, **kwargs)
    plt.close()

    # ChuaCircuit
    # -----------
    sim = SimRes(join(indir, 'ChuaCircuit.mat'))
    ax, __ = sim.plot(ynames1='L.v', ylabel1="Voltage",
                      xname='L.i', xlabel="Current",
                      title="Modelica.Electrical.Analog.Examples.ChuaCircuit\n"
                            "Current through and voltage across the inductor")
    # Mark the start and stop points.
    def mark(time, text):
        i = sim['L.i'].values(time)
        v = sim['L.v'].values(time)
        plt.plot(i, v, 'bo')
        ax.annotate(text, xy=(i, v), xytext=(0, -4), ha='center', va='top',
                    textcoords='offset points')
    mark(0, "Start")
    mark(2500, "Stop")
    # Save and close.
    plt.savefig(join(outdir, 'ChuaCircuit.png'), dpi=dpi, **kwargs)
    plt.savefig(join(outdir, 'ChuaCircuit-small.png'), dpi=dpi_small, **kwargs)
    plt.close()

    # PIDs-bode
    # ---------
    lins = LinResList(join(indir, 'PID.mat'), join(indir, 'PID/*/'))
    for lin in lins:
        lin.label = "Td = %g s" % read_params('Td', join(lin.dirname,
                                                         'dsin.txt'))
    lins.sort(key=lambda lin: lin.label)
    lins.bode(title="Bode plot of Modelica.Blocks.Continuous.PID\n"
                    "with varying differential time constant")
    plt.savefig(join(outdir, 'PIDs-bode.png'), dpi=dpi, **kwargs)
    plt.close()


F = namedtuple("F", ['f', 'description'])
funcs = {'clean'      : F(clean,   "Clean/remove the built documentation."),
         'build'      : F(build,   "Build/make the HTML documentation."),
         'release'    : F(release,
                          "Release/publish the documentation to the webpage."),
        }

def funcs_str():
    """Return a string listing the valid functions and their descriptions.
    """
    return "\n".join(["  %s: %s" % (arg.ljust(10), function.description)
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
