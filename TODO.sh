#!/bin/bash
# List the TODO tags in various project files.

locations="bin/* .travis.yml `find . -name '*.py' ! -path '*build*' ! -path '*dist*' -or -name '*.sh' ! -name TODO.sh ! -iname 'code.py' -or -name '*.md' -or -name '*.txt' ! -path '*ModelicaRes.egg-info*'`"

grep TODO $locations -n --colour=always |
  sed -re  's/^([^:]+:[^:]+):(\x1b\[m\x1b\[K)[[:space:]]*(.*)/\1\x01\2\3/' |
    column -s $'\x01' -t
# The sed part removes the leading whitespace.
echo
echo See also the issues at https://github.com/kdavies4/ModelicaRes/issues.
