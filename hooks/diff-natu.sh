#!/bin/bash
# Compare selected ModelicaRes files to the corresponding ones in natu.
#
# This requires Meld (http://meldmerge.org/).

if [[ $1 == '' ]]; then
    files="
    LICENSE.txt
    MANIFEST.in
    setup.py
    TODO.sh
    .gitignore
    .travis.yml
    doc/changes.rst
    doc/conf.py
    doc/credits.rst
    doc/license.rst
    doc/make.py
    doc/_static/custom.css
    doc/_templates/globaltoc.html
    doc/_templates/links.html
    doc/_templates/search.html
    doc/_templates/searchbox.html
    hooks/code.py
    hooks/code.sh
    hooks/doc.sh
    hooks/post-checkout
    hooks/pre-commit
    hooks/pylint.sh
    hooks/README.md
    .git/hooks/pre-commit
    .git/hooks/post-checkout
    .git/config
    "

    for f in $files; do
        meld ../natu/$f $f
    done
else
    meld ../natu/$1 $1
fi
