#!/usr/bin/env bash
# Copyright 2016 Christoph Reiter, 2019 Dan Yeaw
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

DIR="$( cd "$( dirname "$0" )" && pwd )"
source "$DIR"/_base.sh

set_build_root "${DIR}/_rebuild_root"

function main {
    local INSTALLER_PATH=${1}
    local GIT_TAG=${2:-"master"}

    [[ -d "${BUILD_ROOT}" ]] && (echo "${BUILD_ROOT} already exists"; exit 1)

    # started from the wrong env -> switch
    if [ $(echo "$MSYSTEM" | tr '[A-Z]' '[a-z]') != "$MINGW" ]; then
        "/${MINGW}.exe" "$0"
        exit $?
    fi

    echo "install pre-dependencies"
    install_pre_deps
    echo "create root"
    create_root
    echo "extract installer"
    extract_installer "$INSTALLER_PATH"
    echo "cleanup before installing gaphor"
    cleanup_before
    echo "install gaphor"
    install_gaphor "$GIT_TAG"
    echo "cleanup"
    cleanup_after
    echo "build installer"
    build_installer
    echo "build portable installer"
    build_portable_installer
}

main "$@";
