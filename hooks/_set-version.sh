#!/bin/bash
# Set

# TODO: take argument, default to last tag (without v)

version=0.11.0

rpl {version} $version modelicares/__init__.py
rpl {version} $version doc/_templates/download.html
rpl {version} $version setup.py
rpl {version} $version CHANGES.txt
