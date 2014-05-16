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
	clean-examples = !bash `git rev-parse --show-toplevel`/hooks/clean-examples.sh
	clean-docs = !bash `git rev-parse --show-toplevel`/hooks/clean-docs.sh
	diff-matplotlibrc = !bash `git rev-parse --show-toplevel`/hooks/diff-matplotlibrc.sh
	make-docs = !bash `git rev-parse --show-toplevel`/hooks/make-docs.sh
	release = !bash `git rev-parse --show-toplevel`/hooks/release.sh
	spellcheck = !bash `git rev-parse --show-toplevel`/hooks/spellcheck.sh
