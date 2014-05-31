#!/bin/bash
# Run all of the tests on ModelicaRes.

# Get a list of the tests.
if [ "$1" == "--travis" ]; then
    # Currently, Travis CI seems to use an old version of scipy which doesn't
    # properly support Unicode.  So skip the Unicode tests and some others for
    # now:
    module_tests=`find modelicares -name "*.py" ! -name _freqplot.py ! -name simres.py ! -name linres.py ! -name util.py ! -name _gui.py ! -name _res.py ! -name __init__.py ! -name doe.py ! -path _io`
    tests="tests/tests-travis.txt $module_tests"
else
    module_tests=`find modelicares -name "*.py"`
    tests="tests/tests.txt $module_tests"
fi

# Run the tests.
for f in $tests; do
    echo "Testing $f..."
    python -m doctest $f
    status=$?
    if [ $status -ne 0 ]; then
        echo $f failed.
        exit $status
    fi
done

echo "All tests passed, but simres.SimRes.browse(), the bin/loadres script, "
echo "and the IPython notebooks (examples/*.ipynb) must be tested manually."
