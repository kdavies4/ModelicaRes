#!/bin/bash
# List the TODO tags in the Python files.

locations="modelicares/*.py modelicares/*/*.py bin/* CHANGES.txt"

grep TODO $locations -n --colour=always |
  sed -re  's/^([^:]+:[^:]+):(\x1b\[m\x1b\[K)[[:space:]]*(.*)/\1\x01\2\3/' |
    column -s $'\x01' -t
# The sed part removes the leading whitespace.
echo
echo See also the issues at https://github.com/kdavies4/ModelicaRes/issues.
