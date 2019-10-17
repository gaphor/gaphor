"""
This file provides the code generator which transforms gaphor/UML/uml2.gaphor
into gaphor/UML/uml2.py.

Also a distutils tool, build_uml, is provided.
"""

import os.path
from distutils.core import Command
from distutils.dep_util import newer
from distutils.util import byte_compile
from distutils.dir_util import mkpath

from utils.model import gen_uml


class build_uml(Command):

    description = "Generate gaphor/UML/uml2.py."

    user_options = [("force", "f", "force installation (overwrite existing files)")]

    boolean_options = ["force"]

    def initialize_options(self):
        self.force = None

    def finalize_options(self):
        if self.force is None:
            self.force = False

    def run(self):
        generate_uml2(self.force)


def generate_uml2(force=False):
    """
    Generate gaphor/UML/uml2.py in the source directory.
    """
    gen = os.path.join("utils", "model", "gen_uml.py")
    overrides = os.path.join("gaphor", "UML", "uml2.override")
    model = os.path.join("gaphor", "UML", "uml2.gaphor")
    py_model = os.path.join("gaphor", "UML", "uml2.py")
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
