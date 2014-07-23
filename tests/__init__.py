#!/usr/bin/python
"""Top-level test suite for ModelicaRes
"""

# pylint: disable=I0011, C0111, R0904, W0621

import unittest
import doctest
import modelicares as thismodule

from glob import glob
from natu.util import list_packages
from os import path

THIS_DIR = path.dirname(path.realpath(__file__))
DOCTEST_FILES = [path.basename(fname)
                 for fname in glob(path.join(THIS_DIR, '*.txt'))]
PACKAGE_NAMES = list_packages(thismodule)
PACKAGE_NAMES.remove('modelicares._gui')

# TODO: Add tests here; consider moving tests from tests.txt.


class Tests(unittest.TestCase):

    """Main set of unit tests
    """

    def test_equal(self):
        self.assertEqual(5, 5)


def test_suite():
    """Return a suite of all the tests.
    """
    print("Note: simres.SimRes.browse(), the bin/loadres script, and the "
          "IPython notebooks (examples/*.ipynb) must be tested manually.")
    suite = unittest.TestSuite()
    suite.addTests([unittest.makeSuite(Tests)])
    suite.addTests([doctest.DocFileSuite(fname) for fname in DOCTEST_FILES])
    suite.addTests([doctest.DocTestSuite(package)
                    for package in PACKAGE_NAMES])
    return suite

if __name__ == '__main__':
    # Run the tests here.

    RUNNER = unittest.TextTestRunner()
    RUNNER.run(test_suite())
