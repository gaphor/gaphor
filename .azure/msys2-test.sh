#!/bin/bash

set -e

cd quodlibet
export PYTEST_ADDOPTS="-v --junitxml=junit/test-results.xml"

MSYSTEM= python3 -m pytest