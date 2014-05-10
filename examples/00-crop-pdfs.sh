#!/bin/bash
# Crop the PDF images in this folder
#
# Kevin Davies, 6/3/2012

for fname in *.pdf
do
    pdfcrop "$fname" "$fname"
done