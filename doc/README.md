Documentation for ModelicaRes
-----------------------------

This is the top-level build directory for documenting ModelicaRes.  All of the
documentation is written using [Sphinx], a [Python] documentation system using
[reST].  This directory contains:
 - [make.py](make.py) - The script to build the html or latex/PDF docs
 - [index.rst](index.rst) - The top-level include document for ModelicaRes
 - other .rst files - Placeholders to automatically generate the documentation
 - [conf.py](conf.py) - The [Sphinx] configuration
 - [_static](_static) - Folder of static files used by the [Sphinx] build system
 - [_templates](_templates) - Folder of HTML templates used by the [Sphinx]
   build system

To build the HTML documentation, first create the example images by running
test.py from the base project directory:

    python test.py

Then install [Sphinx] and run the following command in this directory:

    python make.py html

The top file of the results will be build/html/index.html.


[Sphinx]: http://sphinx-doc.org/
[Python]: http://www.python.org
[reST]: http://docutils.sourceforge.net/rst.html
