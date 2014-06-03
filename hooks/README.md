This folder contains scripts that help with the development and distribution of
ModelicaRes.

The [pre-commit script](pre-commit) prevents commits if there are errors in the
Python source or there are filenames with non-ASCII characters.

The [post-checkout script](post-checkout) removes byte-compiled Python files
(*.pyc) when switching branches.  Since the source may change when upon
checkout, the *.pyc files should be recompiled to prevent confusion.

Other scripts ([code.sh](code.sh), [doc.sh](doc.sh), and
[diff-matplotlibrc.sh](diff-matplotlibrc.sh)) are linked to [git] via aliases.

#### Installation

Copy [pre-commit](pre-commit) and [post-checkout](post-checkout) to
*.git/hooks/*.

Add to *.git/config*:

    [alias]
	    diff-matplotlibrc = !bash `git rev-parse --show-toplevel`/hooks/diff-matplotlibrc.sh
	    doc = !bash `git rev-parse --show-toplevel`/hooks/doc.sh
	    code = !bash `git rev-parse --show-toplevel`/hooks/code.sh

#### Usage

##### For documentation:

To clean/remove the documentation:

    git doc clean

To build/make the HTML documentation, with an option to rebuild the static
images and spellcheck the pages:

    git doc build

To release/publish the documentation to the [GitHub webpage]\:

    git doc release

##### For source code:

To clean/remove the built code (alias to `setup.py clean --all`):

    git code clean

To build/make a distributable copy:

    git code build

To release/upload a version to [PyPI]\:

    git code release

##### Other:

To compare the [matplotlibrc](../matplotlibrc) file to the user's configuration:

    git diff-matplotlibrc


[git]: http://git-scm.com/
[GitHub webpage]: kdavies4.github.io/ModelicaRes/
[PyPI]: https://pypi.python.org/pypi/ModelicaRes
