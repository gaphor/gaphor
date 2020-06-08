#!/bin/bash

set -e

rsvg-convert ../../logos/org.gaphor.Gaphor.svg | convert -scale 48x48 - gaphor.ico

# ../_build_root/mingw64/bin/magick convert ../../logos/gaphor-48x48.png gaphor2.ico
