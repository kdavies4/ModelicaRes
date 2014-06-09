#!/usr/bin/env python
"""Clean, build, and release the HTML documentation for ModelicaRes.
"""

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915,
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=C0103, E0611, F0401

import os
import shutil
import sys

from sh import git, python, sphinx_build, ErrorReturnCode_1, ErrorReturnCode_128
from glob import glob
from collections import namedtuple
from modelicares import util

BUILD_DIR = 'build/html'

def html():
    """Build/make the HTML documentation.
    """

    # Rebuild the static images.
    if util.yes("Do you want to rebuild the static images (y/n)?"):
        static()

    # Update the download link.
    try:
        commit = git('rev-list', '--tags', '--max-count=1').stdout.rstrip()
        lastversion = git.describe('--tags', commit).stdout.rstrip()
        # This is simpler but doesn't always return the latest tag:
        # lastversion = git.describe('--tag', abbrev=0).stdout.rstrip()
    except ErrorReturnCode_128:
        pass # No tags recorded; leave download link as is
    else:
        date = git.log('-1', lastversion,
                       date='short', format='%ad').stdout[8:18]
        rpls = [(r'(ModelicaRes)-.+(\.tar)', r'\1-%s\2' % lastversion[1:]),
                (r'(Latest version<br>\().+(\)</a>)',
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
    build_dirs = ['build/doctrees', 'build/html']
    for d in build_dirs:
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
    extensions = ['*.html', '*.inv']
    fnames = util.multiglob('..', extensions)
    for fname in fnames:
        os.remove(fname)

    # Copy the new files to the base folder.
    fnames = util.multiglob(BUILD_DIR, extensions)
    for fname in fnames:
        shutil.copy(fname, '..')

    # Track the new files.
    fnames = util.multiglob('..', extensions)
    git.add(*fnames)

    # Copy but rename the folders referenced in the HTML files.
    # Github only recognizes images, stylesheets, and javascripts as folders.
    folders = [('_images', 'images'),
               ('_static', 'javascripts'),
              ]
    for (src, dst) in folders:
        dst = os.path.join('..', dst)
        # Remove the existing folder.
        shutil.rmtree(dst, ignore_errors=True)
        # Copy the new folder.
        shutil.copytree(os.path.join(BUILD_DIR, src), dst)
        # Track the new folder.
        git.add(dst)
    # Update the HTML files to reference the new folder names.
    html_fnames = glob(os.path.join('..', '*.html'))
    util.replace(html_fnames, folders)

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
    util.replace(html_fnames, [(r'"\./examples/', r'"./examples2/')])

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
    wordfile = os.path.abspath('.modelicares.pws') # Name of custom word file
    extrafile = os.path.abspath('.modelica.pws') # Name of extra word file
    html_files = glob('build/html/*.html') # Names of the HTML files

    print("If there are misspellings, fix them in the Python or ReST "
          "source---not just in the HTML files.")

    # Remove unused words from the custom word file.
    def read(fname):
        """Read all text from a file."""
        with open(fname, 'r') as f:
            return f.read()
    html = "".join(map(read, html_files))
    with open(wordfile, 'r') as f:
        head = f.readline()
        lines = f.readlines()
    with open(wordfile, 'w') as f:
        f.write(head)
        for line in lines:
            if html.find(line.rstrip('\n').rstrip('\r')) != -1:
                f.write(line)

    # Check the spelling.
    for page in html_files:
        if os.system('aspell --dont-backup --personal={1} --extra-dicts={0} '
                     '-c {2}'.format(wordfile, extrafile, page)):
            raise SystemError("aspell (http://aspell.net/) must be installed.")

def static():
    """Create static images for the HTML documentation and the base README.md.
    """
    import matplotlib.pyplot as plt
    from modelicares import SimRes, LinResList, read_params

    join = os.path.join

    # Options
    indir = "../examples" # Directory with the mat files.
    outdir = "_static" # Directory where the images should be generated
    dpi = 90 # DPI for the HTML index images
    dpi_small = 30 # DPI for the README images
    kwargs = dict(bbox_inches='tight', format='png') # Other savefig() options

    # ThreeTanks
    # ----------
    sim = SimRes(join(indir, 'ThreeTanks.mat'))
    sim.sankey(title=("Sankey diagrams of "
                      "Modelica.Fluid.Examples.Tanks.ThreeTanks"),
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
    ax = sim.plot(ynames1='L.v', ylabel1="Voltage",
                  xname='L.i', xlabel="Current",
                  title=("Modelica.Electrical.Analog.Examples.ChuaCircuit\n"
                         "Current through and voltage across the inductor"))[0]
    # Mark the start and stop points.
    def mark(time, text):
        """Mark a frequency point.
        """
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
    lins.bode(title=("Bode plot of Modelica.Blocks.Continuous.PID\n"
                     "with varying differential time constant"))
    plt.savefig(join(outdir, 'PIDs-bode.png'), dpi=dpi, **kwargs)
    plt.savefig(join(outdir, 'PIDs-bode-small.png'), dpi=dpi_small, **kwargs)
    plt.close()


Action = namedtuple("Action", ['f', 'description'])
ACTIONS = {'clean'   : Action(clean, "Clean/remove the built documentation."),
           'build'   : Action(html, "Build/make the HTML documentation."),
           'html'    : Action(html, "Build/make the HTML documentation."),
           'release' : Action(release, ("Release/publish the documentation to "
                                        "the webpage.")),
          }

def funcs_str():
    """Return a string listing the valid functions and their descriptions.
    """
    return "\n".join(["  %s: %s" % (action.ljust(10), function.description)
                      for (action, function) in ACTIONS.items()])


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
