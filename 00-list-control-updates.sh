#!/bin/bash
# List the updates to the python-control module (tagged with "ModelicaRes").
#
# Kevin Davies, 8/3/12

cd control/src
grep --color ModelicaRes *.py
echo -n "Press enter to exit."
read answer
