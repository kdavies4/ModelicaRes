#!/bin/bash
# Compare the matplotlibrc file with the one in the home directory.
#
# This requires Meld (http://meldmerge.org/).

meld ~/.config/matplotlib/matplotlibrc examples/matplotlibrc
