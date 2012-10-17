#!/bin/bash
# List the updates to the python-control module (tagged with "FCSys").
#
# Kevin Davies, 8/3/12

cd control-0.5b/src
grep --color FCSys *.py
echo -n "Press enter to exit."
read answer
