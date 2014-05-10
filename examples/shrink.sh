#!/bin/bash
# Create small copies of some images.
#
# This requires that ImageMagick (http://www.imagemagick.org) is installed.

convert -resize 40% ChuaCircuits.png ChuaCircuits-small.png
convert -resize 40% ThreeTanks.png ThreeTanks-small.png
