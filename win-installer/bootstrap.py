import subprocess


# Update pacman packages
subprocess.run("pacman -Suy")

# install pygobject development environment
subprocess.run(
    [
        "pacman -s --needed --noconfirm",
        "base-devel",
        "mingw-w64-x86_64-toolchain",
        "git",
        "mingw-w64-x86_64-python3",
        "mingw-w64-x86_64-python3-cairo",
        "mingw-w64-x86_64-python3-gobject",
        "mingw-w64-x86_64-python3-pip",
        "mingw-w64-x86_64-setuptools",
    ]
)

# Install Gaphor dependencies
subprocess.run("pip3 install --user -U" "gaphas" "pycairo" "PyGObject")
