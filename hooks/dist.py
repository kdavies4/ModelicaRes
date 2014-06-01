#!/usr/bin/env python
"""
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
bash ../TODO.sh
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


# TODO: take version number as argument
version=x.x.x

# Allow releases only from the release branch.
branch=`git rev-parse --abbrev-ref HEAD` # Current branch
condition="$branch = release"
assert "$condition" $LINENO

# Build the package and update the documentation.
bash make-docs.sh $version

# Make a distributable copy.
python setup.py sdist --formats=gztar,zip

# Use the zip command to change the line endings to Windows format.
name=`python setup.py --fullname`
(cd dist
rm $name.zip
tar -xf $name.tar.gz
zip -rl $name.zip $name
rm -r $name
)

# Rebase the release branch at the current master.
git rebase -i master

# Finish.
cat < post-tag-notes.md


1.  Check if everything is ok.
2.  Upload the release to PyPI (``python setup.py sdist upload``).
3.  Push everything to GitHub
    (``git push --tags origin release; git push origin master``).
"""
