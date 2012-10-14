#!/bin/bash
# Automatically format the Python files in this directory.
# Kevin Davies, 6/2/12

for file in *.py
do
    ./00-tabnanny.py $f
    ./00-reindent.py $file
done
