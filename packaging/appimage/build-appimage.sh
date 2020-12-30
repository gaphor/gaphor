#!/usr/bin/env bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"

APP_DIR="${DIR}"/dist/AppRun
APP_ID="org.gaphor.Gaphor"
VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"

python -m venv pyinstvenv

pyinstvenv/bin/pip install ../../dist/gaphor-"${VERSION}"-py3-none-any.whl
pyinstvenv/bin/pip install pyinstaller==4.1.0

function build_pyinstaller {
    python ../make-script.py ../../pyproject.toml > ../gaphor-script.py
    pyinstvenv/bin/pyinstaller -y ../gaphor.spec
}

function remove_excluded_files {
    # Remove excludelist files known as having bad side effects
    echo "Removing excluded files"
    while IFS= read -r line; do
        file="$(echo "${line}" | cut -d' ' -f1)"
        if [ ! "${file}" = "" ] && [ ! "${file}" = "#" ]; then
            [ -f "dist/gaphor/${file}" ] && rm -fv "dist/gaphor/${file}"
        fi
    done < excludelist
}

function create_package {
    # Inspired by https://github.com/nuxeo/nuxeo-drive
    # Create the final AppImage
    local app_name="Gaphor"
    local output="dist/${app_name}-x86_64.AppImage"

    echo "Adjusting file names to fit in the AppImage"
    # PyInstaller + AppImage inspired by https://gitlab.com/scottywz/ezpyi/
    [ -d "${APP_DIR}" ] && rm -rf "${APP_DIR}"
    mv -v "dist/gaphor" "${APP_DIR}"
    mv -v "${APP_DIR}/gaphor" "${APP_DIR}/AppRun"
    ln -srv "${APP_DIR}/AppRun" "${APP_DIR}/gaphor"

    echo "Copying icon"
    cp -v "${APP_ID}.png" "${APP_DIR}/${APP_ID}.png"

    echo "Copying metadata files"
    mkdir -pv "${APP_DIR}/usr/share/metainfo"
    cp -v "${APP_ID}".appdata.xml "${APP_DIR}"/usr/share/metainfo
    mkdir -pv "${APP_DIR}"/usr/share/applications
    cp -v "${APP_ID}.desktop" "${APP_DIR}/usr/share/applications/"
    ln -srv "${APP_DIR}/usr/share/applications/${APP_ID}.desktop" "${APP_DIR}/${APP_ID}.desktop"

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
    build_pyinstaller
    remove_excluded_files
    create_package
}

main "$@";
