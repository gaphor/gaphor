#!/bin/bash

echo "::set-output name=version::$(poetry version --no-ansi | cut -d' ' -f2)"
