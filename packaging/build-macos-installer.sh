#!/usr/bin/env bash

# Copyright 2016 Christoph Reiter, 2019-2020 Dan Yeaw
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"
mkdir -p output

MISC="${DIR}"/misc

VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"

python -m venv pyinstvenv

pyinstvenv/bin/pip install "../dist/gaphor-${VERSION}-py3-none-any.whl"
pyinstvenv/bin/pip install pyinstaller==4.1.0

function set_build_root {
    DIST_LOCATION="$1"
}

set_build_root "${DIR}/dist/gaphor"

function build_pyinstaller {
    echo "${DIR}"
    sed "s/__version__/$VERSION/g" "${DIR}"/file_version_info.txt.in > "${DIR}"/file_version_info.txt
    sed "s/__version__/$VERSION/g" "${DIR}"/gaphor.spec.in > "${DIR}"/gaphor.spec
    python make-script.py ../pyproject.toml > gaphor-script.py
    pyinstvenv/bin/pyinstaller -y gaphor.spec
}

function sign_app {
    echo 'Signing app'
    
}

function build_installer {
    echo 'Building Gaphor-$VERSION.dmg...'
    
    create-dmg \
      --volname "Gaphor $VERSION" \
      --background "background.png" \
      --window-pos 200 120 \
      --window-size 700 400 \
      --icon-size 100 \
      --icon "Gaphor.app" 200 240 \
      --hide-extension "Gaphor.app" \
      --app-drop-link 500 240 \
      "Gaphor-$VERSION.dmg" \
      '"${DIR}"/Gaphor.app'
    
}


function main {
    build_pyinstaller
    sign_app
    build_installer
    echo 'Done!'
}

main "$@";
