#!/bin/bash
# Run commands related to the documentation.

(cd doc
 python make.py $1
)
