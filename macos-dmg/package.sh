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


VERSION="$(poetry version | cut -d' ' -f2)"

# Obtain the Python version from the python dependency.
PYVER="$(brew deps gobject-introspection | grep '^python@' | cut -d@ -f2)"

test -n "${PYVER}" || { echo "Could not determine Python version!"; exit 1; }
echo "Python version: ${PYVER}"

export LDFLAGS="-L/usr/local/opt/python@${PYVER}/lib"
export PKG_CONFIG_PATH="/usr/local/opt/python@${PYVER}/lib/pkgconfig"

# Make a virtual env, so we are not bothered with site-packages installed on the host system
"/usr/local/opt/python@${PYVER}/bin/python3" -m venv --copies --prompt Gaphor.app "${RESOURCESDIR}"

# Copy all files in the application bundle:

mkdir -p "${MACOSDIR}"
mkdir -p "${RESOURCESDIR}"

cp PkgInfo "${CONTENTSDIR}"
cp gaphor.icns "${RESOURCESDIR}"
sed 's#3\.7#'"${PYVER}"'#' __boot__.py > "${RESOURCESDIR}/__boot__.py"
sed 's#VERSION#'"${VERSION}"'#g' Info.plist | sed 's#3\.7#'"${PYVER}"'#g' > "${CONTENTSDIR}/Info.plist"

cc -o "${MACOSDIR}/gaphor" -Wl,-rpath,@executable_path/../Resources/lib main.c -DREDIRECT_ASL -framework Cocoa

function rel_path {
  # shellcheck disable=SC2001
  echo "$1" | sed 's#/usr/local/Cellar/[^/]*/[^/]*/##'
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
while read -r dep
do
  log "Processing files for Homebrew formula $dep"
  brew list -v "$dep"
done |\
grep -v '^find ' |\
while read -r f
do
  echo "$(rel_path "$f") $f"
done |\
grep '^bin/gdk-pixbuf-query-loaders\|^bin/gtk-query-immodules-3.0\|^lib/\|^share/gir-1.0/\|^share/glib-2.0/schemas/\|^share/locale/\|^share/icons/\|^share/themes/\|^share/fontconfig/\|^Frameworks/' |\
while read -r rf f
do
  # log "Adding ${RESOURCESDIR}/${rf}"
  mkdir -p "${RESOURCESDIR}/$(dirname "$rf")"
  test -L "$f" || cp "$f" "${RESOURCESDIR}/${rf}"
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

# Homebrew executables are writen with mode 555
find "${CONTENTSDIR}" -type f -exec chmod u+w {} \;

log "Installing Gaphor in ${RESOURCESDIR}..."

"${RESOURCESDIR}/bin/pip3" install --no-warn-script-location ../dist/gaphor-"${VERSION}"-py3-none-any.whl

log "Cleaning unneeded resources..."

rm -r "${RESOURCESDIR:?}"/bin
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
  while read -r arg
  do
    $fun "$arg"
  done
}

function resolve_deps {
  local lib=$1
  local dep
  otool -L "$lib" | grep -e "^.$LOCALDIR/" |\
  while read -r dep _
  do
    echo "$dep"
  done
}

function fix_paths {
  local lib="$1"
  log Fixing "$lib"
  for dep in $(resolve_deps "$lib")
  do
    local relname
    if [[ "$dep" =~ ^.*/Frameworks/.* ]]
    then
      # shellcheck disable=SC2001
      relname="../$(echo "$dep" | sed 's#^.*/\(Frameworks/.*$\)#\1#')"
    else
      relname="../Resources/lib/$(basename "$dep")"
    fi
    test -f "${MACOSDIR}/$relname" || {
      local fullname
      fullname=$(eval echo ${MACOSDIR}/"${relname//\.dylib/.*.dylib}")
      log "Library ${MACOSDIR}/$relname not found, using $(basename "$fullname") instead"
      relname="$(dirname "$relname")/$(basename "$fullname")"
    }
    # @executable_path is /path/to/Gaphor.app/Contents/MacOS
    log "  $dep -> @executable_path/$relname"
    install_name_tool -change "$dep" @executable_path/"$relname" "$lib"
  done
}

{
  # Libraries
  find ${CONTENTSDIR} -type f -name '*.so'
  find ${CONTENTSDIR} -type f -name '*.dylib'
  echo ${CONTENTSDIR}/Frameworks/Python.framework/Versions/*/Python
  # Binaries
  find ${MACOSDIR} -type f
} | map fix_paths

log "Compiling .gir files..."

function compile_gir {
  local gir
  local outfile
  gir="$1"
  outfile="$(basename "$gir" | sed 's/gir$/typelib/')"
  sed -i "" 's#/usr/local/Cellar/[^/]*/[^/]*#@executable_path/../Resources#g' "${gir}"
  g-ir-compiler --output="${RESOURCESDIR}/lib/girepository-1.0/${outfile}" "${gir}"
}

find "${RESOURCESDIR}" -type f -name '*.gir' | map compile_gir

log "Compiling schemas..."

glib-compile-schemas ${RESOURCESDIR}/share/glib-2.0/schemas

log "Done!"
