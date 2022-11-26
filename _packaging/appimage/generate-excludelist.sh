#!/usr/bin/env bash

set -euo pipefail

# DIR is the parent directory
DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")"
cd "${DIR}"

EXCLUDELIST_TEMPLATE="https://github.com/AppImage/AppImages/raw/master/excludelist"
EXCLUDELIST="$DIR"/appimage/excludelist

function validate_url(){
  if wget --spider "$1" 2>/dev/null; then
    echo "excludelist URL exists";
  else
    echo "URL is invalid";
  fi
}
validate_url $EXCLUDELIST_TEMPLATE

FILES=$(wget -qO- $EXCLUDELIST_TEMPLATE | sed '/^\s*$/d' | sed '/^#.*$/d' | cut -d " " -f 1)

rm -f -- "$EXCLUDELIST"

for FILE in $FILES; do
  find "$DIR"/dist/gaphor -name "$FILE" -type f -print | cut -d "/" -f 6 >> "$EXCLUDELIST";
done

sort -u -o "$EXCLUDELIST" "$EXCLUDELIST"
echo "Exclude list generated!"
