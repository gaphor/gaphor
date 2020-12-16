"""Fix the macOS application to allow codesign.

Take one or more .app as arguments: "Gaphor-X.X.X.app".

Folders containing a dot in their name like gdk-pixbuf-2.0 are not
allowed in the `Contents/MacOS folder. This script fixes these issues by:
- Moving problematic folders from MacOS to Resources
- Creating the appropriate symbolic link

This script is originally based on:
https://github.com/pyinstaller/pyinstaller/wiki/Recipe-OSX-Code-Signing-Qt
from Mickaël Schoentgen (BoboTiG) and Ben Hagen (cbenhagen)
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Generator, List


def create_symlink(folder: Path) -> None:
    """Create the symlink.

    Creates a symlink in the MacOS folder pointing to the Resources
    folder.
    """
    sibbling = Path(str(folder).replace("MacOS", ""))

    root = str(sibbling).partition("Contents")[2].lstrip("/")
    backward = "../" * (root.count("/") + 1)
    good_path = f"{backward}Resources/{root}"
    print(f"Symlinking to {good_path}")

    folder.symlink_to(good_path)


def find_problematic_folders(folder: Path) -> Generator[Path, None, None]:
    """Recursively yields problematic folders.

    Problematic folders have a dot in their name.
    """
    for path in folder.iterdir():
        if not path.is_dir() or path.is_symlink():
            # Skip simlinks as they are allowed (even with a dot)
            continue
        if "." in path.name:
            print(f"{path} needs to be fixed")
            yield path
        else:
            yield from find_problematic_folders(path)


def main(args: List[str]):
    for app in args:
        name = os.path.basename(app)
        print(f"Fixing GTK folder names {name}")
        path = Path(app) / "Contents" / "MacOS"
        for folder in find_problematic_folders(path):
            shutil.rmtree(folder)
            create_symlink(folder)
            print(f"Completed fixing {folder}")
        print("Application fixed.")


if __name__ == "__main__":
    main(sys.argv[1:])
