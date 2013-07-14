#!/bin/bash
# Run the doctests on modelicares.
#
# Kevin Davies, 7/10/13

# Run the doc tests and recreate the example images.
./modelicares/__init__.py
./modelicares/base.py
./modelicares/exps/__init__.py
python -m modelicares.exps.doe
./modelicares/linres.py
./modelicares/multi.py
./modelicares/simres.py
./modelicares/texunit.py
