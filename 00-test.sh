#!/bin/bash
# Run the doctests on modelicares.
#
# Kevin Davies, 7/10/13

# Run the doc tests and recreate the example images.
python modelicares/__init__.py
python modelicares/base.py
python modelicares/exps/__init__.py
python -m modelicares.exps.doe
python modelicares/linres.py
python modelicares/multi.py
python modelicares/simres.py
python modelicares/texunit.py
