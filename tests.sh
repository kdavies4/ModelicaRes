#!/bin/bash
# Run the doctests on modelicares.
#
# Kevin Davies, 7/10/13


# TODO: Add test for bin/loadres.  If not, place warning here.

# Run the doc tests and recreate the example images.
#(
#    cd bin
#    ln -s ../examples examples
#    python loadres --test
#    rm examples
#)
python modelicares/__init__.py
