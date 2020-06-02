#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2016,2017 Christoph Reiter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Deletes unneeded DLLs and checks DLL dependencies.
Execute with the build python, will figure out the rest.
"""

import os
import subprocess
import sys
from multiprocessing import Process, Queue

import gi
from gi.repository import GIRepository

gi.require_version("GIRepository", "2.0")


def _get_shared_libraries(q, namespace, version):
    repo = GIRepository.Repository()
    repo.require(namespace, version, 0)
    lib = repo.get_shared_library(namespace)
    q.put(lib)


def get_shared_libraries(namespace, version):
    # we have to start a new process because multiple versions can't be loaded
    # in the same process
    q = Queue()
    p = Process(target=_get_shared_libraries, args=(q, namespace, version))
    p.start()
    result = q.get()
    p.join()
    return result


def get_required_by_typelibs():
    deps = set()
    repo = GIRepository.Repository()
    for tl in os.listdir(repo.get_search_path()[0]):
        namespace, version = os.path.splitext(tl)[0].split("-", 1)
        lib = get_shared_libraries(namespace, version)
        libs = lib.lower().split(',') if lib else []
        for lib in libs:
            deps.add((namespace, version, lib))
    return deps


def get_dependencies(filename):
    deps = []
    try:
        data = subprocess.check_output(
            ["objdump", "-p", filename], stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        # can happen with wrong arch binaries
        return []
    data = data.decode("utf-8")
    for line in data.splitlines():
        line = line.strip()
        if line.startswith("DLL Name:"):
            deps.append(line.split(":", 1)[-1].strip().lower())
    return deps


def find_lib(root, name):
    system_search_path = os.path.join("C:", os.sep, "Windows", "System32")
    if get_lib_path(root, name):
        return True
    elif os.path.exists(os.path.join(system_search_path, name)):
        return True
    elif name in ["gdiplus.dll"]:
        return True
    elif name.startswith("msvcr"):
        return True
    return False


def get_lib_path(root, name):
    search_path = os.path.join(root, "bin")
    if os.path.exists(os.path.join(search_path, name)):
        return os.path.join(search_path, name)


def get_things_to_delete(root):
    extensions = [".exe", ".pyd", ".dll"]

    all_libs = set()
    needed = set()
    for base, dirs, files in os.walk(root):
        for f in files:
            lib = f.lower()
            path = os.path.join(base, f)
            ext_lower = os.path.splitext(f)[-1].lower()
            if ext_lower in extensions:
                if ext_lower == ".exe":
                    # we use .exe as dependency root
                    needed.add(lib)
                all_libs.add(f.lower())
                for lib in get_dependencies(path):
                    all_libs.add(lib)
                    needed.add(lib)
                    if not find_lib(root, lib):
                        print("MISSING:", path, lib)

    for namespace, version, lib in get_required_by_typelibs():
        all_libs.add(lib)
        needed.add(lib)
        if not find_lib(root, lib):
            print("MISSING:", namespace, version, lib)

    to_delete = []
    for not_depended_on in all_libs - needed:
        path = get_lib_path(root, not_depended_on)
        if path:
            to_delete.append(path)

    return to_delete


def main(argv):
    libs = get_things_to_delete(sys.prefix)

    if "--delete" in argv[1:]:
        while libs:
            for lib in libs:
                print("DELETE:", lib)
                os.unlink(lib)
            libs = get_things_to_delete(sys.prefix)


if __name__ == "__main__":
    main(sys.argv)
