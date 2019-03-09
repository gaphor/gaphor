import subprocess


# Update pacman packages
subprocess.run("pacman -Suy")

# Install PyGObject Development Environment
subprocess.run(
    "pacman -S --needed --noconfirm"
    "base-devel"
    "mingw-w64-x68_64-toolchain"
    "git"
    "mingw-w64-x68_64-python3"
    "mingw-w64-x68_64-python3-cairo"
    "mingw-w64-x68_64-gobject-introspection"
    "mingw-w64-x68_64-libffi"
    "mingw-w64-x68_64-python3-pip"
    "mingw-w64-x68_64-setuptools"
)

# Install Gaphor dependencies
subprocess.run("pip3 install --user -U" "gaphas" "zope.component")
