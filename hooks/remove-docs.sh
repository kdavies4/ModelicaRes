#!/bin/bash
# Remove the generated docs and examples that are tracked only on the release
# branch.
#
# This is necessary before checking out the release branch from the master
# branch.

# ----------
# Necessary:
# ----------

# PNG images in examples folder
for f in `find ./examples -maxdepth 1 -type f \( -name *.png ! -name *-small.png \)`
do
    rm -f $f
done

# Modelica scripts in examples folder
for f in `find ./examples -type f -name *.mos`; do
    rm -f $f
done

# PDF document doc folder
rm -f doc/ModelicaRes.pdf

# HTML files in doc folder
rm -f doc/*.html

# --------------------------
# Not necessary but helpful:
# --------------------------

# PDF images in examples folder
rm -f examples/*.pdf
rm -f examples/*.mpg

# PDF images in doc folder
rm -f doc/_static/*.pdf
