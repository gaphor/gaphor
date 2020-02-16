#!/usr/bin/env bash

# Copyright 2016 Christoph Reiter, 2019-2020 Dan Yeaw
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

set -euo pipefail

# CONFIG START

ARCH="x86_64"
BUILD_VERSION="0"

# CONFIG END

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"

MISC="${DIR}"/misc
if [ "${ARCH}" = "x86_64" ]; then
    MINGW="mingw64"
else
    MINGW="mingw32"
fi

VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"

function set_build_root {
    DIST_LOCATION="$1"
    GAPHOR_LOCATION="${DIST_LOCATION}"/gaphor
}

set_build_root "${DIR}/dist/gaphor"


function install_build_deps {
    pacman -S --needed --noconfirm p7zip git dos2unix upx \
        mingw-w64-"${ARCH}"-nsis \
	    mingw-w64-"${ARCH}"-wget

    pip install pyinstaller==3.6
}

function build_pyinstaller {
    sed "s/__version__/$VERSION/g" file_version_info.txt.in > file_version_info.txt
    pyinstaller -y gaphor.spec
}

function build_installer {
    cp "${DIR}"/misc/gaphor.ico "${DIST_LOCATION}"
    (cd "${DIST_LOCATION}" && makensis -NOCD -DVERSION="$VERSION" "${MISC}"/win_installer.nsi)

    mv "${DIST_LOCATION}/gaphor-LATEST.exe" "$DIR/gaphor-$VERSION-installer.exe"
}

function build_portable_installer {
    local PORTABLE="$DIR/gaphor-$VERSION-portable"

    rm -rf "$PORTABLE"
    mkdir "$PORTABLE"
    cp "$MISC"/gaphor.lnk "$PORTABLE"
    cp "$MISC"/README-PORTABLE.txt "$PORTABLE"/README.txt
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
    local GIT_TAG=${1:-"master"}

    # started from the wrong env -> switch
    if [ $(echo "$MSYSTEM" | tr '[A-Z]' '[a-z]') != "$MINGW" ]; then
        "/${MINGW}.exe" "$0"
        exit $?
    fi

    echo "install build dependencies"
    install_build_deps
    echo "pyinstall gaphor"
    build_pyinstaller
    echo "build installer"
    build_installer
    echo "build portable installer"
    build_portable_installer
}

main "$@";
