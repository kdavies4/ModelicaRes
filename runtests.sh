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

echo "All tests passed, but simres.SimRes.browse() and the bin/loadres script "
echo "must be tested manually."
