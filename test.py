#!/usr/bin/python
# Top-level test to run all tests on ModelicaRes.

import doctest
import modelicares

# Tests from the tests folder
doctest.testfile('tests/tests.txt')

# Doctests from the modules
#TODO enable doctest.testmod(modelicares._freqplot)
#TODO enable doctest.testmod(modelicares._gui)
doctest.testmod(modelicares._io)
doctest.testmod(modelicares._io.dymola)
doctest.testmod(modelicares.exps)
doctest.testmod(modelicares.exps.doe)
doctest.testmod(modelicares.linres)
doctest.testmod(modelicares.simres)
doctest.testmod(modelicares.texunit)
#TODO enable doctest.testmod(modelicares.util)

print("The bin/loadres script must be tested manually.")
