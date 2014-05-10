#!/bin/bash

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
