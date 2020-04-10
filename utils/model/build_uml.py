#!/usr/bin/env python
"""
This file provides the code generator which transforms models/UML.gaphor
into gaphor/UML/uml2.py.
"""

import os.path
from distutils.util import byte_compile

from utils.model import gen_uml


def generate_uml2(force=False):
    """
    Generate gaphor/UML/uml2.py in the source directory.
    """
    gen = os.path.join("utils", "model", "gen_uml.py")
    overrides = os.path.join("models", "UML.override")
    model = os.path.join("models", "UML.gaphor")
    py_model = os.path.join("gaphor", "UML", "uml2.py")
    outfile = py_model

    print(f"generating {py_model} from {model}...")
    print("  (warnings can be ignored)")

    gen_uml.generate(model, outfile, overrides)
    byte_compile([outfile])


if __name__ == "__main__":
    generate_uml2()
