#!/bin/bash
# List the TODO tags in the *.py files.
#
# Kevin Davies, 12/7/2012

grep -c TODO --color *.py
echo
grep TODO --color *.py
echo -n "Press enter to exit."
read answer
