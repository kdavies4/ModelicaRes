#!/bin/bash
# Run all of the tests on ModelicaRes.

# Get a list of the tests.
module_tests=$(find modelicares -name "*.py" ! -name "_gui.py")
txt_tests=$(find tests -name "*.txt")

# Run the tests.
for f in $module_tests $txt_tests; do
    for python in python python3; do
        echo "Testing $f using $python..."
        $python -m doctest $f
        status=$?
        if [ $status -ne 0 ]; then
            echo $f failed.
            exit $status
        fi
    done
done

echo "All tests passed, but simres.SimRes.browse(), the bin/loadres script, "
echo "and the IPython notebooks (examples/*.ipynb) must be tested manually."
