#!/bin/bash
# Release this package.
#
# Before running this script:
# 1.  Finalize the entries in CHANGES.txt.
# 2.  Update the version number in modelicares/__init__.py,
#     doc/_templates/download.html, and setup.py.
#
# After running this script:
# 1.  See that everything is good.
# 2.  Rebase the gh-pages branch to squash extra commits.  Push it to origin
#     (git push origin gh-pages).
# 3.  If desired, update the sitemap using http://www.xml-sitemaps.com/.  Put
#     it in the base folder of the gh-pages branch and push to origin again
#     (git push origin gh-pages).  Udpate it in Google Webmaster tools
#     (https://www.google.com/webmasters/tools/sitemap-list?hl=en&siteUrl=http%3A%2F%2Fkdavies4.github.com%2FFCSys%2F#MAIN_TAB=1&CARD_TAB=-1).
# 4.  Rebase this develop branch to squash extra commits
#     (git rebase -i origin/develop).
# 5.  Merge this develop branch into master (git checkout master;
#     git merge --squash develop).
# 6.  Tag the master branch with the version number (git tag vx.x.x)
# 7.  Upload the release to PyPI (./setup.py sdist upload).
# 8.  Push everything to github (git push --tags origin master;
#     git push origin develop).
# 9.  Replace the version number in modelicares/__init__.py and setup.py with 
#     x's necessary (for the next version).
#
# Kevin Davies, 7/7/13

# Build and install.
python setup.py build
sudo python setup.py install

# Run the doc tests and recreate the example images.
bash 00-test.sh
cd examples
bash 00-crop-png.sh
cd ..

# Make the local documentation.
cd doc
python make.py html
python make.py latex

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
python setup.py sdist --formats=gztar,zip
# Use the zip command to change all line endings to Windows format.
name=`python setup.py --fullname`
cd dist
rm $name.zip
tar -xf $name.tar.gz
zip -rl $name.zip $name
rm -r $name
cd ..

# Make the web documentation.
git commit -am "Auto-updated documentation"
branch=`git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3` # Original branch
git checkout gh-pages
bash 00-make-gh-pages.sh
git checkout $branch

