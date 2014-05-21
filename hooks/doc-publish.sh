#!/bin/bash
# Publish the documentation to the web page.

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

# Finish.
git commit -am "Updated documentation"


# If desired, push the changes to origin.
push = raw_input("The gh-pages branch has been updated and is currently "
                "checked out.  Do you want to push the changes to origin?")
if push.lower() in ['y', 'yes']:
   os.system('git push origin gh-pages')
