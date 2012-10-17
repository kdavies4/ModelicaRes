#!/bin/bash
# Run aspell (spell checking) on all the HTML help files.
#
# Kevin Davies, 10/6/12

for f in help/*.html
    do
        aspell --extra-dicts=./.modelica.pws --personal=./.modelicares.pws -c $f
    done
