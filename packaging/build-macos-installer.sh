#!/usr/bin/env bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"
mkdir -p output

VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
YEAR="$(python -c "from datetime import date;print(date.today().year)")"

# Create virtualenv for packaging
python -m venv pyinstvenv

# Install Gaphor wheel and PyInstaller
pyinstvenv/bin/pip install "../dist/gaphor-${VERSION}-py3-none-any.whl"
pyinstvenv/bin/pip install pyinstaller==4.1.0

# Apply version and year to config files
sed "s/__version__/$VERSION/g" "${DIR}"/file_version_info.txt.in > "${DIR}"/file_version_info.txt
sed "s/__version__/$VERSION/g;s/__year__/$YEAR/g" "${DIR}"/gaphor.spec.in > "${DIR}"/gaphor.spec

# Create PyInstaller script
python make-script.py ../pyproject.toml > gaphor-script.py

# Run PyInstaller
pyinstvenv/bin/pyinstaller -y gaphor.spec

# App code signing is not supported with a period in the MacOS lib path
# Move gdk-pixbuf-2.0 to Resources and link it back to MacOS
MACOS_DIR="dist/Gaphor.app/Contents/MacOS/lib/gdk-pixbuf-2.0/2.10.0"
RESOURCES_DIR="dist/Gaphor.app/Contents/Resources/lib/gdk-pixbuf-2.0/2.10.0"
mkdir "${RESOURCES_DIR}"/loaders
cp "${MACOS_DIR}"/loaders/* "${RESOURCES_DIR}"/loaders/ 
rm "${MACOS_DIR}"/loaders.cache
rm -f "${MACOS_DIR}"/loaders/*
ln -s ../../../../Resources/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache "${MACOS_DIR}"/loaders.cache
cd "${RESOURCES_DIR}"
find loaders -type f -exec ln -s ../../../../../Resources/lib/gdk-pixbuf-2.0/2.10.0/{} "${DIR}"/"${MACOS_DIR}"/{}  \;

# Cleanup
rm -rf pyinstvenv
echo 'Done!'
