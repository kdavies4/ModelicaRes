#!/usr/bin/python
# Top-level test to run all tests on ModelicaRes.

import doctest
import modelicares

# Tests from the tests folder
doctest.testfile('tests/tests.txt')

# Doctests from the modules
doctest.testfile("modelicares/_gui.py") # Isn't imported in modelicares, so test as file
doctest.testmod(modelicares._freqplot)
doctest.testmod(modelicares._io)
doctest.testmod(modelicares._io.dymola)
doctest.testmod(modelicares.exps)
doctest.testmod(modelicares.exps.doe)
doctest.testmod(modelicares.linres)
doctest.testmod(modelicares.simres)
doctest.testmod(modelicares.texunit)
doctest.testmod(modelicares.util)

# TODO: Note that the GUI isn't tested.
# Create a separate set of tests for the GUIs (in loadres, util.save, util.saveall, and SimRes.browse)

print("The bin/loadres script must be tested manually.")
