#!/bin/bash
# Extract a copy of the relevant files of this folder for distribution.  Zip the
# copy.
#
# Kevin Davies, 11/2/11
# See:
# http://www.clientcide.com/best-practices/exporting-files-from-git-similar-to-svn-export/.

# Destination directory
dest_dir=~

# Delete the existing directory and zip file.
# It seems that otherwise rsync adds to the existing directory and zip appends
# to the existing file.
thisfolder=`pwd`
foldername=$(basename $thisfolder)
rm -r $dest_dir/$foldername
rm $dest_dir/$foldername.zip

# Copy this folder with the relevant files.
rsync $thisfolder -rL --delete --include-from $thisfolder/.include --exclude-from $thisfolder/.exclude $dest_dir/

# Make a zipped copy.
cd $dest_dir
zip -r $foldername.zip $foldername
