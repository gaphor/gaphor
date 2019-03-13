"""
This file provides the code generator which transforms gaphor/UML/uml2.gaphor
into gaphor/UML/uml2.py.

Also a distutils tool, build_uml, is provided.
"""

import os.path
from distutils.core import Command
from distutils.dep_util import newer
from distutils.util import byte_compile


class build_uml(Command):

    description = "Generate gaphor/UML/uml2.py."

    user_options = [
        ("build-lib=", "b", "build directory (where to install from)"),
        ("force", "f", "force installation (overwrite existing files)"),
    ]

    boolean_options = ["force"]

    def initialize_options(self):
        # self.build_lib = None
        self.force = 0
        self.data_dir = None

    def finalize_options(self):
        self.set_undefined_options(
            "build",
            # ('build_lib', 'build_lib'),
            ("force", "force"),
        )

    def run(self):
        # sys.path.insert(0, self.build_lib)
        self.generate_uml2()

    def generate_uml2(self):
        """
        Generate gaphor/UML/uml2.py in the build directory.
        """
        gen = os.path.join("utils", "command", "gen_uml.py")
        overrides = os.path.join("gaphor", "UML", "uml2.override")
        model = os.path.join("gaphor", "UML", "uml2.gaphor")
        py_model = os.path.join("gaphor", "UML", "uml2.py")
        outfile = py_model  # os.path.join(self.build_lib, py_model)
        self.mkpath(os.path.dirname(outfile))
        if (
            self.force
            or newer(model, outfile)
            or newer(overrides, outfile)
            or newer(gen, outfile)
        ):
            print("generating %s from %s..." % (py_model, model))
            print("  (warnings can be ignored)")
            from . import gen_uml

            gen_uml.generate(model, outfile, overrides)
        else:
            print("not generating %s (up-to-date)" % py_model)
        byte_compile([outfile])


# vim:sw=4:et
