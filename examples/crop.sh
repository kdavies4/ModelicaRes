#!/bin/bash
# Crop the PNG and PDF images in this folder
#
# Warning!  This replaces the orginal images.

# PDF
for fname in *.pdf
do
    pdfcrop "$fname" "$fname"
done

# PNG
# This requires that ImageMagick (http://www.imagemagick.org) is installed.
mogrify -fuzz 2% -trim *.png
mogrify -bordercolor '#FFFFFF' -border '10x10' *.png # Add a small white border.
