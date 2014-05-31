#!/usr/bin/env python
# Build the html documentation for ModelicaRes.
#
# This file has been copied and modified from matplotlib v1.2.
# Kevin Davies, 9/17/2012

import os
import shutil
import sys

from glob import glob
from collections import namedtuple


def clean():
    """Clean the built documentation.
    """
    shutil.rmtree('build', ignore_errors=True)

def html():
    """Make the HTML documentation.
    """
    _make_dirs()
    options = ''
    if os.system('sphinx-build %s -b html -d build/doctrees . build/html' % options):
        raise SystemExit("The HTML build failed.")
    os.system('python sitemap_gen.py --config="sitemap_conf.xml"')

def publish():
    """Publish the documentation to the GitHub webpage.
    """
    # TODO: finish this; move sitemap notification here.

    #branch = current branch
    os.system('git stash save "Work in progress while updating gh-pages"')
    os.system('git checkout gh-pages')


    # Copy the documentation to the project's root folder.
    for f in glob('*.html') + glob('*.inv'):
        os.remove(f)
    for f in glob('build/html/*.html') + glob('*.inv'):
        os.copy(f, os.path.split(f))
    """"TODO:
    cp -f doc/build/html/*.html ./
    cp -f doc/build/html/*.inv ./
    git add *.inv
    cp -f doc/ModelicaRes.pdf ./
    # The PDF is built on the source branch, not here.

    # Rename the folders.
    # Github only recognizes images, stylesheets, and javascripts as folders.
    # Images
    rm -r images/*
    mv -f doc/_images/* images
    rpl _images images *.html
    git add images
    rm javascripts/*
    cp doc/build/html/_static/* javascripts
    rpl _static javascripts *.html
    git add javascripts
    cp -f doc/build/html/_sources/* ./
    git add *.rst
    rpl -q "+ '_sources/' " "" javascripts/searchtools.js
    git add *.html

    # Finish.
    git commit -am "Updated documentation"


    # If desired, push the changes to origin.
    push = raw_input("The gh-pages branch has been updated and is currently "
                     "checked out.  Do you want to push the changes to origin?")
    if push.lower() in ['y', 'yes']:
       os.system('git push origin gh-pages')
    git checkout branch
    git stash pop
    """
    print("""If Optional: Update the sitemap using http://www.xml-sitemaps.com/.  Put
    it in the base folder of the *gh-pages* branch and push to origin again
    (``git push origin gh-pages``).  Update it in Google Webmaster tools
    (https://www.google.com/webmasters/tools/sitemap-list?hl=en&siteUrl=http%3A%2F%2Fkdavies4.github.com%2FFCSys%2F#MAIN_TAB=1&CARD_TAB=-1).""")

def spellcheck():
    """Spellcheck the HTML docs.
    """
    # Options
    wordfile = '.modelicares.pws' # Name of custom word file
    extrafile = '.modelica.pws' # Name of extra word file
    html_files = glob('build/html/*.html') # Names of the HTML files

    print("If there are misspellings, fix them in the Python or ReST "
          "source---not just in the HTML files.")


    # Remove unused words from the custom word file.
    def read(fname):
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
    wordfile = os.path.abspath('.modelicares.pws')
    extrafile = os.path.abspath('.modelica.pws')
    for page in html_files:
        if os.system('aspell --dont-backup --extra-dicts={extrafile} '
                     '--personal={wordfile} -c {page}'.format(extrafile=extrafile,
                                                              wordfile=wordfile,
                                                              page=page)):
            raise SystemError("aspell (http://aspell.net/) must be installed.")


def static():
    """Create static images for the HTML documentation and the base README.md.
    """

    import numpy as np
    import matplotlib.pyplot as plt

    from os.path import join, dirname
    from modelicares import SimRes, SimResList, LinResList

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
    results = ['examples/PID.mat', 'examples/PID/1/dslin.mat',
               'examples/PID/2/dslin.mat']
    labels = ["Td = 0.1 s", "Td = 1 s", "Td = 10 s"]
    lins = LinResList(*results)
    lins.bode(title="Bode plot of Modelica.Blocks.Continuous.PID\n"
                    "with varying differential time constant",
              labels=labels)
    plt.savefig(join(outdir, 'PIDs-bode.png'), dpi=dpi, **kwargs)
    plt.close()

def _make_dirs():
    build_dirs = ['build', 'build/doctrees', 'build/html', '_static',
                  '_templates']
    for d in build_dirs:
        try:
            os.mkdir(d)
        except OSError:
            pass

    # Create a link to the examples folder.
    if not os.path.isdir('examples'):
        example_dir = '../examples'
        if not os.path.isdir(example_dir):
            raise IOError("Could not find the examples folder.")
        try:
            os.symlink(example_dir, 'examples')
        except AttributeError:
            raise AttributeError('Create a doc/examples shortcut that points '
                                 'to the examples folder in the base '
                                 'directory.')

F = namedtuple("F", ['f', 'description'])
funcs = {'clean'      : F(clean,      "Remove all built documentation."),
         'html'       : F(html,       "Make the HTML documentation."),
         'publish'    : F(publish,    "Publish the built HTML to GitHub."),
         'spellcheck' : F(spellcheck, "Spellcheck the built HTML."),
         'static'     : F(static,     "Create static images for the "
                                      "documentation and the base README.md."),
        }

def _funcs_str():
    """Return a string listing the valid functions and their descriptions.
    """
    return "\n".join(["  %s: %s" % (arg.ljust(10), function.description)
                      for (arg, function) in funcs.items()])


# Main
if len(sys.argv) != 2:
    raise SystemExit("Exactly one argument is required; valid args are\n"
                     + _funcs_str())
arg = sys.argv[1]
try:
    funcs[arg].f()
except KeyError:
    raise SystemExit("Do not know how to handle %s; valid args are\n%s"
                     % (arg, _funcs_str()))
