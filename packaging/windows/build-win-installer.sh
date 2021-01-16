#!/usr/bin/env bash

set -euo pipefail

# DIR is the parent directory
DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")"
cd "${DIR}"
mkdir -p dist

DIST_LOCATION="${DIR}/dist/gaphor"
VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
MINGW="mingw64"

function build_installer {
    cp "${DIR}"/windows/gaphor.ico "${DIST_LOCATION}"
    (cd "${DIST_LOCATION}" && makensis -NOCD -DVERSION="$VERSION" "${DIR}"/windows/win_installer.nsi)

    mv "${DIST_LOCATION}/gaphor-LATEST.exe" "$DIR/dist/gaphor-$VERSION-installer.exe"
}

function build_portable_installer {
    local PORTABLE="$DIR/dist/gaphor-$VERSION-portable"

    rm -rf "$PORTABLE"
    mkdir "$PORTABLE"
    cp "${DIR}"/windows/gaphor.lnk "$PORTABLE"
    cp "${DIR}"/windows/README-PORTABLE.txt "$PORTABLE"/README.txt
    unix2dos "$PORTABLE"/README.txt
    mkdir "$PORTABLE"/config
    cp -RT "${DIST_LOCATION}" "$PORTABLE"/data

    rm -Rf 7zout 7z1900-x64.exe
    7z a payload.7z "$PORTABLE"
    wget.exe -P "$DIR" -c https://www.7-zip.org/a/7z1900-x64.exe
    7z x -o7zout 7z1900-x64.exe
    cat 7zout/7z.sfx payload.7z > "$PORTABLE".exe
    rm -Rf 7zout 7z1900-x64.exe payload.7z "$PORTABLE"
}

function main {
    # started from the wrong env -> switch
    if [ "$(echo "$MSYSTEM" | tr '[:upper:]' '[:lower:]')" != "$MINGW" ]; then
        "/${MINGW}.exe" "$0"
        exit $?
    fi

    echo "build installer"
    build_installer
    echo "build portable installer"
    build_portable_installer
}

main "$@";
