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
rm dist/Gaphor.app/Contents/MacOS/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache
cp dist/Gaphor.app/Contents/Resources/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache dist/Gaphor.app/Contents/MacOS/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache
rm -rf dist/Gaphor.app/Contents/Resources/lib/gdk-pixbuf-2.0
mv dist/Gaphor.app/Contents/MacOS/lib/gdk-pixbuf-2.0 dist/Gaphor.app/Contents/Resources/lib/gdk-pixbuf-2.0
cd "${DIR}"/dist/Gaphor.app/Contents/MacOS/lib
ln -s ../../Resources/lib/gdk-pixbuf-2.0 gdk-pixbuf-2.0 

# Cleanup
rm -rf pyinstvenv
echo 'Done!'
