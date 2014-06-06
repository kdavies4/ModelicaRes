This folder contains scripts that help with the development and distribution of
ModelicaRes.

The [pre-commit script](pre-commit) prevents commits if there are errors in the
Python source or there are filenames with non-ASCII characters.  It also adds
an "UNRELEASED COPY" markdown file in the base folder if there is no version
marked in [modelicares/__init__.py](../modelicares/__init__.py).

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
        pylint = !bash `git rev-parse --show-toplevel`/hooks/pylint.sh
	    doc = !bash `git rev-parse --show-toplevel`/hooks/doc.sh
	    code = !bash `git rev-parse --show-toplevel`/hooks/code.sh
	    build = !bash `git rev-parse --show-toplevel`/hooks/build.sh
	    release = !bash `git rev-parse --show-toplevel`/hooks/release.sh

#### Usage

##### For source code:

To clean/remove the built code (alias for `setup.py clean --all`):

    git code clean

To build/make a distributable copy and run tests:

    git code build

To release/upload a version to [PyPI]\:

    git code release

##### For documentation:

To clean/remove the built documentation:

    git doc clean

To build/make the HTML documentation, with an option to rebuild the static
images and spellcheck the pages:

    git doc build

To release/publish the documentation to the [GitHub webpage]\:

    git doc release

##### Integrated:

To run `git code build` and then `git doc build`, use `git build`.
To run `git code release` and `git doc release`, use `git release`.

##### Other:

To compare the [matplotlibrc](../matplotlibrc) file to the user's configuration:

    git diff-matplotlibrc

To run [pylint](http://www.pylint.org/) on all of the source files:

    git pylint

#### Development workflow

All releases and updates are on the `master` branch.  During the build process,
(`git code build`), releases are tagged  as "v*major*.*minor*.*micro*", where
*major*, *minor*, and *micro* are the integer parts of the version number.  The
unreleased updates have an "UNRELEASED COPY.md" file in the base folder with the
commit date/time and the author.

The version number is recorded in
[modelicares/__init__.py](../modelicares/__init__.py).  It is *None* for
unreleased copies.  When the documentation is built (`git doc build`), the
download link and text is updated with information from the last tag, which
corresponds to the last release.


[git]: http://git-scm.com/
[GitHub webpage]: kdavies4.github.io/ModelicaRes/
[PyPI]: https://pypi.python.org/pypi/ModelicaRes
