TODO update this:

These files can be copied or linked to .git/hooks to do some checks while
using git for version control.

To release the project, initiate a commit on the release branch.  The
*pre-commit* script will update the documentation, preform some checks, and
prepare the package for upload to PyPI.

The *pre-commit* script will also prevent commits while there are errors in the
Python code, regardless of the branch.

**Installation:**

Copy *pre-commit* and *post-checkout* to *.git/hooks/*.

Add to *.git/config*:

    [alias]
	    diff-matplotlibrc = !bash `git rev-parse --show-toplevel`/hooks/diff-matplotlibrc.sh
	    dist = !bash `git rev-parse --show-toplevel`/hooks/dist.sh
	    doc = !bash `git rev-parse --show-toplevel`/hooks/doc.sh
