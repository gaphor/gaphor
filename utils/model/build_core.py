#!/usr/bin/env python
"""
This file provides the code generator which transforms models/Core.gaphor
into gaphor/core/modeling/coremodel.py.
"""

import os.path
from distutils.util import byte_compile

from utils.model import gen_uml


def generate_core(force=False):
    """
    Generate gaphor/core/modeling/coremodel.py in the source directory.
    """
    gen = os.path.join("utils", "model", "gen_uml.py")
    overrides = os.path.join("models", "Core.override")
    model = os.path.join("models", "Core.gaphor")
    py_model = os.path.join("gaphor", "core", "modeling", "coremodel.py")
    outfile = py_model

    print(f"generating {py_model} from {model}...")
    print("  (warnings can be ignored)")

    gen_uml.generate(model, outfile, overrides)
    byte_compile([outfile])


if __name__ == "__main__":
    generate_core()
