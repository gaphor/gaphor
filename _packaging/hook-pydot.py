# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
# Adapted for pydot
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

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
        "gvplugin_" not in binary
        or "gvplugin_core" in binary
        or "gvplugin_dot_layout" in binary
        or "gvplugin_neato_layout" in binary
    )


if is_win:
    # For Windows, we move all graphviz stuff in a separate folder.
    # This way the GV binaries do not interfere with Gaphor.

    # 13-10-2022  12:56            24.576 cdt.dll
    # 13-10-2022  12:56            11.264 cgraph++.dll
    # 13-10-2022  12:56            74.240 cgraph.dll
    # 11-10-2022  11:36             3.057 config6
    # 13-10-2022  12:56            10.752 dot.exe
    # 13-10-2022  12:56           184.832 expat.dll
    # 13-10-2022  12:56            19.968 getopt.dll
    # 13-10-2022  12:56            18.432 gvc++.dll
    # 13-10-2022  12:56           552.960 gvc.dll
    # 13-10-2022  12:56           123.904 gvplugin_core.dll
    # 13-10-2022  12:56           158.208 gvplugin_dot_layout.dll
    # 13-10-2022  12:56           368.128 gvplugin_neato_layout.dll
    # 13-10-2022  12:56            39.936 pathplan.dll
    # 13-10-2022  12:56           101.664 vcruntime140.dll
    # 13-10-2022  12:56            44.328 vcruntime140_1.dll

    for prog in progs:
        binaries.extend(
            (binary, "graphviz")
            for binary in glob.glob(f"c:/Program Files/Graphviz*/bin/{prog}.exe")
        )

    # Do not include all plugins: some have dependencys on Pango and Cairo, different version from what we need
    binaries.extend(
        (binary, "graphviz")
        for binary in glob.glob("c:/Program Files/Graphviz*/bin/*.dll")
        if required_plugin(binary)
    )

    # Instead of opying the config file, what we should really do is call `dot -c` on our new plugins folder.
    datas.extend(
        (data, "graphviz")
        for data in glob.glob("c:/Program Files/Graphviz*/bin/config*")
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
