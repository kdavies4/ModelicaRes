#!/bin/bash
# Remove the generated examples.

# ----------
# Necessary:
# ----------

# PNG images in examples folder, except the small versions of some images.
for f in `find ./examples -maxdepth 1 -type f -name *.png ! -name *-small.png`
do
    rm -f $f
done

# CSV files in examples folder, except load-csv.csv
for f in `find ./examples -maxdepth 1 -type f -name *.csv ! -name load-csv.csv`
do
    rm -f $f
done

# Modelica scripts in examples folder
for f in `find ./examples -type f -name *.mos`; do
    rm -f $f
done


# --------------------------
# Not necessary but helpful:
# --------------------------

# PDF images in examples folder
rm -f examples/*.pdf
rm -f examples/*.mpg
