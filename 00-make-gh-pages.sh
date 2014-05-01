#!/bin/bash
# Make the web pages for github.
#
# First, build and install the package using setup.py on the master or
# development branch:
#    $ ./setup.py build
#    $ sudo ./setup.py install
#
# Afterwards, once ready to update the web site:
#    $ git commit -am "Updated documentation"
#    $ git rebase -i origin/gh-pages # Optional, to remove intermediate commits
#    $ git push origin gh-pages
#
# Kevin Davies, 10/15/12

# Source for some of the files
branch=develop
files="doc/_static/*
       doc/_templates/*
       doc/_images/*
       doc/make.py
       doc/base.rst
       doc/exps.doe.rst
       doc/exps.rst
       doc/linres.rst
       doc/Changelog.rst
       doc/License.rst
       CHANGES.txt
       LICENSE.txt
       doc/loadres.rst
       doc/modelicares.rst
       doc/multi.rst
       doc/simres.rst
       doc/texunit.rst" # index.rst isn't included because it's custom here.

# Get the essential files from the source branch.
for f in $files
do
    git checkout $branch $f
done

# Make the HTML documentation.
python doc/make.py html

# Copy the documentation to the project's root folder.
rm *.html
cp -f doc/build/html/*.html ./
rm doc/*.inv
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

# Don't retain the source files here.
for f in $files
do
    rm -r $f
done

# Finish.
git commit -am "Auto-updated documentation"
#git push origin gh-pages
