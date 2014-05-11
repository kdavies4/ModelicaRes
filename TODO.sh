#!/bin/bash
# List the TODO tags in the Python files.

grep TODO modelicares/*.py --exclude _freqplot.py -n --colour=always |
  sed -re  's/^([^:]+:[^:]+):(\x1b\[m\x1b\[K)[[:space:]]*(.*)/\1\x01\2\3/' |
    column -s $'\x01' -t
grep TODO bin/* -n --colour=always --with-filename |
  sed -re  's/^([^:]+:[^:]+):(\x1b\[m\x1b\[K)[[:space:]]*(.*)/\1\x01\2\3/' |
    column -s $'\x01' -t
echo
echo See also the issues at https://github.com/kdavies4/ModelicaRes/issues.
