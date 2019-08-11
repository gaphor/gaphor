#!C:/tools/msys64/home/DYEAW/gaphor/.venv/bin/python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'gaphor','console_scripts','gaphor'
import re
import sys
import importlib_metadata


if __name__ == '__main__':
    eps = importlib_metadata.entry_points()
    scripts = eps["console_scripts"]
    gaphor = [ep for ep in scripts if ep.name == "gaphor"][0]
    main = gaphor.load()
    main()

