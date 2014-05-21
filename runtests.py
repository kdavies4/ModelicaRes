#!/usr/bin/python
# Top-level test to run all of the main tests on ModelicaRes.
#
# To raise an error if a test fails, run this with option '--raise'.  Otherwise,
# the results are just printed.

import sys
import doctest
import modelicares

raise_on_error = len(sys.argv) > 1 and sys.argv[1] == '--raise'
testfile = lambda fname: doctest.testfile(fname, raise_on_error=raise_on_error)
testmod = lambda mod: doctest.testmod(mod, raise_on_error=raise_on_error)

# Tests from the tests folder
testfile('tests/tests.txt')

# Doctests from the modules
testfile("modelicares/_gui.py") # Test as file; isn't imported in modelicares
testmod(modelicares._freqplot)
testmod(modelicares._io)
testmod(modelicares._io.dymola)
testmod(modelicares.exps)
testmod(modelicares.exps.doe)
testmod(modelicares.linres)
testmod(modelicares.simres)
testmod(modelicares.texunit)
testmod(modelicares.util)

# TODO: Include test of the GUIs, but add an option to bypass it for Travis CI.
print("The bin/loadres script and the GUI-based functions and methods "
      "util.save, util.saveall, and simres.SimRes.browse must be tested "
      "manually.")
