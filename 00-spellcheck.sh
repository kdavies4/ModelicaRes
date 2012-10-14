#!/bin/bash
# Run aspell (spell checking) on all the HTML help files.
#
# Kevin L. Davies, 10/6/12

for f in help/*.html
    do
        aspell --extra-dicts=./.modelica.pws --personal=./.fcsys.pws -c $f
    done
