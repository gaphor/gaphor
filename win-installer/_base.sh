#!/usr/bin/env bash

# Copyright 2016 Christoph Reiter, 2019 Dan Yeaw
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

set -e
DIR="$( cd "$( dirname "$0" )" && pwd )"
cd "${DIR}"

# CONFIG START

ARCH="x86_64"
BUILD_VERSION="0"

# CONFIG END

MISC="${DIR}"/misc
if [ "${ARCH}" = "x86_64" ]; then
    MINGW="mingw64"
else
    MINGW="mingw32"
fi

VERSION="0.0.0"
VERSION_DESC="UNKNOWN"

function set_build_root {
    BUILD_ROOT="$1"
    REPO_CLONE="${BUILD_ROOT}"/gaphor
    MINGW_ROOT="${BUILD_ROOT}/${MINGW}"
}

set_build_root "${DIR}/_build_root"

function build_pacman {
    pacman --cachedir "/var/cache/pacman/pkg" --root "${BUILD_ROOT}" "$@"
}

function build_pip {
    "${BUILD_ROOT}"/"${MINGW}"/bin/pip3.exe "$@"
}

function build_python {
    "${BUILD_ROOT}"/"${MINGW}"/bin/python3.exe "$@"
}

function build_compileall_pyconly {
    MSYSTEM= build_python -m compileall --invalidation-mode unchecked-hash -b "$@"
}

function build_compileall {
    MSYSTEM= build_python -m compileall --invalidation-mode unchecked-hash "$@"
}

function install_pre_deps {
    pacman -S --needed --noconfirm p7zip git dos2unix \
        mingw-w64-"${ARCH}"-nsis mingw-w64-"${ARCH}"-wget mingw-w64-"${ARCH}"-toolchain
}

function create_root {
    mkdir -p "${BUILD_ROOT}"

    mkdir -p "${BUILD_ROOT}"/var/lib/pacman
    mkdir -p "${BUILD_ROOT}"/var/log
    mkdir -p "${BUILD_ROOT}"/tmp

    build_pacman --noconfirm -Syu
    build_pacman --noconfirm -S base
}

function extract_installer {
    [ -z "$1" ] && (echo "Missing arg"; exit 1)

    mkdir -p "$BUILD_ROOT"
    7z x -o"$BUILD_ROOT"/"$MINGW" "$1"
    rm -rf "$MINGW_ROOT"/'$PLUGINSDIR' "$MINGW_ROOT"/*.txt "$MINGW_ROOT"/*.nsi
}

function install_deps {
    # Temporarily using our own remote repository while waiting for
    # https://github.com/msys2/MINGW-packages/pull/5114 to be merged
    mkdir -p "$BUILD_ROOT"/etc
    cp "${DIR}"/pacman.conf "$BUILD_ROOT"/etc/
    build_pacman --noconfirm -Syu

    build_pacman --noconfirm -S \
        mingw-w64-"${ARCH}"-gtk3 \
        mingw-w64-"${ARCH}"-python3 \
        mingw-w64-"${ARCH}"-python3-gobject \
	mingw-w64-"${ARCH}"-gobject-introspection \
        mingw-w64-"${ARCH}"-python3-cairo \
        mingw-w64-"${ARCH}"-python3-pip \
        mingw-w64-"${ARCH}"-python3-setuptools \
        mingw-w64-"${ARCH}"-python3-zope.interface

    # Temporary workaround until mingw64 python3 is patched
    # Line 296 changed to not raise a VC 6.0 version error
    cp "${DIR}"/msvc9compiler "${MINGW_ROOT}"/lib/python3.7/distutils/msvc9compiler.py

    PIP_REQUIREMENTS="\
        pycairo==1.18.0
        PyGObject==3.30.4
        gaphas==1.0.0
        zope.component==4.5
        tomlkit==0.5.3
        "
    build_pip install -I $(echo "$PIP_REQUIREMENTS" | tr ["\\n"] [" "])

}

# function get_version {
# 	python3 - <<END
# from tomlkit import parse
# with open('../pyproject.toml', 'r') as f:
# 	parsed_toml = parse(f.read())
# 	print(parsed_toml["tool"]["poetry"]["version"])
# END
# }

function install_gaphor {
    [ -z "$1" ] && (echo "Missing arg"; exit 1)

    rm -Rf "${REPO_CLONE}"
    git clone "${DIR}"/.. "${REPO_CLONE}"

    cd "${REPO_CLONE}"
    git checkout "$1" 
    
    # Don't use PEP517 until Poetry unicode issues resolved
    # https://github.com/sdispater/poetry/pull/1029
    rm pyproject.toml

    build_python setup.py install

    cd "${DIR}"

    # Create launchers
    python3 "${MISC}"/create-launcher.py \
        "${VERSION}" "${MINGW_ROOT}"/bin

    VERSION=$(get_version)
    VERSION_DESC="$VERSION"
    if [ "$1" = "master" ]
    then
        local GIT_REV=$(git rev-list --count HEAD)
        local GIT_HASH=$(git rev-parse --short HEAD)
        VERSION_DESC="$VERSION-rev$GIT_REV-$GIT_HASH"
    fi

    build_compileall -d "" -f -q "$(cygpath -w "${MINGW_ROOT}")"
}

function cleanup_before {
    # these all have svg variants
    find "${MINGW_ROOT}"/share/icons -name "*.symbolic.png" -exec rm -f {} \;

    # remove some larger ones
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/512x512"
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/256x256"
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/96x96"
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/48x48"
    "${MINGW_ROOT}"/bin/gtk-update-icon-cache-3.0.exe \
        "${MINGW_ROOT}"/share/icons/Adwaita

    # python related, before installing gaphor
    rm -Rf "${MINGW_ROOT}"/lib/python3.*/test
    rm -f "${MINGW_ROOT}"/lib/python3.*/lib-dynload/_tkinter*
    find "${MINGW_ROOT}"/lib/python3.* -type d -name "test*" \
        -prune -exec rm -rf {} \;
    find "${MINGW_ROOT}"/lib/python3.* -type d -name "*_test*" \
        -prune -exec rm -rf {} \;

    find "${MINGW_ROOT}"/bin -name "*.pyo" -exec rm -f {} \;
    find "${MINGW_ROOT}"/bin -name "*.pyc" -exec rm -f {} \;

    build_compileall_pyconly -d "" -f -q "$(cygpath -w "${MINGW_ROOT}")"
    find "${MINGW_ROOT}" -name "*.py" -exec rm -f {} \;
    find "${MINGW_ROOT}" -type d -name "__pycache__" -prune -exec rm -rf {} \;
}

function cleanup_after {
    # delete translations we don't support
    for d in "${MINGW_ROOT}"/share/locale/*/LC_MESSAGES; do
        if [ ! -f "${d}"/gaphor.mo ]; then
            rm -Rf "${d}"
        fi
    done

    find "${MINGW_ROOT}" -regextype "posix-extended" -name "*.exe" -a ! \
        -iregex ".*/(gaphor|exfalso|operon|python|gspawn-)[^/]*\\.exe" \
        -exec rm -f {} \;

    rm -Rf "${MINGW_ROOT}"/libexec
    rm -Rf "${MINGW_ROOT}"/share/gtk-doc
    rm -Rf "${MINGW_ROOT}"/include
    rm -Rf "${MINGW_ROOT}"/var
    rm -Rf "${MINGW_ROOT}"/etc/config.site
    rm -Rf "${MINGW_ROOT}"/etc/pki
    rm -Rf "${MINGW_ROOT}"/etc/pkcs11
    rm -Rf "${MINGW_ROOT}"/etc/gtk-3.0/im-multipress.conf
    rm -Rf "${MINGW_ROOT}"/share/zsh
    rm -Rf "${MINGW_ROOT}"/share/pixmaps
    rm -Rf "${MINGW_ROOT}"/share/gnome-shell
    rm -Rf "${MINGW_ROOT}"/share/dbus-1
    rm -Rf "${MINGW_ROOT}"/share/gir-1.0
    rm -Rf "${MINGW_ROOT}"/share/doc
    rm -Rf "${MINGW_ROOT}"/share/man
    rm -Rf "${MINGW_ROOT}"/share/info
    rm -Rf "${MINGW_ROOT}"/share/mime
    rm -Rf "${MINGW_ROOT}"/share/gettext
    rm -Rf "${MINGW_ROOT}"/share/libtool
    rm -Rf "${MINGW_ROOT}"/share/licenses
    rm -Rf "${MINGW_ROOT}"/share/appdata
    rm -Rf "${MINGW_ROOT}"/share/aclocal
    rm -Rf "${MINGW_ROOT}"/share/ffmpeg
    rm -Rf "${MINGW_ROOT}"/share/vala
    rm -Rf "${MINGW_ROOT}"/share/readline
    rm -Rf "${MINGW_ROOT}"/share/xml
    rm -Rf "${MINGW_ROOT}"/share/bash-completion
    rm -Rf "${MINGW_ROOT}"/share/common-lisp
    rm -Rf "${MINGW_ROOT}"/share/emacs
    rm -Rf "${MINGW_ROOT}"/share/gdb
    rm -Rf "${MINGW_ROOT}"/share/libcaca
    rm -Rf "${MINGW_ROOT}"/share/gettext
    rm -Rf "${MINGW_ROOT}"/share/gst-plugins-base
    rm -Rf "${MINGW_ROOT}"/share/gst-plugins-bad
    rm -Rf "${MINGW_ROOT}"/share/libgpg-error
    rm -Rf "${MINGW_ROOT}"/share/p11-kit
    rm -Rf "${MINGW_ROOT}"/share/pki
    rm -Rf "${MINGW_ROOT}"/share/thumbnailers
    rm -Rf "${MINGW_ROOT}"/share/gtk-3.0
    rm -Rf "${MINGW_ROOT}"/share/nghttp2
    rm -Rf "${MINGW_ROOT}"/share/themes
    rm -Rf "${MINGW_ROOT}"/share/fontconfig
    rm -Rf "${MINGW_ROOT}"/share/gettext-*
    rm -Rf "${MINGW_ROOT}"/share/installed-tests

    find "${MINGW_ROOT}"/share/glib-2.0 -type f ! \
        -name "*.compiled" -exec rm -f {} \;

    rm -Rf "${MINGW_ROOT}"/lib/cmake
    rm -Rf "${MINGW_ROOT}"/lib/gettext
    rm -Rf "${MINGW_ROOT}"/lib/gtk-3.0
    rm -Rf "${MINGW_ROOT}"/lib/mpg123
    rm -Rf "${MINGW_ROOT}"/lib/p11-kit
    rm -Rf "${MINGW_ROOT}"/lib/pkcs11
    rm -Rf "${MINGW_ROOT}"/lib/ruby
    rm -Rf "${MINGW_ROOT}"/lib/engines

    find "${MINGW_ROOT}" -name "*.a" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.whl" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.h" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.la" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.sh" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.jar" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.def" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.cmd" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.cmake" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.pc" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.desktop" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.manifest" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.pyo" -exec rm -f {} \;

    find "${MINGW_ROOT}"/bin -name "*-config" -exec rm -f {} \;
    find "${MINGW_ROOT}"/bin -name "easy_install*" -exec rm -f {} \;
    find "${MINGW_ROOT}" -regex ".*/bin/[^.]+" -exec rm -f {} \;
    find "${MINGW_ROOT}" -regex ".*/bin/[^.]+\\.[0-9]+" -exec rm -f {} \;

    find "${MINGW_ROOT}" -name "gtk30-properties.mo" -exec rm -rf {} \;
    find "${MINGW_ROOT}" -name "gettext-tools.mo" -exec rm -rf {} \;
    find "${MINGW_ROOT}" -name "libexif-12.mo" -exec rm -rf {} \;
    find "${MINGW_ROOT}" -name "xz.mo" -exec rm -rf {} \;
    find "${MINGW_ROOT}" -name "libgpg-error.mo" -exec rm -rf {} \;

    find "${MINGW_ROOT}" -name "old_root.pem" -exec rm -rf {} \;
    find "${MINGW_ROOT}" -name "weak.pem" -exec rm -rf {} \;

    find "${MINGW_ROOT}"/bin -name "*.pyo" -exec rm -f {} \;
    find "${MINGW_ROOT}"/bin -name "*.pyc" -exec rm -f {} \;

    build_python "${MISC}/depcheck.py" --delete

    find "${MINGW_ROOT}" -type d -empty -delete
}

function build_installer {
    BUILDPY=$(echo "${MINGW_ROOT}"/lib/python3.*/site-packages/gaphor*egg/gaphor)/build.py
    cp "${REPO_CLONE}"/win-installer/build.py "$BUILDPY"
    echo 'BUILD_TYPE = u"windows"' >> "$BUILDPY"
    echo "BUILD_VERSION = $BUILD_VERSION" >> "$BUILDPY"
    (cd "$REPO_CLONE" && echo "BUILD_INFO = u\"$(git rev-parse --short HEAD)\"" >> "$BUILDPY")
    build_compileall -d "" -q -f "$BUILDPY"

    cp misc/gaphor.ico "${BUILD_ROOT}"
    (cd "${MINGW_ROOT}" && makensis -NOCD -DVERSION="$VERSION_DESC" "${MISC}"/win_installer.nsi)

    mv "${MINGW_ROOT}/gaphor-LATEST.exe" "$DIR/gaphor-$VERSION_DESC-installer.exe"
}

function build_portable_installer {
    cp "${REPO_CLONE}"/win-installer/build.py "$BUILDPY"
    echo 'BUILD_TYPE = u"windows-portable"' >> "$BUILDPY"
    echo "BUILD_VERSION = $BUILD_VERSION" >> "$BUILDPY"
    (cd "$REPO_CLONE" && echo "BUILD_INFO = u\"$(git rev-parse --short HEAD)\"" >> "$BUILDPY")
    build_compileall -d "" -q -f "$BUILDPY"

    local PORTABLE="$DIR/gaphor-$VERSION_DESC-portable"

    rm -rf "$PORTABLE"
    mkdir "$PORTABLE"
    cp "$MISC"/gaphor.lnk "$PORTABLE"
    cp "$MISC"/README-PORTABLE.txt "$PORTABLE"/README.txt
    unix2dos "$PORTABLE"/README.txt
    mkdir "$PORTABLE"/config
    cp -RT "${MINGW_ROOT}" "$PORTABLE"/data

    rm -Rf 7zout 7z1900-x64.exe
    7z a payload.7z "$PORTABLE"
    wget.exe -P "$DIR" -c https://www.7-zip.org/a/7z1900-x64.exe
    7z x -o7zout 7z1900-x64.exe
    cat 7zout/7z.sfx payload.7z > "$PORTABLE".exe
    rm -Rf 7zout 7z1900-x64.exe payload.7z "$PORTABLE"
}
