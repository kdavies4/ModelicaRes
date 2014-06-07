#!/bin/bash
# Run pylint on the source files.
#
# The standard/project-wide pylint disable settings are not included here but
# rather in each file so that https://landscape.io respects them.

for f in $(find modelicares -name '*.py'); do
    pylint -r n --msg-template='{line}: [{msg_id}({symbol}), {obj}] {msg}' -f colorized $f
done
