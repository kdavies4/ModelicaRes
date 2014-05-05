#!/bin/bash
# List the TODO tags in the Python files.
#
# Kevin Davies, 12/7/2012

echo modelicares folder:
grep -c TODO --color modelicares/*.py
echo
grep TODO -n --color modelicares/*.py
echo

echo bin folder:
grep -c TODO --color bin/*
echo
grep TODO -n --color bin/*