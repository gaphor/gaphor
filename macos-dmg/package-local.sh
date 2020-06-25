#!/bin/bash
#
# This wrapper for the package script contains some
# env vars, so it can build Gaphor with Python 3.8.
#
# It is intended to run from a local Mac, not CI.
#
export PATH="/usr/local/opt/python@3.8/bin:$PATH"
export LDFLAGS="-L/usr/local/opt/python@3.8/lib"
export PKG_CONFIG_PATH="/usr/local/opt/python@3.8/lib/pkgconfig"

./package.sh
