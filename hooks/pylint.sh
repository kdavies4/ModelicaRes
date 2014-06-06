#!/bin/bash
# Run pylint on the source files.

disable='C0302,C0325,I0011,R0903,R0904,R0912,R0913,R0914,R0915,W0141,W0142'

for f in $(find modelicares -name '*.py'); do
    pylint -r n --msg-template='{line}: [{msg_id}({symbol}), {obj}] {msg}' --disable=$disable -f colorized $f
done
