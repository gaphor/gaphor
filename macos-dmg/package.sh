#!/bin/bash
#
# Package script for Gaphor.
#
# Thanks: http://stackoverflow.com/questions/1596945/building-osx-app-bundle

set -euo pipefail

# Also fix $INSTALLDIR/MacOS/gaphor in case this number changes
APP=Gaphor.app
INSTALLDIR=$APP/Contents
LIBDIR=$INSTALLDIR/lib

LOCALDIR=/usr/local

function log() {
  echo $* >&2
}

libffi_path="$(brew ls libffi | grep pkgconfig | xargs dirname)"
echo "Adding libffi pkg-config path ${libffi_path} to \$PKG_CONFIG_PATH"
export PKG_CONFIG_PATH="${libffi_path}:${PKG_CONFIG_PATH:-}"

rm -rf Gaphor.app Gaphor-*.dmg Gaphor-*-macos.zip

mkdir -p ${INSTALLDIR}/MacOS
mkdir -p ${INSTALLDIR}/Resources

cp Info.plist ${INSTALLDIR}
cp PkgInfo ${INSTALLDIR}
cp gaphor ${INSTALLDIR}/MacOS
cp gaphor.icns ${INSTALLDIR}/Resources

function rel_path {
  echo $1 | sed 's#/usr/local/Cellar/[^/]*/[^/]*/##'
}

brew deps gtk+3 |\
while read dep
do
  log "Scanning Homebrew files for $dep"
  brew list -v $dep
done |\
grep -v '^find ' |\
while read f
do
  echo "$(rel_path $f) $f"
done |\
grep '^bin\|^lib/\|^share/gir-1.0/\|^share/locale/\|^Frameworks/' |\
while read rf f
do
  # log "Adding ${INSTALLDIR}/${rf}"
  mkdir -p "${INSTALLDIR}/$(dirname $rf)"
  test -L "$f" || cp $f "${INSTALLDIR}/${rf}"
done

# Somehow files are writen with mode 444
find $INSTALLDIR -type f -exec chmod u+w {} \;

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
  local lib=$1
  log Fixing $lib
  for dep in `resolve_deps $lib`
  do
    log "|  $dep"
    # @executable_path is /path/to/Gaphor.app/MacOS
    if [[ "$dep" =~ ^.*/Frameworks/.* ]]
    then
      log ">> Framework: @executable_path/../$(echo $dep | sed 's#^.*/\(Frameworks/.*$\)#\1#')"
      install_name_tool -change $dep @executable_path/../$(echo $dep | sed 's#^.*/\(Frameworks/.*$\)#\1#') $lib
    else
      log ">> Lib: @executable_path/../lib/$(basename $dep)"
      install_name_tool -change $dep @executable_path/../lib/$(basename $dep) $lib
    fi
  done
}

{
  find $INSTALLDIR -type f -name '*.so'
  find $INSTALLDIR -type f -name '*.dylib'
  file $INSTALLDIR/bin/* | grep Mach-O | cut -f1 -d:
  file $INSTALLDIR/Frameworks/Python.framework/Versions/*/bin/* | grep Mach-O | cut -f1 -d:
  echo $INSTALLDIR/Frameworks/Python.framework/Versions/*/Python
} |\
while read lib
do
  # echo $lib
  fix_paths $lib
done

# cp /usr/local/bin/gdk-pixbuf-query-loaders ${INSTALLDIR}/bin
# fix_paths ${INSTALLDIR}/bin/gdk-pixbuf-query-loaders
log "Installing Gaphor in ${INSTALLDIR}..."

PYVER="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info))')"

pip3 install --prefix ${INSTALLDIR} ../dist/gaphor-*.tar.gz

# Package it up!

# VERSION=`find . -name 'gaphor*egg' | sed -e 's|.*/gaphor-||' -e 's|-py.*egg$||'`
# zip -r Gaphor-$VERSION-macos.zip $APP
# hdiutil create -srcfolder $APP Gaphor-$VERSION.dmg
