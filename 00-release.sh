#!/bin/bash
# Create a release version.
#
# This script is incomplete.
# **Automate all of the items in 00-relase-checklist.txt and the steps to
# update the website in 00-make-doc.sh.
#
# First, run 00-make-doc.sh.
#
# Kevin Davies, 6/17/13

# Unzip the release archive.
#name=`./setup.py --fullname`
#unzip -f dist/$name

# Check out the release branch.
#stash_msg=`git stash save "Work in progress while running 00-release.sh"`
#git checkout release

# Update the files.
#git rm -r ./ # Remove everything,
#git checkout HEAD~1 -- .gitignore # except the gitignore file.
#mv $name/ ./
#rm -r $name
#git add --all
#git commit -am "Auto-updated files for $name"

# Return to the original state.
#git checkout $branch
#if [ "$stash_msg" != "No local changes to save" ]; then
#   git stash pop
#fi
