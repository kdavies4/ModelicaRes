Documentation for ModelicaRes
-----------------------------

This is the top-level build directory for documenting ModelicaRes.  All of the
documentation is written using [Sphinx], a Python documentation system built on
top of [reST].  This directory contains:
 - [make.py](make.py) - The build script to build the html or latex/PDF docs
 - [index.rst](index.rst) - The top-level include document for ModelicaRes
 - other .rst files - Placeholders to automatically generate the documentation
 - [conf.py](conf.py) - The [Sphinx] configuration
 - [_static](_static) - Used by the [Sphinx] build system
 - [_templates](_templates) - Used by the [Sphinx] build system

To build the HTML documentation, install [Sphinx] (1.0 or greater required),
type "python make.py html" in this directory.  The top file of the results will
be build/html/index.html.

This file has been copied and adapted from
[matplotlib v1.2](http://matplotlib.org/), which is licensed as open source
(http://matplotlib.org/users/license.html).

[Sphinx]: http://sphinx-doc.org/
[reST]: http://docutils.sourceforge.net/rst.html
