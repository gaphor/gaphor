#!/bin/bash

set -euo pipefail

APP=Gaphor.app
MACOSDIR=Gaphor.app/Contents/MacOS
EXITCODE=0

function log() {
  echo "$*" >&2
}

function err() {
  echo "ERROR: $*" >&2
  EXITCODE=1
}

test -d $MACOSDIR || err "Missing MacOS directory"

#echo Gaphor.app/Contents/lib/libicuuc.63.1.dylib |\
find $APP -type f -exec file {} \; | grep 'Mach-O\|G-IR' | cut -f1 -d: |\
while read lib
do
  #log Validating $lib
  otool -L $lib | grep -e '^\t' |\
  while read dep _
  do
    if [[ "$dep" =~ ^@loader_path ]]
    then
      test -f ${dep//@loader_path/$(dirname $lib)} || err "Dependency $dep of $lib missing!"
    else
      test -f ${dep//@executable_path/$MACOSDIR} || err "Dependency $dep of $lib missing!"
    fi
  done
done

exit $EXITCODE
