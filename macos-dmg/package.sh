#!/bin/bash
#
# Package script for Gaphor.
#
# Thanks:
# - http://stackoverflow.com/questions/1596945/building-osx-app-bundle
# - Py2app: https://bitbucket.org/ronaldoussoren/py2app

set -euo pipefail

APP=Gaphor.app

CONTENTSDIR="${APP}/Contents"
MACOSDIR="${CONTENTSDIR}/MacOS"
RESOURCESDIR="${CONTENTSDIR}/Resources"

LOCALDIR=/usr/local

function log() {
  echo "$*" >&2
}

rm -rf Gaphor.app Gaphor-*.dmg


# Make a virtual env, so we are not bothered with site-packages installed on the host system

python3 -m venv --copies --prompt Gaphor.app "${RESOURCESDIR}"

VERSION="$(poetry version | cut -d' ' -f2)"
PYVER="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info))')"


# Copy all files in the application bundle:

mkdir -p "${MACOSDIR}"
mkdir -p "${RESOURCESDIR}"

cp PkgInfo "${CONTENTSDIR}"
cp gaphor.icns "${RESOURCESDIR}"
cat __boot__.py | sed 's#3\.7#'${PYVER}'#' >"${RESOURCESDIR}/__boot__.py"
cat Info.plist | sed 's#VERSION#'${VERSION}'#g' | sed 's#3\.7#'${PYVER}'#g' > "${CONTENTSDIR}/Info.plist"

cc -o "${MACOSDIR}/gaphor" -Wl,-rpath,@executable_path/../Resources/lib main.c -DREDIRECT_ASL -framework Cocoa

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
  echo gtk-mac-integration
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
grep '^bin/gdk-pixbuf-query-loaders\|^bin/gtk-query-immodules-3.0\|^lib/\|^share/gir-1.0/\|^share/glib-2.0/schemas/\|^share/locale/\|^share/icons/\|^share/themes/\|^share/fontconfig/\|^Frameworks/' |\
while read rf f
do
  # log "Adding ${RESOURCESDIR}/${rf}"
  mkdir -p "${RESOURCESDIR}/$(dirname $rf)"
  test -L "$f" || cp $f "${RESOURCESDIR}/${rf}"
done

mv "${RESOURCESDIR}/Frameworks" "${CONTENTSDIR}"
mv "${RESOURCESDIR}/bin/gdk-pixbuf-query-loaders" "${MACOSDIR}"
mv "${RESOURCESDIR}/bin/gtk-query-immodules-3.0" "${MACOSDIR}"
mkdir -p "${RESOURCESDIR}/etc"
cp -r "${LOCALDIR}/etc/fonts" "${RESOURCESDIR}/etc"

# (from py2app/build_app.py:1458)
# When we're using a python framework bin/python refers to a stub executable
# that we don't want to use. We need the executable in Resources/Python.app.
mv "${CONTENTSDIR}/Frameworks/Python.framework/Versions/${PYVER}/Resources/Python.app/Contents/MacOS/Python" "${MACOSDIR}/python"

# Somehow files are writen with mode 444
find "${RESOURCESDIR}" -type f -exec chmod u+w {} \;

log "Installing Gaphor in ${RESOURCESDIR}..."

"${RESOURCESDIR}/bin/pip3" install --no-warn-script-location ../dist/gaphor-${VERSION}-py3-none-any.whl

log "Cleaning unneeded resources..."

rm -r "${RESOURCESDIR}"/bin
rm "${RESOURCESDIR}"/lib/*.a
rm "${RESOURCESDIR}/lib/libgtkmacintegration-gtk2.2.dylib"
rm -r "${RESOURCESDIR}/lib/cairo"
rm -r "${RESOURCESDIR}/lib/cmake"
rm -r "${RESOURCESDIR}/lib/gettext"
rm -r "${RESOURCESDIR}/lib/glib-2.0"
rm -r "${RESOURCESDIR}/lib/gobject-introspection"
rm -r "${RESOURCESDIR}/lib/pkgconfig"

rm -r "${CONTENTSDIR}/Frameworks/Python.framework/Versions/${PYVER}/Resources/Python.app"
rm -r "${CONTENTSDIR}/Frameworks/Python.framework/Versions/${PYVER}/bin"
rm -r "${CONTENTSDIR}/Frameworks/Python.framework/Versions/${PYVER}/include"
rm -r "${CONTENTSDIR}/Frameworks/Python.framework/Versions/${PYVER}/share"

log "Fixing dynamic link dependencies..."

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
      relname="../Resources/lib/$(basename $dep)"
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

{
  # Libraries
  find ${CONTENTSDIR} -type f -name '*.so'
  find ${CONTENTSDIR} -type f -name '*.dylib'
  echo ${CONTENTSDIR}/Frameworks/Python.framework/Versions/*/Python
  # Binaries
  file ${RESOURCESDIR}/bin/* | grep Mach-O | cut -f1 -d:
  echo ${MACOSDIR}/python
} | map fix_paths

log "Compiling .gir files..."

function compile_gir {
  local gir="$1"
  local outfile="$(basename $gir | sed 's/gir$/typelib/')"
  sed -i "" 's#/usr/local/Cellar/[^/]*/[^/]*#@executable_path/../Resources#g' "${gir}"
  g-ir-compiler --output="${RESOURCESDIR}/lib/girepository-1.0/${outfile}" "${gir}"
}

find "${RESOURCESDIR}" -type f -name '*.gir' | map compile_gir

log "Compiling schemas..."

glib-compile-schemas ${RESOURCESDIR}/share/glib-2.0/schemas

log "Building Gaphor-$VERSION.dmg..."

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
  "Gaphor.app"

log "Done!"
