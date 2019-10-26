#!/bin/bash

set -e

export PYTEST_ADDOPTS="-v --junitxml=junit/test-results.xml"

# Pytest is currently failing in MSYS2
# python3 -m pytest