#!/usr/bin/env python
"""
This file provides the code generator which transforms gaphor/UML/uml2.gaphor
into gaphor/UML/uml2.py.

Also a distutils tool, build_uml, is provided.
"""

import os.path
from distutils.core import Command
from distutils.dep_util import newer
from distutils.dir_util import mkpath
from distutils.util import byte_compile

from utils.model import gen_uml


def generate_uml2(force=False):
    """
    Generate gaphor/UML/uml2.py in the source directory.
    """
    gen = os.path.join("utils", "model", "gen_uml.py")
    overrides = os.path.join("models", "Core.override")
    model = os.path.join("models", "Core.gaphor")
    py_model = os.path.join("gaphor", "core", "modeling", "coremodel.py")
    outfile = py_model
    mkpath(os.path.dirname(outfile))
    if (
        force
        or newer(model, outfile)
        or newer(overrides, outfile)
        or newer(gen, outfile)
    ):
        print(f"generating {py_model} from {model}...")
        print("  (warnings can be ignored)")

        gen_uml.generate(model, outfile, overrides)
    else:
        print(f"not generating {py_model} (up-to-date)")
    byte_compile([outfile])


if __name__ == "__main__":
    generate_uml2()
