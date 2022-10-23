import os
import sys

# https://github.com/pyinstaller/pyinstaller/issues/6100
# On one Windows computer, PyInstaller was adding a ; to
# end of the path, this removes it if it exists
if os.environ["PATH"][-1] == ";":
    os.environ["PATH"] = os.environ["PATH"][:-1]

# Check for and remove two semicolons in path
os.environ["PATH"] = os.environ["PATH"].replace(";;", ";")

os.environ["GAPHOR_USE_GTK"] = "4"

from gaphor.ui import main

sys.exit(main(sys.argv))
