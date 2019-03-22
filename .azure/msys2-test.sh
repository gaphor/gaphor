#!/bin/bash

set -e

export PYTEST_ADDOPTS="-v --junitxml=junit/test-results.xml"

python3 -m pytest