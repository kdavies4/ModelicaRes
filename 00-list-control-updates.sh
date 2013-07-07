#!/bin/bash
# List the updates to the python-control module (tagged with "ModelicaRes").
#
# Kevin Davies, 8/3/12

cd external/control
grep --color ModelicaRes *.py
cd src
grep --color ModelicaRes *.py
echo
read -p "Press [Enter] to exit."
