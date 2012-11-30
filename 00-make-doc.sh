#!/bin/bash
# Make the documentation.
#
# First, build and install the package using setup.py on the master or
# development branch:
#    $ ./setup.py build
#    $ sudo ./setup.py install
#
# Afterwards, once ready to update the web site:
#    $ git commit -am "Updated documentation"
#    $ git rebase -i origin/gh-pages # Optional--to remove intermediate commits
#    $ git push origin gh-pages
#
# Kevin Davies, 10/15/12

# Install
./setup.py build
sudo python ./setup.py install

# Run the doc tests and recreate the example images.
cd modelicares
./__init__.py
./base.py
./exps.py
./linres.py
./multi.py
./simres.py
./texunit.py
cd ../examples
./00-crop-png.sh
cd ..

# Make the local documentation.
cd doc
./make.py clean
./make.py html
./make.py latex

# Copy the HTML and PDF documentation to root of the doc folder.
cp -f build/html/* ./
rm -r _images
cp -r build/html/_images ./
cp -r build/html/_sources ./
cp -r build/html/_static ./
cp -f build/latex/ModelicaRes.pdf ./
cd ..

# Make a distributable copy.
#./setup.py sdist --formats=gztar,zip
# Use the zip command to change all line endings to Windows format.
./setup.py sdist
name=`./setup.py --fullname`
cd dist
tar -xf $name.tar.gz
zip -rl $name.zip $name
rm -r $name
cd ..

# Make the web documentation.
branch=`git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3` # Original branch
stash_msg=`git stash save`
git checkout gh-pages
./00-make-gh-pages.sh
git checkout $branch
if [ "$stash_msg" != "No local changes to save" ]; then
   git stash pop
fi
