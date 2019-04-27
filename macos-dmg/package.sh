#!/bin/bash
#
# Package script for Gaphor.
#
# Thanks:
# - http://stackoverflow.com/questions/1596945/building-osx-app-bundle
# - Py2app: https://bitbucket.org/ronaldoussoren/py2app

set -euo pipefail

# Also fix $INSTALLDIR/MacOS/gaphor in case this number changes
APP=Gaphor.app
VERSION="$(ls ../dist/gaphor-*.tar.gz | tail -1 | sed 's#^.*gaphor-\(.*\).tar.gz#\1#')"

APPHOME="${APP}/Contents"
MACOSDIR="${APPHOME}/MacOS"
RESOURCESDIR="${APPHOME}/Resources"
INSTALLDIR="${APPHOME}"

LOCALDIR=/usr/local

PYVER="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info))')"

function log() {
  echo "$*" >&2
}

rm -rf Gaphor.app Gaphor-*.dmg Gaphor-*-macos.zip


# Copy all files in the application bundle:

mkdir -p "${MACOSDIR}"
mkdir -p "${RESOURCESDIR}"

cp PkgInfo "${INSTALLDIR}"
cp gaphor.icns "${RESOURCESDIR}"
cat Info.plist | sed 's#VERSION#'${VERSION}'#g' > "${INSTALLDIR}/Info.plist"
cat gaphor | sed 's#3.7#'${PYVER}'#' > "${MACOSDIR}/gaphor"
chmod +x "${MACOSDIR}/gaphor"

function rel_path {
  echo $1 | sed 's#/usr/local/Cellar/[^/]*/[^/]*/##'
}

{
  echo gtk+3
  brew deps gtk+3
  echo gobject-introspection
  brew deps gobject-introspection
  echo adwaita-icon-theme
  brew deps adwaita-icon-theme
} | sort -u |\
while read dep
do
  log "Processing files for Homebrew formula $dep"
  brew list -v $dep
done |\
grep -v '^find ' |\
while read f
do
  echo "$(rel_path $f) $f"
done |\
grep '^bin/gdk-pixbuf-query-loaders\|^bin/gtk-query-immodules-3.0\|^lib/\|^share/gir-1.0/\|^share/locale/\|^share/icons/\|^share/themes/\|^Frameworks/' |\
while read rf f
do
  # log "Adding ${INSTALLDIR}/${rf}"
  mkdir -p "${INSTALLDIR}/$(dirname $rf)"
  test -L "$f" || cp $f "${INSTALLDIR}/${rf}"
done

mkdir -p "${RESOURCESDIR}/etc"
cp -r "${LOCALDIR}/etc/fonts" "${RESOURCESDIR}/etc"

# Somehow files are writen with mode 444
find "${INSTALLDIR}" -type f -exec chmod u+w {} \;

# (from py2app/build_app.py:1458)
# When we're using a python framework bin/python refers to a stub executable
# that we don't want use, we need the executable in Resources/Python.app.
cp "${INSTALLDIR}/Frameworks/Python.framework/Versions/${PYVER}/Resources/Python.app/Contents/MacOS/Python" "${MACOSDIR}/python"

rm "${INSTALLDIR}"/lib/*.a
rm -r "${INSTALLDIR}/lib/gobject-introspection"

rm -r "${INSTALLDIR}/Frameworks/Python.framework/Versions/${PYVER}/Resources/Python.app"
rm -r "${INSTALLDIR}/Frameworks/Python.framework/Versions/${PYVER}/bin"
rm -r "${INSTALLDIR}/Frameworks/Python.framework/Versions/${PYVER}/include"
rm -r "${INSTALLDIR}/Frameworks/Python.framework/Versions/${PYVER}/share"

log "Installing Gaphor in ${INSTALLDIR}..."

pip3 install --prefix "${INSTALLDIR}" --no-warn-script-location ../dist/gaphor-${VERSION}.tar.gz


# Fix dynamic link dependencies:

function map {
  local fun=$1
  while read arg
  do
    $fun $arg
  done
}

function resolve_deps {
  local lib=$1
  local dep
  otool -L $lib | grep -e "^.$LOCALDIR/" |\
  while read dep _
  do
    echo $dep
  done
}

function fix_paths {
  local lib="$1"
  log Fixing $lib
  for dep in $(resolve_deps $lib)
  do
    local relname
    if [[ "$dep" =~ ^.*/Frameworks/.* ]]
    then
      relname="../$(echo $dep | sed 's#^.*/\(Frameworks/.*$\)#\1#')"
    else
      relname="../lib/$(basename $dep)"
    fi
    test -f "${MACOSDIR}/$relname" || {
      local fullname=$(eval echo ${MACOSDIR}/${relname//\.dylib/.*.dylib})
      log "Library ${MACOSDIR}/$relname not found, using $(basename $fullname) instead"
      relname="$(dirname $relname)/$(basename $fullname)"
    }
    # @executable_path is /path/to/Gaphor.app/MacOS
    log "  $dep -> @executable_path/$relname"
    install_name_tool -change $dep @executable_path/$relname $lib
  done
}

function fix_gir {
  local gir="$1"
  log Fixing $gir
  local outfile="$(basename $gir | sed 's/gir$/typelib/')"
  sed -i "" 's#/usr/local/Cellar/[^/]*/[^/]*#@executable_path/..#' "${gir}"
  g-ir-compiler --output="${INSTALLDIR}/lib/girepository-1.0/${outfile}" "${gir}"
}

{
  # Libraries
  find ${APPHOME} -type f -name '*.so'
  find ${APPHOME} -type f -name '*.dylib'
  echo ${APPHOME}/Frameworks/Python.framework/Versions/*/Python
  # Binaries
  file ${INSTALLDIR}/bin/* | grep Mach-O | cut -f1 -d:
  echo ${MACOSDIR}/python
} | map fix_paths

find "${INSTALLDIR}" -type f -name '*.gir' | map fix_gir


log "Building Gaphor-$VERSION.dmg..."

hdiutil create -srcfolder $APP Gaphor-$VERSION.dmg

log "Done!"
