#!/bin/bash
#
# Package script for Gaphor.
#
# Thanks: http://stackoverflow.com/questions/1596945/building-osx-app-bundle

# Also fix $INSTALLDIR/MacOS/gaphor in case this number changes
APP=Gaphor.app
INSTALLDIR=$APP/Contents/Resources
LIBDIR=$INSTALLDIR/lib

LOCALDIR=/usr/local

function log() {
  echo $* >&2
}

python -m venv --prompt Gaphor.app --copies ${INSTALLDIR}

source ${INSTALLDIR}/bin/activate

log "Installing Gaphor in ${INSTALLDIR}..."

pip install ../dist/gaphor-*.tar.gz

# Check with Homebrew which version to pick
cp /usr/local/lib/libgtk-3.0.dylib ${INSTALLDIR}/lib


# Modules, config, etc.
for dir in etc/fonts etc/gtk-3.0 lib/gtk-3.0 lib/gdk-pixbuf-2.0 lib/girepository-1.0 share/gir-1.0 share/themes/Default/gtk-3.0; do
  mkdir -p ${INSTALLDIR}/$dir
  cp -r ${LOCALDIR}/$dir/* ${INSTALLDIR}/$dir
done


# Somehow files are writen with mode 444
find $INSTALLDIR -type f -exec chmod u+w {} \;

function resolve_deps {
  local lib=$1
  local dep
  otool -L $lib | grep -e "^.$LOCALDIR/" |\
      while read dep _; do
    echo $dep
  done
}

function fix_paths {
  local lib=$1
  log Fixing $lib
  for dep in `resolve_deps $lib`; do
    #log Fixing `basename $lib`
    log "|  $dep"
    install_name_tool -change $dep @executable_path/../Resources/lib/`basename $dep` $lib
  done
}

binlibs=`find $INSTALLDIR -type f -name '*.so'`

for lib in $binlibs; do
  log Resolving $lib
  resolve_deps $lib
  fix_paths $lib
done | sort -u | while read lib; do
  log Copying $lib
  cp $lib $LIBDIR
  chmod u+w $LIBDIR/`basename $lib`
  fix_paths $LIBDIR/`basename $lib`
done

function fix_config {
  local file=$1
  local replace=$2

  mv $file $file.orig
  sed "$replace" $file.orig > $file
}

# Fix config files

#fix_config $INSTALLDIR/etc/pango/pango.modules 's#/usr/local/.*lib/#${CWD}/../lib/#'
#fix_config $INSTALLDIR/etc/gtk-2.0/gtk.immodules 's#/usr/local/.*lib/#${CWD}/../lib/#'
#fix_config $INSTALLDIR/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache 's#/usr/local/.*lib/#${CWD}/../lib/#'

# Normalize paths (Homebrew refers everything from it's Cellar)
# fix_config $INSTALLDIR/Resources/etc/pango/pango.modules 's#/usr/local/.*lib/#/usr/local/lib/#'
# fix_config $INSTALLDIR/Resources/etc/gtk-3.0/gtk.immodules 's#/usr/local/.*lib/#/usr/local/lib/#'
# fix_config $INSTALLDIR/Resources/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache 's#/usr/local/.*lib/#/usr/local/lib/#'

# Package!

VERSION=`find . -name 'gaphor*egg' | sed -e 's|.*/gaphor-||' -e 's|-py.*egg$||'`
zip -r Gaphor-$VERSION-macos.zip $APP
hdiutil create -srcfolder $APP Gaphor-$VERSION.dmg
