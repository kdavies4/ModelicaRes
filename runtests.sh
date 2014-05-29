#!/bin/bash
# Run all of the tests on ModelicaRes.

for f in tests/tests.txt `find modelicares -name "*.py"`; do
    python -m doctest $f
    status=$?
    if [ $status -ne 0 ]; then
        echo Failed on $f
        exit $status
    fi
done

echo "All tests passed, but simres.SimRes.browse(), the bin/loadres script, "
echo "and the IPython notebooks (examples/tutorial.ipynb and "
echo "examples/advanced.ipynb) must be tested manually."
