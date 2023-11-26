#!/bin/bash

set -e

rsvg-convert ../../data/logos/org.gaphor.Gaphor.svg | magick convert -scale 48x48 - gaphor.ico
