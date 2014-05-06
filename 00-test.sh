#!/bin/bash
# Run the doctests on modelicares.
#
# Kevin Davies, 7/10/13

# Run the doc tests and recreate the example images.
(
    cd bin
    ln -s ../examples examples
    python loadres --test
    rm examples
)
for f in modelicares/*.py; do
    python $f
done
python -m modelicares.exps.doe
