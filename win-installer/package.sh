#!/bin/bash
#
# Package script for Gaphor.
#
# Thanks:
# - Based on https://github.com/quodlibet/quodlibet

set -euo pipefail

BUILD_ROOT="build/gaphor"
VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
MSYS2_ARCH=x86_64
MINGW_ROOT=${BUILD_ROOT}/mingw64
MINGW_BIN=${MINGW_ROOT}/bin

rm -rf ${BUILD_ROOT}
mkdir -p ${BUILD_ROOT}

# python3 -m venv --copies --prompt Gaphor-win "${BUILD_ROOT}"
# source "${BUILD_ROOT}/bin/activate"

function install_dependencies() {
    mkdir -p "${BUILD_ROOT}"/var/lib/pacman
    mkdir -p "${BUILD_ROOT}"/var/log
    mkdir -p "${BUILD_ROOT}"/tmp


    pacman --noconfirm --cachedir "/var/cache/pacman/pkg" --root "${BUILD_ROOT}" -Suy

    pacman --noconfirm -S --needed --cachedir "/var/cache/pacman/pkg" --root "${BUILD_ROOT}" \
        mingw-w64-$MSYS2_ARCH-gtk3 \
        mingw-w64-$MSYS2_ARCH-pkg-config \
        mingw-w64-$MSYS2_ARCH-cairo \
        mingw-w64-$MSYS2_ARCH-gobject-introspection \
        mingw-w64-$MSYS2_ARCH-python3 \
        mingw-w64-$MSYS2_ARCH-python3-gobject \
        mingw-w64-$MSYS2_ARCH-python3-cairo \
        mingw-w64-$MSYS2_ARCH-python3-pip

    pacman --noconfirm -Rdds --cachedir "/var/cache/pacman/pkg" --root "${BUILD_ROOT}" \
        mingw-w64-$MSYS2_ARCH-ncurses \
        mingw-w64-$MSYS2_ARCH-tk \
        mingw-w64-$MSYS2_ARCH-tcl \
        mingw-w64-$MSYS2_ARCH-ca-certificates
}

function install_gaphor() {
    pip3 --disable-pip-version-check install --ignore-installed --prefix ${MINGW_ROOT} ../dist/gaphor-${VERSION}-py3-none-any.whl

    cp ../LICENSE.txt ${MINGW_ROOT}
    cp gaphor.ico ${MINGW_BIN}
    
    python3 create-launcher.py "${VERSION}" "${MINGW_BIN}"
}

function prepackage_cleanup() {
    rm -rf ${MINGW_ROOT}/ssl
    rm -rf ${MINGW_ROOT}/libexec
    rm -rf ${MINGW_ROOT}/lib/*.a
    rm -rf ${MINGW_ROOT}/share/doc
    rm -rf ${MINGW_ROOT}/share/gtk-doc
    rm -rf ${MINGW_ROOT}/share/info
    rm -rf ${MINGW_ROOT}/share/man
}

function build_installer {
    (cd $MINGW_ROOT && makensis -NOCD -DVERSION="$VERSION" ../../../gaphor.nsi)

    mv "${MINGW_ROOT}/gaphor-LATEST.exe" "gaphor-$VERSION-installer.exe"
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

install_dependencies
install_gaphor
build_installer
