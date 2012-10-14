Python Utilities for FCSys
==========================

This is the top-level build directory for documenting the Python utilities of
FCSys.  All of the documentation is written using Sphinx, a Python documentation
system built on top of ReST.  This file has been copied and adapted from
matplotlib v1.2 (http://matplotlib.org/), which is licensed as open source
(http://matplotlib.org/users/license.html).  This directory contains:

* make.py - The build script to build the html or latex/PDF docs

* index.rst - The top-level include document for FCSys Utilities

* other .rst files - Placeholders to automatically generate the documentation

* conf.py - The Sphinx configuration

* _static - Used by the Sphinx build system

* _templates - Used by the Sphinx build system

To build the HTML documentation, install Sphinx (1.0 or greater required), then
type "python make.py html" in this directory.  The top file of the results will
be ./build/html/index.html.
