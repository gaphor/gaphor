#!/bin/bash

set -e

export PYTEST_ADDOPTS="--doctest-modules --junitxml=junit/test-results.xml"
export PY_IGNORE_IMPORTMISMATCH=1

poetry run pytest --collect-only -vvv
poetry run pytest -vvv