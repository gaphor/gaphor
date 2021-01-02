#!/usr/bin/env bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"
mkdir -p output

# Run PyInstaller
pyinstvenv/bin/pyinstaller -y gaphor.spec
