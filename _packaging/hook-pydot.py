# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------
# Adapted for Gaphor and Pydot by Arjan Molenaar

import glob
import os
import shutil

from PyInstaller.compat import is_darwin, is_win
from PyInstaller.depend.bindepend import findLibrary

binaries: list[tuple[str, str]] = []
datas: list[tuple[str, str]] = []

# List of binaries agraph.py may invoke.
progs = [
    "dot",
]


def required_plugin(binary):
    return (
        "gvplugin_core" in binary
        or "gvplugin_dot_layout" in binary
        or "gvplugin_neato_layout" in binary
    )


if is_win:
    # For Windows, we move the minimal number of graphviz binaries to a separate folder.
    # This way the GV binaries do not interfere with Gaphor.
    files = [
        "dot.exe",
        "cdt.dll",
        "cgraph++.dll",
        "cgraph.dll",
        "getopt.dll",
        "gvc++.dll",
        "gvc.dll",
        "gvplugin_core.dll",
        "gvplugin_dot_layout.dll",
        "gvplugin_neato_layout.dll",
        "pathplan.dll",
        "vcruntime140.dll",
        "vcruntime140_1.dll",
    ]

    binaries.extend((f"C:/Program Files/Graphviz/bin/{f}", "graphviz") for f in files)

    # Instead of copying the config file, what we should really do
    # is call `dot -c` on our new plugins folder.
    datas.extend(
        (data, "graphviz")
        for data in glob.glob("C:/Program Files/Graphviz/bin/config*")
    )

else:
    if is_darwin:
        # The dot binary in PATH is typically a symlink, handle that.
        # graphviz_bindir is e.g. /usr/local/Cellar/graphviz/2.46.0/bin
        graphviz_bindir = os.path.dirname(os.path.realpath(shutil.which("dot")))  # type: ignore[type-var]

        suffix = "dylib"
        # graphviz_libdir is e.g. /usr/local/Cellar/graphviz/2.46.0/lib/graphviz
        graphviz_libdir = os.path.realpath(f"{graphviz_bindir}/../lib/graphviz")
    else:
        # Do not resolve symlinks: on Ubuntu Bionic, the symlink is
        # /usr/bin/dot -> ../sbin/libgvc6-config-update
        graphviz_bindir = os.path.dirname(shutil.which("dot"))  # type: ignore[type-var]

        suffix = "so.?"
        # graphviz_libdir is e.g. /usr/lib64/graphviz
        graphviz_libdir = os.path.join(
            os.path.dirname(findLibrary("libcdt")), "graphviz"
        )

    binaries.extend((f"{graphviz_bindir}/{binary}", ".") for binary in progs)
    binaries.extend(
        (binary, "graphviz")
        for binary in glob.glob(f"{graphviz_libdir}/*.{suffix}")
        if required_plugin(binary)
    )

    datas.extend((data, "graphviz") for data in glob.glob(f"{graphviz_libdir}/config*"))
