#!/bin/bash
# Release this package.
#
# Before running this script:
# 1.  Finalize the entries in CHANGES.txt.
# 2.  Update the version number in modelicares/__init__.py and
#     doc/_templates/download.html.
#
# Afterward running this script:
# 1.  See that everything is good.
# 2.  Rebase the gh-pages branch to squash extra commits.  Push it to origin
#     (git push origin gh-pages).
# 3.  If desired, update the sitemap using http://www.xml-sitemaps.com/.  Put
#     it in the base folder of the gh-pages branch and push to origin again
#     (git push origin gh-pages).  Udpate it in Google Webmaster tools
#     (https://www.google.com/webmasters/tools/sitemap-list?hl=en&siteUrl=http%3A%2F%2Fkdavies4.github.com%2FFCSys%2F#MAIN_TAB=1&CARD_TAB=-1).
# 4.  Rebase this development branch to squash extra commits
#     (git rebase -i origin/development).
# 5.  Merge this development branch into master (git checkout master;
#     git merge --squash development).
# 6.  Tag the master branch with the version number (git tag vx.x.x)
# 7.  Upload the release to PyPI (./setup.py sdist upload).
# 8.  Push everything to github (git push --tags origin master;
#     git push origin development).
# 9.  Replace the version number in modelicares/__init__.py with x's as
#     necessary (for the next version).
#
# Kevin Davies, 7/7/13

# Build and install.
./setup.py build
sudo ./setup.py install

# Run the doc tests and recreate the example images.
./test.sh
cd examples
./00-crop-png.sh
cd ..

# Make the local documentation.
cd doc
./make.py html
./make.py latex

# Copy the HTML and PDF documentation to the root of the doc folder.
rm *.html
cp -f build/html/* ./
rm -r _images
cp -r build/html/_images _images
rm -r _sources
cp build/html/_sources ./
git add _images
git add _sources
git add *.html
git add *.inv
git add *.js
cp -f build/latex/ModelicaRes.pdf ./
cd ..

# Make a distributable copy.
./setup.py sdist --formats=gztar,zip
# Use the zip command to change all line endings to Windows format.
name=`./setup.py --fullname`
cd dist
rm $name.zip
tar -xf $name.tar.gz
zip -rl $name.zip $name
rm -r $name
cd ..

# Make the web documentation.
git commit -am "Auto-updated documentation"
branch=`git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3` # Original branch
#stash_msg=`git stash save "Work in progress while running 00-release.sh"`
git checkout gh-pages
./00-make-gh-pages.sh
git checkout $branch
#if [ "$stash_msg" != "No local changes to save" ]; then
#   git stash pop
#fi
