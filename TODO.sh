#!/bin/bash
# List the TODO tags in various project files.

locations="bin/* .travis.yml "$(find . \( -name '*.py' -or -name '*.sh' -or -name '*.md' -or -name '*.rst' -or -name '*.txt' -or -name '*.ipynb' \) ! \( -name code.py -or -name TODO.sh -or -name diff-natu.sh -or -path '*dist*' -or -path '*build*' -or -path '*egg*' -or -path '*-checkpoint.ipynb' \))

grep TODO $locations -n --colour=always |
  sed -re  's/^([^:]+:[^:]+):(\x1b\[m\x1b\[K)[[:space:]]*(.*)/\1\x01\2\3/' |
    column -s $'\x01' -t
# The sed part removes the leading whitespace.
echo
echo See also the issues at https://github.com/kdavies4/ModelicaRes/issues.
