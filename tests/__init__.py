#!/usr/bin/python
"""Top-level test suite for ModelicaRes
"""

import unittest
import doctest
import modelicares as thismodule

from glob import glob
from modelicares import util
from os import path

this_dir = path.dirname(path.realpath(__file__))
doctest_files = [path.basename(fname)
                 for fname in glob(path.join(this_dir, '*.txt'))]
package_names = util.list_packages(thismodule)
package_names.remove('modelicares._gui')

# TODO: Add tests here; consider moving tests from tests.txt.
class MyTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(5, 5)

def test_suite():
    print("Note: simres.SimRes.browse(), the bin/loadres script, and the "
          "IPython notebooks (examples/*.ipynb) must be tested manually.")
    suite = unittest.TestSuite()
    suite.addTests([unittest.makeSuite(MyTest)])
    suite.addTests([doctest.DocFileSuite(fname) for fname in doctest_files])
    suite.addTests([doctest.DocTestSuite(package) for package in package_names])
    return suite

if __name__ == '__main__':
    """Run the tests here.
    """
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
