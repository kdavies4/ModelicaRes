#!/bin/bash
# Build the package and update the documentation.

#######################################################################
assert ()                 #  If condition false,
{                         #+ exit from script
                          #+ with appropriate error message.
  E_PARAM_ERR=98
  E_ASSERT_FAILED=99


  if [ -z "$2" ]          #  Not enough parameters passed
  then                    #+ to assert() function.
    return $E_PARAM_ERR   #  No damage done.
  fi

  lineno=$2

  if [ ! $1 ]
  then
    echo "Assertion failed:  \"$1\""
    echo "File \"$0\", line $lineno"    # Give name of file and line number.
    echo "Check out the release branch before releasing."
    exit $E_ASSERT_FAILED
  # else
  #   return
  #   and continue executing the script.
  fi
} # Insert a similar assert() function into a script you need to debug.
#######################################################################

# Confirm continue
echo
cat < pre-tag-notes.md
echo
echo "Here's a list of the TODO items:"
bash ../TODO-list.sh
echo
read -r -p 'Do you want to continue by building the documentation (y/n)? ' choice
if [[ "$choice" != "Y" && "$choice" != "y" ]]; then
    echo aborting...
    exit
fi

# Build and install the package.
python setup.py build
sudo python setup.py install

# Run the doc tests and recreate the example images.
bash test.sh
bash examples/crop.sh
bash examples/shrink.sh


# Local documentation ----------------------------------------------------------
(cd doc

# Update the local docs.
python make.py clean
python make.py html
python make.py latex

# Copy the built docs to the root of the doc folder.
# HTML
rm *.html
cp -f build/html/* ./
git add *.html
# Images
rm -r _images
cp -r build/html/_images .
git add _images
# Source files
rm -r _sources
cp -r build/html/_sources .
git add _sources
# Files for search function
cp -f build/html/objects.inv ./
cp -f build/html/searchindex.js ./
git add objects.inv # Just to be sure.
git searchindex.js # Just to be sure.
# PDF
cp -f build/latex/ModelicaRes.pdf ./
git ModelicaRes.pdf # Just to be sure.

# Spell check the HTML docs.
echo Now running spell check on the HTML docs...
for f in doc/*.html; do
    aspell --extra-dicts=../.modelica.pws --personal=../.modelicares.pws -c $f
done

git commit -am "Updated documentation"
)

# Online documentation ---------------------------------------------------------
git checkout gh-pages
bash doc/make.sh
git checkout $branch


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
git commit -am "Updated documentation"
