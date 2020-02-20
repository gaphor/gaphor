#!/bin/bash
#
# Package script for Gaphor.
#
# Thanks:
# - Based on https://github.com/quodlibet/quodlibet

set -xeuo pipefail

BUILD_ROOT="build"
VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
MSYS2_ARCH=x86_64
MINGW_ROOT=${BUILD_ROOT}/mingw64
MINGW_BIN=${MINGW_ROOT}/bin

function clean_all() {
    rm -rf ${BUILD_ROOT}
    mkdir -p ${BUILD_ROOT}
    rm -f gaphor-*-installer.exe gaphor-*-portable.exe
}

function install_dependencies() {
    mkdir -p "${BUILD_ROOT}"/var/lib/pacman
    mkdir -p "${BUILD_ROOT}"/var/log
    mkdir -p "${BUILD_ROOT}"/tmp


    pacman --noconfirm --cachedir "/var/cache/pacman/pkg" --root "${BUILD_ROOT}" -Suy

    pacman --noconfirm -S --needed --cachedir "/var/cache/pacman/pkg" --root "${BUILD_ROOT}" \
        mingw-w64-$MSYS2_ARCH-gtk3 \
        mingw-w64-$MSYS2_ARCH-cairo \
        mingw-w64-$MSYS2_ARCH-gobject-introspection \
        mingw-w64-$MSYS2_ARCH-python3 \
        mingw-w64-$MSYS2_ARCH-python3-gobject \
        mingw-w64-$MSYS2_ARCH-python3-cairo

    # Run again, since install script will not always work
    (cd ${MINGW_BIN} && ./gdk-pixbuf-query-loaders --update-cache && glib-compile-schemas ../share/glib-2.0/schemas)

    pacman --noconfirm -Rdds --cachedir "/var/cache/pacman/pkg" --root "${BUILD_ROOT}" \
        mingw-w64-$MSYS2_ARCH-ncurses \
        mingw-w64-$MSYS2_ARCH-tk \
        mingw-w64-$MSYS2_ARCH-tcl \
        mingw-w64-$MSYS2_ARCH-ca-certificates \
        mingw-w64-$MSYS2_ARCH-sqlite3 \
        mingw-w64-$MSYS2_ARCH-libtasn1 \
        mingw-w64-$MSYS2_ARCH-pygobject-devel-3.34.0-3 \
        mingw-w64-$MSYS2_ARCH-sqlite3 \
        mingw-w64-$MSYS2_ARCH-python-mako \
        mingw-w64-$MSYS2_ARCH-python-colorama || true

}

function install_gaphor() {
    pip3 --disable-pip-version-check install --ignore-installed --prefix ${MINGW_ROOT} ../dist/gaphor-${VERSION}-py3-none-any.whl

    cp ../LICENSE.txt ${MINGW_ROOT}
    cp gaphor.ico ${MINGW_BIN}
    
    python3 create-launcher.py "${VERSION}" "${MINGW_BIN}"
}

function prepackage_cleanup() {
    rm -rf ${MINGW_ROOT}/ssl
    rm -rf ${MINGW_ROOT}/include
    rm -rf ${MINGW_ROOT}/lib/cmake
    rm -rf ${MINGW_ROOT}/libexec
    rm -rf ${MINGW_ROOT}/share/doc
    rm -rf ${MINGW_ROOT}/share/gtk-doc
    rm -rf ${MINGW_ROOT}/share/info
    rm -rf ${MINGW_ROOT}/share/man
    rm -rf ${MINGW_ROOT}/share/installed-tests
    rm -rf ${MINGW_ROOT}/share/vala
    find ${MINGW_ROOT}/lib -name '*.a' | xargs rm

    # remove some larger ones
    rm -rf ${MINGW_ROOT}/share/icons/Adwaita/512x512
    rm -rf ${MINGW_ROOT}/share/icons/Adwaita/256x256
    rm -rf ${MINGW_ROOT}/share/icons/Adwaita/96x96
    ${MINGW_ROOT}/bin/gtk-update-icon-cache-3.0 ${MINGW_ROOT}/share/icons/Adwaita

    # remove some gtk demo icons
    find "${MINGW_ROOT}/share/icons/hicolor" -name "gtk3-*" | xargs rm -f
    ${MINGW_ROOT}/bin/gtk-update-icon-cache-3.0 ${MINGW_ROOT}/share/icons/hicolor

    # python related
    rm -rf "${MINGW_ROOT}"/lib/python3.*/test
    rm -f "${MINGW_ROOT}"/lib/python3.*/lib-dynload/_tkinter*
    find "${MINGW_ROOT}"/lib/python3.* -type d -name "test*" | xargs rm -rf
    find "${MINGW_ROOT}"/lib/python3.* -type d -name "*_test*" | xargs rm -rf
    find ${MINGW_ROOT}/lib -name '__pycache__' | xargs rm -r
}

function build_installer {
    (cd $MINGW_ROOT && makensis -NOCD -DVERSION="$VERSION" ../../gaphor.nsi)

    mv "${MINGW_ROOT}/gaphor-LATEST.exe" "gaphor-$VERSION-installer.exe"
}

function build_portable_installer {
    local PORTABLE="$(pwd)/gaphor-$VERSION-portable"

    rm -rf "$PORTABLE"
    mkdir "$PORTABLE"
    cp gaphor.lnk "$PORTABLE"
    cp README-PORTABLE.txt "$PORTABLE"/README.txt
    unix2dos "$PORTABLE"/README.txt
    mkdir "$PORTABLE"/config
    cp -RT "${MINGW_ROOT}" "$PORTABLE"/data

    rm -Rf 7zout 7z1900-x64.exe
    7z a payload.7z "$PORTABLE"
    wget.exe -P "$(pwd)" -c https://www.7-zip.org/a/7z1900-x64.exe
    7z x -o7zout 7z1900-x64.exe
    cat 7zout/7z.sfx payload.7z > "$PORTABLE".exe
    rm -Rf 7zout 7z1900-x64.exe payload.7z "$PORTABLE"
}

clean_all
install_dependencies
install_gaphor
prepackage_cleanup
build_installer
build_portable_installer