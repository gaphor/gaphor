#!/usr/bin/env bash

set -euo pipefail

# DIR is the parent directory
DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")"
cd "${DIR}"

DIST_LOCATION="${DIR}/dist/gaphor"
VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
APP_DIR="${DIR}"/dist/AppRun
APP_NAME="Gaphor"
APP_ID="org.gaphor.${APP_NAME}"

function remove_excluded_files {
    # Remove excludelist files known as having bad side effects
    echo "Removing excluded files"
    while IFS= read -r line; do
        file="$(echo "${line}" | cut -d' ' -f1)"
        if [ ! "${file}" = "" ] && [ ! "${file}" = "#" ]; then
            [ -f "${DIST_LOCATION}/{file}" ] && rm -fv "${DIST_LOCATION}/{file}"
            echo "${file}"
        fi
    done < "${DIR}/appimage/excludelist"
}

function create_package {
    # Inspired by https://github.com/nuxeo/nuxeo-drive
    # Create the final AppImage
    local output="${DIR}/dist/${APP_NAME}-${VERSION}-x86_64.AppImage"

    echo "Adjusting file names to fit in the AppImage"
    # PyInstaller + AppImage inspired by https://gitlab.com/scottywz/ezpyi/
    [ -d "${APP_DIR}" ] && rm -rf "${APP_DIR}"
    mv -v "${DIST_LOCATION}" "${APP_DIR}"

    echo "Copying icon"
    cp -v "${DIR}/appimage/${APP_ID}.png" "${APP_DIR}/${APP_ID}.png"

    echo "Copying metadata files"
    mkdir -pv "${APP_DIR}/usr/share/metainfo"
    cp -v "${DIR}/appimage/${APP_ID}".appdata.xml "${APP_DIR}"/usr/share/metainfo
    mkdir -pv "${APP_DIR}"/usr/share/applications
    cp -v "${DIR}/appimage/${APP_ID}.desktop" "${APP_DIR}/usr/share/applications/"
    ln -srv "${APP_DIR}/usr/share/applications/${APP_ID}.desktop" "${APP_DIR}/${APP_ID}.desktop"
    cp -v "${DIR}/appimage/AppRun" "${APP_DIR}/AppRun"

    echo "Decompressing the AppImage tool"
    mkdir -p build
    cd build
    [ -d "squashfs-root" ] && rm -frv "squashfs-root"
    wget https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
    ./appimagetool-x86_64.AppImage --appimage-extract
    cd ..

    echo "Creating the AppImage file"
    # --no-appstream because appstreamcli is not easily installable on CentOS
    ./build/squashfs-root/AppRun --no-appstream "${APP_DIR}" "${output}"

    echo "Clean-up"
    rm -rf squashfs-root
}

function main {
    remove_excluded_files
    create_package
}

main "$@";
